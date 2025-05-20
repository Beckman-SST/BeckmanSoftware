import cv2 as cv
import numpy as np
import mediapipe as mp
from .config import MIN_DETECTION_CONFIDENCE, MIN_TRACKING_CONFIDENCE

# Configurações do MediaPipe
mpDraw = mp.solutions.drawing_utils
mpHolistic = mp.solutions.holistic

# Inicializando o modelo Holistic com parâmetros otimizados
holistic = mpHolistic.Holistic(
    min_detection_confidence=MIN_DETECTION_CONFIDENCE,
    min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
    model_complexity=2 
)

# Buffer para média móvel dos landmarks
landmark_buffer = []

# Conexões personalizadas para mostrar apenas o necessário
custom_pose_connections = [
    # Upper body connections
    (mpHolistic.PoseLandmark.RIGHT_SHOULDER.value, mpHolistic.PoseLandmark.RIGHT_ELBOW.value),
    (mpHolistic.PoseLandmark.RIGHT_ELBOW.value, mpHolistic.PoseLandmark.RIGHT_WRIST.value),
    (mpHolistic.PoseLandmark.LEFT_SHOULDER.value, mpHolistic.PoseLandmark.LEFT_ELBOW.value),
    (mpHolistic.PoseLandmark.LEFT_ELBOW.value, mpHolistic.PoseLandmark.LEFT_WRIST.value),
    # Lower body connections with heel and ankle-foot connections
    (mpHolistic.PoseLandmark.RIGHT_HIP.value, mpHolistic.PoseLandmark.RIGHT_KNEE.value),
    (mpHolistic.PoseLandmark.RIGHT_KNEE.value, mpHolistic.PoseLandmark.RIGHT_ANKLE.value),
    (mpHolistic.PoseLandmark.RIGHT_ANKLE.value, mpHolistic.PoseLandmark.RIGHT_HEEL.value),
    (mpHolistic.PoseLandmark.RIGHT_HEEL.value, mpHolistic.PoseLandmark.RIGHT_FOOT_INDEX.value),
    (mpHolistic.PoseLandmark.RIGHT_ANKLE.value, mpHolistic.PoseLandmark.RIGHT_FOOT_INDEX.value),
    (mpHolistic.PoseLandmark.LEFT_HIP.value, mpHolistic.PoseLandmark.LEFT_KNEE.value),
    (mpHolistic.PoseLandmark.LEFT_KNEE.value, mpHolistic.PoseLandmark.LEFT_ANKLE.value),
    (mpHolistic.PoseLandmark.LEFT_ANKLE.value, mpHolistic.PoseLandmark.LEFT_HEEL.value),
    (mpHolistic.PoseLandmark.LEFT_HEEL.value, mpHolistic.PoseLandmark.LEFT_FOOT_INDEX.value),
    (mpHolistic.PoseLandmark.LEFT_ANKLE.value, mpHolistic.PoseLandmark.LEFT_FOOT_INDEX.value)
]

# Função para calcular a visibilidade de um conjunto de landmarks
def calculate_visibility(landmarks, indices):
    visibility_sum = 0
    valid_count = 0
    for idx in indices:
        if landmarks[idx].visibility:
            visibility_sum += landmarks[idx].visibility
            valid_count += 1
    
    # Retorna 0 se não houver landmarks válidos
    if valid_count == 0:
        return 0
    
    # Calcula a média de visibilidade
    avg_visibility = visibility_sum / valid_count
    
    # Aplica um limiar mínimo de confiança
    return avg_visibility if avg_visibility > MIN_DETECTION_CONFIDENCE else 0

