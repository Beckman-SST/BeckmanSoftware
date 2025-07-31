import cv2
import numpy as np
import mediapipe as mp
from ..core.utils import adjust_text_position

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
        
    def draw_video_landmarks(self, frame, results, show_upper_body=True, show_lower_body=True, more_visible_side=None):
        """
        Desenha landmarks de pose especificamente para vídeos usando a lógica original.
        
        Args:
            frame (numpy.ndarray): Frame onde os landmarks serão desenhados
            results: Resultados do MediaPipe
            show_upper_body (bool): Se True, desenha landmarks do corpo superior
            show_lower_body (bool): Se True, desenha landmarks do corpo inferior
            more_visible_side (str): Lado mais visível ('left' ou 'right'). Se None, será determinado localmente.
            
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
                if landmark.visibility >= 0.3:  # Threshold mais permissivo para mostrar mais landmarks
                    x = int(landmark.x * w)
                    y = int(landmark.y * h)
                    landmarks_dict[i] = (x, y)
            
            # Filtra conexões baseado nas configurações
            connections_to_draw = self._filter_video_connections(
                show_upper_body, 
                show_lower_body,
                more_visible_side
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
                show_lower_body,
                more_visible_side
            )
            
        except Exception as e:
            print(f"Erro ao desenhar landmarks do vídeo: {str(e)}")
            
        return frame
    
    def draw_angle_text(self, frame, angle, position, label=None, color=(255, 255, 255), font_scale=0.6, thickness=2):
        """
        Desenha o texto de um ângulo no frame com sistema avançado de anticolisão.
        
        Args:
            frame (numpy.ndarray): Frame onde o texto será desenhado
            angle (float): Valor do ângulo
            position (tuple): Posição (x, y) da articulação de referência
            label (str): Rótulo adicional para o ângulo
            color (tuple): Cor do texto (B, G, R)
            font_scale (float): Escala da fonte
            thickness (int): Espessura do texto
            
        Returns:
            numpy.ndarray: Frame com o texto do ângulo desenhado
        """
        # Verificações de segurança
        if frame is None:
            print("Erro: Frame é None no draw_angle_text")
            return frame
            
        if angle is None:
            return frame
        
        # Formata o texto do ângulo (sem símbolo de grau)
        try:
            angle_value = float(angle)
            if label:
                text = f"{label}: {angle_value:.1f}"
            else:
                text = f"{angle_value:.1f}"
        except (ValueError, TypeError) as e:
            print(f"Erro ao formatar ângulo {angle}: {e}")
            return frame
        
        # Offset inicial para separar da articulação
        offset_x = 40  # Maior offset para vídeos
        offset_y = -15  # Pequeno offset vertical para cima
        initial_position = (position[0] + offset_x, position[1] + offset_y)
        
        # Ajusta a posição do texto usando o sistema avançado de anticolisão
        adjusted_position = adjust_text_position(
            frame, text, initial_position, cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness
        )
        
        # Obtém o tamanho do texto para calcular posição do símbolo de grau
        text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
        text_w, text_h = text_size
        
        # Padding aumentado para o fundo do texto (incluindo espaço para o símbolo)
        bg_padding = 8  # Aumentado de 6 para 8 pixels
        symbol_space = 18  # Espaço extra aumentado para o símbolo de grau maior
        
        # Adiciona um fundo semi-transparente para destacar o texto
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
        
        # Aplica o retângulo com transparência
        alpha = 0.7
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
        # Desenha uma linha sutil conectando a articulação ao texto
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
        
        # Desenha o símbolo de grau manualmente (círculo maior e mais visível)
        symbol_x = adjusted_position[0] + text_w + 5  # 5 pixels de espaço após o texto (aumentado)
        symbol_y = adjusted_position[1] - int(text_h * 0.65)  # Posição superior ajustada
        symbol_radius = max(4, int(font_scale * 6))  # Raio maior e mais proporcional à fonte
        
        # Desenha o círculo do símbolo de grau com espessura maior
        cv2.circle(frame, (symbol_x, symbol_y), symbol_radius, color, max(2, thickness//2))
        
        # Adiciona um círculo interno menor para criar um efeito de anel mais visível
        inner_radius = max(2, symbol_radius - 1)
        cv2.circle(frame, (symbol_x, symbol_y), inner_radius, (0, 0, 0), 1)
        
        return frame
    
    def _filter_video_connections(self, show_upper_body, show_lower_body, more_visible_side=None):
        """
        Filtra as conexões baseado nas configurações de exibição e lado mais visível.
        Agora usa um threshold de visibilidade mais flexível em vez de ocultar completamente um lado.
        
        Args:
            show_upper_body (bool): Se deve mostrar corpo superior
            show_lower_body (bool): Se deve mostrar corpo inferior
            more_visible_side (str): Lado mais visível ('left' ou 'right'). Se None, mostra ambos os lados.
            
        Returns:
            list: Lista de conexões filtradas
        """
        filtered_connections = []
        
        # IDs dos landmarks do corpo superior
        upper_body_ids = [11, 12, 13, 14, 15, 16]
        
        # IDs dos landmarks do corpo inferior
        lower_body_ids = [23, 24, 25, 26, 27, 28, 29, 30, 31, 32]
        
        # Nova lógica: mostra ambos os lados, mas prioriza o lado mais visível
        # Só oculta um lado se a diferença de visibilidade for muito grande
        for connection in custom_video_pose_connections:
            start_id, end_id = connection
            
            # Verifica se a conexão pertence ao corpo superior
            is_upper = (start_id in upper_body_ids or end_id in upper_body_ids)
            
            # Verifica se a conexão pertence ao corpo inferior
            is_lower = (start_id in lower_body_ids or end_id in lower_body_ids)
            
            # Lógica mais permissiva: mostra a conexão se ela pertence à parte do corpo habilitada
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
    
    def _draw_video_landmarks_points(self, frame, landmarks_dict, show_upper_body, show_lower_body, more_visible_side=None):
        """
        Desenha os pontos dos landmarks baseado nas configurações de exibição e threshold de visibilidade.
        Agora usa um threshold mínimo de visibilidade em vez de ocultar completamente um lado.
        
        Args:
            frame (numpy.ndarray): Frame onde desenhar
            landmarks_dict (dict): Dicionário com coordenadas dos landmarks
            show_upper_body (bool): Se deve mostrar corpo superior
            show_lower_body (bool): Se deve mostrar corpo inferior
            more_visible_side (str): Lado mais visível ('left' ou 'right'). Usado apenas para referência.
        """
        # IDs dos landmarks do corpo superior
        upper_body_ids = [11, 12, 13, 14, 15, 16]
        
        # IDs dos landmarks do corpo inferior
        lower_body_ids = [23, 24, 25, 26, 27, 28, 29, 30, 31, 32]
        
        # Nova lógica: desenha todos os landmarks que passaram pelo filtro de visibilidade inicial
        # O filtro de visibilidade já foi aplicado na função draw_video_landmarks (visibility >= 0.3)
        for landmark_id, (x, y) in landmarks_dict.items():
            # Verifica se deve desenhar este landmark baseado apenas nas configurações de corpo
            should_draw = False
            
            if show_upper_body and landmark_id in upper_body_ids:
                should_draw = True
            elif show_lower_body and landmark_id in lower_body_ids:
                should_draw = True
            
            if should_draw:
                # Ajusta a cor baseado no lado mais visível (opcional - para dar feedback visual)
                color = landmark_color
                if more_visible_side:
                    # IDs do lado esquerdo
                    left_side_ids = [11, 13, 15, 23, 25, 27, 29, 31]
                    # IDs do lado direito  
                    right_side_ids = [12, 14, 16, 24, 26, 28, 30, 32]
                    
                    if more_visible_side == 'left' and landmark_id in left_side_ids:
                        # Lado mais visível - cor mais intensa
                        color = (255, 140, 80)  # Laranja mais brilhante
                    elif more_visible_side == 'right' and landmark_id in right_side_ids:
                        # Lado mais visível - cor mais intensa
                        color = (255, 140, 80)  # Laranja mais brilhante
                    else:
                        # Lado menos visível - cor mais suave, mas ainda visível
                        color = (200, 100, 50)  # Laranja mais suave
                
                cv2.circle(
                    frame, 
                    (x, y), 
                    radius=6,  # Aumentado de 4 para 6 pixels
                    color=color, 
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
        # Verificação de segurança
        if frame is None:
            print("Erro: Frame é None no draw_spine_angle")
            return frame, None
            
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
                radius=7,
                color=spine_color,
                thickness=-1  # Preenchido
            )
            
            cv2.circle(
                frame,
                hip_midpoint,
                radius=7,
                color=spine_color,
                thickness=-1  # Preenchido
            )
            
            # Texto do ângulo removido para vídeos conforme solicitado
            # self.draw_angle_text(
            #     frame, 
            #     spine_angle, 
            #     shoulder_midpoint, 
            #     label="Coluna",
            #     color=(255, 255, 255)
            # )
            
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
        Desenha o ângulo do braço superior (ombro) no frame, alterando a cor da linha de acordo com a avaliação da postura.
        
        Args:
            frame (numpy.ndarray): Frame onde desenhar
            landmarks_dict (dict): Dicionário com coordenadas dos landmarks
            side (str): Lado do corpo ('right' ou 'left')
            
        Returns:
            numpy.ndarray: Frame com o ângulo do ombro desenhado
            float: Ângulo do ombro calculado ou None se não foi possível calcular
        """
        # Verificação de segurança
        if frame is None:
            print("Erro: Frame é None no draw_shoulder_angle")
            return frame, None
            
        if side == 'right':
            # Ombro e cotovelo direitos
            shoulder_id, elbow_id = 12, 14
        else:
            # Ombro e cotovelo esquerdos
            shoulder_id, elbow_id = 11, 13
        
        # Verifica se todos os landmarks necessários estão disponíveis
        if not all(lm_id in landmarks_dict for lm_id in [shoulder_id, elbow_id]):
            return frame, None
        
        try:
            # Calcula o ângulo do ombro
            shoulder_angle = self.angle_analyzer.calculate_shoulder_angle(
                landmarks_dict, 
                side=side
            )
            
            if shoulder_angle is None:
                return frame, None
            
            # Obtém as coordenadas dos pontos
            shoulder = landmarks_dict[shoulder_id]
            elbow = landmarks_dict[elbow_id]
            
            # Determina a cor com base no ângulo (lógica anterior simples)
            if shoulder_angle <= 20:
                color = (0, 255, 0)  # Verde (Nível 1)
            elif shoulder_angle <= 45:
                color = (0, 255, 255)  # Amarelo (Nível 2)
            elif shoulder_angle <= 90:
                color = (0, 165, 255)  # Laranja (Nível 3)
            else:
                color = (0, 0, 255)  # Vermelho (Nível 4)
            
            # Desenha a linha do braço com a cor determinada pela avaliação
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
                radius=7,
                color=color,
                thickness=-1  # Preenchido
            )

            cv2.circle(
                frame,
                elbow,
                radius=7,
                color=color,
                thickness=-1  # Preenchido
            )
            
            # Texto do ângulo removido para vídeos conforme solicitado
            # self.draw_angle_text(
            #     frame, 
            #     shoulder_angle, 
            #     shoulder, 
            #     label=f"Ombro {side.title()}",
            #     color=(255, 255, 255)
            # )
            
            return frame, shoulder_angle
            
        except Exception as e:
            print(f"Erro ao desenhar ângulo do ombro: {str(e)}")
            return frame, None
    
    def draw_forearm_angle(self, frame, landmarks_dict, side='right'):
        """
        Desenha o ângulo do antebraço (cotovelo a punho) no frame, alterando a cor da linha de acordo com a avaliação da postura.
        
        Args:
            frame (numpy.ndarray): Frame onde desenhar
            landmarks_dict (dict): Dicionário com coordenadas dos landmarks
            side (str): Lado do corpo ('right' ou 'left')
            
        Returns:
            numpy.ndarray: Frame com o ângulo do antebraço desenhado
            float: Ângulo do antebraço calculado ou None se não foi possível calcular
        """
        # Verificação de segurança
        if frame is None:
            print("Erro: Frame é None no draw_forearm_angle")
            return frame, None
            
        if side == 'right':
            # Ombro, cotovelo e punho direitos
            shoulder_id, elbow_id, wrist_id = 12, 14, 16
        else:
            # Ombro, cotovelo e punho esquerdos
            shoulder_id, elbow_id, wrist_id = 11, 13, 15
        
        # Verifica se todos os landmarks necessários estão disponíveis
        if not all(lm_id in landmarks_dict for lm_id in [shoulder_id, elbow_id, wrist_id]):
            return frame, None
        
        try:
            # Calcula o ângulo do antebraço
            forearm_angle = self.angle_analyzer.calculate_forearm_angle(
                landmarks_dict, 
                side=side
            )
            
            if forearm_angle is None:
                return frame, None
            
            # Obtém as coordenadas dos pontos
            elbow = landmarks_dict[elbow_id]
            wrist = landmarks_dict[wrist_id]
            
            # Determina a cor com base no ângulo (lógica anterior simples)
            if forearm_angle <= 60:
                color = (0, 255, 0)  # Verde (Nível 1)
            elif forearm_angle <= 100:
                color = (0, 255, 255)  # Amarelo (Nível 2)
            else:
                color = (0, 0, 255)  # Vermelho (Nível 3)
            
            # Desenha a linha do antebraço com a cor determinada pela avaliação
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
                radius=7,
                color=color,
                thickness=-1  # Preenchido
            )
            
            cv2.circle(
                frame,
                wrist,
                radius=7,
                color=color,
                thickness=-1  # Preenchido
            )
            
            # Texto do ângulo removido para vídeos conforme solicitado
            # self.draw_angle_text(
            #     frame, 
            #     forearm_angle, 
            #     elbow, 
            #     label=f"Antebraço {side.title()}",
            #     color=(255, 255, 255)
            # )
            
            return frame, forearm_angle
            
        except Exception as e:
            print(f"Erro ao desenhar ângulo do antebraço: {str(e)}")
            return frame, None
    
    def draw_knee_angle(self, frame, landmarks_dict, side='right'):
        """
        Desenha o ângulo do joelho no frame, alterando a cor da linha de acordo com a avaliação da postura.
        
        Args:
            frame (numpy.ndarray): Frame onde desenhar
            landmarks_dict (dict): Dicionário com coordenadas dos landmarks
            side (str): Lado do corpo ('right' ou 'left')
            
        Returns:
            numpy.ndarray: Frame com o ângulo do joelho desenhado
            float: Ângulo do joelho calculado ou None se não foi possível calcular
        """
        # Verificação de segurança
        if frame is None:
            print("Erro: Frame é None no draw_knee_angle")
            return frame, None
            
        if side == 'right':
            # Quadril, joelho e tornozelo direitos
            hip_id, knee_id, ankle_id = 24, 26, 28
        else:
            # Quadril, joelho e tornozelo esquerdos
            hip_id, knee_id, ankle_id = 23, 25, 27
        
        # Verifica se todos os landmarks necessários estão disponíveis
        if not all(lm_id in landmarks_dict for lm_id in [hip_id, knee_id, ankle_id]):
            return frame, None
        
        try:
            # Calcula o ângulo do joelho
            knee_angle = self.angle_analyzer.calculate_knee_angle(
                landmarks_dict, 
                side=side
            )
            
            if knee_angle is None:
                return frame, None
            
            # Obtém as coordenadas dos pontos
            hip = landmarks_dict[hip_id]
            knee = landmarks_dict[knee_id]
            ankle = landmarks_dict[ankle_id]
            
            # Determina a cor com base no ângulo (lógica anterior simples)
            if knee_angle >= 60:
                color = (0, 255, 0)  # Verde (Nível 1)
            elif knee_angle >= 30:
                color = (0, 255, 255)  # Amarelo (Nível 2)
            else:
                color = (0, 0, 255)  # Vermelho (Nível 3)
            
            # Desenha a linha da coxa com a cor determinada pela avaliação
            cv2.line(
                frame,
                hip,
                knee,
                color,
                thickness=4
            )
            
            # Desenha a linha da perna com a cor determinada pela avaliação
            cv2.line(
                frame,
                knee,
                ankle,
                color,
                thickness=4
            )
            
            # Desenha círculos nos pontos
            cv2.circle(
                frame,
                hip,
                radius=7,
                color=color,
                thickness=-1  # Preenchido
            )
            
            cv2.circle(
                frame,
                knee,
                radius=7,
                color=color,
                thickness=-1  # Preenchido
            )
            
            cv2.circle(
                frame,
                ankle,
                radius=7,
                color=color,
                thickness=-1  # Preenchido
            )
            
            # Texto do ângulo removido para vídeos conforme solicitado
            # self.draw_angle_text(
            #     frame, 
            #     knee_angle, 
            #     knee, 
            #     label=f"Joelho {side.title()}",
            #     color=(255, 255, 255)
            # )
            
            return frame, knee_angle
            
        except Exception as e:
            print(f"Erro ao desenhar ângulo do joelho: {str(e)}")
            return frame, None
    
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
    
    def draw_neck_line(self, frame, landmarks_dict, face_landmarks=None, eye_landmarks=None):
        """
        Desenha uma linha do ponto médio dos ombros até o centro da tarja facial,
        colorida com base nos critérios de angulação do pescoço.
        
        Args:
            frame (numpy.ndarray): Frame onde a linha será desenhada
            landmarks_dict (dict): Dicionário com as coordenadas dos landmarks do corpo
            face_landmarks (dict): Dicionário com os landmarks do rosto
            eye_landmarks (dict): Dicionário com os landmarks dos olhos
            
        Returns:
            tuple: (frame modificado, ângulo do pescoço)
        """
        try:
            # IDs dos landmarks dos ombros
            left_shoulder_id, right_shoulder_id = 11, 12
            
            # Verifica se os ombros estão disponíveis
            if not all(lm_id in landmarks_dict for lm_id in [left_shoulder_id, right_shoulder_id]):
                return frame, None
            
            # Calcula o ponto médio entre os ombros
            left_shoulder = landmarks_dict[left_shoulder_id]
            right_shoulder = landmarks_dict[right_shoulder_id]
            shoulder_midpoint = (
                (left_shoulder[0] + right_shoulder[0]) // 2,
                (left_shoulder[1] + right_shoulder[1]) // 2
            )
            
            # Determina o centro da tarja facial
            face_center = None
            
            if face_landmarks:
                # Calcula centro dos landmarks faciais
                x_coords = [coord[0] for coord in face_landmarks.values()]
                y_coords = [coord[1] for coord in face_landmarks.values()]
                
                if x_coords and y_coords:
                    face_center = (
                        sum(x_coords) // len(x_coords),
                        sum(y_coords) // len(y_coords)
                    )
            elif eye_landmarks:
                # Usa landmarks dos olhos como fallback
                left_eye = eye_landmarks.get(2)  # LEFT_EYE
                right_eye = eye_landmarks.get(5)  # RIGHT_EYE
                
                if left_eye and right_eye:
                    face_center = (
                        (left_eye[0] + right_eye[0]) // 2,
                        (left_eye[1] + right_eye[1]) // 2
                    )
                elif left_eye:
                    face_center = left_eye
                elif right_eye:
                    face_center = right_eye
            
            # Se não conseguiu determinar o centro da face, usa o nariz
            if not face_center:
                nose_id = 0
                if nose_id in landmarks_dict:
                    face_center = landmarks_dict[nose_id]
                else:
                    return frame, None
            
            # Calcula o ângulo do pescoço
            neck_angle = self.angle_analyzer.calculate_neck_angle(
                landmarks_dict, 
                face_center=face_center
            )
            
            if neck_angle is None:
                return frame, None
            
            # Determina a cor com base no ângulo do pescoço
            # Usando critérios similares aos outros ângulos
            if neck_angle <= 15:  # Posição neutra/boa
                color = (0, 255, 0)  # Verde (Nível 1)
            elif neck_angle <= 30:  # Inclinação moderada
                color = (0, 255, 255)  # Amarelo (Nível 2)
            else:  # Inclinação excessiva
                color = (0, 0, 255)  # Vermelho (Nível 3)
            
            # Desenha a linha do pescoço
            cv2.line(
                frame,
                shoulder_midpoint,
                face_center,
                color,
                thickness=4
            )
            
            # Desenha círculos nos pontos
            cv2.circle(
                frame,
                shoulder_midpoint,
                radius=7,
                color=color,
                thickness=-1  # Preenchido
            )
            
            cv2.circle(
                frame,
                face_center,
                radius=7,
                color=color,
                thickness=-1  # Preenchido
            )
            
            return frame, neck_angle
            
        except Exception as e:
            print(f"Erro ao desenhar linha do pescoço: {str(e)}")
            return frame, None
    
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