import cv2
import mediapipe as mp
import numpy as np
from ..core.utils import apply_moving_average

class PoseDetector:
    def __init__(self, min_detection_confidence=0.8, min_tracking_confidence=0.8, moving_average_window=5):
        """
        Inicializa o detector de pose usando MediaPipe Holistic.
        
        Args:
            min_detection_confidence (float): Confiança mínima para detecção
            min_tracking_confidence (float): Confiança mínima para rastreamento
            moving_average_window (int): Tamanho da janela para média móvel
        """
        self.mp_holistic = mp.solutions.holistic
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.holistic = self.mp_holistic.Holistic(
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        self.moving_average_window = moving_average_window
        self.landmarks_history = []
    
    def detect(self, frame):
        """
        Detecta landmarks de pose em um frame.
        
        Args:
            frame (numpy.ndarray): Frame a ser processado
            
        Returns:
            tuple: (frame RGB, resultados do MediaPipe)
        """
        # Converte o frame para RGB (MediaPipe usa RGB)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Processa o frame
        results = self.holistic.process(frame_rgb)
        
        # Aplica média móvel se houver landmarks de pose
        if results.pose_landmarks:
            results.pose_landmarks = apply_moving_average(
                self.landmarks_history, 
                results.pose_landmarks, 
                self.moving_average_window
            )
        
        return frame_rgb, results
    
    def get_landmark_coordinates(self, results, landmark_id, image_width, image_height):
        """
        Obtém as coordenadas de um landmark específico.
        
        Args:
            results: Resultados do MediaPipe
            landmark_id (int): ID do landmark
            image_width (int): Largura da imagem
            image_height (int): Altura da imagem
            
        Returns:
            tuple: Coordenadas (x, y) do landmark ou None se não for detectado
        """
        if not results.pose_landmarks:
            return None
        
        landmark = results.pose_landmarks.landmark[landmark_id]
        
        # Converte as coordenadas normalizadas para coordenadas de pixel
        x = int(landmark.x * image_width)
        y = int(landmark.y * image_height)
        
        # Verifica se o landmark está visível
        if landmark.visibility < 0.5:
            return None
            
        return (x, y)
    
    def get_all_landmarks(self, results, image_width, image_height):
        """
        Obtém as coordenadas de todos os landmarks detectados.
        
        Args:
            results: Resultados do MediaPipe
            image_width (int): Largura da imagem
            image_height (int): Altura da imagem
            
        Returns:
            dict: Dicionário com as coordenadas de todos os landmarks detectados
        """
        landmarks = {}
        
        if not results.pose_landmarks:
            return landmarks
        
        for i, landmark in enumerate(results.pose_landmarks.landmark):
            # Converte as coordenadas normalizadas para coordenadas de pixel
            x = int(landmark.x * image_width)
            y = int(landmark.y * image_height)
            
            # Adiciona o landmark ao dicionário se estiver visível
            if landmark.visibility >= 0.5:
                landmarks[i] = (x, y)
                
        return landmarks
    
    def determine_more_visible_side(self, landmarks):
        """
        Determina qual lado do corpo está mais visível.
        
        Args:
            landmarks (dict): Dicionário com as coordenadas dos landmarks
            
        Returns:
            str: 'left' ou 'right'
        """
        # Landmarks do lado esquerdo e direito para verificar
        left_landmarks = [11, 13, 15, 23, 25, 27]  # Ombro, cotovelo, pulso, quadril, joelho, tornozelo esquerdos
        right_landmarks = [12, 14, 16, 24, 26, 28]  # Ombro, cotovelo, pulso, quadril, joelho, tornozelo direitos
        
        left_visible = sum(1 for lm in left_landmarks if lm in landmarks)
        right_visible = sum(1 for lm in right_landmarks if lm in landmarks)
        
        return 'left' if left_visible >= right_visible else 'right'
        
    def should_process_lower_body(self, landmarks):
        """
        Determina se deve processar a parte inferior do corpo com base na visibilidade dos landmarks.
        
        Args:
            landmarks (dict): Dicionário com as coordenadas dos landmarks
            
        Returns:
            bool: True se deve processar a parte inferior do corpo, False caso contrário
        """
        # IDs dos landmarks inferiores (joelho, tornozelo, pé)
        lower_landmarks_ids = [25, 26, 27, 28, 31, 32]  # Joelhos, tornozelos, pés
        
        # IDs dos landmarks superiores (ombro, cotovelo, pulso)
        upper_landmarks_ids = [11, 12, 13, 14, 15, 16]  # Ombros, cotovelos, pulsos
        
        # Verifica a visibilidade dos landmarks inferiores
        lower_landmarks_visible = sum(1 for lm_id in lower_landmarks_ids if lm_id in landmarks)
        lower_visibility_avg = lower_landmarks_visible / len(lower_landmarks_ids) if lower_landmarks_ids else 0
        
        # Verifica a visibilidade dos landmarks superiores
        upper_landmarks_visible = sum(1 for lm_id in upper_landmarks_ids if lm_id in landmarks)
        upper_visibility_avg = upper_landmarks_visible / len(upper_landmarks_ids) if upper_landmarks_ids else 0
        
        # Verifica se os tornozelos e pés estão visíveis
        ankle_foot_visible = any(lm_id in landmarks for lm_id in [27, 28, 31, 32])
        
        # Se os tornozelos ou pés não estiverem visíveis, processa como imagem de perfil (ângulos superiores)
        if not ankle_foot_visible:
            return False
        
        # Compara a visibilidade dos landmarks inferiores com os superiores
        # Se os landmarks inferiores têm visibilidade significativamente maior que os superiores
        # ou se os landmarks inferiores têm visibilidade muito alta em geral, processa como parte inferior
        if lower_landmarks_visible >= 4 and (lower_visibility_avg > upper_visibility_avg * 0.8 or lower_visibility_avg > 0.8):
            return True
        
        return False
    
    def get_face_landmarks(self, results, image_width, image_height):
        """
        Obtém os landmarks do rosto.
        
        Args:
            results: Resultados do MediaPipe
            image_width (int): Largura da imagem
            image_height (int): Altura da imagem
            
        Returns:
            dict: Dicionário com os landmarks do rosto
        """
        face_landmarks = {}
        
        # Verifica se há landmarks de face mesh
        if results.face_landmarks:
            for i, landmark in enumerate(results.face_landmarks.landmark):
                # Converte as coordenadas normalizadas para coordenadas de pixel
                x = int(landmark.x * image_width)
                y = int(landmark.y * image_height)
                
                face_landmarks[i] = (x, y)
        
        return face_landmarks
    
    def release(self):
        """
        Libera os recursos do detector.
        """
        self.holistic.close()