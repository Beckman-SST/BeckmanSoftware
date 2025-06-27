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

# As conexões para visualização do pescoço foram removidas

# Define as conexões para visualização da coluna vertebral
spine_connections = [(11, 12), (23, 24)]  # Ombros e quadris

class VideoVisualizer:
    """
    Visualizador específico para processamento de vídeos.
    Mantém a lógica original de desenho de landmarks para vídeos.
    """
    
    def __init__(self, tarja_ratio=0.12):
        """
        Inicializa o visualizador de vídeo.
        
        Args:
            tarja_ratio (float): Proporção da largura do frame para calcular tamanho mínimo da tarja (padrão: 0.12 = 12%)
        """
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        self.tarja_ratio = tarja_ratio  # Proporção para calcular tamanho da tarja
        
        # Importa o analisador de ângulos para cálculos
        from ..analysis.angle_analyzer import AngleAnalyzer
        self.angle_analyzer = AngleAnalyzer()
        
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
                
    def draw_spine_angle(self, frame, landmarks_dict, use_vertical_reference=True):
        """
        Desenha o ângulo da coluna vertebral no frame, alterando a cor da linha de acordo com a avaliação da postura.
        
        Args:
            frame (numpy.ndarray): Frame onde desenhar
            landmarks_dict (dict): Dicionário com coordenadas dos landmarks
            use_vertical_reference (bool): Se True, calcula o ângulo em relação à vertical
                                          Se False, calcula o ângulo interno
            
        Returns:
            numpy.ndarray: Frame com o ângulo da coluna desenhado
            float: Ângulo da coluna calculado ou None se não foi possível calcular
        """
        # Verifica se temos landmarks suficientes
        required_landmarks = [11, 12, 23, 24]  # Ombros e quadris
        if not all(lm_id in landmarks_dict for lm_id in required_landmarks):
            return frame, None
        
        try:
            # Calcula o ângulo da coluna
            spine_angle = self.angle_analyzer.calculate_spine_angle(
                landmarks_dict, 
                use_vertical_reference=use_vertical_reference
            )
            
            if spine_angle is None:
                return frame, None
            
            # Calcula o ponto médio entre os ombros
            left_shoulder = landmarks_dict[11]
            right_shoulder = landmarks_dict[12]
            shoulder_midpoint = (
                (left_shoulder[0] + right_shoulder[0]) // 2,
                (left_shoulder[1] + right_shoulder[1]) // 2
            )
            
            # Calcula o ponto médio entre os quadris
            left_hip = landmarks_dict[23]
            right_hip = landmarks_dict[24]
            hip_midpoint = (
                (left_hip[0] + right_hip[0]) // 2,
                (left_hip[1] + right_hip[1]) // 2
            )
            
            # Arredonda o ângulo para avaliação
            spine_angle_rounded = round(spine_angle, 1)
            
            # Determina a cor da linha da coluna com base no ângulo
            if use_vertical_reference:
                if spine_angle_rounded <= 5:
                    # Postura excelente - Verde
                    spine_color = (0, 255, 0)  # BGR - Verde
                elif spine_angle_rounded <= 10:
                    # Postura com atenção - Amarelo
                    spine_color = (0, 255, 255)  # BGR - Amarelo
                else:
                    # Postura ruim - Vermelho
                    spine_color = (0, 0, 255)  # BGR - Vermelho
            else:
                # Para ângulo interno, usar uma lógica diferente se necessário
                spine_color = (0, 255, 0)  # Verde por padrão
            
            # Desenha a linha da coluna com a cor determinada pela avaliação
            cv2.line(
                frame,
                shoulder_midpoint,
                hip_midpoint,
                spine_color,
                thickness=4
            )
            
            # Desenha os pontos médios com a mesma cor da linha
            cv2.circle(
                frame,
                shoulder_midpoint,
                radius=5,
                color=spine_color,
                thickness=-1  # Preenchido
            )
            
            cv2.circle(
                frame,
                hip_midpoint,
                radius=5,
                color=spine_color,
                thickness=-1  # Preenchido
            )
            
            if use_vertical_reference:
                # Linha vertical de referência removida conforme solicitado
                pass  # Mantém o bloco if com um pass para evitar erros
            
            return frame, spine_angle
            
        except Exception as e:
            print(f"Erro ao desenhar ângulo da coluna: {str(e)}")
            return frame, None
    
    # A função draw_neck_angle foi removida
    
    def draw_shoulder_angle(self, frame, landmarks_dict, side='right'):
        """
        Desenha o ângulo do braço superior (ombro) no frame, alterando a cor da linha de acordo com a pontuação.
        
        Args:
            frame (numpy.ndarray): Frame onde desenhar
            landmarks_dict (dict): Dicionário com coordenadas dos landmarks
            side (str): Lado do corpo ('right' ou 'left')
            
        Returns:
            numpy.ndarray: Frame com o ângulo do ombro desenhado
            float: Ângulo do ombro calculado ou None se não foi possível calcular
            int: Pontuação baseada no ângulo (1-4 pontos) ou None se não foi possível calcular
        """
        if side == 'right':
            # Ombro e cotovelo direitos
            shoulder_id, elbow_id = 12, 14
            # Ombro oposto para verificar abdução
            opposite_shoulder_id = 11
        else:
            # Ombro e cotovelo esquerdos
            shoulder_id, elbow_id = 11, 13
            # Ombro oposto para verificar abdução
            opposite_shoulder_id = 12
        
        # Verifica se todos os landmarks necessários estão disponíveis
        if not all(lm_id in landmarks_dict for lm_id in [shoulder_id, elbow_id, opposite_shoulder_id]):
            return frame, None, None
        
        try:
            # Calcula o ângulo do ombro e a pontuação
            shoulder_angle, score, is_abducted = self.angle_analyzer.calculate_shoulder_angle(
                landmarks_dict, 
                side=side
            )
            
            if shoulder_angle is None:
                return frame, None, None
            
            # Obtém as coordenadas dos pontos
            shoulder = landmarks_dict[shoulder_id]
            elbow = landmarks_dict[elbow_id]
            
            # Determina a cor com base na pontuação
            if score == 1:
                color = (0, 255, 0)  # Verde (0° a 20°)
            elif score == 2:
                color = (0, 255, 255)  # Amarelo (>20° a 45°)
            elif score == 3:
                color = (0, 165, 255)  # Laranja (>45° a 90°)
            else:  # score == 4
                color = (0, 0, 255)  # Vermelho (>90°)
            
            # Desenha a linha do braço com a cor determinada pela pontuação
            cv2.line(
                frame,
                shoulder,
                elbow,
                color,
                thickness=4
            )
            
            # Desenha círculos nos pontos
            cv2.circle(
                frame,
                shoulder,
                radius=5,
                color=color,
                thickness=-1  # Preenchido
            )
            
            cv2.circle(
                frame,
                elbow,
                radius=5,
                color=color,
                thickness=-1  # Preenchido
            )
            
            # Linha vertical de referência removida conforme solicitado
            
            return frame, shoulder_angle, score
            
        except Exception as e:
            print(f"Erro ao desenhar ângulo do ombro: {str(e)}")
            return frame, None, None
    
    def draw_forearm_angle(self, frame, landmarks_dict, side='right'):
        """
        Desenha o ângulo do antebraço (cotovelo a punho) no frame, alterando a cor da linha de acordo com a pontuação.
        
        Args:
            frame (numpy.ndarray): Frame onde desenhar
            landmarks_dict (dict): Dicionário com coordenadas dos landmarks
            side (str): Lado do corpo ('right' ou 'left')
            
        Returns:
            numpy.ndarray: Frame com o ângulo do antebraço desenhado
            float: Ângulo do antebraço calculado ou None se não foi possível calcular
            int: Pontuação baseada no ângulo (1-2 pontos) ou None se não foi possível calcular
        """
        if side == 'right':
            # Ombro, cotovelo e punho direitos
            shoulder_id, elbow_id, wrist_id = 12, 14, 16
        else:
            # Ombro, cotovelo e punho esquerdos
            shoulder_id, elbow_id, wrist_id = 11, 13, 15
        
        # Verifica se todos os landmarks necessários estão disponíveis
        if not all(lm_id in landmarks_dict for lm_id in [shoulder_id, elbow_id, wrist_id]):
            return frame, None, None
        
        try:
            # Calcula o ângulo do antebraço e a pontuação
            forearm_angle, score = self.angle_analyzer.calculate_forearm_angle(
                landmarks_dict, 
                side=side
            )
            
            if forearm_angle is None:
                return frame, None, None
            
            # Obtém as coordenadas dos pontos
            elbow = landmarks_dict[elbow_id]
            wrist = landmarks_dict[wrist_id]
            
            # Determina a cor com base na pontuação
            if score == 1:
                color = (0, 255, 0)  # Verde (60° a 100°)
            else:  # score == 2
                color = (0, 255, 255)  # Amarelo (fora da faixa)
            
            # Desenha a linha do antebraço com a cor determinada pela pontuação
            cv2.line(
                frame,
                elbow,
                wrist,
                color,
                thickness=4
            )
            
            # Desenha círculos nos pontos
            cv2.circle(
                frame,
                elbow,
                radius=5,
                color=color,
                thickness=-1  # Preenchido
            )
            
            cv2.circle(
                frame,
                wrist,
                radius=5,
                color=color,
                thickness=-1  # Preenchido
            )
            
            # Texto com ângulo removido conforme solicitado
            
            return frame, forearm_angle, score
            
        except Exception as e:
            print(f"Erro ao desenhar ângulo do antebraço: {str(e)}")
            return frame, None, None
    
    def apply_face_blur(self, frame, face_landmarks=None, eye_landmarks=None):
        """
        Aplica tarja no rosto usando landmarks faciais ou dos olhos.
        Método específico para vídeos que mantém compatibilidade.
        
        Args:
            frame (numpy.ndarray): Frame onde a tarja será aplicada
            face_landmarks (dict): Dicionário com os landmarks do rosto
            eye_landmarks (dict): Dicionário com os landmarks dos olhos
            
        Returns:
            numpy.ndarray: Frame com a tarja aplicada
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
        tarja_size = max(80, int(frame_width * self.tarja_ratio))  # Mínimo 80px, máximo 12% da largura
        
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
        tarja_size = max(80, int(frame_width * self.tarja_ratio))  # Mínimo 80px, máximo 12% da largura
        
        # Calcula coordenadas do quadrado centrado
        half_size = tarja_size // 2
        x_min = max(0, center_x - half_size)
        y_min = max(0, center_y - half_size)
        x_max = min(frame.shape[1], center_x + half_size)
        y_max = min(frame.shape[0], center_y + half_size)
        
        # Aplica retângulo preto quadrado
        cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 0, 0), -1)
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame