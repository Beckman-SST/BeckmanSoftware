import cv2
import numpy as np
import mediapipe as mp

# Configurações globais do MediaPipe
mpDraw = mp.solutions.drawing_utils
mpDrawingStyles = mp.solutions.drawing_styles
mpHolistic = mp.solutions.holistic
mpPose = mp.solutions.pose

# Cores para desenho específicas para vídeos
landmark_color = (245, 117, 66)  # Laranja para landmarks
connection_color = (214, 121, 108)  # Rosa para conexões
text_color = (255, 255, 255)  # Branco para texto

# Define as conexões personalizadas para vídeos (lógica original)
custom_video_pose_connections = [
    # Corpo superior
    (11, 13), (13, 15),  # Braço esquerdo
    (12, 14), (14, 16),  # Braço direito
    (11, 12),            # Ombros
    (11, 23), (12, 24),  # Tronco
    
    # Corpo inferior
    (23, 24),            # Quadril
    (23, 25), (25, 27),  # Perna esquerda
    (24, 26), (26, 28),  # Perna direita
    (27, 31), (28, 32),  # Tornozelo-pé
    (27, 29), (28, 30)   # Tornozelo-calcanhar
]

class VideoVisualizer:
    """
    Visualizador específico para processamento de vídeos.
    Mantém a lógica original de desenho de landmarks para vídeos.
    """
    
    def __init__(self, tarja_ratio=0.20):
        """
        Inicializa o visualizador de vídeo.
        
        Args:
            tarja_ratio (float): Proporção da largura do frame para calcular tamanho mínimo da tarja (padrão: 0.20 = 20%)
        """
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        self.tarja_ratio = tarja_ratio  # Proporção para calcular tamanho da tarja
        
    def draw_video_landmarks(self, frame, results, show_upper_body=True, show_lower_body=True):
        """
        Desenha landmarks de pose especificamente para vídeos usando a lógica original.
        
        Args:
            frame (numpy.ndarray): Frame onde os landmarks serão desenhados
            results: Resultados do MediaPipe
            show_upper_body (bool): Se True, desenha landmarks do corpo superior
            show_lower_body (bool): Se True, desenha landmarks do corpo inferior
            
        Returns:
            numpy.ndarray: Frame com os landmarks desenhados
        """
        if not results.pose_landmarks:
            return frame
            
        try:
            # Obtém dimensões do frame
            h, w, _ = frame.shape
            
            # Converte landmarks para coordenadas de pixel
            landmarks_dict = {}
            for i, landmark in enumerate(results.pose_landmarks.landmark):
                if landmark.visibility >= 0.5:  # Só considera landmarks visíveis
                    x = int(landmark.x * w)
                    y = int(landmark.y * h)
                    landmarks_dict[i] = (x, y)
            
            # Filtra conexões baseado nas configurações
            connections_to_draw = self._filter_video_connections(
                show_upper_body, 
                show_lower_body
            )
            
            # Desenha as conexões personalizadas
            self._draw_video_connections(
                frame, 
                landmarks_dict, 
                connections_to_draw
            )
            
            # Desenha os landmarks
            self._draw_video_landmarks_points(
                frame, 
                landmarks_dict, 
                show_upper_body, 
                show_lower_body
            )
            
        except Exception as e:
            print(f"Erro ao desenhar landmarks do vídeo: {str(e)}")
            
        return frame
    
    def _filter_video_connections(self, show_upper_body, show_lower_body):
        """
        Filtra as conexões baseado nas configurações de exibição.
        
        Args:
            show_upper_body (bool): Se deve mostrar corpo superior
            show_lower_body (bool): Se deve mostrar corpo inferior
            
        Returns:
            list: Lista de conexões filtradas
        """
        filtered_connections = []
        
        # IDs dos landmarks do corpo superior
        upper_body_ids = [11, 12, 13, 14, 15, 16]
        
        # IDs dos landmarks do corpo inferior
        lower_body_ids = [23, 24, 25, 26, 27, 28, 29, 30, 31, 32]
        
        for connection in custom_video_pose_connections:
            start_id, end_id = connection
            
            # Verifica se a conexão pertence ao corpo superior
            is_upper = (start_id in upper_body_ids or end_id in upper_body_ids)
            
            # Verifica se a conexão pertence ao corpo inferior
            is_lower = (start_id in lower_body_ids or end_id in lower_body_ids)
            
            # Adiciona a conexão se deve ser mostrada
            if (show_upper_body and is_upper) or (show_lower_body and is_lower):
                filtered_connections.append(connection)
        
        return filtered_connections
    
    def _draw_video_connections(self, frame, landmarks_dict, connections):
        """
        Desenha as conexões entre landmarks.
        
        Args:
            frame (numpy.ndarray): Frame onde desenhar
            landmarks_dict (dict): Dicionário com coordenadas dos landmarks
            connections (list): Lista de conexões para desenhar
        """
        for connection in connections:
            start_id, end_id = connection
            
            if start_id in landmarks_dict and end_id in landmarks_dict:
                start_point = landmarks_dict[start_id]
                end_point = landmarks_dict[end_id]
                
                cv2.line(
                    frame, 
                    start_point, 
                    end_point, 
                    connection_color, 
                    thickness=4
                )
    
    def _draw_video_landmarks_points(self, frame, landmarks_dict, show_upper_body, show_lower_body):
        """
        Desenha os pontos dos landmarks.
        
        Args:
            frame (numpy.ndarray): Frame onde desenhar
            landmarks_dict (dict): Dicionário com coordenadas dos landmarks
            show_upper_body (bool): Se deve mostrar corpo superior
            show_lower_body (bool): Se deve mostrar corpo inferior
        """
        # IDs dos landmarks do corpo superior
        upper_body_ids = [11, 12, 13, 14, 15, 16]
        
        # IDs dos landmarks do corpo inferior
        lower_body_ids = [23, 24, 25, 26, 27, 28, 29, 30, 31, 32]
        
        for landmark_id, (x, y) in landmarks_dict.items():
            # Verifica se deve desenhar este landmark
            should_draw = False
            
            if show_upper_body and landmark_id in upper_body_ids:
                should_draw = True
            elif show_lower_body and landmark_id in lower_body_ids:
                should_draw = True
            
            if should_draw:
                cv2.circle(
                    frame, 
                    (x, y), 
                    radius=4, 
                    color=landmark_color, 
                    thickness=-1  # Preenchido
                )
    
    def apply_face_blur(self, frame, face_landmarks=None, eye_landmarks=None):
        """
        Aplica tarja no rosto usando landmarks faciais ou dos olhos.
        Método específico para vídeos que mantém compatibilidade.
        
        Args:
            frame (numpy.ndarray): Frame onde aplicar a tarja
            face_landmarks (dict): Landmarks faciais (prioridade)
            eye_landmarks (dict): Landmarks dos olhos (fallback)
            
        Returns:
            numpy.ndarray: Frame com tarja aplicada
        """
        try:
            if face_landmarks:
                # Usa landmarks faciais completos
                return self._apply_face_tarja_from_face(frame, face_landmarks)
            elif eye_landmarks:
                # Usa landmarks dos olhos como fallback
                return self._apply_face_tarja_from_eyes(frame, eye_landmarks)
            else:
                return frame
                
        except Exception as e:
            print(f"Erro ao aplicar tarja facial: {str(e)}")
            return frame
    
    def _apply_face_tarja_from_face(self, frame, face_landmarks):
        """
        Aplica tarja baseada em landmarks faciais completos.
        Usa tamanho fixo grande para garantir privacidade constante.
        """
        if not face_landmarks:
            return frame
            
        # Calcula centro dos landmarks faciais
        x_coords = [coord[0] for coord in face_landmarks.values()]
        y_coords = [coord[1] for coord in face_landmarks.values()]
        
        if not x_coords or not y_coords:
            return frame
            
        center_x = sum(x_coords) // len(x_coords)
        center_y = sum(y_coords) // len(y_coords)
        
        # Calcula tamanho da tarja baseado na largura do frame (similar ao processamento de imagens)
        frame_width = frame.shape[1]
        tarja_size = max(100, int(frame_width * self.tarja_ratio))  # Mínimo 100px, máximo 20% da largura
        
        # Calcula coordenadas do quadrado centrado
        half_size = tarja_size // 2
        x_min = max(0, center_x - half_size)
        y_min = max(0, center_y - half_size)
        x_max = min(frame.shape[1], center_x + half_size)
        y_max = min(frame.shape[0], center_y + half_size)
        
        # Aplica retângulo preto quadrado
        cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 0, 0), -1)
        
        return frame
    
    def _apply_face_tarja_from_eyes(self, frame, eye_landmarks):
        """
        Aplica tarja baseada em landmarks dos olhos.
        Usa tamanho fixo grande para garantir privacidade constante.
        """
        if not eye_landmarks:
            return frame
            
        # Procura por landmarks dos olhos (IDs 2 e 5 do MediaPose)
        left_eye = eye_landmarks.get(2)  # LEFT_EYE
        right_eye = eye_landmarks.get(5)  # RIGHT_EYE
        
        if left_eye and right_eye:
            # Calcula centro baseado nos dois olhos
            center_x = (left_eye[0] + right_eye[0]) // 2
            center_y = (left_eye[1] + right_eye[1]) // 2
        elif left_eye:
            # Usa apenas olho esquerdo
            center_x, center_y = left_eye[0], left_eye[1]
        elif right_eye:
            # Usa apenas olho direito
            center_x, center_y = right_eye[0], right_eye[1]
        else:
            # Tenta usar outros landmarks faciais disponíveis
            available_landmarks = [(x, y) for x, y in eye_landmarks.values() if x > 0 and y > 0]
            if not available_landmarks:
                return frame
            center_x = sum(x for x, y in available_landmarks) // len(available_landmarks)
            center_y = sum(y for x, y in available_landmarks) // len(available_landmarks)
        
        # Calcula tamanho da tarja baseado na largura do frame (similar ao processamento de imagens)
        frame_width = frame.shape[1]
        tarja_size = max(100, int(frame_width * self.tarja_ratio))  # Mínimo 100px, máximo 20% da largura
        
        # Calcula coordenadas do quadrado centrado
        half_size = tarja_size // 2
        x_min = max(0, center_x - half_size)
        y_min = max(0, center_y - half_size)
        x_max = min(frame.shape[1], center_x + half_size)
        y_max = min(frame.shape[0], center_y + half_size)
        
        # Aplica retângulo preto quadrado
        cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 0, 0), -1)
        
        return frame