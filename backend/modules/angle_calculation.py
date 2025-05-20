import numpy as np
import cv2 as cv

# Função para calcular ângulos entre três pontos
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle

# Função para desenhar ângulos na imagem
def draw_angles(frame, landmarks, mpHolistic, show_angles=True, show_upper_body=True, show_lower_body=True):
    if not show_angles:
        return frame
        
    h, w, _ = frame.shape
    
    # Desenha ângulos da parte superior do corpo
    if show_upper_body:
        # Ângulo do cotovelo direito
        right_shoulder = (int(landmarks[mpHolistic.PoseLandmark.RIGHT_SHOULDER.value].x * w),
                        int(landmarks[mpHolistic.PoseLandmark.RIGHT_SHOULDER.value].y * h))
        right_elbow = (int(landmarks[mpHolistic.PoseLandmark.RIGHT_ELBOW.value].x * w),
                    int(landmarks[mpHolistic.PoseLandmark.RIGHT_ELBOW.value].y * h))
        right_wrist = (int(landmarks[mpHolistic.PoseLandmark.RIGHT_WRIST.value].x * w),
                    int(landmarks[mpHolistic.PoseLandmark.RIGHT_WRIST.value].y * h))
        
        # Calcula o ângulo do cotovelo direito
        right_elbow_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)
        
        # Desenha o ângulo do cotovelo direito
        cv.putText(frame, f"Cotovelo D: {right_elbow_angle:.1f}", right_elbow, 
                cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv.LINE_AA)
        
        # Ângulo do cotovelo esquerdo
        left_shoulder = (int(landmarks[mpHolistic.PoseLandmark.LEFT_SHOULDER.value].x * w),
                        int(landmarks[mpHolistic.PoseLandmark.LEFT_SHOULDER.value].y * h))
        left_elbow = (int(landmarks[mpHolistic.PoseLandmark.LEFT_ELBOW.value].x * w),
                    int(landmarks[mpHolistic.PoseLandmark.LEFT_ELBOW.value].y * h))
        left_wrist = (int(landmarks[mpHolistic.PoseLandmark.LEFT_WRIST.value].x * w),
                    int(landmarks[mpHolistic.PoseLandmark.LEFT_WRIST.value].y * h))
        
        # Calcula o ângulo do cotovelo esquerdo
        left_elbow_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
        
        # Desenha o ângulo do cotovelo esquerdo
        cv.putText(frame, f"Cotovelo E: {left_elbow_angle:.1f}", left_elbow, 
                cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv.LINE_AA)
    
    # Desenha ângulos da parte inferior do corpo
    if show_lower_body:
        # Ângulo do joelho direito
        right_hip = (int(landmarks[mpHolistic.PoseLandmark.RIGHT_HIP.value].x * w),
                    int(landmarks[mpHolistic.PoseLandmark.RIGHT_HIP.value].y * h))
        right_knee = (int(landmarks[mpHolistic.PoseLandmark.RIGHT_KNEE.value].x * w),
                    int(landmarks[mpHolistic.PoseLandmark.RIGHT_KNEE.value].y * h))
        right_ankle = (int(landmarks[mpHolistic.PoseLandmark.RIGHT_ANKLE.value].x * w),
                    int(landmarks[mpHolistic.PoseLandmark.RIGHT_ANKLE.value].y * h))
        
        # Calcula o ângulo do joelho direito
        right_knee_angle = calculate_angle(right_hip, right_knee, right_ankle)
        
        # Desenha o ângulo do joelho direito
        cv.putText(frame, f"Joelho D: {right_knee_angle:.1f}", right_knee, 
                cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv.LINE_AA)
        
        # Ângulo do joelho esquerdo
        left_hip = (int(landmarks[mpHolistic.PoseLandmark.LEFT_HIP.value].x * w),
                    int(landmarks[mpHolistic.PoseLandmark.LEFT_HIP.value].y * h))
        left_knee = (int(landmarks[mpHolistic.PoseLandmark.LEFT_KNEE.value].x * w),
                    int(landmarks[mpHolistic.PoseLandmark.LEFT_KNEE.value].y * h))
        left_ankle = (int(landmarks[mpHolistic.PoseLandmark.LEFT_ANKLE.value].x * w),
                    int(landmarks[mpHolistic.PoseLandmark.LEFT_ANKLE.value].y * h))
        
        # Calcula o ângulo do joelho esquerdo
        left_knee_angle = calculate_angle(left_hip, left_knee, left_ankle)
        
        # Desenha o ângulo do joelho esquerdo
        cv.putText(frame, f"Joelho E: {left_knee_angle:.1f}", left_knee, 
                cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv.LINE_AA)
    
    return frame