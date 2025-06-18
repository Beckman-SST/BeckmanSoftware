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
    
    def __init__(self, tarja_ratio=0.20, tarja_max_size=200, landmark_quality_threshold=0.6):
        """
        Inicializa o visualizador de vídeo.
        
        Args:
            tarja_ratio (float): Proporção da largura do frame para calcular tamanho mínimo da tarja (padrão: 0.20 = 20%)
            tarja_max_size (int): Tamanho máximo da tarja em pixels (padrão: 200px)
            landmark_quality_threshold (float): Limiar de qualidade para exibição de landmarks (0.0 a 1.0)
                                              Landmarks com confiança abaixo deste valor não serão exibidos
        """
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        self.tarja_ratio = tarja_ratio  # Proporção para calcular tamanho da tarja
        self.tarja_max_size = tarja_max_size  # Tamanho máximo da tarja em pixels
        self.landmark_quality_threshold = landmark_quality_threshold  # Limiar de qualidade para exibição
        
        # Importa o analisador de ângulos para cálculos
        from ..analysis.angle_analyzer import AngleAnalyzer
        self.angle_analyzer = AngleAnalyzer()
        
    def draw_video_landmarks(self, frame, results, show_upper_body=True, show_lower_body=True):
        """
        Desenha landmarks de pose especificamente para vídeos usando a lógica original.
        Aplica um limiar de qualidade para exibir apenas landmarks com confiança satisfatória.
        
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
            
            # Converte landmarks para coordenadas de pixel, aplicando o limiar de qualidade
            landmarks_dict = {}
            for i, landmark in enumerate(results.pose_landmarks.landmark):
                # Só considera landmarks com visibilidade acima do limiar de qualidade
                if landmark.visibility >= self.landmark_quality_threshold:  
                    x = int(landmark.x * w)
                    y = int(landmark.y * h)
                    landmarks_dict[i] = (x, y)
            
            # Se não houver landmarks com qualidade suficiente, retorna o frame sem alterações
            if not landmarks_dict:
                return frame
            
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
            
            # Linha vertical de referência removida conforme solicitado
            
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
                # Usa landmarks faciais completos para criar uma tarja oval
                return self._apply_face_oval_tarja_from_face_mesh(frame, face_landmarks)
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
        Ajusta o tamanho da tarja com base na distância estimada da pessoa.
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
        
        # Estima a distância da pessoa com base na dispersão dos landmarks faciais
        # Quanto maior a dispersão, mais próxima a pessoa está da câmera
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        face_width = x_max - x_min
        face_height = y_max - y_min
        face_size = max(face_width, face_height)
        
        # Calcula tamanho da tarja proporcional ao tamanho do rosto
        # Quanto menor o rosto (pessoa mais distante), menor a tarja
        frame_width = frame.shape[1]
        face_ratio = face_size / frame_width  # Proporção do rosto em relação à largura do frame
        
        # Ajusta o tamanho da tarja com base na proporção do rosto
        # Usa um fator de escala para garantir que a tarja cubra adequadamente o rosto
        scale_factor = 1.5  # Fator para garantir que a tarja seja maior que o rosto
        tarja_size = max(100, min(int(face_size * scale_factor), self.tarja_max_size))  # Mínimo 100px, máximo limitado
        
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
        Ajusta o tamanho da tarja com base na distância estimada da pessoa.
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
            
            # Calcula a distância entre os olhos para estimar o tamanho do rosto
            # Quanto maior a distância, mais próxima a pessoa está da câmera
            eye_distance = np.sqrt((right_eye[0] - left_eye[0])**2 + (right_eye[1] - left_eye[1])**2)
            
            # Calcula tamanho da tarja proporcional à distância entre os olhos
            frame_width = frame.shape[1]
            eye_ratio = eye_distance / frame_width  # Proporção da distância dos olhos em relação à largura do frame
            
            # Ajusta o tamanho da tarja com base na distância entre os olhos
            # Usa um fator de escala para garantir que a tarja cubra adequadamente o rosto
            scale_factor = 3.0  # Fator para garantir que a tarja seja maior que a distância entre os olhos
            tarja_size = max(100, min(int(eye_distance * scale_factor), self.tarja_max_size))  # Mínimo 100px, máximo limitado
        elif left_eye or right_eye:
            # Se tiver apenas um olho, usa um tamanho padrão menor
            center_x, center_y = left_eye if left_eye else right_eye
            frame_width = frame.shape[1]
            tarja_size = max(100, min(int(frame_width * 0.15), self.tarja_max_size))  # Usa 15% da largura do frame
        else:
            # Tenta usar outros landmarks faciais disponíveis
            available_landmarks = [(x, y) for x, y in eye_landmarks.values() if x > 0 and y > 0]
            if not available_landmarks:
                return frame
            
            # Calcula o centro e estima o tamanho com base na dispersão dos landmarks
            center_x = sum(x for x, y in available_landmarks) // len(available_landmarks)
            center_y = sum(y for x, y in available_landmarks) // len(available_landmarks)
            
            # Calcula a dispersão dos landmarks para estimar o tamanho do rosto
            x_coords = [x for x, y in available_landmarks]
            y_coords = [y for x, y in available_landmarks]
            x_min, x_max = min(x_coords), max(x_coords)
            y_min, y_max = min(y_coords), max(y_coords)
            face_size = max(x_max - x_min, y_max - y_min)
            
            # Ajusta o tamanho da tarja com base na dispersão dos landmarks
            frame_width = frame.shape[1]
            tarja_size = max(100, min(int(face_size * 1.5), self.tarja_max_size))  # Fator 1.5 para garantir cobertura
        
        # Calcula coordenadas do quadrado centrado
        half_size = tarja_size // 2
        x_min = max(0, center_x - half_size)
        y_min = max(0, center_y - half_size)
        x_max = min(frame.shape[1], center_x + half_size)
        y_max = min(frame.shape[0], center_y + half_size)
        
        # Aplica retângulo preto quadrado
        cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 0, 0), -1)
        
        return frame
        
    def _apply_face_oval_tarja_from_face_mesh(self, frame, face_landmarks):
        """
        Aplica tarja oval baseada nos landmarks do face_mesh.
        Cria uma elipse que se adapta ao formato do rosto.
        
        Args:
            frame (numpy.ndarray): Frame a ser processado
            face_landmarks (dict): Dicionário com os landmarks do face_mesh
            
        Returns:
            numpy.ndarray: Frame com tarja oval aplicada
        """
        if not face_landmarks or len(face_landmarks) < 10:
            return frame
            
        try:
            # Extrai os pontos do contorno do rosto do face_mesh
            # Pontos do contorno facial no face_mesh (aproximadamente)
            contour_indices = [
                10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
                397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
                172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109
            ]
            
            contour_points = []
            for idx in contour_indices:
                if idx in face_landmarks:
                    contour_points.append(face_landmarks[idx])
            
            if len(contour_points) < 5:  # Precisamos de pelo menos 5 pontos para uma elipse
                # Fallback para todos os pontos se não tivermos pontos de contorno suficientes
                contour_points = list(face_landmarks.values())
            
            # Converte para o formato numpy para cálculos
            contour_points = np.array(contour_points, dtype=np.int32)
            
            # Calcula o retângulo delimitador da elipse
            x_coords = contour_points[:, 0]
            y_coords = contour_points[:, 1]
            
            # Calcula o centro do rosto
            center_x = int(np.mean(x_coords))
            center_y = int(np.mean(y_coords))
            
            # Calcula os eixos da elipse
            # Adiciona uma margem para garantir que todo o rosto seja coberto
            margin_factor = 1.2  # 20% de margem
            axis_x = int((np.max(x_coords) - np.min(x_coords)) * margin_factor / 2)
            axis_y = int((np.max(y_coords) - np.min(y_coords)) * margin_factor / 2)
            
            # Garante tamanho mínimo e máximo para a elipse
            min_axis = 50  # Tamanho mínimo para cada eixo
            axis_x = max(min_axis, min(axis_x, self.tarja_max_size // 2))
            axis_y = max(min_axis, min(axis_y, self.tarja_max_size // 2))
            
            # Cria uma máscara do tamanho do frame
            mask = np.zeros(frame.shape[:2], dtype=np.uint8)
            
            # Desenha a elipse preenchida na máscara
            cv2.ellipse(
                mask,
                (center_x, center_y),  # centro
                (axis_x, axis_y),      # eixos
                0,                     # ângulo
                0, 360,                # ângulo inicial e final
                (255),                 # cor (branco)
                -1                     # espessura (preenchido)
            )
            
            # Aplica a máscara ao frame (pinta de preto onde a máscara é branca)
            frame_with_mask = frame.copy()
            frame_with_mask[mask == 255] = (0, 0, 0)  # Preto
            
            return frame_with_mask
            
        except Exception as e:
            print(f"Erro ao aplicar tarja oval: {str(e)}")
            # Em caso de erro, volta para o método retangular
            return self._apply_face_tarja_from_face(frame, face_landmarks)
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame
        
        return frame