"""
Módulo de Suavização Temporal Avançada para Landmarks
Implementa filtro de Kalman, média móvel ponderada e detecção de outliers.
"""

import numpy as np
import cv2
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from collections import deque
import math


@dataclass
class LandmarkPoint:
    """Representa um ponto de landmark com coordenadas e metadados."""
    x: float
    y: float
    z: float = 0.0
    visibility: float = 1.0
    timestamp: float = 0.0
    confidence: float = 1.0


class KalmanLandmarkFilter:
    """
    Filtro de Kalman para suavização de landmarks individuais.
    Prediz e corrige a posição de landmarks considerando velocidade e aceleração.
    """
    
    def __init__(self, process_noise=0.01, measurement_noise=0.1):
        """
        Inicializa o filtro de Kalman para um landmark.
        
        Args:
            process_noise (float): Ruído do processo (incerteza do modelo)
            measurement_noise (float): Ruído da medição (incerteza dos sensores)
        """
        self.process_noise = process_noise
        self.measurement_noise = measurement_noise
        self.initialized = False
        
        # Estado: [x, y, vx, vy] (posição e velocidade)
        self.state = np.zeros(4)
        
        # Matriz de covariância do estado
        self.P = np.eye(4) * 1000  # Alta incerteza inicial
        
        # Matriz de transição de estado (modelo de movimento constante)
        self.F = np.array([
            [1, 0, 1, 0],  # x = x + vx*dt
            [0, 1, 0, 1],  # y = y + vy*dt
            [0, 0, 1, 0],  # vx = vx
            [0, 0, 0, 1]   # vy = vy
        ])
        
        # Matriz de observação (observamos apenas posição)
        self.H = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0]
        ])
        
        # Matriz de ruído do processo
        self.Q = np.array([
            [0.25, 0, 0.5, 0],
            [0, 0.25, 0, 0.5],
            [0.5, 0, 1, 0],
            [0, 0.5, 0, 1]
        ]) * self.process_noise
        
        # Matriz de ruído da medição
        self.R = np.eye(2) * self.measurement_noise
    
    def predict(self, dt=1.0):
        """
        Etapa de predição do filtro de Kalman.
        
        Args:
            dt (float): Intervalo de tempo desde a última atualização
        """
        if not self.initialized:
            return
        
        # Atualiza a matriz de transição com dt
        self.F[0, 2] = dt
        self.F[1, 3] = dt
        
        # Predição do estado
        self.state = self.F @ self.state
        
        # Predição da covariância
        self.P = self.F @ self.P @ self.F.T + self.Q
    
    def update(self, measurement: Tuple[float, float], confidence: float = 1.0):
        """
        Etapa de atualização do filtro de Kalman.
        
        Args:
            measurement (tuple): Medição (x, y)
            confidence (float): Confiança na medição (0-1)
        """
        z = np.array(measurement)
        
        if not self.initialized:
            # Inicialização com a primeira medição
            self.state[0] = z[0]
            self.state[1] = z[1]
            self.state[2] = 0  # velocidade inicial zero
            self.state[3] = 0
            self.initialized = True
            return self.state[:2]
        
        # Ajusta o ruído da medição baseado na confiança
        R_adjusted = self.R / max(confidence, 0.1)
        
        # Inovação (diferença entre medição e predição)
        y = z - self.H @ self.state
        
        # Covariância da inovação
        S = self.H @ self.P @ self.H.T + R_adjusted
        
        # Ganho de Kalman
        K = self.P @ self.H.T @ np.linalg.inv(S)
        
        # Atualização do estado
        self.state = self.state + K @ y
        
        # Atualização da covariância
        I = np.eye(4)
        self.P = (I - K @ self.H) @ self.P
        
        return self.state[:2]
    
    def get_position(self) -> Tuple[float, float]:
        """Retorna a posição atual estimada."""
        return (self.state[0], self.state[1])
    
    def get_velocity(self) -> Tuple[float, float]:
        """Retorna a velocidade atual estimada."""
        return (self.state[2], self.state[3])
    
    def reset(self):
        """Reseta o filtro."""
        self.initialized = False
        self.state = np.zeros(4)
        self.P = np.eye(4) * 1000


