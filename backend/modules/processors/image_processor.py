import cv2
import numpy as np
import os
from ..core.utils import ensure_directory_exists, resize_frame
from ..detection.pose_detector import PoseDetector
from ..detection.electronics_detector import ElectronicsDetector
from ..analysis.angle_analyzer import AngleAnalyzer
from ..visualization.pose_visualizer import PoseVisualizer

class ImageProcessor:
    def __init__(self, config):
        """
        Inicializa o processador de imagens.
        
        Args:
            config (dict): Configurações para o processamento
        """
        self.config = config
        
        # Inicializa os detectores e analisadores
        self.pose_detector = PoseDetector(
            min_detection_confidence=config.get('min_detection_confidence', 0.8),
            min_tracking_confidence=config.get('min_tracking_confidence', 0.8),
            moving_average_window=config.get('moving_average_window', 5)
        )
        
        self.electronics_detector = ElectronicsDetector(
            yolo_confidence=config.get('yolo_confidence', 0.65)
        )
        
        self.angle_analyzer = AngleAnalyzer()
        self.visualizer = PoseVisualizer()
    
    def process_image(self, image_path, output_folder):
        """
        Processa uma imagem.
        
        Args:
            image_path (str): Caminho da imagem a ser processada
            output_folder (str): Pasta onde a imagem processada será salva
            
        Returns:
            tuple: (sucesso, caminho da imagem processada ou mensagem de erro)
        """
        try:
            # Verifica se a imagem existe
            if not os.path.exists(image_path):
                return False, f"Arquivo não encontrado: {image_path}"
            
            # Verifica se a pasta de saída existe, se não, cria
            ensure_directory_exists(output_folder)
            
            # Carrega a imagem
            frame = cv2.imread(image_path)
            if frame is None:
                return False, f"Não foi possível carregar a imagem: {image_path}"
            
            # Redimensiona o frame se necessário
            resize_width = self.config.get('resize_width')
            if resize_width and resize_width > 0:
                frame = resize_frame(frame, resize_width)
            
            # Processa o frame
            processed_frame = self._process_frame(frame)
            
            # Salva a imagem processada
            output_filename = os.path.basename(image_path)
            output_path = os.path.join(output_folder, output_filename)
            cv2.imwrite(output_path, processed_frame)
            
            return True, output_path
        
        except Exception as e:
            return False, f"Erro ao processar a imagem: {str(e)}"
    
    def _process_frame(self, frame):
        """
        Processa um frame.
        
        Args:
            frame (numpy.ndarray): Frame a ser processado
            
        Returns:
            numpy.ndarray: Frame processado
        """
        # Detecta landmarks de pose
        frame_rgb, results = self.pose_detector.detect(frame)
        
        # Se não houver landmarks de pose, retorna o frame original
        if not results.pose_landmarks:
            return frame
        
        # Obtém as dimensões do frame
        height, width, _ = frame.shape
        
        # Obtém todos os landmarks detectados
        landmarks = self.pose_detector.get_all_landmarks(results, width, height)
        
        # Determina qual lado do corpo está mais visível
        more_visible_side = self.pose_detector.determine_more_visible_side(landmarks)
        
        # Verifica se deve processar a parte inferior do corpo
        is_lower_body = self.pose_detector.should_process_lower_body(landmarks) if self.config.get('process_lower_body', True) else False
        
        # Detecta dispositivos eletrônicos se a opção estiver habilitada e não for processamento de corpo inferior
        electronics_detections = []
        if self.config.get('show_electronics', True) and (not is_lower_body or self.config.get('show_upper_body', True)):
            electronics_detections = self.electronics_detector.detect(frame)
        
        # Cria uma cópia limpa do frame para desenhar
        processed_frame = frame.copy()
        
        # Aplica desfoque no rosto se a opção estiver habilitada
        if self.config.get('show_face_blur', True):
            # Obtém os landmarks do rosto
            face_landmarks = self.pose_detector.get_face_landmarks(results, width, height)
            
            # Aplica o desfoque
            processed_frame = self.visualizer.apply_face_blur(processed_frame, face_landmarks, landmarks)
        
        # Processa o corpo com base no tipo de pose detectada (inferior ou lateral)
        if is_lower_body and self.config.get('show_lower_body', True):
            # Processa o corpo inferior
            processed_frame = self._process_lower_body(processed_frame, landmarks, results, more_visible_side)
        else:
            # Processa o corpo lateral (superior)
            processed_frame = self._process_lateral_body(processed_frame, landmarks, results, more_visible_side, electronics_detections)
        
        return processed_frame
    
    def _process_lower_body(self, frame, landmarks, results, more_visible_side):
        """
        Processa a parte inferior do corpo.
        
        Args:
            frame (numpy.ndarray): Frame a ser processado
            landmarks (dict): Dicionário com as coordenadas dos landmarks
            results: Resultados do MediaPipe
            more_visible_side (str): Lado mais visível ('left' ou 'right')
            
        Returns:
            numpy.ndarray: Frame processado
        """
        # Calcula os ângulos do joelho e tornozelo
        knee_angle = self.angle_analyzer.calculate_knee_angle(landmarks, more_visible_side)
        ankle_angle = self.angle_analyzer.calculate_ankle_angle(landmarks, more_visible_side)
        
        # Desenha os ângulos se a opção estiver habilitada
        if self.config.get('show_angles', True):
            # Posições para os textos dos ângulos
            if more_visible_side == 'right':
                knee_id, ankle_id = 26, 28
            else:
                knee_id, ankle_id = 25, 27
            
            if knee_id in landmarks and knee_angle is not None:
                knee_position = landmarks[knee_id]
                frame = self.visualizer.draw_angle(
                    frame, knee_angle, knee_position, "Joelho", color=(0, 255, 255)  # Amarelo
                )
            
            if ankle_id in landmarks and ankle_angle is not None:
                ankle_position = landmarks[ankle_id]
                frame = self.visualizer.draw_angle(
                    frame, ankle_angle, ankle_position, "Tornozelo", color=(0, 255, 255)  # Amarelo
                )
        
        # Desenha os landmarks de pose (apenas parte inferior)
        frame = self.visualizer.draw_landmarks(
            frame,
            results,
            show_face=not self.config.get('show_face_blur', True),
            show_upper_body=False,  # Não mostra a parte superior
            show_lower_body=True    # Mostra apenas a parte inferior
        )
        
        # Opcionalmente, recorta o frame para mostrar apenas a parte inferior
        if self.config.get('crop_lower_body', False):
            frame = self.visualizer.crop_frame(frame, landmarks, region='lower_body')
        
        return frame
    
    def _process_lateral_body(self, frame, landmarks, results, more_visible_side, electronics_detections):
        """
        Processa o corpo em vista lateral (superior).
        
        Args:
            frame (numpy.ndarray): Frame a ser processado
            landmarks (dict): Dicionário com as coordenadas dos landmarks
            results: Resultados do MediaPipe
            more_visible_side (str): Lado mais visível ('left' ou 'right')
            electronics_detections (list): Lista de detecções de dispositivos eletrônicos
            
        Returns:
            numpy.ndarray: Frame processado
        """
        # Processa o corpo superior se a opção estiver habilitada
        if self.config.get('show_upper_body', True):
            # Calcula os ângulos do cotovelo e pulso
            elbow_angle = self.angle_analyzer.calculate_elbow_angle(landmarks, more_visible_side)
            wrist_angle = self.angle_analyzer.calculate_wrist_angle(landmarks, more_visible_side)
            
            # Calcula o ângulo entre os olhos e o dispositivo eletrônico mais próximo
            eyes_to_device_angle = None
            if electronics_detections and self.config.get('show_electronics', True):
                # Obtém o centro do primeiro dispositivo eletrônico detectado
                device_center = self.electronics_detector.get_detection_center(electronics_detections[0])
                
                # Calcula o ângulo entre os olhos e o dispositivo
                eyes_to_device_angle = self.angle_analyzer.calculate_eyes_to_device_angle(
                    landmarks, device_center
                )
            
            # Desenha os ângulos se a opção estiver habilitada
            if self.config.get('show_angles', True):
                # Posições para os textos dos ângulos
                if more_visible_side == 'right':
                    elbow_id, wrist_id = 14, 16
                else:
                    elbow_id, wrist_id = 13, 15
                
                if elbow_id in landmarks and elbow_angle is not None:
                    elbow_position = landmarks[elbow_id]
                    frame = self.visualizer.draw_angle(
                        frame, elbow_angle, elbow_position, "Cotovelo", color=(0, 255, 255)  # Amarelo
                    )
                
                if wrist_id in landmarks and wrist_angle is not None:
                    wrist_position = landmarks[wrist_id]
                    frame = self.visualizer.draw_angle(
                        frame, wrist_angle, wrist_position, "Pulso", color=(0, 255, 255)  # Amarelo
                    )
                
                # Desenha o ângulo entre os olhos e o dispositivo
                if eyes_to_device_angle is not None:
                    # Posição para o texto do ângulo (entre os olhos)
                    if 2 in landmarks and 5 in landmarks:
                        left_eye = landmarks[2]
                        right_eye = landmarks[5]
                        eyes_position = (
                            (left_eye[0] + right_eye[0]) // 2,
                            (left_eye[1] + right_eye[1]) // 2 - 30  # Um pouco acima dos olhos
                        )
                        
                        frame = self.visualizer.draw_angle(
                            frame, eyes_to_device_angle, eyes_position, "Olhos-Dispositivo", color=(0, 0, 255)  # Vermelho
                        )
            
            # Desenha as detecções de dispositivos eletrônicos
            if electronics_detections and self.config.get('show_electronics', True):
                frame = self.electronics_detector.draw_detections(
                    frame, electronics_detections
                )
        
        # Processa o corpo inferior se a opção estiver habilitada
        if self.config.get('show_lower_body', True):
            # Calcula os ângulos do joelho e tornozelo
            knee_angle = self.angle_analyzer.calculate_knee_angle(landmarks, more_visible_side)
            ankle_angle = self.angle_analyzer.calculate_ankle_angle(landmarks, more_visible_side)
            
            # Desenha os ângulos se a opção estiver habilitada
            if self.config.get('show_angles', True):
                # Posições para os textos dos ângulos
                if more_visible_side == 'right':
                    knee_id, ankle_id = 26, 28
                else:
                    knee_id, ankle_id = 25, 27
                
                if knee_id in landmarks and knee_angle is not None:
                    knee_position = landmarks[knee_id]
                    frame = self.visualizer.draw_angle(
                        frame, knee_angle, knee_position, "Joelho", color=(0, 255, 255)  # Amarelo
                    )
                
                if ankle_id in landmarks and ankle_angle is not None:
                    ankle_position = landmarks[ankle_id]
                    frame = self.visualizer.draw_angle(
                        frame, ankle_angle, ankle_position, "Tornozelo", color=(0, 255, 255)  # Amarelo
                    )
        
        # Desenha os landmarks de pose
        frame = self.visualizer.draw_landmarks(
            frame,
            results,
            show_face=not self.config.get('show_face_blur', True),
            show_upper_body=self.config.get('show_upper_body', True),
            show_lower_body=self.config.get('show_lower_body', True)
        )
        
        return frame
    
    def release(self):
        """
        Libera os recursos do processador.
        """
        self.pose_detector.release()