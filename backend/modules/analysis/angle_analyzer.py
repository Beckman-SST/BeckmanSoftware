import numpy as np
from ..core.utils import calculate_angle, calculate_angle_with_vertical

class AngleAnalyzer:
    def __init__(self):
        """
        Inicializa o analisador de ângulos.
        """
        pass
        
    # A função calculate_neck_angle foi removida
    
    def calculate_spine_angle(self, landmarks, use_vertical_reference=True):
        """
        Calcula o ângulo da coluna vertebral usando os pontos médios dos ombros e quadris.
        
        Args:
            landmarks (dict): Dicionário com as coordenadas dos landmarks
            use_vertical_reference (bool): Se True, calcula o ângulo em relação à vertical
                                          Se False, calcula o ângulo interno
            
        Returns:
            float: Ângulo da coluna ou None se não for possível calcular
        """
        # IDs dos landmarks dos ombros
        left_shoulder_id, right_shoulder_id = 11, 12
        
        # IDs dos landmarks dos quadris
        left_hip_id, right_hip_id = 23, 24
        
        # Verifica se todos os landmarks necessários estão disponíveis
        required_landmarks = [left_shoulder_id, right_shoulder_id, left_hip_id, right_hip_id]
        if not all(lm_id in landmarks for lm_id in required_landmarks):
            return None
        
        # Calcula o ponto médio entre os ombros
        left_shoulder = landmarks[left_shoulder_id]
        right_shoulder = landmarks[right_shoulder_id]
        shoulder_midpoint = (
            (left_shoulder[0] + right_shoulder[0]) // 2,
            (left_shoulder[1] + right_shoulder[1]) // 2
        )
        
        # Calcula o ponto médio entre os quadris
        left_hip = landmarks[left_hip_id]
        right_hip = landmarks[right_hip_id]
        hip_midpoint = (
            (left_hip[0] + right_hip[0]) // 2,
            (left_hip[1] + right_hip[1]) // 2
        )
        
        if use_vertical_reference:
            # Calcula o ângulo em relação à vertical
            return calculate_angle_with_vertical(shoulder_midpoint, hip_midpoint)
        else:
            # Para calcular o ângulo interno, precisamos de um terceiro ponto
            # Vamos criar um ponto acima do ponto médio dos ombros (na mesma vertical)
            vertical_point = (shoulder_midpoint[0], shoulder_midpoint[1] - 100)
            
            # Calcula o ângulo interno
            return calculate_angle(vertical_point, shoulder_midpoint, hip_midpoint)
    
    def calculate_elbow_angle(self, landmarks, side='right'):
        """
        Calcula o ângulo do cotovelo.
        
        Args:
            landmarks (dict): Dicionário com as coordenadas dos landmarks
            side (str): Lado do corpo ('right' ou 'left')
            
        Returns:
            float: Ângulo do cotovelo ou None se não for possível calcular
        """
        if side == 'right':
            # Ombro, cotovelo e pulso direitos
            shoulder_id, elbow_id, wrist_id = 12, 14, 16
        else:
            # Ombro, cotovelo e pulso esquerdos
            shoulder_id, elbow_id, wrist_id = 11, 13, 15
        
        # Verifica se todos os landmarks necessários estão disponíveis
        if not all(lm_id in landmarks for lm_id in [shoulder_id, elbow_id, wrist_id]):
            return None
        
        # Calcula o ângulo
        return calculate_angle(
            landmarks[shoulder_id],
            landmarks[elbow_id],
            landmarks[wrist_id]
        )
    
    def calculate_wrist_angle(self, landmarks, side='right'):
        """
        Calcula o ângulo do pulso entre cotovelo, pulso e dedo médio.
        
        Args:
            landmarks (dict): Dicionário com as coordenadas dos landmarks
            side (str): Lado do corpo ('right' ou 'left')
            
        Returns:
            float: Ângulo do pulso ou None se não for possível calcular
        """
        if side == 'right':
            # Cotovelo, pulso e dedo médio direitos
            elbow_id, wrist_id, middle_finger_id = 14, 16, 18
        else:
            # Cotovelo, pulso e dedo médio esquerdos
            elbow_id, wrist_id, middle_finger_id = 13, 15, 17
        
        # Verifica se todos os landmarks necessários estão disponíveis
        if not all(lm_id in landmarks for lm_id in [elbow_id, wrist_id, middle_finger_id]):
            return None
        
        # Calcula o ângulo entre cotovelo, pulso e dedo médio
        return calculate_angle(
            landmarks[elbow_id],
            landmarks[wrist_id],
            landmarks[middle_finger_id]
        )
    
    def calculate_knee_angle(self, landmarks, side='right'):
        """
        Calcula o ângulo do joelho.
        
        Args:
            landmarks (dict): Dicionário com as coordenadas dos landmarks
            side (str): Lado do corpo ('right' ou 'left')
            
        Returns:
            float: Ângulo do joelho ou None se não for possível calcular
        """
        if side == 'right':
            # Quadril, joelho e tornozelo direitos
            hip_id, knee_id, ankle_id = 24, 26, 28
        else:
            # Quadril, joelho e tornozelo esquerdos
            hip_id, knee_id, ankle_id = 23, 25, 27
        
        # Verifica se todos os landmarks necessários estão disponíveis
        if not all(lm_id in landmarks for lm_id in [hip_id, knee_id, ankle_id]):
            return None
        
        # Calcula o ângulo
        return calculate_angle(
            landmarks[hip_id],
            landmarks[knee_id],
            landmarks[ankle_id]
        )
    
    def calculate_ankle_angle(self, landmarks, side='right'):
        """
        Calcula o ângulo do tornozelo em relação à horizontal.
        
        Args:
            landmarks (dict): Dicionário com as coordenadas dos landmarks
            side (str): Lado do corpo ('right' ou 'left')
            
        Returns:
            float: Ângulo do tornozelo ou None se não for possível calcular
        """
        if side == 'right':
            # Joelho e tornozelo direitos
            knee_id, ankle_id = 26, 28
        else:
            # Joelho e tornozelo esquerdos
            knee_id, ankle_id = 25, 27
        
        # Verifica se todos os landmarks necessários estão disponíveis
        if not all(lm_id in landmarks for lm_id in [knee_id, ankle_id]):
            return None
        
        # Calcula o ângulo com a horizontal (90 - ângulo com a vertical)
        vertical_angle = calculate_angle_with_vertical(
            landmarks[knee_id],
            landmarks[ankle_id]
        )
        
        return 90 - vertical_angle if vertical_angle is not None else None
    
    def calculate_shoulder_angle(self, landmarks, side='right'):
        """
        Calcula o ângulo do braço superior (ombro) em relação à vertical.
        
        Args:
            landmarks (dict): Dicionário com as coordenadas dos landmarks
            side (str): Lado do corpo ('right' ou 'left')
            
        Returns:
            float: Ângulo do ombro ou None se não for possível calcular
            int: Pontuação baseada no ângulo (1-4 pontos)
            bool: Indica se o braço está em abdução (para o lado)
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
        if not all(lm_id in landmarks for lm_id in [shoulder_id, elbow_id, opposite_shoulder_id]):
            return None, None, False
        
        # Calcula o ângulo com a vertical
        shoulder_angle = calculate_angle_with_vertical(
            landmarks[shoulder_id],
            landmarks[elbow_id]
        )
        
        if shoulder_angle is None:
            return None, None, False
        
        # Determina a pontuação com base no ângulo
        score = 1  # Valor padrão
        
        if shoulder_angle <= 20:
            score = 1  # Verde (0° a 20°)
        elif shoulder_angle <= 45:
            score = 2  # Amarelo (>20° a 45°)
        elif shoulder_angle <= 90:
            score = 3  # Laranja (>45° a 90°)
        else:
            score = 4  # Vermelho (>90°)
        
        # Verifica se o braço está em abdução (para o lado)
        # Calculamos a diferença horizontal entre o cotovelo e a linha vertical do ombro
        is_abducted = False
        
        # Calcula a diferença horizontal entre os ombros
        shoulder_x = landmarks[shoulder_id][0]
        opposite_shoulder_x = landmarks[opposite_shoulder_id][0]
        shoulder_distance = abs(shoulder_x - opposite_shoulder_x)
        
        # Calcula a diferença horizontal entre o ombro e o cotovelo
        elbow_x = landmarks[elbow_id][0]
        horizontal_diff = abs(elbow_x - shoulder_x)
        
        # Se a diferença horizontal for significativa em relação à distância entre os ombros,
        # consideramos que o braço está em abdução
        if horizontal_diff > (shoulder_distance * 0.4):
            is_abducted = True
        
        return shoulder_angle, score, is_abducted
    
    def calculate_eyes_to_device_angle(self, landmarks, device_center):
        """
        Calcula o ângulo entre os olhos e o dispositivo eletrônico.
        
        Args:
            landmarks (dict): Dicionário com as coordenadas dos landmarks
            device_center (tuple): Coordenadas (x, y) do centro do dispositivo
            
        Returns:
            float: Ângulo entre os olhos e o dispositivo ou None se não for possível calcular
        """
        # IDs dos olhos (MediaPipe Pose)
        left_eye_id, right_eye_id = 2, 5
        
        # Verifica se ambos os olhos estão disponíveis
        if not all(eye_id in landmarks for eye_id in [left_eye_id, right_eye_id]):
            return None
        
        # Calcula o ponto médio entre os olhos
        left_eye = landmarks[left_eye_id]
        right_eye = landmarks[right_eye_id]
        
        eyes_center = (
            (left_eye[0] + right_eye[0]) // 2,
            (left_eye[1] + right_eye[1]) // 2
        )
        
        # Calcula o ângulo com a vertical
        return calculate_angle_with_vertical(eyes_center, device_center)