class OutlierDetector:
    """
    Detector de outliers para landmarks usando múltiplos critérios.
    """
    
    def __init__(self, history_size=10, velocity_threshold=50.0, acceleration_threshold=100.0):
        """
        Inicializa o detector de outliers.
        
        Args:
            history_size (int): Tamanho do histórico para análise
            velocity_threshold (float): Threshold de velocidade para detectar outliers
            acceleration_threshold (float): Threshold de aceleração para detectar outliers
        """
        self.history_size = history_size
        self.velocity_threshold = velocity_threshold
        self.acceleration_threshold = acceleration_threshold
        self.position_history = deque(maxlen=history_size)
        self.velocity_history = deque(maxlen=history_size-1)
    
    def is_outlier(self, point, previous_point=None) -> bool:
        """
        Determina se um ponto é um outlier.
        
        Args:
            point: Ponto atual (pode ser tupla (x, y) ou LandmarkPoint)
            previous_point: Ponto anterior (opcional)
            
        Returns:
            bool: True se o ponto é um outlier
        """
        # Converte tupla para objeto LandmarkPoint se necessário
        if isinstance(point, tuple):
            point = LandmarkPoint(point[0], point[1], 0.0, 1.0, 1.0)
        
        if previous_point and isinstance(previous_point, tuple):
            previous_point = LandmarkPoint(previous_point[0], previous_point[1], 0.0, 1.0, 1.0)
        
        # Critério 1: Baixa visibilidade
        if hasattr(point, 'visibility') and point.visibility < 0.3:
            return True
        
        # Critério 2: Baixa confiança
        if hasattr(point, 'confidence') and point.confidence < 0.5:
            return True
        
        # Se não há histórico suficiente, aceita o ponto
        if len(self.position_history) < 2:
            self.position_history.append((point.x, point.y))
            return False
        
        # Critério 3: Velocidade excessiva
        if previous_point:
            velocity = math.sqrt(
                (point.x - previous_point.x)**2 + 
                (point.y - previous_point.y)**2
            )
            
            if velocity > self.velocity_threshold:
                return True
            
            self.velocity_history.append(velocity)
        
        # Critério 4: Aceleração excessiva
        if len(self.velocity_history) >= 2:
            current_velocity = self.velocity_history[-1]
            previous_velocity = self.velocity_history[-2]
            acceleration = abs(current_velocity - previous_velocity)
            
            if acceleration > self.acceleration_threshold:
                return True
        
        # Critério 5: Distância estatística (Z-score)
        if len(self.position_history) >= 5:
            positions = np.array(self.position_history)
            mean_pos = np.mean(positions, axis=0)
            std_pos = np.std(positions, axis=0)
            
            # Evita divisão por zero
            std_pos = np.maximum(std_pos, 1.0)
            
            z_score = np.abs((np.array([point.x, point.y]) - mean_pos) / std_pos)
            
            # Se qualquer coordenada tem Z-score > 3, é outlier
            if np.any(z_score > 3.0):
                return True
        
        # Atualiza histórico
        self.position_history.append((point.x, point.y))
        
        return False
    
    def reset(self):
        """Reseta o detector."""
        self.position_history.clear()
        self.velocity_history.clear()


