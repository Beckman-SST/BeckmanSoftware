import cv2
import numpy as np
import os
import mediapipe as mp
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
        self.visualizer = PoseVisualizer(face_padding=10)  # Usa padding menor para a tarja facial
    
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
            processed_frame = self._process_frame(frame, image_path, output_folder, 0)
            
            # Verifica se o processamento foi bem-sucedido
            # Se o frame retornado é None, significa que houve erro no processamento
            if processed_frame is None:
                # Não salva a imagem normal, apenas o arquivo de erro já foi salvo
                return True, "Imagem salva como arquivo de erro devido à falha na detecção de landmarks"
            
            # Salva a imagem processada apenas se o processamento foi bem-sucedido
            original_filename = os.path.basename(image_path)
            name, ext = os.path.splitext(original_filename)
            output_filename = f"ex_{name}{ext}"
            output_path = os.path.join(output_folder, output_filename)
            cv2.imwrite(output_path, processed_frame)
            
            return True, output_path
        
        except Exception as e:
            return False, f"Erro ao processar a imagem: {str(e)}"
    
    def _process_frame(self, frame, image_path=None, output_folder=None, frame_idx=0):
        """
        Processa um frame.
        
        Args:
            frame (numpy.ndarray): Frame a ser processado
            image_path (str, optional): Caminho da imagem original (para salvamento de erro)
            output_folder (str, optional): Pasta de saída (para salvamento de erro)
            frame_idx (int): Índice do frame (para vídeos)
            
        Returns:
            numpy.ndarray: Frame processado
        """
        # Detecta landmarks de pose
        frame_rgb, results = self.pose_detector.detect(frame)
        
        # Se não houver landmarks de pose, salva a imagem original sem processamento
        if not results.pose_landmarks:
            print("\nERRO: Não foi possível detectar os landmarks principais do corpo na imagem.")
            
            # Se temos informações para salvar a imagem com erro
            if image_path and output_folder:
                # Salva a imagem original sem processamento
                error_filename = f"error_{os.path.basename(image_path)}_{frame_idx}.jpg"
                error_output_path = os.path.join(output_folder, error_filename)
                cv2.imwrite(error_output_path, frame)
                print(f"Imagem original salva em: {error_output_path}")
            
            # Retorna o frame original sem processamento
            return frame
        
        # Obtém as dimensões do frame
        height, width, _ = frame.shape
        
        # Obtém todos os landmarks detectados
        landmarks = self.pose_detector.get_all_landmarks(results, width, height)
        
        # Determina qual lado do corpo está mais visível
        more_visible_side = self.pose_detector.determine_more_visible_side(landmarks, results)
        
        # Verifica se deve processar a parte inferior do corpo baseado no novo sistema
        processing_mode = self.config.get('processing_mode', 'auto')
        
        if processing_mode == 'upper_only':
            is_lower_body = False
        elif processing_mode == 'lower_only':
            is_lower_body = True
        else:  # processing_mode == 'auto'
            is_lower_body = self.pose_detector.should_process_lower_body(landmarks, results)
        
        # Detecta dispositivos eletrônicos independentemente da opção de exibição
        # A detecção é feita sempre, mas o desenho das caixas depende da configuração 'show_electronics'
        electronics_detections = []
        if not is_lower_body or self.config.get('show_upper_body', True):
            # Calcula a posição dos olhos para melhorar a seleção do dispositivo
            eye_position = None
            if 2 in landmarks and 5 in landmarks:  # Se ambos os olhos estão visíveis
                left_eye = landmarks[2]
                right_eye = landmarks[5]
                # Usa o centro entre os olhos
                eye_position = (
                    (left_eye[0] + right_eye[0]) // 2,
                    (left_eye[1] + right_eye[1]) // 2
                )
            elif 2 in landmarks:  # Apenas olho esquerdo visível
                eye_position = landmarks[2]
            elif 5 in landmarks:  # Apenas olho direito visível
                eye_position = landmarks[5]
            
            # Calcula a posição do pulso para proximidade
            wrist_position = None
            if more_visible_side == 'right' and 16 in landmarks:
                wrist_position = landmarks[16]  # Pulso direito
            elif more_visible_side == 'left' and 15 in landmarks:
                wrist_position = landmarks[15]  # Pulso esquerdo
            
            electronics_detections = self.electronics_detector.detect(frame, wrist_position, is_lower_body, eye_position)
        
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
        # Cria uma cópia limpa do frame para desenhar
        frame_clean = frame.copy()
        
        # Define os índices dos landmarks para cada perna
        right_leg_indices = [24, 26, 28, 32]  # Quadril, joelho, tornozelo, pé direito
        left_leg_indices = [23, 25, 27, 31]   # Quadril, joelho, tornozelo, pé esquerdo
        
        # Determina qual perna processar baseado no lado mais visível
        if more_visible_side == 'right':
            print("Perna direita mais visível. Processando lado direito.")
            side = "right"
            indices_manter = right_leg_indices
        else:
            print("Perna esquerda mais visível. Processando lado esquerdo.")
            side = "left"
            indices_manter = left_leg_indices
        
        # Cria uma cópia dos landmarks para manipulação
        visible_landmarks = results.pose_landmarks
        
        # Oculta landmarks indesejados (seta visibilidade para 0)
        # Garante que apenas os landmarks da perna selecionada sejam desenhados
        for i in range(len(visible_landmarks.landmark)):
            if i not in indices_manter:
                visible_landmarks.landmark[i].visibility = 0
        
        # Calcula os ângulos do joelho e tornozelo
        knee_angle, knee_score = self.angle_analyzer.calculate_knee_angle(landmarks, side)
        ankle_angle = self.angle_analyzer.calculate_ankle_angle(landmarks, side)
        
        # Desenha os ângulos se a opção estiver habilitada
        if self.config.get('show_angles', True):
            # Posições para os textos dos ângulos
            if side == 'right':
                knee_id, ankle_id = 26, 28
            else:
                knee_id, ankle_id = 25, 27
            
        # Define conexões personalizadas para a perna selecionada
        import mediapipe as mp
        mp_drawing = mp.solutions.drawing_utils
        
        if side == "right":
            custom_pose_connections = [
                (24, 26),  # Quadril direito -> Joelho direito
                (26, 28),  # Joelho direito -> Tornozelo direito
                (28, 32),  # Tornozelo direito -> Pé direito
            ]
        else:
            custom_pose_connections = [
                (23, 25),  # Quadril esquerdo -> Joelho esquerdo
                (25, 27),  # Joelho esquerdo -> Tornozelo esquerdo
                (27, 31),  # Tornozelo esquerdo -> Pé esquerdo
            ]
        
        # Desenha apenas os landmarks visíveis com conexões personalizadas
        mp_drawing.draw_landmarks(
            frame_clean,
            visible_landmarks,
            custom_pose_connections,
            mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=4, circle_radius=4),
            mp_drawing.DrawingSpec(color=(214, 121, 108), thickness=4, circle_radius=4)
        )
            
        # Desenha os ângulos por último para garantir que fiquem visíveis por cima dos landmarks
        if knee_id in landmarks and knee_angle is not None:
            knee_position = landmarks[knee_id]
            frame_clean = self.visualizer.draw_angle(
                frame_clean, knee_angle, knee_position, "", color=(0, 255, 255)  # Amarelo
            )
        
        if ankle_id in landmarks and ankle_angle is not None:
            ankle_position = landmarks[ankle_id]
            frame_clean = self.visualizer.draw_angle(
                frame_clean, ankle_angle, ankle_position, "", color=(0, 255, 255)  # Amarelo
            )
        
        # Corta a imagem acima da cintura para mostrar apenas a parte inferior
        # Usa os landmarks do quadril (hip) do MediaPipe para determinar a posição da cintura
        h, w, _ = frame_clean.shape
        
        # Determina qual quadril usar baseado no lado selecionado
        if side == 'right':
            hip_landmark_id = 24  # RIGHT_HIP
        else:
            hip_landmark_id = 23  # LEFT_HIP
        
        # Se o landmark do quadril estiver disponível, corta a imagem
        if hip_landmark_id in landmarks:
            hip_y = int(landmarks[hip_landmark_id][1])  # Coordenada Y do quadril em pixels
            
            # Adiciona uma margem acima do quadril para incluir um pouco da cintura
            margin_above_hip = 120
            crop_y_start = max(0, hip_y - margin_above_hip)
            
            # Corta o frame para mostrar apenas da cintura para baixo
            frame_clean = frame_clean[crop_y_start:h, 0:w]
        
        return frame_clean
    
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
        # Cria uma cópia limpa do frame para desenhar
        frame_clean = frame.copy()
        
        # Define os índices dos landmarks para cada lado (apenas parte superior)
        right_indices = [12, 14, 16, 5]  # Ombro, cotovelo, pulso, olho direito
        left_indices = [11, 13, 15, 2]   # Ombro, cotovelo, pulso, olho esquerdo
        
        # Define os índices dos landmarks inferiores que devem ser ocultados no processamento lateral
        lower_body_indices = [23, 24, 25, 26, 27, 28, 29, 30, 31, 32]  # Quadris, joelhos, tornozelos, pés
        
        # Função para calcular visibilidade baseada no processamentoTXT.txt
        def calculate_visibility(landmarks_data, indices):
            MIN_DETECTION_CONFIDENCE = self.config.get('min_detection_confidence', 0.8)
            visibility_sum = 0
            valid_count = 0
            for idx in indices:
                if idx in landmarks_data and hasattr(results.pose_landmarks.landmark[idx], 'visibility'):
                    if results.pose_landmarks.landmark[idx].visibility:  # Verifica se o landmark tem um valor de visibilidade
                        visibility_sum += results.pose_landmarks.landmark[idx].visibility  # Soma o valor de visibilidade
                        valid_count += 1  # Conta quantos landmarks foram considerados válidos
            
            # Retorna 0 se não houver landmarks válidos no conjunto
            if valid_count == 0:
                return 0
                
            # Calcula a média de visibilidade
            avg_visibility = visibility_sum / valid_count
            
            # Aplica um limiar mínimo de confiança
            # O landmark só é considerado "visível" se sua média de visibilidade for maior que MIN_DETECTION_CONFIDENCE
            return avg_visibility if avg_visibility > MIN_DETECTION_CONFIDENCE else 0
        
        # Calcula a visibilidade média para cada lado
        right_visibility = calculate_visibility(landmarks, right_indices)
        left_visibility = calculate_visibility(landmarks, left_indices)
        
        # Compara as visibilidades para decidir qual lado é mais visível
        if right_visibility > left_visibility:
            print("Lado direito mais visível. Processando lado direito.")
            side = "right"
            indices_manter = right_indices
            eye_position = landmarks.get(5)  # Olho direito
        else:
            print("Lado esquerdo mais visível. Processando lado esquerdo.")
            side = "left"
            indices_manter = left_indices
            eye_position = landmarks.get(2)  # Olho esquerdo
        
        # Cria uma cópia dos landmarks para manipulação
        visible_landmarks = results.pose_landmarks
        
        # Loop para "esconder" os landmarks do lado menos visível e todos os landmarks inferiores
        for i in range(len(visible_landmarks.landmark)):
            # Oculta landmarks que não são do lado mais visível OU que são da parte inferior do corpo
            if i not in indices_manter or i in lower_body_indices:
                visible_landmarks.landmark[i].visibility = 0  # Define visibilidade como 0 para não desenhar
        
        # Processa o corpo superior se a opção estiver habilitada
        if self.config.get('show_upper_body', True):
            # Calcula os ângulos do cotovelo, pulso e pescoço para o lado mais visível
            elbow_angle = self.angle_analyzer.calculate_elbow_angle(landmarks, side)
            wrist_angle = self.angle_analyzer.calculate_wrist_angle(landmarks, side)
            # O cálculo do ângulo do pescoço foi removido
            
            # Calcula o ângulo entre os olhos e o dispositivo eletrônico mais próximo
            # Sempre calcula os ângulos dos olhos, independente da configuração SHOW_ELECTRONICS
            eyes_to_device_angle = None
            
            # Calcula e desenha o ângulo dos olhos em relação ao dispositivo eletrônico (novo método)
            # Usa a posição dos olhos já definida anteriormente
            if electronics_detections and eye_position:
                detection = electronics_detections[0]  # Assume que pegamos o eletrônico mais próximo
                class_name, confidence, bbox = detection  # Coordenadas da caixa do eletrônico
                x, y, w, h = bbox
                x1, y1 = x, y
                x2, y2 = x + w, y + h
                
                # Usa o lado mais visível para determinar quais vértices da caixa usar
                # Regra corrigida baseada no processamentoTXT.txt:
                # - Lado esquerdo (pessoa virada à esquerda): superior esquerdo e inferior direito
                # - Lado direito (pessoa virada à direita): superior direito e inferior esquerdo
                from ..core.utils import prolongar_reta
                
                if side == "left":
                    # Para pessoa virada à esquerda: superior esquerdo e inferior direito
                    top_left = (x1, y1)
                    bottom_right = (x2, y2)
                    
                    # Usa os vértices da caixa como pontos finais das retas
                    prolonged_top = prolongar_reta(eye_position, top_left)
                    prolonged_bottom = prolongar_reta(eye_position, bottom_right)
                else:  # side == "right"
                    # Para pessoa virada à direita: superior direito e inferior esquerdo
                    top_right = (x2, y1)
                    bottom_left = (x1, y2)
                    
                    # Usa os vértices da caixa como pontos finais das retas
                    prolonged_top = prolongar_reta(eye_position, top_right)
                    prolonged_bottom = prolongar_reta(eye_position, bottom_left)
                
                # Desenha as retas prolongadas apenas se SHOW_ANGLES estiver ativado
                if self.config.get('show_angles', True):
                    cv2.line(frame_clean, eye_position, prolonged_top, (0, 0, 255), 2)  # Linha vermelha
                    cv2.line(frame_clean, eye_position, prolonged_bottom, (0, 0, 255), 2)  # Linha vermelha
                
                # Calcula o ângulo entre as retas
                from ..core.utils import calculate_angle
                try:
                    eye_angle = calculate_angle(prolonged_top, eye_position, prolonged_bottom)
                    
                    # Adiciona o texto do ângulo próximo ao olho se SHOW_ANGLES estiver ativado
                    if self.config.get('show_angles', True):
                        eye_text = f"{eye_angle:.2f} graus"
                        text_position = (eye_position[0] + 10, eye_position[1] - 10)  # Posição ligeiramente deslocada do olho
                        cv2.putText(frame_clean, eye_text, text_position,
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)  # Texto em amarelo/ciano
                except Exception as e:
                    print(f"Erro ao calcular ângulo dos olhos: {e}")
                    eye_angle = None
                
                # Obtém o centro do primeiro dispositivo eletrônico detectado para o cálculo do ângulo original
                device_center = self.electronics_detector.get_detection_center(detection)
                
                # Calcula o ângulo entre os olhos e o dispositivo (método original)
                eyes_to_device_angle = self.angle_analyzer.calculate_eyes_to_device_angle(
                    landmarks, device_center
                )
            
            # Prepara as informações dos ângulos para desenhar depois
            angle_info = []
            
            if self.config.get('show_angles', True):
                # Posições para os textos dos ângulos
                if side == 'right':
                    elbow_id, wrist_id = 14, 16
                else:
                    elbow_id, wrist_id = 13, 15
                
                # Coleta informações do ângulo do cotovelo
                if elbow_id in landmarks and elbow_angle is not None:
                    elbow_position = landmarks[elbow_id]
                    angle_info.append({
                        'angle': elbow_angle,
                        'position': elbow_position,
                        'label': "",
                        'color': (0, 255, 255)  # Amarelo
                    })
                
                # Coleta informações do ângulo do pulso
                if wrist_id in landmarks and wrist_angle is not None:
                    wrist_position = landmarks[wrist_id]
                    angle_info.append({
                        'angle': wrist_angle,
                        'position': wrist_position,
                        'label': "",
                        'color': (0, 255, 255)  # Amarelo
                    })
                
                # A visualização do ângulo do pescoço foi removida
                
                # Coleta informações do ângulo entre os olhos e o dispositivo (método original)
                if eyes_to_device_angle is not None and not electronics_detections:  # Só desenha se não tiver desenhado com o novo método
                    # Posição para o texto do ângulo (entre os olhos)
                    if 2 in landmarks and 5 in landmarks:
                        left_eye = landmarks[2]
                        right_eye = landmarks[5]
                        eyes_position = (
                            (left_eye[0] + right_eye[0]) // 2,
                            (left_eye[1] + right_eye[1]) // 2 - 30  # Um pouco acima dos olhos
                        )
                        
                        angle_info.append({
                            'angle': eyes_to_device_angle,
                            'position': eyes_position,
                            'label': "",
                            'color': (0, 0, 255)  # Vermelho
                        })
            
            # Desenha as detecções de dispositivos eletrônicos
            if electronics_detections and self.config.get('show_electronics', True):
                frame_clean = self.electronics_detector.draw_detections(
                    frame_clean, electronics_detections
                )
        
        # No processamento lateral, não calculamos ângulos inferiores
        
        # Desenha apenas os landmarks visíveis com conexões personalizadas
        mp_drawing = mp.solutions.drawing_utils
        
        # Define conexões personalizadas para o lado mais visível
        if side == "right":
            custom_pose_connections = [
                (12, 14),  # Ombro direito -> Cotovelo direito
                (14, 16),  # Cotovelo direito -> Pulso direito
            ]
        else:
            custom_pose_connections = [
                (11, 13),  # Ombro esquerdo -> Cotovelo esquerdo
                (13, 15),  # Cotovelo esquerdo -> Pulso esquerdo
            ]
        
        # Desenha apenas os landmarks visíveis com conexões personalizadas
        mp_drawing.draw_landmarks(
            frame_clean,
            visible_landmarks,
            custom_pose_connections,
            mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=4, circle_radius=4),
            mp_drawing.DrawingSpec(color=(214, 121, 108), thickness=4, circle_radius=4)
        )
        
        # Desenha todos os ângulos por último para garantir que fiquem visíveis por cima dos landmarks
        for info in angle_info:
            frame_clean = self.visualizer.draw_angle(
                frame_clean, 
                info['angle'], 
                info['position'], 
                info['label'], 
                color=info['color']
            )
        
        return frame_clean
    
    def release(self):
        """
        Libera os recursos do processador.
        """
        self.pose_detector.release()