import numpy as np
from ..core.utils import calculate_angle, calculate_angle_with_vertical

class AngleAnalyzer:
    def __init__(self):
        """
        Inicializa o analisador de ângulos.
        """
        pass
    
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