class WeightedMovingAverage:
    """
    Média móvel ponderada melhorada com pesos adaptativos.
    """
    
    def __init__(self, window_size=5, decay_factor=0.8):
        """
        Inicializa a média móvel ponderada.
        
        Args:
            window_size (int): Tamanho da janela
            decay_factor (float): Fator de decaimento para pesos (0-1)
        """
        self.window_size = window_size
        self.decay_factor = decay_factor
        self.history = deque(maxlen=window_size)
        self.weights = self._calculate_weights()
    
    def _calculate_weights(self) -> np.ndarray:
        """Calcula os pesos para a média móvel."""
        weights = np.array([self.decay_factor ** i for i in range(self.window_size)])
        weights = weights[::-1]  # Inverte para dar mais peso aos recentes
        return weights / np.sum(weights)  # Normaliza
    
    def update(self, point):
        """
        Método simples para atualizar com tupla (x, y).
        
        Args:
            point: Tupla (x, y) ou LandmarkPoint
            
        Returns:
            tuple: Posição suavizada (x, y)
        """
        # Converte tupla para LandmarkPoint se necessário
        if isinstance(point, tuple):
            landmark_point = LandmarkPoint(point[0], point[1], 0.0, 1.0, 1.0)
        else:
            landmark_point = point
        
        smoothed_point = self.add_point(landmark_point)
        return (smoothed_point.x, smoothed_point.y)
    
    def add_point(self, point: LandmarkPoint) -> LandmarkPoint:
        """
        Adiciona um ponto e retorna a média ponderada.
        
        Args:
            point (LandmarkPoint): Ponto a ser adicionado
            
        Returns:
            LandmarkPoint: Ponto suavizado
        """
        self.history.append(point)
        
        if len(self.history) < 2:
            return point
        
        # Calcula pesos baseados no número de pontos disponíveis
        n_points = len(self.history)
        current_weights = self.weights[-n_points:]
        current_weights = current_weights / np.sum(current_weights)
        
        # Calcula média ponderada
        weighted_x = sum(w * p.x for w, p in zip(current_weights, self.history))
        weighted_y = sum(w * p.y for w, p in zip(current_weights, self.history))
        weighted_z = sum(w * p.z for w, p in zip(current_weights, self.history))
        weighted_visibility = sum(w * p.visibility for w, p in zip(current_weights, self.history))
        weighted_confidence = sum(w * p.confidence for w, p in zip(current_weights, self.history))
        
        return LandmarkPoint(
            x=weighted_x,
            y=weighted_y,
            z=weighted_z,
            visibility=weighted_visibility,
            confidence=weighted_confidence,
            timestamp=point.timestamp
        )
    
    def reset(self):
        """Reseta a média móvel."""
        self.history.clear()