# Função para determinar se deve processar parte inferior do corpo
def should_process_lower_body(landmarks, process_lower_body=True):
    # Se o processamento da parte inferior estiver desativado nas configurações, retorna False
    if not process_lower_body:
        return False
        
    # Verifica a visibilidade dos landmarks inferiores
    right_ankle_visibility = landmarks[mpHolistic.PoseLandmark.RIGHT_ANKLE.value].visibility
    left_ankle_visibility = landmarks[mpHolistic.PoseLandmark.LEFT_ANKLE.value].visibility
    ankle_visibility = max(right_ankle_visibility, left_ankle_visibility)
    
    right_knee_visibility = landmarks[mpHolistic.PoseLandmark.RIGHT_KNEE.value].visibility
    left_knee_visibility = landmarks[mpHolistic.PoseLandmark.LEFT_KNEE.value].visibility
    knee_visibility = max(right_knee_visibility, left_knee_visibility)
    
    right_foot_visibility = landmarks[mpHolistic.PoseLandmark.RIGHT_FOOT_INDEX.value].visibility
    left_foot_visibility = landmarks[mpHolistic.PoseLandmark.LEFT_FOOT_INDEX.value].visibility
    foot_visibility = max(right_foot_visibility, left_foot_visibility)
    
    # Verifica a visibilidade dos landmarks superiores
    right_shoulder_visibility = landmarks[mpHolistic.PoseLandmark.RIGHT_SHOULDER.value].visibility
    left_shoulder_visibility = landmarks[mpHolistic.PoseLandmark.LEFT_SHOULDER.value].visibility
    shoulder_visibility = max(right_shoulder_visibility, left_shoulder_visibility)
    
    right_elbow_visibility = landmarks[mpHolistic.PoseLandmark.RIGHT_ELBOW.value].visibility
    left_elbow_visibility = landmarks[mpHolistic.PoseLandmark.LEFT_ELBOW.value].visibility
    elbow_visibility = max(right_elbow_visibility, left_elbow_visibility)
    
    right_wrist_visibility = landmarks[mpHolistic.PoseLandmark.RIGHT_WRIST.value].visibility
    left_wrist_visibility = landmarks[mpHolistic.PoseLandmark.LEFT_WRIST.value].visibility
    wrist_visibility = max(right_wrist_visibility, left_wrist_visibility)
    
    # Calcula a visibilidade média dos pontos inferiores e superiores
    lower_visibility_avg = (knee_visibility + ankle_visibility + foot_visibility) / 3
    upper_visibility_avg = (shoulder_visibility + elbow_visibility + wrist_visibility) / 3
    
    # Se a visibilidade do tornozelo for 0, processa como imagem de perfil (ângulos superiores)
    if ankle_visibility == 0 or foot_visibility == 0:
        return False
    
    # Verifica se os landmarks inferiores têm visibilidade alta
    lower_landmarks_visible = all(v > 0.5 for v in [knee_visibility, ankle_visibility, foot_visibility])
    
    # Compara a visibilidade dos landmarks inferiores com os superiores
    # Se os landmarks inferiores têm visibilidade significativamente maior que os superiores
    # ou se os landmarks inferiores têm visibilidade muito alta em geral, processa como parte inferior
    if lower_landmarks_visible and (lower_visibility_avg > upper_visibility_avg * 0.8 or lower_visibility_avg > 0.8):
        return True
    
    return False

# Função para processar landmarks e aplicar média móvel
def process_landmarks(results, moving_average_window):
    if not results.pose_landmarks:
        return results
        
    # Validação e suavização dos landmarks
    current_landmarks = [(lm.x, lm.y, lm.z, lm.visibility) for lm in results.pose_landmarks.landmark]
    
    # Atualiza o buffer de landmarks
    global landmark_buffer
    landmark_buffer.append(current_landmarks)
    if len(landmark_buffer) > moving_average_window:
        landmark_buffer.pop(0)
    
    # Aplica média móvel se houver landmarks suficientes
    if len(landmark_buffer) >= 3:
        # Calcula a média das posições dos landmarks
        for i in range(len(current_landmarks)):
            x_avg = sum(frame[i][0] for frame in landmark_buffer) / len(landmark_buffer)
            y_avg = sum(frame[i][1] for frame in landmark_buffer) / len(landmark_buffer)
            z_avg = sum(frame[i][2] for frame in landmark_buffer) / len(landmark_buffer)
            vis_avg = sum(frame[i][3] for frame in landmark_buffer) / len(landmark_buffer)
            
            # Atualiza os landmarks com os valores suavizados
            results.pose_landmarks.landmark[i].x = x_avg
            results.pose_landmarks.landmark[i].y = y_avg
            results.pose_landmarks.landmark[i].z = z_avg
            results.pose_landmarks.landmark[i].visibility = vis_avg
    
    return results