"""
Módulo de Validação Anatômica para Landmarks
Detecta landmarks incorretos e poses anatomicamente impossíveis.
"""

import numpy as np
import math
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
import cv2


@dataclass
class ValidationResult:
    """Resultado da validação anatômica."""
    is_valid: bool
    confidence_score: float
    issues: List[str]
    corrected_landmarks: Optional[Dict] = None


class AnatomicalValidator:
    """
    Validador anatômico para landmarks de pose.
    Implementa verificações básicas de proporções corporais e poses realistas.
    """
    
    def __init__(self):
        """Inicializa o validador com parâmetros anatômicos padrão."""
        
        # === PROPORÇÕES CORPORAIS BASEADAS EM ESTUDOS ANTROPOMÉTRICOS ===
        self.body_proportions = {
            # Proporções em relação à altura total do corpo
            'shoulder_width_ratio': (0.15, 0.25),      # 15-25% da altura
            'arm_span_ratio': (0.95, 1.05),            # 95-105% da altura
            'torso_ratio': (0.25, 0.35),               # 25-35% da altura
            'leg_ratio': (0.45, 0.55),                 # 45-55% da altura
            
            # Proporções de segmentos corporais
            'upper_arm_ratio': (0.18, 0.25),           # Ombro-cotovelo
            'forearm_ratio': (0.15, 0.22),             # Cotovelo-pulso
            'thigh_ratio': (0.22, 0.28),               # Quadril-joelho
            'shin_ratio': (0.20, 0.26),                # Joelho-tornozelo
        }
        
        # === LIMITES DE ÂNGULOS ARTICULARES (em graus) ===
        self.joint_angle_limits = {
            'elbow_flexion': (0, 150),          # Flexão do cotovelo
            'knee_flexion': (0, 140),           # Flexão do joelho
            'shoulder_abduction': (0, 180),     # Abdução do ombro
            'hip_flexion': (0, 120),            # Flexão do quadril
            'neck_rotation': (-45, 45),         # Rotação do pescoço
        }
        
        # === LANDMARKS DO MEDIAPIPE POSE ===
        self.landmark_indices = {
            'nose': 0, 'left_eye_inner': 1, 'left_eye': 2, 'left_eye_outer': 3,
            'right_eye_inner': 4, 'right_eye': 5, 'right_eye_outer': 6,
            'left_ear': 7, 'right_ear': 8, 'mouth_left': 9, 'mouth_right': 10,
            'left_shoulder': 11, 'right_shoulder': 12,
            'left_elbow': 13, 'right_elbow': 14,
            'left_wrist': 15, 'right_wrist': 16,
            'left_pinky': 17, 'right_pinky': 18,
            'left_index': 19, 'right_index': 20,
            'left_thumb': 21, 'right_thumb': 22,
            'left_hip': 23, 'right_hip': 24,
            'left_knee': 25, 'right_knee': 26,
            'left_ankle': 27, 'right_ankle': 28,
            'left_heel': 29, 'right_heel': 30,
            'left_foot_index': 31, 'right_foot_index': 32
        }
    
    def validate_landmarks(self, landmarks, image_shape=None) -> ValidationResult:
        """
        Valida um conjunto de landmarks usando múltiplos critérios anatômicos.
        
        Args:
            landmarks: Lista de landmarks (formato MediaPipe ou array numpy)
            image_shape: Forma da imagem (height, width) para normalização
            
        Returns:
            ValidationResult: Resultado da validação com score e issues
        """
        issues = []
        confidence_score = 1.0
        
        # Converte landmarks para formato padrão se necessário
        landmarks_array = self._normalize_landmarks(landmarks, image_shape)
        
        if landmarks_array is None:
            return ValidationResult(False, 0.0, ["Landmarks inválidos ou ausentes"])
        
        # === VALIDAÇÃO 1: VERIFICAÇÃO DE PROPORÇÕES CORPORAIS ===
        proportion_result = self._validate_body_proportions(landmarks_array)
        if not proportion_result['is_valid']:
            issues.extend(proportion_result['issues'])
            confidence_score *= 0.7
        
        # === VALIDAÇÃO 2: VERIFICAÇÃO DE SIMETRIA CORPORAL ===
        symmetry_result = self._validate_body_symmetry(landmarks_array)
        if not symmetry_result['is_valid']:
            issues.extend(symmetry_result['issues'])
            confidence_score *= 0.8
        
        # === VALIDAÇÃO 3: VERIFICAÇÃO DE ÂNGULOS ARTICULARES ===
        angle_result = self._validate_joint_angles(landmarks_array)
        if not angle_result['is_valid']:
            issues.extend(angle_result['issues'])
            confidence_score *= 0.75
        
        # === VALIDAÇÃO 4: DETECÇÃO DE POSES IMPOSSÍVEIS ===
        pose_result = self._detect_impossible_poses(landmarks_array)
        if not pose_result['is_valid']:
            issues.extend(pose_result['issues'])
            confidence_score *= 0.5
        
        is_valid = confidence_score > 0.6  # Threshold de aceitação
        
        return ValidationResult(
            is_valid=is_valid,
            confidence_score=confidence_score,
            issues=issues
        )
    
    def _normalize_landmarks(self, landmarks, image_shape):
        """Normaliza landmarks para formato padrão (x, y, z, visibility)."""
        try:
            if hasattr(landmarks, 'landmark'):  # MediaPipe format
                return np.array([[lm.x, lm.y, lm.z, lm.visibility] 
                               for lm in landmarks.landmark])
            elif isinstance(landmarks, np.ndarray):
                return landmarks
            elif isinstance(landmarks, list):
                return np.array(landmarks)
            else:
                return None
        except:
            return None
    
    def _validate_body_proportions(self, landmarks) -> Dict:
        """Valida proporções corporais básicas."""
        issues = []
        
        try:
            # Calcula altura corporal (cabeça aos pés)
            nose = landmarks[self.landmark_indices['nose']]
            left_ankle = landmarks[self.landmark_indices['left_ankle']]
            right_ankle = landmarks[self.landmark_indices['right_ankle']]
            
            # Usa o tornozelo mais baixo
            ankle_y = max(left_ankle[1], right_ankle[1])
            body_height = abs(ankle_y - nose[1])
            
            if body_height < 0.1:  # Altura muito pequena
                issues.append("Altura corporal muito pequena")
                return {'is_valid': False, 'issues': issues}
            
            # Verifica largura dos ombros
            left_shoulder = landmarks[self.landmark_indices['left_shoulder']]
            right_shoulder = landmarks[self.landmark_indices['right_shoulder']]
            shoulder_width = abs(right_shoulder[0] - left_shoulder[0])
            shoulder_ratio = shoulder_width / body_height
            
            min_ratio, max_ratio = self.body_proportions['shoulder_width_ratio']
            if not (min_ratio <= shoulder_ratio <= max_ratio):
                issues.append(f"Proporção de ombros anormal: {shoulder_ratio:.3f}")
            
            # Verifica comprimento do braço
            left_elbow = landmarks[self.landmark_indices['left_elbow']]
            left_wrist = landmarks[self.landmark_indices['left_wrist']]
            
            upper_arm_length = np.linalg.norm(left_shoulder[:2] - left_elbow[:2])
            forearm_length = np.linalg.norm(left_elbow[:2] - left_wrist[:2])
            
            upper_arm_ratio = upper_arm_length / body_height
            forearm_ratio = forearm_length / body_height
            
            if not (self.body_proportions['upper_arm_ratio'][0] <= upper_arm_ratio <= 
                   self.body_proportions['upper_arm_ratio'][1]):
                issues.append(f"Proporção do braço superior anormal: {upper_arm_ratio:.3f}")
            
            if not (self.body_proportions['forearm_ratio'][0] <= forearm_ratio <= 
                   self.body_proportions['forearm_ratio'][1]):
                issues.append(f"Proporção do antebraço anormal: {forearm_ratio:.3f}")
            
        except Exception as e:
            issues.append(f"Erro na validação de proporções: {str(e)}")
        
        return {'is_valid': len(issues) == 0, 'issues': issues}
    
    def _validate_body_symmetry(self, landmarks) -> Dict:
        """Valida simetria corporal básica."""
        issues = []
        
        try:
            # Pares simétricos para verificação
            symmetric_pairs = [
                ('left_shoulder', 'right_shoulder'),
                ('left_elbow', 'right_elbow'),
                ('left_wrist', 'right_wrist'),
                ('left_hip', 'right_hip'),
                ('left_knee', 'right_knee'),
                ('left_ankle', 'right_ankle')
            ]
            
            # Calcula linha central do corpo
            nose = landmarks[self.landmark_indices['nose']]
            left_hip = landmarks[self.landmark_indices['left_hip']]
            right_hip = landmarks[self.landmark_indices['right_hip']]
            center_x = (left_hip[0] + right_hip[0]) / 2
            
            for left_name, right_name in symmetric_pairs:
                left_point = landmarks[self.landmark_indices[left_name]]
                right_point = landmarks[self.landmark_indices[right_name]]
                
                # Verifica se os pontos estão em lados opostos da linha central
                left_distance = abs(left_point[0] - center_x)
                right_distance = abs(right_point[0] - center_x)
                
                # Tolerância para assimetria (30%)
                asymmetry_ratio = abs(left_distance - right_distance) / max(left_distance, right_distance, 0.01)
                
                if asymmetry_ratio > 0.5:  # Mais de 50% de assimetria
                    issues.append(f"Assimetria excessiva em {left_name}/{right_name}: {asymmetry_ratio:.3f}")
            
        except Exception as e:
            issues.append(f"Erro na validação de simetria: {str(e)}")
        
        return {'is_valid': len(issues) == 0, 'issues': issues}
    
    def _validate_joint_angles(self, landmarks) -> Dict:
        """Valida ângulos articulares dentro de limites fisiológicos."""
        issues = []
        
        try:
            # Verifica ângulo do cotovelo esquerdo
            shoulder = landmarks[self.landmark_indices['left_shoulder']]
            elbow = landmarks[self.landmark_indices['left_elbow']]
            wrist = landmarks[self.landmark_indices['left_wrist']]
            
            elbow_angle = self._calculate_angle(shoulder[:2], elbow[:2], wrist[:2])
            min_angle, max_angle = self.joint_angle_limits['elbow_flexion']
            
            if not (min_angle <= elbow_angle <= max_angle):
                issues.append(f"Ângulo do cotovelo fora dos limites: {elbow_angle:.1f}°")
            
            # Verifica ângulo do joelho esquerdo
            hip = landmarks[self.landmark_indices['left_hip']]
            knee = landmarks[self.landmark_indices['left_knee']]
            ankle = landmarks[self.landmark_indices['left_ankle']]
            
            knee_angle = self._calculate_angle(hip[:2], knee[:2], ankle[:2])
            min_angle, max_angle = self.joint_angle_limits['knee_flexion']
            
            if not (min_angle <= knee_angle <= max_angle):
                issues.append(f"Ângulo do joelho fora dos limites: {knee_angle:.1f}°")
            
        except Exception as e:
            issues.append(f"Erro na validação de ângulos: {str(e)}")
        
        return {'is_valid': len(issues) == 0, 'issues': issues}
    
    def _detect_impossible_poses(self, landmarks) -> Dict:
        """Detecta poses fisicamente impossíveis."""
        issues = []
        
        try:
            # Verifica se membros estão cruzando o corpo de forma impossível
            left_wrist = landmarks[self.landmark_indices['left_wrist']]
            right_wrist = landmarks[self.landmark_indices['right_wrist']]
            left_shoulder = landmarks[self.landmark_indices['left_shoulder']]
            right_shoulder = landmarks[self.landmark_indices['right_shoulder']]
            
            # Verifica se pulso esquerdo está muito à direita do ombro direito
            if left_wrist[0] > right_shoulder[0] + 0.1:  # Tolerância de 10%
                issues.append("Pulso esquerdo cruzando excessivamente para a direita")
            
            # Verifica se pulso direito está muito à esquerda do ombro esquerdo
            if right_wrist[0] < left_shoulder[0] - 0.1:  # Tolerância de 10%
                issues.append("Pulso direito cruzando excessivamente para a esquerda")
            
            # Verifica se pernas estão cruzadas de forma impossível
            left_ankle = landmarks[self.landmark_indices['left_ankle']]
            right_ankle = landmarks[self.landmark_indices['right_ankle']]
            left_hip = landmarks[self.landmark_indices['left_hip']]
            right_hip = landmarks[self.landmark_indices['right_hip']]
            
            # Calcula centro dos quadris
            hip_center_x = (left_hip[0] + right_hip[0]) / 2
            
            # Verifica cruzamento excessivo das pernas
            left_ankle_offset = left_ankle[0] - hip_center_x
            right_ankle_offset = right_ankle[0] - hip_center_x
            
            if left_ankle_offset > 0.15 and right_ankle_offset < -0.15:
                issues.append("Pernas cruzadas de forma impossível")
            
        except Exception as e:
            issues.append(f"Erro na detecção de poses impossíveis: {str(e)}")
        
        return {'is_valid': len(issues) == 0, 'issues': issues}
    
    def _calculate_angle(self, point1, point2, point3):
        """Calcula ângulo entre três pontos (point2 é o vértice)."""
        try:
            # Vetores
            v1 = np.array(point1) - np.array(point2)
            v2 = np.array(point3) - np.array(point2)
            
            # Produto escalar e magnitudes
            dot_product = np.dot(v1, v2)
            magnitude1 = np.linalg.norm(v1)
            magnitude2 = np.linalg.norm(v2)
            
            # Evita divisão por zero
            if magnitude1 == 0 or magnitude2 == 0:
                return 0
            
            # Calcula ângulo em radianos e converte para graus
            cos_angle = dot_product / (magnitude1 * magnitude2)
            cos_angle = np.clip(cos_angle, -1.0, 1.0)  # Garante que está no range válido
            angle_rad = np.arccos(cos_angle)
            angle_deg = np.degrees(angle_rad)
            
            return angle_deg
            
        except Exception:
            return 0
    
    def get_validation_summary(self, landmarks) -> str:
        """Retorna um resumo textual da validação."""
        result = self.validate_landmarks(landmarks)
        
        if result.is_valid:
            return f"✅ Pose válida (Confiança: {result.confidence_score:.2f})"
        else:
            issues_text = "; ".join(result.issues[:3])  # Primeiros 3 problemas
            return f"❌ Pose inválida (Confiança: {result.confidence_score:.2f}) - {issues_text}"


# === FUNÇÃO DE CONVENIÊNCIA ===
def create_anatomical_validator():
    """Cria uma instância do validador anatômico com configurações padrão."""
    return AnatomicalValidator()


# === EXEMPLO DE USO ===
if __name__ == "__main__":
    # Teste básico do validador
    validator = create_anatomical_validator()
    
    # Landmarks de exemplo (formato simplificado)
    test_landmarks = np.random.rand(33, 4)  # 33 landmarks com x, y, z, visibility
    
    result = validator.validate_landmarks(test_landmarks)
    print(f"Resultado: {result.is_valid}")
    print(f"Confiança: {result.confidence_score:.3f}")
    print(f"Problemas: {result.issues}")