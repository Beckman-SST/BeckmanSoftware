import cv2
import numpy as np
import mediapipe as mp
from ..core.utils import adjust_text_position

# Configurações globais do MediaPipe
mpDraw = mp.solutions.drawing_utils
mpDrawingStyles = mp.solutions.drawing_styles
mpHolistic = mp.solutions.holistic

# Cores para desenho
landmark_color = (0, 255, 0)  # Verde
connection_color = (214, 121, 108)  # Cor personalizada (mesma do processamento original)
text_color = (255, 255, 255)  # Branco
angle_color = (0, 255, 255)  # Amarelo

# Define as conexões personalizadas para o corpo
custom_pose_connections = [
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

class PoseVisualizer:
    def __init__(self, face_padding=10):
        """
        Inicializa o visualizador de pose.
        
        Args:
            face_padding (int): Padding em pixels para a tarja facial (padrão: 10)
        """
        self.face_padding = face_padding
    
    def draw_landmarks(self, frame, results, show_face=True, show_upper_body=True, show_lower_body=True):
        """
        Desenha os landmarks de pose no frame.
        
        Args:
            frame (numpy.ndarray): Frame onde os landmarks serão desenhados
            results: Resultados do MediaPipe
            show_face (bool): Se True, desenha os landmarks do rosto
            show_upper_body (bool): Se True, desenha os landmarks do corpo superior
            show_lower_body (bool): Se True, desenha os landmarks do corpo inferior
            
        Returns:
            numpy.ndarray: Frame com os landmarks desenhados
        """
        # Desenha os landmarks do rosto
        if show_face and results.face_landmarks:
            mpDraw.draw_landmarks(
                frame,
                results.face_landmarks,
                mpHolistic.FACEMESH_CONTOURS,
                landmark_drawing_spec=None,
                connection_drawing_spec=mpDrawingStyles.get_default_face_mesh_contours_style()
            )
        
        # Desenha os landmarks da pose
        if results.pose_landmarks:
            # Cria uma cópia dos landmarks para modificação
            modified_landmarks = self._filter_landmarks(
                results.pose_landmarks,
                show_upper_body,
                show_lower_body
            )
            
            # Converte os landmarks para o formato de dicionário
            h, w, _ = frame.shape
            landmarks_dict = {}
            for i, landmark in enumerate(modified_landmarks.landmark):
                if landmark.visibility >= 0.5:
                    x = int(landmark.x * w)
                    y = int(landmark.y * h)
                    landmarks_dict[i] = (x, y)
            
            # Filtra as conexões personalizadas com base nas configurações
            filtered_connections = []
            
            # Adiciona conexões do corpo superior se necessário
            if show_upper_body:
                upper_body_connections = [
                    conn for conn in custom_pose_connections 
                    if conn[0] in [11, 12, 13, 14, 15, 16] or conn[1] in [11, 12, 13, 14, 15, 16]
                ]
                filtered_connections.extend(upper_body_connections)
            
            # Adiciona conexões do corpo inferior se necessário
            if show_lower_body:
                lower_body_connections = [
                    conn for conn in custom_pose_connections 
                    if conn[0] in [23, 24, 25, 26, 27, 28, 29, 30, 31, 32] or 
                       conn[1] in [23, 24, 25, 26, 27, 28, 29, 30, 31, 32]
                ]
                filtered_connections.extend(lower_body_connections)
            
            # Desenha os landmarks modificados
            mpDraw.draw_landmarks(
                frame,
                modified_landmarks,
                None,  # Não usa as conexões padrão
                landmark_drawing_spec=mpDraw.DrawingSpec(color=(245, 117, 66), thickness=4, circle_radius=4),
                connection_drawing_spec=None  # Não desenha conexões aqui
            )
            
            # Desenha as conexões personalizadas
            self.draw_custom_connections(
                frame, 
                landmarks_dict, 
                filtered_connections,
                color=connection_color,
                thickness=4
            )
        
        return frame
    
    def _filter_landmarks(self, landmarks, show_upper_body, show_lower_body):
        """
        Filtra os landmarks com base nas opções de visualização.
        
        Args:
            landmarks: Landmarks do MediaPipe
            show_upper_body (bool): Se True, mostra os landmarks do corpo superior
            show_lower_body (bool): Se True, mostra os landmarks do corpo inferior
            
        Returns:
            Landmarks filtrados
        """
        # Cria uma cópia dos landmarks para modificação
        import copy
        modified_landmarks = copy.deepcopy(landmarks)
        
        # IDs dos landmarks de interesse específicos
        # Corpo superior - apenas ombro, cotovelo, pulso e dedo médio
        right_upper_body_ids = [12, 14, 16, 18]  # Ombro, cotovelo, pulso e dedo médio direito
        left_upper_body_ids = [11, 13, 15, 17]   # Ombro, cotovelo, pulso e dedo médio esquerdo
        
        # Corpo inferior - apenas quadril, joelho, tornozelo e foot index
        right_lower_body_ids = [24, 26, 28, 32]  # Quadril, joelho, tornozelo e foot index direito
        left_lower_body_ids = [23, 25, 27, 31]   # Quadril, joelho, tornozelo e foot index esquerdo
        
        # Determina qual lado é mais visível para o corpo superior
        right_upper_visibility = 0
        left_upper_visibility = 0
        
        if show_upper_body:
            # Calcula a visibilidade média dos landmarks do lado direito
            for i in right_upper_body_ids:
                if i < len(modified_landmarks.landmark):
                    right_upper_visibility += modified_landmarks.landmark[i].visibility
            right_upper_visibility /= len(right_upper_body_ids)
            
            # Calcula a visibilidade média dos landmarks do lado esquerdo
            for i in left_upper_body_ids:
                if i < len(modified_landmarks.landmark):
                    left_upper_visibility += modified_landmarks.landmark[i].visibility
            left_upper_visibility /= len(left_upper_body_ids)
        
        # Determina qual lado é mais visível para o corpo inferior
        right_lower_visibility = 0
        left_lower_visibility = 0
        
        if show_lower_body:
            # Calcula a visibilidade média dos landmarks do lado direito
            for i in right_lower_body_ids:
                if i < len(modified_landmarks.landmark):
                    right_lower_visibility += modified_landmarks.landmark[i].visibility
            right_lower_visibility /= len(right_lower_body_ids)
            
            # Calcula a visibilidade média dos landmarks do lado esquerdo
            for i in left_lower_body_ids:
                if i < len(modified_landmarks.landmark):
                    left_lower_visibility += modified_landmarks.landmark[i].visibility
            left_lower_visibility /= len(left_lower_body_ids)
        
        # Determina se a imagem é lateral (corpo superior) ou frontal (corpo inferior)
        # Verifica se os tornozelos e pés estão visíveis
        ankle_foot_ids = [27, 28, 31, 32]  # Tornozelos e pés
        ankle_foot_visible = any(i < len(modified_landmarks.landmark) and modified_landmarks.landmark[i].visibility > 0.5 for i in ankle_foot_ids)
        
        # Se os tornozelos ou pés não estiverem visíveis, considera como imagem lateral
        is_lateral_view = not ankle_foot_visible
        
        # Lista para armazenar os IDs dos landmarks a serem mantidos
        ids_to_keep = []
        
        # Determina qual lado é mais visível no geral
        more_visible_side_upper = "right" if right_upper_visibility > left_upper_visibility else "left"
        more_visible_side_lower = "right" if right_lower_visibility > left_lower_visibility else "left"
        
        # Adiciona apenas o olho do lado mais visível
        if show_upper_body:
            if more_visible_side_upper == "right":
                ids_to_keep.append(5)  # RIGHT_EYE
            else:
                ids_to_keep.append(2)  # LEFT_EYE
        
        # Adiciona os IDs do corpo superior do lado mais visível se necessário
        if show_upper_body:
            if more_visible_side_upper == "right":
                ids_to_keep.extend(right_upper_body_ids)
            else:
                ids_to_keep.extend(left_upper_body_ids)
        
        # Adiciona os IDs do corpo inferior do lado mais visível apenas se não for vista lateral
        if show_lower_body and not is_lateral_view:
            if more_visible_side_lower == "right":
                ids_to_keep.extend(right_lower_body_ids)
            else:
                ids_to_keep.extend(left_lower_body_ids)
        
        # Oculta todos os landmarks que não estão na lista de IDs a serem mantidos
        # e também oculta os pontos da mão, exceto o dedo médio que é usado para o cálculo do ângulo
        for i in range(len(modified_landmarks.landmark)):
            # Verifica se o landmark não está na lista de IDs a serem mantidos
            # ou se é um ponto da mão que não é o dedo médio (17 ou 18)
            hand_landmarks = list(range(17, 23)) + list(range(18, 24))  # IDs dos landmarks da mão
            middle_finger_ids = [17, 18]  # IDs do dedo médio (esquerdo e direito)
            
            if i not in ids_to_keep or (i in hand_landmarks and i not in middle_finger_ids):
                modified_landmarks.landmark[i].visibility = 0
        
        return modified_landmarks
    
    def draw_custom_connections(self, frame, landmarks, connections, color=None, thickness=4):
        """
        Desenha conexões personalizadas entre landmarks.
        
        Args:
            frame (numpy.ndarray): Frame onde as conexões serão desenhadas
            landmarks (dict): Dicionário com as coordenadas dos landmarks
            connections (list): Lista de tuplas (landmark_id1, landmark_id2) representando as conexões
            color (tuple): Cor das conexões (B, G, R)
            thickness (int): Espessura das linhas
            
        Returns:
            numpy.ndarray: Frame com as conexões desenhadas
        """
        if color is None:
            color = connection_color
        
        for connection in connections:
            start_id, end_id = connection
            
            if start_id in landmarks and end_id in landmarks:
                # Desenha a linha com a espessura especificada
                cv2.line(
                    frame,
                    landmarks[start_id],
                    landmarks[end_id],
                    color,
                    thickness
                )
                
                # Desenha círculos nos pontos de início e fim para destacar os landmarks
                cv2.circle(
                    frame,
                    landmarks[start_id],
                    thickness + 1,  # Raio um pouco maior que a espessura da linha
                    (245, 117, 66),  # Cor laranja para os landmarks
                    -1  # Preenchido
                )
                
                cv2.circle(
                    frame,
                    landmarks[end_id],
                    thickness + 1,  # Raio um pouco maior que a espessura da linha
                    (245, 117, 66),  # Cor laranja para os landmarks
                    -1  # Preenchido
                )
        
        return frame
    
    def draw_angle(self, frame, angle, position, label=None, color=None, font_scale=0.7, thickness=2):
        """
        Desenha um ângulo no frame com sistema avançado de anticolisão.
        
        Args:
            frame (numpy.ndarray): Frame onde o ângulo será desenhado
            angle (float): Valor do ângulo
            position (tuple): Posição (x, y) onde o texto será desenhado
            label (str): Rótulo adicional para o ângulo
            color (tuple): Cor do texto (B, G, R)
            font_scale (float): Escala da fonte
            thickness (int): Espessura do texto
            
        Returns:
            numpy.ndarray: Frame com o ângulo desenhado
        """
        if angle is None:
            return frame
        
        if color is None:
            color = angle_color
        
        # Formata o texto do ângulo (sem símbolo de grau)
        try:
            # Verifica se o ângulo é um número válido
            if isinstance(angle, (tuple, list)):
                print(f"Aviso: ângulo é uma tupla/lista: {angle}")
                return frame
            
            angle_value = float(angle)
            if label:
                text = f"{label}: {angle_value:.1f}"
            else:
                text = f"{angle_value:.1f}"
        except (ValueError, TypeError) as e:
            print(f"Erro ao formatar ângulo {angle}: {e}")
            return frame
        
        # Offset inicial maior para melhor separação da articulação
        offset_x = 35  # Aumentado de 20 para 35 pixels
        offset_y = -10  # Pequeno offset vertical para cima
        initial_position = (position[0] + offset_x, position[1] + offset_y)
        
        # Ajusta a posição do texto usando o sistema avançado de anticolisão
        adjusted_position = adjust_text_position(
            frame, text, initial_position, cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness
        )
        
        # Obtém o tamanho do texto para calcular posição do símbolo de grau
        text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
        text_w, text_h = text_size
        
        # Padding aumentado para o fundo do texto (incluindo espaço para o símbolo)
        bg_padding = 8  # Aumentado de 5 para 8 pixels
        symbol_space = 12  # Espaço extra para o símbolo de grau
        
        # Adiciona um fundo semi-transparente para destacar o texto
        # Coordenadas do retângulo (x1, y1) é o canto superior esquerdo e (x2, y2) é o canto inferior direito
        x1 = adjusted_position[0] - bg_padding
        y1 = adjusted_position[1] - text_h - bg_padding
        x2 = adjusted_position[0] + text_w + symbol_space + bg_padding
        y2 = adjusted_position[1] + bg_padding
        
        # Garante que o retângulo de fundo fique dentro dos limites do frame
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(frame.shape[1], x2)
        y2 = min(frame.shape[0], y2)
        
        # Cria uma cópia do frame para aplicar o retângulo semi-transparente
        overlay = frame.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 0, 0), -1)  # Retângulo preto preenchido
        
        # Aplica o retângulo com transparência ligeiramente aumentada
        alpha = 0.7  # Aumentado de 0.6 para 0.7 para melhor contraste
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
        # Desenha uma linha sutil conectando a articulação ao texto (opcional)
        # Isso ajuda a identificar visualmente qual ângulo pertence a qual articulação
        line_color = tuple(int(c * 0.7) for c in color)  # Cor mais escura que o texto
        cv2.line(frame, position, adjusted_position, line_color, 1)
        
        # Desenha o texto sobre o retângulo
        cv2.putText(
            frame,
            text,
            adjusted_position,
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            color,
            thickness
        )
        
        # Desenha o símbolo de grau manualmente (pequeno círculo)
        symbol_x = adjusted_position[0] + text_w + 3  # 3 pixels de espaço após o texto
        symbol_y = adjusted_position[1] - int(text_h * 0.7)  # Posição superior
        symbol_radius = max(2, int(font_scale * 4))  # Raio proporcional à fonte
        
        # Desenha o círculo do símbolo de grau
        cv2.circle(frame, (symbol_x, symbol_y), symbol_radius, color, thickness//2 or 1)
        
        return frame
    
    def apply_face_blur(self, frame, face_landmarks=None, eye_landmarks=None):
        """
        Aplica desfoque no rosto.
        
        Args:
            frame (numpy.ndarray): Frame onde o desfoque será aplicado
            face_landmarks (dict): Dicionário com os landmarks do rosto
            eye_landmarks (dict): Dicionário com os landmarks dos olhos
            
        Returns:
            numpy.ndarray: Frame com o rosto desfocado
        """
        # Cria uma cópia do frame
        blurred_frame = frame.copy()
        h, w, _ = frame.shape
        
        # Tenta aplicar o desfoque usando os landmarks do rosto completo
        if face_landmarks and len(face_landmarks) > 0:
            # Obtém os pontos do contorno do rosto
            face_points = []
            for i in face_landmarks.keys():
                x = int(face_landmarks[i][0])
                y = int(face_landmarks[i][1])
                face_points.append((x, y))
            
            # Obtém as coordenadas mínimas e máximas para criar o retângulo
            x_coords = [p[0] for p in face_points]
            y_coords = [p[1] for p in face_points]
            x_min, x_max = min(x_coords), max(x_coords)
            y_min, y_max = min(y_coords), max(y_coords)
            
            # Adiciona padding ao retângulo usando o valor configurado
            x_min = max(0, x_min - self.face_padding)
            x_max = min(w, x_max + self.face_padding)
            y_min = max(0, y_min - self.face_padding)
            y_max = min(h, y_max + self.face_padding)
            
            # Aplica um retângulo preto para ocultar o rosto
            cv2.rectangle(blurred_frame, (x_min, y_min), (x_max, y_max), (0, 0, 0), -1)
            
            return blurred_frame
        
        # Se não houver landmarks do rosto, tenta usar os landmarks dos olhos da pose
        elif eye_landmarks:
            # Verifica se os landmarks dos olhos estão disponíveis
            left_eye = eye_landmarks.get(2)  # ID do olho esquerdo
            right_eye = eye_landmarks.get(5)  # ID do olho direito
            
            if left_eye and right_eye:
                # Obtém as coordenadas mínimas e máximas para criar o retângulo
                x_min = min(left_eye[0], right_eye[0])
                x_max = max(left_eye[0], right_eye[0])
                y_min = min(left_eye[1], right_eye[1])
                y_max = max(left_eye[1], right_eye[1])
                
                # Garante um tamanho mínimo para a tarja (reduzido)
                tarja_width = max(x_max - x_min, int(w * 0.12))
                tarja_height = int(tarja_width * 0.9)  # Altura ligeiramente menor que a largura para melhor ajuste
                
                # Centraliza a tarja horizontalmente
                center_x = (x_min + x_max) // 2
                x_min = max(0, center_x - tarja_width // 2)
                x_max = min(w, center_x + tarja_width // 2)
                
                # Ajusta a altura da tarja
                y_min = max(0, y_min - tarja_height // 2)
                y_max = min(h, y_max + tarja_height // 2)
                
                # Aplica um retângulo preto para ocultar a região dos olhos
                cv2.rectangle(blurred_frame, (x_min, y_min), (x_max, y_max), (0, 0, 0), -1)
                
                return blurred_frame
            else:
                print("Landmarks dos olhos não detectados. Não foi possível desenhar a tarja.")
        
        # Se não for possível aplicar o desfoque, retorna o frame original
        return frame
    
    def crop_frame(self, frame, landmarks, region='lower_body', margin=50):
        """
        Recorta o frame para mostrar apenas uma região específica do corpo.
        
        Args:
            frame (numpy.ndarray): Frame a ser recortado
            landmarks (dict): Dicionário com as coordenadas dos landmarks
            region (str): Região a ser recortada ('lower_body' ou 'upper_body')
            margin (int): Margem adicional em pixels
            
        Returns:
            numpy.ndarray: Frame recortado ou o frame original se não for possível recortar
        """
        if region == 'lower_body':
            # IDs dos landmarks para o corpo inferior (quadris, joelhos, tornozelos)
            region_ids = [23, 24, 25, 26, 27, 28]
        elif region == 'upper_body':
            # IDs dos landmarks para o corpo superior (ombros, cotovelos, pulsos)
            region_ids = [11, 12, 13, 14, 15, 16]
        else:
            return frame
        
        # Filtra os landmarks disponíveis na região
        region_landmarks = [landmarks[i] for i in region_ids if i in landmarks]
        
        if len(region_landmarks) < 2:
            return frame
        
        # Converte para numpy array
        points = np.array(region_landmarks)
        
        # Obtém os limites da região
        x_min = max(0, np.min(points[:, 0]) - margin)
        y_min = max(0, np.min(points[:, 1]) - margin)
        x_max = min(frame.shape[1], np.max(points[:, 0]) + margin)
        y_max = min(frame.shape[0], np.max(points[:, 1]) + margin)
        
        # Recorta o frame
        cropped_frame = frame[int(y_min):int(y_max), int(x_min):int(x_max)]
        
        # Verifica se o recorte foi bem-sucedido
        if cropped_frame.size == 0:
            return frame
        
        return cropped_frame