class AdvancedTemporalSmoother:
    """
    Sistema avançado de suavização temporal que combina filtro de Kalman,
    média móvel ponderada e detecção de outliers.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Inicializa o suavizador temporal avançado.
        
        Args:
            config (dict): Configurações do suavizador
        """
        self.config = config or {}
        
        # Configurações padrão
        self.kalman_enabled = self.config.get('enable_kalman_filter', True)
        self.outlier_detection_enabled = self.config.get('enable_outlier_detection', True)
        self.weighted_average_enabled = self.config.get('enable_weighted_average', True)
        
        # Parâmetros do filtro de Kalman
        self.kalman_process_noise = self.config.get('kalman_process_noise', 0.01)
        self.kalman_measurement_noise = self.config.get('kalman_measurement_noise', 0.1)
        
        # Parâmetros da detecção de outliers
        self.outlier_velocity_threshold = self.config.get('outlier_velocity_threshold', 50.0)
        self.outlier_acceleration_threshold = self.config.get('outlier_acceleration_threshold', 100.0)
        
        # Parâmetros da média móvel ponderada
        self.weighted_window_size = self.config.get('weighted_window_size', 5)
        self.weighted_decay_factor = self.config.get('weighted_decay_factor', 0.8)
        
        # Filtros por landmark
        self.kalman_filters: Dict[int, KalmanLandmarkFilter] = {}
        self.outlier_detectors: Dict[int, OutlierDetector] = {}
        self.weighted_averages: Dict[int, WeightedMovingAverage] = {}
        
        # Histórico de landmarks
        self.previous_landmarks: Dict[int, LandmarkPoint] = {}
        
        # Estatísticas
        self.stats = {
            'total_frames': 0,
            'outliers_detected': 0,
            'kalman_corrections': 0,
            'smoothing_applied': 0
        }
    
    def smooth_landmarks(self, landmarks_data):
        """
        Método principal para suavizar landmarks do MediaPipe.
        
        Args:
            landmarks_data: Dados dos landmarks do MediaPipe
            
        Returns:
            landmarks_data: Landmarks suavizados no formato MediaPipe
        """
        if not landmarks_data or not landmarks_data.landmark:
            return landmarks_data
        
        # Processa landmarks (assume imagem 640x480 como padrão)
        smoothed_landmarks = self.process_landmarks(landmarks_data, 640, 480)
        
        # Atualiza os landmarks originais com os valores suavizados
        for i, landmark in enumerate(landmarks_data.landmark):
            if i in smoothed_landmarks:
                smoothed_point = smoothed_landmarks[i]
                landmark.x = smoothed_point.x / 640  # Normaliza de volta
                landmark.y = smoothed_point.y / 480  # Normaliza de volta
                landmark.z = smoothed_point.z
                landmark.visibility = smoothed_point.visibility
        
        return landmarks_data
    
    def process_landmarks(self, landmarks_data, image_width: int, image_height: int) -> Dict[int, LandmarkPoint]:
        """
        Processa landmarks aplicando suavização temporal avançada.
        
        Args:
            landmarks_data: Dados dos landmarks do MediaPipe
            image_width (int): Largura da imagem
            image_height (int): Altura da imagem
            
        Returns:
            dict: Landmarks suavizados
        """
        if not landmarks_data or not landmarks_data.landmark:
            return {}
        
        self.stats['total_frames'] += 1
        current_landmarks = {}
        smoothed_landmarks = {}
        
        # Converte landmarks do MediaPipe para LandmarkPoint
        for i, landmark in enumerate(landmarks_data.landmark):
            point = LandmarkPoint(
                x=landmark.x * image_width,
                y=landmark.y * image_height,
                z=landmark.z,
                visibility=landmark.visibility,
                confidence=landmark.visibility,  # Usa visibility como proxy para confidence
                timestamp=self.stats['total_frames']
            )
            current_landmarks[i] = point
        
        # Processa cada landmark
        for landmark_id, point in current_landmarks.items():
            smoothed_point = self._process_single_landmark(landmark_id, point)
            smoothed_landmarks[landmark_id] = smoothed_point
        
        # Atualiza histórico
        self.previous_landmarks = current_landmarks.copy()
        
        return smoothed_landmarks
    
    def _process_single_landmark(self, landmark_id: int, point: LandmarkPoint) -> LandmarkPoint:
        """
        Processa um único landmark aplicando todas as técnicas de suavização.
        
        Args:
            landmark_id (int): ID do landmark
            point (LandmarkPoint): Ponto atual
            
        Returns:
            LandmarkPoint: Ponto suavizado
        """
        # Inicializa filtros se necessário
        if landmark_id not in self.kalman_filters:
            self.kalman_filters[landmark_id] = KalmanLandmarkFilter(
                self.kalman_process_noise, 
                self.kalman_measurement_noise
            )
            self.outlier_detectors[landmark_id] = OutlierDetector(
                velocity_threshold=self.outlier_velocity_threshold,
                acceleration_threshold=self.outlier_acceleration_threshold
            )
            self.weighted_averages[landmark_id] = WeightedMovingAverage(
                self.weighted_window_size,
                self.weighted_decay_factor
            )
        
        processed_point = point
        
        # 1. Detecção de outliers
        if self.outlier_detection_enabled:
            previous_point = self.previous_landmarks.get(landmark_id)
            is_outlier = self.outlier_detectors[landmark_id].is_outlier(point, previous_point)
            
            if is_outlier:
                self.stats['outliers_detected'] += 1
                
                # Se é outlier, usa predição do Kalman ou ponto anterior
                if self.kalman_enabled and self.kalman_filters[landmark_id].initialized:
                    self.kalman_filters[landmark_id].predict()
                    predicted_pos = self.kalman_filters[landmark_id].get_position()
                    processed_point = LandmarkPoint(
                        x=predicted_pos[0],
                        y=predicted_pos[1],
                        z=point.z,
                        visibility=max(point.visibility * 0.5, 0.3),  # Reduz confiança
                        confidence=max(point.confidence * 0.5, 0.3),
                        timestamp=point.timestamp
                    )
                elif previous_point:
                    # Usa ponto anterior se disponível
                    processed_point = previous_point
                
                # Não atualiza filtros com outliers
                return processed_point
        
        # 2. Filtro de Kalman
        if self.kalman_enabled:
            kalman_filter = self.kalman_filters[landmark_id]
            kalman_filter.predict()
            kalman_pos = kalman_filter.update((point.x, point.y), point.confidence)
            
            processed_point = LandmarkPoint(
                x=kalman_pos[0],
                y=kalman_pos[1],
                z=point.z,
                visibility=point.visibility,
                confidence=point.confidence,
                timestamp=point.timestamp
            )
            self.stats['kalman_corrections'] += 1
        
        # 3. Média móvel ponderada
        if self.weighted_average_enabled:
            processed_point = self.weighted_averages[landmark_id].add_point(processed_point)
            self.stats['smoothing_applied'] += 1
        
        return processed_point
    
    def reset(self):
        """Reseta todos os filtros e históricos."""
        for kalman_filter in self.kalman_filters.values():
            kalman_filter.reset()
        
        for outlier_detector in self.outlier_detectors.values():
            outlier_detector.reset()
        
        for weighted_average in self.weighted_averages.values():
            weighted_average.reset()
        
        self.previous_landmarks.clear()
        
        # Reseta estatísticas
        self.stats = {
            'total_frames': 0,
            'outliers_detected': 0,
            'kalman_corrections': 0,
            'smoothing_applied': 0
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do processamento."""
        total_frames = max(self.stats['total_frames'], 1)
        return {
            'total_frames': self.stats['total_frames'],
            'outliers_detected': self.stats['outliers_detected'],
            'outlier_rate': self.stats['outliers_detected'] / total_frames,
            'kalman_corrections': self.stats['kalman_corrections'],
            'smoothing_applied': self.stats['smoothing_applied'],
            'active_landmarks': len(self.kalman_filters)
        }
    
    def update_config(self, new_config: Dict[str, Any]):
        """Atualiza configurações do suavizador."""
        self.config.update(new_config)
        
        # Atualiza flags
        self.kalman_enabled = self.config.get('enable_kalman_filter', True)
        self.outlier_detection_enabled = self.config.get('enable_outlier_detection', True)
        self.weighted_average_enabled = self.config.get('enable_weighted_average', True)
        
        # Se mudou configurações críticas, reseta filtros
        if ('kalman_process_noise' in new_config or 
            'kalman_measurement_noise' in new_config or
            'outlier_velocity_threshold' in new_config or
            'outlier_acceleration_threshold' in new_config):
            self.reset()


def create_advanced_temporal_smoother(config: Dict[str, Any] = None) -> AdvancedTemporalSmoother:
    """
    Factory function para criar um suavizador temporal avançado.
    
    Args:
        config (dict): Configurações do suavizador
        
    Returns:
        AdvancedTemporalSmoother: Instância configurada
    """
    default_config = {
        'enable_kalman_filter': True,
        'enable_outlier_detection': True,
        'enable_weighted_average': True,
        'kalman_process_noise': 0.01,
        'kalman_measurement_noise': 0.1,
        'outlier_velocity_threshold': 50.0,
        'outlier_acceleration_threshold': 100.0,
        'weighted_window_size': 5,
        'weighted_decay_factor': 0.8
    }
    
    if config:
        default_config.update(config)
    
    return AdvancedTemporalSmoother(default_config)