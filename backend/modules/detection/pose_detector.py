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
            min_tracking_confidence=min_tracking_confidence,
            model_complexity=2
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
    
    def determine_more_visible_side(self, landmarks, results=None):
        """
        Determina qual lado do corpo está mais visível usando múltiplos critérios.
        
        Args:
            landmarks (dict): Dicionário com as coordenadas dos landmarks
            results: Resultados originais do MediaPipe (opcional, para usar dados de visibilidade)
            
        Returns:
            str: 'left' ou 'right'
        """
        print("\n=== ANÁLISE DO LADO MAIS VISÍVEL ===")
        
        # Se temos os resultados do MediaPipe, usa análise avançada com visibilidade
        if results is not None and hasattr(results, 'pose_landmarks') and results.pose_landmarks:
            return self._enhanced_side_detection(landmarks, results)
        else:
            # Caso contrário, usa análise baseada apenas na presença dos landmarks
            return self._fallback_side_detection(landmarks)
    
    def _enhanced_side_detection(self, landmarks, results):
        """
        Análise avançada do lado mais visível usando dados de visibilidade do MediaPipe.
        
        Args:
            landmarks (dict): Dicionário com as coordenadas dos landmarks
            results: Resultados originais do MediaPipe
            
        Returns:
            str: 'left' ou 'right'
        """
        mp_landmarks = results.pose_landmarks.landmark
        
        # === CRITÉRIO 1: VISIBILIDADE DOS OMBROS ===
        # Os ombros são críticos para determinar o lado visível
        left_shoulder_vis = mp_landmarks[self.mp_holistic.PoseLandmark.LEFT_SHOULDER.value].visibility
        right_shoulder_vis = mp_landmarks[self.mp_holistic.PoseLandmark.RIGHT_SHOULDER.value].visibility
        
        shoulder_score_left = left_shoulder_vis
        shoulder_score_right = right_shoulder_vis
        
        print(f"Visibilidade dos ombros - Esquerdo: {left_shoulder_vis:.3f}, Direito: {right_shoulder_vis:.3f}")
        
        # === CRITÉRIO 2: VISIBILIDADE DOS OLHOS E ORELHAS ===
        # Olhos e orelhas ajudam a determinar a orientação da cabeça
        left_eye_vis = mp_landmarks[self.mp_holistic.PoseLandmark.LEFT_EYE.value].visibility if self.mp_holistic.PoseLandmark.LEFT_EYE.value < len(mp_landmarks) else 0
        right_eye_vis = mp_landmarks[self.mp_holistic.PoseLandmark.RIGHT_EYE.value].visibility if self.mp_holistic.PoseLandmark.RIGHT_EYE.value < len(mp_landmarks) else 0
        
        # Para orelhas, usamos índices específicos do MediaPipe
        left_ear_vis = mp_landmarks[7].visibility if 7 < len(mp_landmarks) else 0  # LEFT_EAR
        right_ear_vis = mp_landmarks[8].visibility if 8 < len(mp_landmarks) else 0  # RIGHT_EAR
        
        eye_ear_score_left = (left_eye_vis + left_ear_vis) / 2
        eye_ear_score_right = (right_eye_vis + right_ear_vis) / 2
        
        print(f"Visibilidade olhos - Esquerdo: {left_eye_vis:.3f}, Direito: {right_eye_vis:.3f}")
        print(f"Visibilidade orelhas - Esquerda: {left_ear_vis:.3f}, Direita: {right_ear_vis:.3f}")
        
        # === CRITÉRIO 3: ANÁLISE DA PROJEÇÃO DOS ÂNGULOS DOS OLHOS ===
        # Calcula a orientação da cabeça baseada na posição relativa dos olhos
        eye_angle_score_left = 0
        eye_angle_score_right = 0
        
        if 2 in landmarks and 5 in landmarks:  # Ambos os olhos visíveis
            left_eye_pos = landmarks[2]   # LEFT_EYE
            right_eye_pos = landmarks[5]  # RIGHT_EYE
            
            # Calcula o ângulo da linha dos olhos
            import math
            dx = right_eye_pos[0] - left_eye_pos[0]
            dy = right_eye_pos[1] - left_eye_pos[1]
            eye_angle = math.atan2(dy, dx) * 180 / math.pi
            
            # Se o ângulo indica inclinação para um lado, esse lado está mais próximo da câmera
            if abs(eye_angle) > 5:  # Threshold para considerar inclinação significativa
                if eye_angle > 0:  # Inclinado para baixo à direita
                    eye_angle_score_right += 0.3
                else:  # Inclinado para baixo à esquerda
                    eye_angle_score_left += 0.3
            
            print(f"Ângulo dos olhos: {eye_angle:.1f}° (>0: direita mais próxima, <0: esquerda mais próxima)")
        
        # === CRITÉRIO 4: VISIBILIDADE GERAL DOS LANDMARKS DE CADA LADO ===
        # Landmarks do lado esquerdo (do ponto de vista da pessoa)
        left_landmarks_ids = [
            self.mp_holistic.PoseLandmark.LEFT_SHOULDER.value,   # 11
            self.mp_holistic.PoseLandmark.LEFT_ELBOW.value,      # 13
            self.mp_holistic.PoseLandmark.LEFT_WRIST.value,      # 15
            self.mp_holistic.PoseLandmark.LEFT_HIP.value,        # 23
            self.mp_holistic.PoseLandmark.LEFT_KNEE.value,       # 25
            self.mp_holistic.PoseLandmark.LEFT_ANKLE.value       # 27
        ]
        
        # Landmarks do lado direito (do ponto de vista da pessoa)
        right_landmarks_ids = [
            self.mp_holistic.PoseLandmark.RIGHT_SHOULDER.value,  # 12
            self.mp_holistic.PoseLandmark.RIGHT_ELBOW.value,     # 14
            self.mp_holistic.PoseLandmark.RIGHT_WRIST.value,     # 16
            self.mp_holistic.PoseLandmark.RIGHT_HIP.value,       # 24
            self.mp_holistic.PoseLandmark.RIGHT_KNEE.value,      # 26
            self.mp_holistic.PoseLandmark.RIGHT_ANKLE.value      # 28
        ]
        
        # Calcula visibilidade média de cada lado
        left_visibilities = [mp_landmarks[idx].visibility for idx in left_landmarks_ids]
        right_visibilities = [mp_landmarks[idx].visibility for idx in right_landmarks_ids]
        
        avg_left_visibility = sum(left_visibilities) / len(left_visibilities)
        avg_right_visibility = sum(right_visibilities) / len(right_visibilities)
        
        # Conta landmarks altamente visíveis (>0.7) de cada lado
        highly_visible_left = sum(1 for v in left_visibilities if v > 0.7)
        highly_visible_right = sum(1 for v in right_visibilities if v > 0.7)
        
        general_score_left = avg_left_visibility + (highly_visible_left * 0.1)
        general_score_right = avg_right_visibility + (highly_visible_right * 0.1)
        
        print(f"Visibilidade geral - Esquerda: {avg_left_visibility:.3f} ({highly_visible_left} altamente visíveis)")
        print(f"Visibilidade geral - Direita: {avg_right_visibility:.3f} ({highly_visible_right} altamente visíveis)")
        
        # === CRITÉRIO 5: ANÁLISE DE PROFUNDIDADE BASEADA EM COORDENADAS Z ===
        # Landmarks mais próximos da câmera tendem a ter valores Z menores
        depth_score_left = 0
        depth_score_right = 0
        
        # Compara profundidade dos ombros (mais confiável)
        if left_shoulder_vis > 0.5 and right_shoulder_vis > 0.5:
            left_shoulder_z = mp_landmarks[self.mp_holistic.PoseLandmark.LEFT_SHOULDER.value].z
            right_shoulder_z = mp_landmarks[self.mp_holistic.PoseLandmark.RIGHT_SHOULDER.value].z
            
            # Ombro com menor Z está mais próximo da câmera
            if left_shoulder_z < right_shoulder_z:
                depth_score_left += 0.2
            else:
                depth_score_right += 0.2
            
            print(f"Profundidade dos ombros - Esquerdo: {left_shoulder_z:.3f}, Direito: {right_shoulder_z:.3f}")
        
        # === CÁLCULO FINAL DOS SCORES ===
        # Pesos para cada critério
        SHOULDER_WEIGHT = 0.35      # Ombros são muito importantes
        EYE_EAR_WEIGHT = 0.25       # Olhos e orelhas indicam orientação da cabeça
        GENERAL_WEIGHT = 0.25       # Visibilidade geral dos landmarks
        EYE_ANGLE_WEIGHT = 0.10     # Ângulo dos olhos
        DEPTH_WEIGHT = 0.05         # Análise de profundidade
        
        final_score_left = (
            shoulder_score_left * SHOULDER_WEIGHT +
            eye_ear_score_left * EYE_EAR_WEIGHT +
            general_score_left * GENERAL_WEIGHT +
            eye_angle_score_left * EYE_ANGLE_WEIGHT +
            depth_score_left * DEPTH_WEIGHT
        )
        
        final_score_right = (
            shoulder_score_right * SHOULDER_WEIGHT +
            eye_ear_score_right * EYE_EAR_WEIGHT +
            general_score_right * GENERAL_WEIGHT +
            eye_angle_score_right * EYE_ANGLE_WEIGHT +
            depth_score_right * DEPTH_WEIGHT
        )
        
        # Determina o lado mais visível
        more_visible_side = 'left' if final_score_left > final_score_right else 'right'
        confidence = abs(final_score_left - final_score_right)
        
        print(f"\nScores finais:")
        print(f"  - Lado esquerdo: {final_score_left:.3f}")
        print(f"  - Lado direito: {final_score_right:.3f}")
        print(f"  - Diferença: {confidence:.3f}")
        print(f"  - LADO MAIS VISÍVEL: {more_visible_side.upper()}")
        print("=" * 40)
        
        return more_visible_side
    
    def _fallback_side_detection(self, landmarks):
        """
        Análise de fallback baseada apenas na presença dos landmarks.
        
        Args:
            landmarks (dict): Dicionário com as coordenadas dos landmarks
            
        Returns:
            str: 'left' ou 'right'
        """
        print("Usando análise de fallback (sem dados de visibilidade)")
        
        # Landmarks críticos para cada lado
        left_critical = [11, 13, 15]   # Ombro, cotovelo, pulso esquerdos
        right_critical = [12, 14, 16]  # Ombro, cotovelo, pulso direitos
        
        # Landmarks adicionais para cada lado
        left_additional = [23, 25, 27, 2, 7]   # Quadril, joelho, tornozelo, olho, orelha esquerdos
        right_additional = [24, 26, 28, 5, 8]  # Quadril, joelho, tornozelo, olho, orelha direitos
        
        # Conta landmarks presentes
        left_critical_count = sum(1 for lm in left_critical if lm in landmarks and landmarks[lm] is not None)
        right_critical_count = sum(1 for lm in right_critical if lm in landmarks and landmarks[lm] is not None)
        
        left_additional_count = sum(1 for lm in left_additional if lm in landmarks and landmarks[lm] is not None)
        right_additional_count = sum(1 for lm in right_additional if lm in landmarks and landmarks[lm] is not None)
        
        # Score baseado em landmarks críticos (peso maior) e adicionais
        left_score = left_critical_count * 2 + left_additional_count
        right_score = right_critical_count * 2 + right_additional_count
        
        more_visible_side = 'left' if left_score >= right_score else 'right'
        
        print(f"Landmarks críticos - Esquerda: {left_critical_count}/3, Direita: {right_critical_count}/3")
        print(f"Landmarks adicionais - Esquerda: {left_additional_count}/5, Direita: {right_additional_count}/5")
        print(f"Score total - Esquerda: {left_score}, Direita: {right_score}")
        print(f"LADO MAIS VISÍVEL: {more_visible_side.upper()}")
        print("=" * 40)
        
        return more_visible_side
        
    def should_process_lower_body(self, landmarks, results=None):
        """
        Determina se deve processar a parte inferior do corpo com base em critérios robustos.
        
        Critérios para Vista Lateral (processamento superior):
        - Landmarks do pé e tornozelo com visibilidade próxima de 0
        - Pessoa vista de perfil
        
        Critérios para Vista Inferior (processamento inferior):
        - Todos os landmarks bem visíveis (superiores e inferiores)
        - Imagem geralmente tirada na vertical
        - Boa visibilidade de pés, tornozelos e joelhos
        
        Args:
            landmarks (dict): Dicionário com as coordenadas dos landmarks
            results: Resultados originais do MediaPipe (opcional)
            
        Returns:
            bool: True se deve processar a parte inferior do corpo, False caso contrário
        """
        try:
            # Se temos os resultados originais, usa a verificação baseada em visibilidade
            if results is not None:
                return self._enhanced_lower_body_check(results, landmarks)
            else:
                # Caso contrário, usa a lógica de fallback baseada na presença dos landmarks
                return self._fallback_lower_body_check(landmarks)
        except Exception as e:
            print(f"Erro na decisão de processamento: {e}")
            # Em caso de erro, usa a lógica de fallback baseada na presença dos landmarks
            return self._fallback_lower_body_check(landmarks)
    
    def _enhanced_lower_body_check(self, results, landmarks):
        """
        Verificação aprimorada usando múltiplos critérios para determinar o tipo de processamento.
        
        Args:
            results: Resultados originais do MediaPipe
            landmarks (dict): Dicionário com as coordenadas dos landmarks
            
        Returns:
            bool: True se deve processar a parte inferior do corpo
        """
        if not hasattr(results, 'pose_landmarks') or not results.pose_landmarks:
            return False
            
        mp_landmarks = results.pose_landmarks.landmark
        
        # === CRITÉRIO 1: VISIBILIDADE DOS PÉS E TORNOZELOS ===
        # Vista lateral: pés e tornozelos com visibilidade ~0
        # Vista inferior: pés e tornozelos bem visíveis
        
        foot_ankle_landmarks = [
            self.mp_holistic.PoseLandmark.RIGHT_ANKLE.value,    # 28
            self.mp_holistic.PoseLandmark.LEFT_ANKLE.value,     # 27
            self.mp_holistic.PoseLandmark.RIGHT_FOOT_INDEX.value, # 32
            self.mp_holistic.PoseLandmark.LEFT_FOOT_INDEX.value   # 31
        ]
        
        foot_ankle_visibilities = [mp_landmarks[idx].visibility for idx in foot_ankle_landmarks]
        avg_foot_ankle_visibility = sum(foot_ankle_visibilities) / len(foot_ankle_visibilities)
        min_foot_ankle_visibility = min(foot_ankle_visibilities)
        
        # Se a visibilidade mínima dos pés/tornozelos for muito baixa, é vista lateral
        if min_foot_ankle_visibility < 0.1 or avg_foot_ankle_visibility < 0.3:
            print(f"Vista lateral detectada - Pés/tornozelos pouco visíveis (min: {min_foot_ankle_visibility:.2f}, avg: {avg_foot_ankle_visibility:.2f})")
            return False
        
        # === CRITÉRIO 2: VISIBILIDADE GERAL DOS LANDMARKS INFERIORES ===
        lower_body_landmarks = [
            self.mp_holistic.PoseLandmark.RIGHT_HIP.value,      # 24
            self.mp_holistic.PoseLandmark.LEFT_HIP.value,       # 23
            self.mp_holistic.PoseLandmark.RIGHT_KNEE.value,     # 26
            self.mp_holistic.PoseLandmark.LEFT_KNEE.value,      # 25
            self.mp_holistic.PoseLandmark.RIGHT_ANKLE.value,    # 28
            self.mp_holistic.PoseLandmark.LEFT_ANKLE.value,     # 27
            self.mp_holistic.PoseLandmark.RIGHT_FOOT_INDEX.value, # 32
            self.mp_holistic.PoseLandmark.LEFT_FOOT_INDEX.value   # 31
        ]
        
        lower_visibilities = [mp_landmarks[idx].visibility for idx in lower_body_landmarks]
        avg_lower_visibility = sum(lower_visibilities) / len(lower_visibilities)
        visible_lower_count = sum(1 for v in lower_visibilities if v > 0.5)
        
        # === CRITÉRIO 3: VISIBILIDADE DOS LANDMARKS SUPERIORES ===
        upper_body_landmarks = [
            self.mp_holistic.PoseLandmark.RIGHT_SHOULDER.value,  # 12
            self.mp_holistic.PoseLandmark.LEFT_SHOULDER.value,   # 11
            self.mp_holistic.PoseLandmark.RIGHT_ELBOW.value,     # 14
            self.mp_holistic.PoseLandmark.LEFT_ELBOW.value,      # 13
            self.mp_holistic.PoseLandmark.RIGHT_WRIST.value,     # 16
            self.mp_holistic.PoseLandmark.LEFT_WRIST.value       # 15
        ]
        
        upper_visibilities = [mp_landmarks[idx].visibility for idx in upper_body_landmarks]
        avg_upper_visibility = sum(upper_visibilities) / len(upper_visibilities)
        visible_upper_count = sum(1 for v in upper_visibilities if v > 0.5)
        
        # === CRITÉRIO 4: ANÁLISE DA ORIENTAÇÃO DA IMAGEM ===
        # Verifica se a imagem parece ser tirada na vertical (vista inferior)
        # Calcula a distribuição vertical dos landmarks
        
        all_visible_landmarks = []
        for idx in range(len(mp_landmarks)):
            if mp_landmarks[idx].visibility > 0.5:
                all_visible_landmarks.append({
                    'idx': idx,
                    'y': mp_landmarks[idx].y,
                    'visibility': mp_landmarks[idx].visibility
                })
        
        # Se temos poucos landmarks visíveis, não é vista inferior
        if len(all_visible_landmarks) < 10:
            print(f"Poucos landmarks visíveis ({len(all_visible_landmarks)}) - Vista lateral")
            return False
        
        # Calcula a distribuição vertical
        y_positions = [lm['y'] for lm in all_visible_landmarks]
        y_range = max(y_positions) - min(y_positions)
        
        # === CRITÉRIO 5: PROPORÇÃO DE LANDMARKS VISÍVEIS ===
        total_key_landmarks = len(lower_body_landmarks) + len(upper_body_landmarks)
        total_visible_key = visible_lower_count + visible_upper_count
        visibility_ratio = total_visible_key / total_key_landmarks
        
        # === DECISÃO FINAL ===
        print(f"Análise de processamento:")
        print(f"  - Visibilidade pés/tornozelos: min={min_foot_ankle_visibility:.2f}, avg={avg_foot_ankle_visibility:.2f}")
        print(f"  - Visibilidade inferior: avg={avg_lower_visibility:.2f}, visíveis={visible_lower_count}/{len(lower_body_landmarks)}")
        print(f"  - Visibilidade superior: avg={avg_upper_visibility:.2f}, visíveis={visible_upper_count}/{len(upper_body_landmarks)}")
        print(f"  - Landmarks totais visíveis: {len(all_visible_landmarks)}")
        print(f"  - Proporção de landmarks-chave visíveis: {visibility_ratio:.2f}")
        print(f"  - Distribuição vertical: {y_range:.2f}")
        
        # Condições para processamento inferior (vista de baixo/vertical):
        conditions_for_lower = [
            avg_foot_ankle_visibility > 0.6,  # Pés e tornozelos bem visíveis
            visible_lower_count >= 6,          # Pelo menos 6 dos 8 landmarks inferiores visíveis
            avg_lower_visibility > 0.7,       # Alta visibilidade geral da parte inferior
            visibility_ratio > 0.75,          # Mais de 75% dos landmarks-chave visíveis
            len(all_visible_landmarks) >= 15, # Muitos landmarks visíveis no geral
            y_range > 0.4                     # Boa distribuição vertical (corpo inteiro visível)
        ]
        
        conditions_met = sum(conditions_for_lower)
        
        print(f"  - Condições atendidas para vista inferior: {conditions_met}/6")
        
        # Precisa atender pelo menos 4 das 6 condições para ser considerado vista inferior
        is_lower_body = conditions_met >= 4
        
        # Verificação adicional: se os pés/tornozelos têm visibilidade muito baixa, força vista lateral
        if avg_foot_ankle_visibility < 0.4:
            print("  - Forçando vista lateral devido à baixa visibilidade de pés/tornozelos")
            is_lower_body = False
        
        # Verificação adicional: se há muito poucos landmarks inferiores visíveis, força vista lateral
        if visible_lower_count < 4:
            print("  - Forçando vista lateral devido a poucos landmarks inferiores visíveis")
            is_lower_body = False
        
        decision = "Vista inferior (processamento inferior)" if is_lower_body else "Vista lateral (processamento superior)"
        print(f"  - DECISÃO: {decision}")
        
        return is_lower_body
    
    def _check_lower_body_visibility(self, results):
        """
        Verifica a visibilidade dos landmarks usando os valores de visibilidade do MediaPipe.
        
        Args:
            results: Resultados originais do MediaPipe
            
        Returns:
            bool: True se deve processar a parte inferior do corpo
        """
        if not hasattr(results, 'pose_landmarks') or not results.pose_landmarks:
            return False
            
        landmarks = results.pose_landmarks.landmark
        
        # Verifica a visibilidade dos landmarks inferiores
        right_ankle_visibility = landmarks[self.mp_holistic.PoseLandmark.RIGHT_ANKLE.value].visibility
        left_ankle_visibility = landmarks[self.mp_holistic.PoseLandmark.LEFT_ANKLE.value].visibility
        ankle_visibility = max(right_ankle_visibility, left_ankle_visibility)  # Pega a maior visibilidade entre os tornozelos
        
        right_knee_visibility = landmarks[self.mp_holistic.PoseLandmark.RIGHT_KNEE.value].visibility
        left_knee_visibility = landmarks[self.mp_holistic.PoseLandmark.LEFT_KNEE.value].visibility
        knee_visibility = max(right_knee_visibility, left_knee_visibility)  # Pega a maior visibilidade entre os joelhos
        
        right_foot_visibility = landmarks[self.mp_holistic.PoseLandmark.RIGHT_FOOT_INDEX.value].visibility
        left_foot_visibility = landmarks[self.mp_holistic.PoseLandmark.LEFT_FOOT_INDEX.value].visibility
        foot_visibility = max(right_foot_visibility, left_foot_visibility)  # Pega a maior visibilidade entre os pés
        
        # Verifica a visibilidade dos landmarks superiores
        right_shoulder_visibility = landmarks[self.mp_holistic.PoseLandmark.RIGHT_SHOULDER.value].visibility
        left_shoulder_visibility = landmarks[self.mp_holistic.PoseLandmark.LEFT_SHOULDER.value].visibility
        shoulder_visibility = max(right_shoulder_visibility, left_shoulder_visibility)  # Pega a maior visibilidade entre os ombros
        
        right_elbow_visibility = landmarks[self.mp_holistic.PoseLandmark.RIGHT_ELBOW.value].visibility
        left_elbow_visibility = landmarks[self.mp_holistic.PoseLandmark.LEFT_ELBOW.value].visibility
        elbow_visibility = max(right_elbow_visibility, left_elbow_visibility)  # Pega a maior visibilidade entre os cotovelos
        
        right_wrist_visibility = landmarks[self.mp_holistic.PoseLandmark.RIGHT_WRIST.value].visibility
        left_wrist_visibility = landmarks[self.mp_holistic.PoseLandmark.LEFT_WRIST.value].visibility
        wrist_visibility = max(right_wrist_visibility, left_wrist_visibility)  # Pega a maior visibilidade entre os pulsos
        
        # Calcula a visibilidade média dos pontos inferiores e superiores
        lower_visibility_avg = (knee_visibility + ankle_visibility + foot_visibility) / 3
        upper_visibility_avg = (shoulder_visibility + elbow_visibility + wrist_visibility) / 3
        
        # Se a visibilidade do tornozelo ou pé for 0, trata como "imagem de perfil" ou foco na parte superior (retorna False)
        # Isso impede que o código tente processar a parte inferior se ela não estiver presente ou visível.
        if ankle_visibility == 0 or foot_visibility == 0:
            return False
            
        # Verifica se os landmarks inferiores têm visibilidade alta
        # Garante que os três pontos principais da perna (joelho, tornozelo, pé) tenham visibilidade individualmente > 0.5
        lower_landmarks_visible = all(v > 0.5 for v in [knee_visibility, ankle_visibility, foot_visibility])
        
        # Compara a visibilidade dos landmarks inferiores com os superiores
        # Condição 1: Visibilidade média da parte inferior > 80% da visibilidade média da parte superior
        # OU
        # Condição 2: Visibilidade média da parte inferior é MUITO alta (ex: > 0.8) em geral, independente da superior
        if lower_landmarks_visible and (lower_visibility_avg > upper_visibility_avg * 0.8 or lower_visibility_avg > 0.8):
            return True
            
        return False
    
    def _fallback_lower_body_check(self, landmarks):
        """
        Verificação de fallback baseada na presença dos landmarks quando não temos dados de visibilidade.
        
        Args:
            landmarks (dict): Dicionário com as coordenadas dos landmarks
            
        Returns:
            bool: True se deve processar a parte inferior do corpo
        """
        print("Usando verificação de fallback (sem dados de visibilidade)")
        
        # Landmarks críticos para pés e tornozelos
        critical_foot_ankle_landmarks = [
            'RIGHT_ANKLE', 'LEFT_ANKLE', 
            'RIGHT_FOOT_INDEX', 'LEFT_FOOT_INDEX'
        ]
        
        # Landmarks da parte inferior do corpo
        lower_body_landmarks = [
            'RIGHT_HIP', 'LEFT_HIP',
            'RIGHT_KNEE', 'LEFT_KNEE', 
            'RIGHT_ANKLE', 'LEFT_ANKLE',
            'RIGHT_FOOT_INDEX', 'LEFT_FOOT_INDEX'
        ]
        
        # Landmarks da parte superior do corpo
        upper_body_landmarks = [
            'RIGHT_SHOULDER', 'LEFT_SHOULDER',
            'RIGHT_ELBOW', 'LEFT_ELBOW',
            'RIGHT_WRIST', 'LEFT_WRIST'
        ]
        
        # Conta landmarks presentes
        foot_ankle_present = sum(1 for lm in critical_foot_ankle_landmarks if lm in landmarks and landmarks[lm] is not None)
        lower_present = sum(1 for lm in lower_body_landmarks if lm in landmarks and landmarks[lm] is not None)
        upper_present = sum(1 for lm in upper_body_landmarks if lm in landmarks and landmarks[lm] is not None)
        
        total_landmarks_present = len([lm for lm in landmarks.values() if lm is not None])
        
        print(f"Fallback - Landmarks presentes:")
        print(f"  - Pés/tornozelos: {foot_ankle_present}/{len(critical_foot_ankle_landmarks)}")
        print(f"  - Parte inferior: {lower_present}/{len(lower_body_landmarks)}")
        print(f"  - Parte superior: {upper_present}/{len(upper_body_landmarks)}")
        print(f"  - Total de landmarks: {total_landmarks_present}")
        
        # Critérios para vista lateral (processamento superior):
        # - Poucos ou nenhum landmark de pé/tornozelo
        # - Menos landmarks inferiores em geral
        
        if foot_ankle_present <= 1:  # Muito poucos pés/tornozelos visíveis
            print("  - Vista lateral detectada: poucos pés/tornozelos presentes")
            return False
        
        if lower_present < 4:  # Menos da metade dos landmarks inferiores
            print("  - Vista lateral detectada: poucos landmarks inferiores presentes")
            return False
        
        # Critérios para vista inferior (processamento inferior):
        # - Boa presença de landmarks de pés/tornozelos
        # - Boa presença geral de landmarks inferiores
        # - Muitos landmarks totais presentes
        
        conditions_for_lower = [
            foot_ankle_present >= 3,           # Pelo menos 3 dos 4 pés/tornozelos
            lower_present >= 6,               # Pelo menos 6 dos 8 landmarks inferiores
            upper_present >= 4,               # Pelo menos 4 dos 6 landmarks superiores
            total_landmarks_present >= 15,    # Muitos landmarks no total
            lower_present >= upper_present    # Mais landmarks inferiores que superiores
        ]
        
        conditions_met = sum(conditions_for_lower)
        print(f"  - Condições atendidas para vista inferior: {conditions_met}/5")
        
        # Precisa atender pelo menos 3 das 5 condições
        is_lower_body = conditions_met >= 3
        
        decision = "Vista inferior (processamento inferior)" if is_lower_body else "Vista lateral (processamento superior)"
        print(f"  - DECISÃO FALLBACK: {decision}")
        
        return is_lower_body
    
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