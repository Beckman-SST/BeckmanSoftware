"""
Módulo de Interpolação Inteligente para Landmarks
Preenche landmarks ausentes ou inválidos usando múltiplas estratégias.
"""

import numpy as np
import math
from typing import List, Dict, Tuple, Optional, Any, Union
from dataclasses import dataclass
from collections import deque
from scipy import interpolate
import cv2


@dataclass
class InterpolationResult:
    """Resultado da interpolação de landmarks."""
    success: bool
    interpolated_landmarks: Optional[np.ndarray]
    method_used: str
    confidence: float
    notes: List[str]


class SmartInterpolator:
    """
    Interpolador inteligente para landmarks ausentes.
    Utiliza múltiplas estratégias: temporal, anatômica, simetria e cinemática.
    """
    
    def __init__(self, history_size=10):
        """
        Inicializa o interpolador.
        
        Args:
            history_size: Tamanho do histórico temporal para interpolação
        """
        self.history_size = history_size
        self.landmark_history = deque(maxlen=history_size)
        self.timestamp_history = deque(maxlen=history_size)
        
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
        
        # === PARES SIMÉTRICOS PARA INTERPOLAÇÃO ===
        self.symmetric_pairs = {
            'left_shoulder': 'right_shoulder',
            'right_shoulder': 'left_shoulder',
            'left_elbow': 'right_elbow',
            'right_elbow': 'left_elbow',
            'left_wrist': 'right_wrist',
            'right_wrist': 'left_wrist',
            'left_hip': 'right_hip',
            'right_hip': 'left_hip',
            'left_knee': 'right_knee',
            'right_knee': 'left_knee',
            'left_ankle': 'right_ankle',
            'right_ankle': 'left_ankle',
            'left_eye': 'right_eye',
            'right_eye': 'left_eye',
            'left_ear': 'right_ear',
            'right_ear': 'left_ear'
        }
        
        # === RELAÇÕES ANATÔMICAS PARA INTERPOLAÇÃO ===
        self.anatomical_chains = {
            # Braço esquerdo
            'left_elbow': ['left_shoulder', 'left_wrist'],
            'left_wrist': ['left_elbow', 'left_shoulder'],
            
            # Braço direito
            'right_elbow': ['right_shoulder', 'right_wrist'],
            'right_wrist': ['right_elbow', 'right_shoulder'],
            
            # Perna esquerda
            'left_knee': ['left_hip', 'left_ankle'],
            'left_ankle': ['left_knee', 'left_hip'],
            
            # Perna direita
            'right_knee': ['right_hip', 'right_ankle'],
            'right_ankle': ['right_knee', 'right_hip'],
        }
        
        # === PROPORÇÕES ANATÔMICAS MÉDIAS ===
        self.anatomical_ratios = {
            'upper_arm_ratio': 0.215,      # Ombro-cotovelo / altura
            'forearm_ratio': 0.185,        # Cotovelo-pulso / altura
            'thigh_ratio': 0.25,           # Quadril-joelho / altura
            'shin_ratio': 0.23,            # Joelho-tornozelo / altura
        }
    
    def interpolate_missing_landmarks(self, landmarks, missing_indices, timestamp=None) -> InterpolationResult:
        """
        Interpola landmarks ausentes usando a melhor estratégia disponível.
        
        Args:
            landmarks: Array de landmarks atual (pode ter valores None/NaN para ausentes)
            missing_indices: Lista de índices dos landmarks ausentes
            timestamp: Timestamp atual (opcional)
            
        Returns:
            InterpolationResult: Resultado da interpolação
        """
        if not missing_indices:
            return InterpolationResult(
                success=True,
                interpolated_landmarks=landmarks,
                method_used="none_needed",
                confidence=1.0,
                notes=["Nenhum landmark ausente"]
            )
        
        # Copia landmarks para modificação
        result_landmarks = landmarks.copy() if landmarks is not None else np.zeros((33, 4))
        interpolated_count = 0
        methods_used = []
        total_confidence = 0.0
        notes = []
        
        for landmark_idx in missing_indices:
            # Tenta diferentes estratégias em ordem de preferência
            interpolation_success = False
            
            # === ESTRATÉGIA 1: INTERPOLAÇÃO TEMPORAL ===
            if len(self.landmark_history) >= 3:
                temporal_result = self._temporal_interpolation(landmark_idx, timestamp)
                if temporal_result.success:
                    result_landmarks[landmark_idx] = temporal_result.interpolated_landmarks
                    interpolated_count += 1
                    total_confidence += temporal_result.confidence
                    methods_used.append("temporal")
                    notes.extend(temporal_result.notes)
                    interpolation_success = True
            
            # === ESTRATÉGIA 2: INTERPOLAÇÃO POR SIMETRIA ===
            if not interpolation_success:
                symmetry_result = self._symmetry_interpolation(landmark_idx, result_landmarks)
                if symmetry_result.success:
                    result_landmarks[landmark_idx] = symmetry_result.interpolated_landmarks
                    interpolated_count += 1
                    total_confidence += symmetry_result.confidence
                    methods_used.append("symmetry")
                    notes.extend(symmetry_result.notes)
                    interpolation_success = True
            
            # === ESTRATÉGIA 3: INTERPOLAÇÃO ANATÔMICA ===
            if not interpolation_success:
                anatomical_result = self._anatomical_interpolation(landmark_idx, result_landmarks)
                if anatomical_result.success:
                    result_landmarks[landmark_idx] = anatomical_result.interpolated_landmarks
                    interpolated_count += 1
                    total_confidence += anatomical_result.confidence
                    methods_used.append("anatomical")
                    notes.extend(anatomical_result.notes)
                    interpolation_success = True
            
            # === ESTRATÉGIA 4: INTERPOLAÇÃO CINEMÁTICA (FALLBACK) ===
            if not interpolation_success:
                kinematic_result = self._kinematic_interpolation(landmark_idx, result_landmarks)
                if kinematic_result.success:
                    result_landmarks[landmark_idx] = kinematic_result.interpolated_landmarks
                    interpolated_count += 1
                    total_confidence += kinematic_result.confidence
                    methods_used.append("kinematic")
                    notes.extend(kinematic_result.notes)
                    interpolation_success = True
            
            if not interpolation_success:
                notes.append(f"Falha ao interpolar landmark {landmark_idx}")
        
        # Atualiza histórico
        self._update_history(result_landmarks, timestamp)
        
        # Calcula confiança média
        avg_confidence = total_confidence / max(interpolated_count, 1)
        success = interpolated_count > 0
        
        return InterpolationResult(
            success=success,
            interpolated_landmarks=result_landmarks,
            method_used="+".join(set(methods_used)) if methods_used else "failed",
            confidence=avg_confidence,
            notes=notes
        )
    
    def _temporal_interpolation(self, landmark_idx, timestamp=None) -> InterpolationResult:
        """Interpola usando histórico temporal com spline cúbica."""
        try:
            if len(self.landmark_history) < 3:
                return InterpolationResult(False, None, "temporal", 0.0, 
                                         ["Histórico insuficiente para interpolação temporal"])
            
            # Extrai dados históricos do landmark específico
            historical_data = []
            timestamps = []
            
            for i, (landmarks, ts) in enumerate(zip(self.landmark_history, self.timestamp_history)):
                if landmarks is not None and landmark_idx < len(landmarks):
                    landmark_data = landmarks[landmark_idx]
                    # Verifica se o landmark é válido (não NaN/None)
                    if not np.isnan(landmark_data).any():
                        historical_data.append(landmark_data[:3])  # x, y, z
                        timestamps.append(ts if ts is not None else i)
            
            if len(historical_data) < 3:
                return InterpolationResult(False, None, "temporal", 0.0,
                                         ["Dados históricos insuficientes"])
            
            # Converte para arrays numpy
            historical_data = np.array(historical_data)
            timestamps = np.array(timestamps)
            
            # Interpola cada coordenada (x, y, z) separadamente
            current_time = timestamp if timestamp is not None else timestamps[-1] + 1
            interpolated_coords = []
            
            for coord_idx in range(3):  # x, y, z
                coord_values = historical_data[:, coord_idx]
                
                # Usa interpolação linear se poucos pontos, spline se mais pontos
                if len(coord_values) <= 3:
                    interp_func = interpolate.interp1d(timestamps, coord_values, 
                                                     kind='linear', fill_value='extrapolate')
                else:
                    interp_func = interpolate.interp1d(timestamps, coord_values, 
                                                     kind='cubic', fill_value='extrapolate')
                
                interpolated_value = float(interp_func(current_time))
                interpolated_coords.append(interpolated_value)
            
            # Estima visibilidade baseada na tendência histórica
            visibility_history = historical_data[:, -1] if historical_data.shape[1] > 3 else [0.8] * len(historical_data)
            avg_visibility = np.mean(visibility_history) * 0.8  # Reduz confiança por ser interpolado
            
            interpolated_landmark = np.array([
                interpolated_coords[0],  # x
                interpolated_coords[1],  # y
                interpolated_coords[2],  # z
                avg_visibility            # visibility
            ])
            
            confidence = min(0.9, avg_visibility + 0.1)  # Confiança baseada na visibilidade
            
            return InterpolationResult(
                success=True,
                interpolated_landmarks=interpolated_landmark,
                method_used="temporal",
                confidence=confidence,
                notes=[f"Interpolação temporal usando {len(historical_data)} pontos históricos"]
            )
            
        except Exception as e:
            return InterpolationResult(False, None, "temporal", 0.0,
                                     [f"Erro na interpolação temporal: {str(e)}"])
    
    def _symmetry_interpolation(self, landmark_idx, landmarks) -> InterpolationResult:
        """Interpola usando simetria corporal (espelhamento)."""
        try:
            # Encontra o nome do landmark
            landmark_name = None
            for name, idx in self.landmark_indices.items():
                if idx == landmark_idx:
                    landmark_name = name
                    break
            
            if landmark_name is None or landmark_name not in self.symmetric_pairs:
                return InterpolationResult(False, None, "symmetry", 0.0,
                                         ["Landmark não tem par simétrico"])
            
            # Encontra o landmark simétrico
            symmetric_name = self.symmetric_pairs[landmark_name]
            symmetric_idx = self.landmark_indices[symmetric_name]
            
            if symmetric_idx >= len(landmarks) or np.isnan(landmarks[symmetric_idx]).any():
                return InterpolationResult(False, None, "symmetry", 0.0,
                                         ["Landmark simétrico não disponível"])
            
            symmetric_landmark = landmarks[symmetric_idx]
            
            # Calcula linha central do corpo
            try:
                left_hip = landmarks[self.landmark_indices['left_hip']]
                right_hip = landmarks[self.landmark_indices['right_hip']]
                center_x = (left_hip[0] + right_hip[0]) / 2
            except:
                # Fallback: usa centro da imagem
                center_x = 0.5
            
            # Espelha o landmark simétrico
            mirrored_x = 2 * center_x - symmetric_landmark[0]
            interpolated_landmark = np.array([
                mirrored_x,
                symmetric_landmark[1],  # y permanece igual
                symmetric_landmark[2],  # z permanece igual
                symmetric_landmark[3] * 0.7  # reduz visibilidade por ser espelhado
            ])
            
            confidence = symmetric_landmark[3] * 0.7  # Confiança baseada no landmark original
            
            return InterpolationResult(
                success=True,
                interpolated_landmarks=interpolated_landmark,
                method_used="symmetry",
                confidence=confidence,
                notes=[f"Espelhamento de {symmetric_name}"]
            )
            
        except Exception as e:
            return InterpolationResult(False, None, "symmetry", 0.0,
                                     [f"Erro na interpolação por simetria: {str(e)}"])
    
    def _anatomical_interpolation(self, landmark_idx, landmarks) -> InterpolationResult:
        """Interpola usando relações anatômicas (proporções corporais)."""
        try:
            # Encontra o nome do landmark
            landmark_name = None
            for name, idx in self.landmark_indices.items():
                if idx == landmark_idx:
                    landmark_name = name
                    break
            
            if landmark_name is None or landmark_name not in self.anatomical_chains:
                return InterpolationResult(False, None, "anatomical", 0.0,
                                         ["Landmark não tem relações anatômicas definidas"])
            
            # Obtém landmarks relacionados
            related_names = self.anatomical_chains[landmark_name]
            related_landmarks = []
            
            for related_name in related_names:
                related_idx = self.landmark_indices[related_name]
                if related_idx < len(landmarks) and not np.isnan(landmarks[related_idx]).any():
                    related_landmarks.append((related_name, landmarks[related_idx]))
            
            if len(related_landmarks) < 2:
                return InterpolationResult(False, None, "anatomical", 0.0,
                                         ["Landmarks relacionados insuficientes"])
            
            # Interpola usando proporções anatômicas
            if 'elbow' in landmark_name:
                # Interpola cotovelo usando ombro e pulso
                shoulder_name = landmark_name.replace('elbow', 'shoulder')
                wrist_name = landmark_name.replace('elbow', 'wrist')
                
                shoulder_idx = self.landmark_indices[shoulder_name]
                wrist_idx = self.landmark_indices[wrist_name]
                
                if (shoulder_idx < len(landmarks) and wrist_idx < len(landmarks) and
                    not np.isnan(landmarks[shoulder_idx]).any() and 
                    not np.isnan(landmarks[wrist_idx]).any()):
                    
                    shoulder_point = landmarks[shoulder_idx]
                    wrist_point = landmarks[wrist_idx]
                    
                    # Cotovelo fica aproximadamente no meio, mas mais próximo do ombro
                    elbow_ratio = 0.6  # 60% do caminho do ombro para o pulso
                    interpolated_landmark = shoulder_point + elbow_ratio * (wrist_point - shoulder_point)
                    interpolated_landmark[3] = min(shoulder_point[3], wrist_point[3]) * 0.8
                    
                    confidence = min(shoulder_point[3], wrist_point[3]) * 0.8
                    
                    return InterpolationResult(
                        success=True,
                        interpolated_landmarks=interpolated_landmark,
                        method_used="anatomical",
                        confidence=confidence,
                        notes=[f"Interpolação anatômica de {landmark_name} usando {shoulder_name} e {wrist_name}"]
                    )
            
            elif 'knee' in landmark_name:
                # Interpola joelho usando quadril e tornozelo
                hip_name = landmark_name.replace('knee', 'hip')
                ankle_name = landmark_name.replace('knee', 'ankle')
                
                hip_idx = self.landmark_indices[hip_name]
                ankle_idx = self.landmark_indices[ankle_name]
                
                if (hip_idx < len(landmarks) and ankle_idx < len(landmarks) and
                    not np.isnan(landmarks[hip_idx]).any() and 
                    not np.isnan(landmarks[ankle_idx]).any()):
                    
                    hip_point = landmarks[hip_idx]
                    ankle_point = landmarks[ankle_idx]
                    
                    # Joelho fica aproximadamente no meio
                    knee_ratio = 0.55  # 55% do caminho do quadril para o tornozelo
                    interpolated_landmark = hip_point + knee_ratio * (ankle_point - hip_point)
                    interpolated_landmark[3] = min(hip_point[3], ankle_point[3]) * 0.8
                    
                    confidence = min(hip_point[3], ankle_point[3]) * 0.8
                    
                    return InterpolationResult(
                        success=True,
                        interpolated_landmarks=interpolated_landmark,
                        method_used="anatomical",
                        confidence=confidence,
                        notes=[f"Interpolação anatômica de {landmark_name} usando {hip_name} e {ankle_name}"]
                    )
            
            return InterpolationResult(False, None, "anatomical", 0.0,
                                     ["Não foi possível aplicar interpolação anatômica"])
            
        except Exception as e:
            return InterpolationResult(False, None, "anatomical", 0.0,
                                     [f"Erro na interpolação anatômica: {str(e)}"])
    
    def _kinematic_interpolation(self, landmark_idx, landmarks) -> InterpolationResult:
        """Interpolação cinemática básica (fallback usando média de landmarks próximos)."""
        try:
            # Lista de landmarks próximos para cada landmark (baseado na anatomia)
            nearby_landmarks = {
                # Braços
                13: [11, 15],  # left_elbow: left_shoulder, left_wrist
                14: [12, 16],  # right_elbow: right_shoulder, right_wrist
                15: [13, 11],  # left_wrist: left_elbow, left_shoulder
                16: [14, 12],  # right_wrist: right_elbow, right_shoulder
                
                # Pernas
                25: [23, 27],  # left_knee: left_hip, left_ankle
                26: [24, 28],  # right_knee: right_hip, right_ankle
                27: [25, 23],  # left_ankle: left_knee, left_hip
                28: [26, 24],  # right_ankle: right_knee, right_hip
                
                # Torso
                11: [12, 23],  # left_shoulder: right_shoulder, left_hip
                12: [11, 24],  # right_shoulder: left_shoulder, right_hip
                23: [24, 11],  # left_hip: right_hip, left_shoulder
                24: [23, 12],  # right_hip: left_hip, right_shoulder
            }
            
            if landmark_idx not in nearby_landmarks:
                return InterpolationResult(False, None, "kinematic", 0.0,
                                         ["Landmark não tem vizinhos definidos"])
            
            nearby_indices = nearby_landmarks[landmark_idx]
            valid_neighbors = []
            
            for neighbor_idx in nearby_indices:
                if (neighbor_idx < len(landmarks) and 
                    not np.isnan(landmarks[neighbor_idx]).any()):
                    valid_neighbors.append(landmarks[neighbor_idx])
            
            if len(valid_neighbors) == 0:
                return InterpolationResult(False, None, "kinematic", 0.0,
                                         ["Nenhum vizinho válido encontrado"])
            
            # Calcula média ponderada dos vizinhos
            weights = [1.0 / (i + 1) for i in range(len(valid_neighbors))]  # Peso decrescente
            total_weight = sum(weights)
            
            interpolated_landmark = np.zeros(4)
            for i, neighbor in enumerate(valid_neighbors):
                interpolated_landmark += neighbor * (weights[i] / total_weight)
            
            # Reduz visibilidade por ser interpolação de fallback
            interpolated_landmark[3] *= 0.5
            
            confidence = interpolated_landmark[3]
            
            return InterpolationResult(
                success=True,
                interpolated_landmarks=interpolated_landmark,
                method_used="kinematic",
                confidence=confidence,
                notes=[f"Interpolação cinemática usando {len(valid_neighbors)} vizinhos"]
            )
            
        except Exception as e:
            return InterpolationResult(False, None, "kinematic", 0.0,
                                     [f"Erro na interpolação cinemática: {str(e)}"])
    
    def _update_history(self, landmarks, timestamp):
        """Atualiza o histórico de landmarks."""
        self.landmark_history.append(landmarks.copy() if landmarks is not None else None)
        self.timestamp_history.append(timestamp)
    
    def reset_history(self):
        """Reseta o histórico de landmarks."""
        self.landmark_history.clear()
        self.timestamp_history.clear()
    
    def get_interpolation_stats(self) -> Dict:
        """Retorna estatísticas do interpolador."""
        return {
            'history_size': len(self.landmark_history),
            'max_history': self.history_size,
            'has_sufficient_history': len(self.landmark_history) >= 3
        }


# === FUNÇÃO DE CONVENIÊNCIA ===
def create_smart_interpolator(history_size=10):
    """Cria uma instância do interpolador inteligente."""
    return SmartInterpolator(history_size=history_size)


# === EXEMPLO DE USO ===
if __name__ == "__main__":
    # Teste básico do interpolador
    interpolator = create_smart_interpolator()
    
    # Landmarks de exemplo com alguns ausentes
    test_landmarks = np.random.rand(33, 4)
    test_landmarks[13] = np.nan  # Remove cotovelo esquerdo
    test_landmarks[25] = np.nan  # Remove joelho esquerdo
    
    missing_indices = [13, 25]
    
    result = interpolator.interpolate_missing_landmarks(test_landmarks, missing_indices)
    print(f"Sucesso: {result.success}")
    print(f"Método: {result.method_used}")
    print(f"Confiança: {result.confidence:.3f}")
    print(f"Notas: {result.notes}")