"""
Sistema de Kalman Adaptativo - Fase 3
Implementa filtro de Kalman que se adapta automaticamente às condições de movimento.
"""

import numpy as np
import time
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import cv2


class MovementType(Enum):
    """Tipos de movimento detectados."""
    STATIC = "static"           # Parado ou movimento mínimo
    SLOW = "slow"              # Movimento lento e suave
    NORMAL = "normal"          # Movimento normal
    FAST = "fast"              # Movimento rápido
    ERRATIC = "erratic"        # Movimento errático/instável
    SUDDEN = "sudden"          # Mudança súbita


class ConfidenceLevel(Enum):
    """Níveis de confiança na detecção."""
    VERY_LOW = 0.2
    LOW = 0.4
    MEDIUM = 0.6
    HIGH = 0.8
    VERY_HIGH = 0.95


@dataclass
class AdaptiveConfig:
    """Configuração adaptativa do filtro de Kalman."""
    process_noise: float
    measurement_noise: float
    prediction_weight: float
    measurement_weight: float
    adaptation_rate: float
    confidence_threshold: float


@dataclass
class MovementAnalysis:
    """Análise do movimento atual."""
    movement_type: MovementType
    velocity_magnitude: float
    acceleration_magnitude: float
    direction_stability: float
    confidence_level: ConfidenceLevel
    noise_estimate: float


class AdaptiveKalmanFilter:
    """
    Filtro de Kalman que se adapta automaticamente às condições de movimento,
    confiança da detecção e características do landmark.
    """
    
    def __init__(self, landmark_id: int, config: Dict = None):
        """
        Inicializa o filtro de Kalman adaptativo.
        
        Args:
            landmark_id: ID do landmark
            config: Configurações do filtro
        """
        self.landmark_id = landmark_id
        self.config = config or {}
        
        # === CONFIGURAÇÕES ADAPTATIVAS ===
        self.base_process_noise = self.config.get('base_process_noise', 0.005)
        self.base_measurement_noise = self.config.get('base_measurement_noise', 0.08)
        self.adaptation_rate = self.config.get('adaptation_rate', 0.1)
        self.confidence_adaptation = self.config.get('confidence_adaptation', True)
        self.movement_adaptation = self.config.get('movement_adaptation', True)
        
        # === ESTADO DO FILTRO ===
        # Estado: [x, y, vx, vy, ax, ay] - posição, velocidade, aceleração
        self.state = np.zeros(6)
        self.covariance = np.eye(6) * 1000  # Incerteza inicial alta
        
        # === MATRIZES DO SISTEMA ===
        self.dt = 1.0 / 30.0  # Assume 30 FPS
        self._initialize_matrices()
        
        # === HISTÓRICO PARA ANÁLISE ===
        self.position_history = []
        self.velocity_history = []
        self.confidence_history = []
        self.measurement_history = []
        self.max_history = 20
        
        # === CONFIGURAÇÕES ADAPTATIVAS ATUAIS ===
        self.current_config = AdaptiveConfig(
            process_noise=self.base_process_noise,
            measurement_noise=self.base_measurement_noise,
            prediction_weight=0.7,
            measurement_weight=0.3,
            adaptation_rate=self.adaptation_rate,
            confidence_threshold=0.5
        )
        
        # === ANÁLISE DE MOVIMENTO ===
        self.movement_analyzer = MovementAnalyzer()
        
        # === ESTATÍSTICAS ===
        self.stats = {
            'updates': 0,
            'adaptations': 0,
            'movement_changes': 0,
            'confidence_adaptations': 0,
            'prediction_errors': [],
            'adaptation_history': []
        }
        
        self.initialized = False
    
    def _initialize_matrices(self):
        """Inicializa matrizes do sistema Kalman."""
        # Matriz de transição de estado (modelo de aceleração constante)
        self.F = np.array([
            [1, 0, self.dt, 0, 0.5*self.dt**2, 0],
            [0, 1, 0, self.dt, 0, 0.5*self.dt**2],
            [0, 0, 1, 0, self.dt, 0],
            [0, 0, 0, 1, 0, self.dt],
            [0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 1]
        ])
        
        # Matriz de observação (observamos apenas posição)
        self.H = np.array([
            [1, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0]
        ])
        
        # Matriz de ruído do processo (será adaptada)
        self.Q = self._create_process_noise_matrix(self.base_process_noise)
        
        # Matriz de ruído da medição (será adaptada)
        self.R = np.eye(2) * self.base_measurement_noise
    
    def _create_process_noise_matrix(self, noise_level: float) -> np.ndarray:
        """Cria matriz de ruído do processo."""
        # Modelo de ruído para aceleração
        dt = self.dt
        dt2 = dt * dt
        dt3 = dt2 * dt
        dt4 = dt3 * dt
        
        return noise_level * np.array([
            [dt4/4, 0, dt3/2, 0, dt2/2, 0],
            [0, dt4/4, 0, dt3/2, 0, dt2/2],
            [dt3/2, 0, dt2, 0, dt, 0],
            [0, dt3/2, 0, dt2, 0, dt],
            [dt2/2, 0, dt, 0, 1, 0],
            [0, dt2/2, 0, dt, 0, 1]
        ])
    
    def predict(self) -> Tuple[float, float]:
        """
        Etapa de predição do filtro.
        
        Returns:
            Posição predita (x, y)
        """
        if not self.initialized:
            return (0.0, 0.0)
        
        # Predição do estado
        self.state = self.F @ self.state
        
        # Predição da covariância
        self.covariance = self.F @ self.covariance @ self.F.T + self.Q
        
        return (self.state[0], self.state[1])
    
    def update(self, measurement: Tuple[float, float], confidence: float = 1.0, 
               timestamp: float = None) -> Tuple[float, float]:
        """
        Etapa de atualização do filtro com adaptação automática.
        
        Args:
            measurement: Medição (x, y)
            confidence: Confiança na medição (0-1)
            timestamp: Timestamp da medição
            
        Returns:
            Posição filtrada (x, y)
        """
        z = np.array(measurement)
        current_time = timestamp or time.time()
        
        if not self.initialized:
            # Inicialização
            self.state[:2] = z
            self.state[2:] = 0  # Velocidade e aceleração iniciais zero
            self.initialized = True
            self._add_to_history(z, confidence, current_time)
            return tuple(z)
        
        # === ANÁLISE DE MOVIMENTO ===
        movement_analysis = self._analyze_movement(z, confidence)
        
        # === ADAPTAÇÃO AUTOMÁTICA ===
        if self.movement_adaptation or self.confidence_adaptation:
            self._adapt_filter_parameters(movement_analysis, confidence)
        
        # === CÁLCULO DO GANHO DE KALMAN ===
        # Inovação
        y = z - (self.H @ self.state)
        
        # Covariância da inovação
        S = self.H @ self.covariance @ self.H.T + self.R
        
        # Ganho de Kalman
        K = self.covariance @ self.H.T @ np.linalg.inv(S)
        
        # === ATUALIZAÇÃO ADAPTATIVA ===
        # Ajusta ganho baseado na confiança e análise de movimento
        confidence_factor = self._calculate_confidence_factor(confidence, movement_analysis)
        K_adapted = K * confidence_factor
        
        # Atualização do estado
        self.state = self.state + K_adapted @ y
        
        # Atualização da covariância
        I_KH = np.eye(6) - K_adapted @ self.H
        self.covariance = I_KH @ self.covariance
        
        # === ATUALIZA HISTÓRICO E ESTATÍSTICAS ===
        self._add_to_history(z, confidence, current_time)
        self._update_stats(y, movement_analysis)
        
        return (self.state[0], self.state[1])
    
    def _analyze_movement(self, measurement: np.ndarray, confidence: float) -> MovementAnalysis:
        """Analisa o tipo de movimento atual."""
        if len(self.position_history) < 3:
            return MovementAnalysis(
                movement_type=MovementType.STATIC,
                velocity_magnitude=0.0,
                acceleration_magnitude=0.0,
                direction_stability=1.0,
                confidence_level=ConfidenceLevel.MEDIUM,
                noise_estimate=self.base_measurement_noise
            )
        
        return self.movement_analyzer.analyze(
            self.position_history[-10:],  # Últimas 10 posições
            self.confidence_history[-10:],
            measurement,
            confidence
        )
    
    def _adapt_filter_parameters(self, movement_analysis: MovementAnalysis, confidence: float):
        """Adapta parâmetros do filtro baseado na análise."""
        old_config = self.current_config
        
        # === ADAPTAÇÃO BASEADA NO MOVIMENTO ===
        if self.movement_adaptation:
            if movement_analysis.movement_type == MovementType.STATIC:
                # Movimento estático - reduz ruído do processo
                self.current_config.process_noise = self.base_process_noise * 0.5
                self.current_config.measurement_noise = self.base_measurement_noise * 0.8
                
            elif movement_analysis.movement_type == MovementType.FAST:
                # Movimento rápido - aumenta ruído do processo
                self.current_config.process_noise = self.base_process_noise * 2.0
                self.current_config.measurement_noise = self.base_measurement_noise * 1.2
                
            elif movement_analysis.movement_type == MovementType.ERRATIC:
                # Movimento errático - favorece predição
                self.current_config.process_noise = self.base_process_noise * 1.5
                self.current_config.measurement_noise = self.base_measurement_noise * 2.0
                self.current_config.prediction_weight = 0.8
                self.current_config.measurement_weight = 0.2
                
            elif movement_analysis.movement_type == MovementType.SUDDEN:
                # Mudança súbita - favorece medição
                self.current_config.process_noise = self.base_process_noise * 3.0
                self.current_config.measurement_noise = self.base_measurement_noise * 0.5
                self.current_config.prediction_weight = 0.3
                self.current_config.measurement_weight = 0.7
        
        # === ADAPTAÇÃO BASEADA NA CONFIANÇA ===
        if self.confidence_adaptation:
            if confidence < 0.3:
                # Baixa confiança - favorece predição
                self.current_config.measurement_noise *= 3.0
                self.current_config.prediction_weight = 0.9
                self.current_config.measurement_weight = 0.1
                
            elif confidence > 0.9:
                # Alta confiança - favorece medição
                self.current_config.measurement_noise *= 0.5
                self.current_config.prediction_weight = 0.4
                self.current_config.measurement_weight = 0.6
        
        # === APLICA ADAPTAÇÕES ===
        if self._config_changed(old_config, self.current_config):
            self._apply_config_changes()
            self.stats['adaptations'] += 1
            self.stats['adaptation_history'].append({
                'timestamp': time.time(),
                'movement_type': movement_analysis.movement_type.value,
                'confidence': confidence,
                'config': self.current_config
            })
    
    def _calculate_confidence_factor(self, confidence: float, movement_analysis: MovementAnalysis) -> float:
        """Calcula fator de confiança para ajustar ganho de Kalman."""
        base_factor = 1.0
        
        # Ajuste baseado na confiança da medição
        confidence_factor = 0.5 + (confidence * 0.5)  # 0.5 a 1.0
        
        # Ajuste baseado no tipo de movimento
        movement_factor = {
            MovementType.STATIC: 1.0,
            MovementType.SLOW: 1.0,
            MovementType.NORMAL: 0.9,
            MovementType.FAST: 0.8,
            MovementType.ERRATIC: 0.6,
            MovementType.SUDDEN: 1.2  # Favorece medição em mudanças súbitas
        }.get(movement_analysis.movement_type, 1.0)
        
        return base_factor * confidence_factor * movement_factor
    
    def _config_changed(self, old_config: AdaptiveConfig, new_config: AdaptiveConfig) -> bool:
        """Verifica se configuração mudou significativamente."""
        threshold = 0.1  # 10% de mudança
        
        return (abs(old_config.process_noise - new_config.process_noise) > threshold * old_config.process_noise or
                abs(old_config.measurement_noise - new_config.measurement_noise) > threshold * old_config.measurement_noise)
    
    def _apply_config_changes(self):
        """Aplica mudanças de configuração às matrizes."""
        self.Q = self._create_process_noise_matrix(self.current_config.process_noise)
        self.R = np.eye(2) * self.current_config.measurement_noise
    
    def _add_to_history(self, measurement: np.ndarray, confidence: float, timestamp: float):
        """Adiciona medição ao histórico."""
        self.position_history.append(measurement.copy())
        self.confidence_history.append(confidence)
        self.measurement_history.append(timestamp)
        
        # Calcula velocidade se possível
        if len(self.position_history) >= 2:
            dt = timestamp - self.measurement_history[-2] if len(self.measurement_history) >= 2 else self.dt
            velocity = (self.position_history[-1] - self.position_history[-2]) / max(dt, 0.001)
            self.velocity_history.append(np.linalg.norm(velocity))
        
        # Limita tamanho do histórico
        if len(self.position_history) > self.max_history:
            self.position_history.pop(0)
            self.confidence_history.pop(0)
            self.measurement_history.pop(0)
            if self.velocity_history:
                self.velocity_history.pop(0)
    
    def _update_stats(self, innovation: np.ndarray, movement_analysis: MovementAnalysis):
        """Atualiza estatísticas do filtro."""
        self.stats['updates'] += 1
        
        # Erro de predição
        prediction_error = np.linalg.norm(innovation)
        self.stats['prediction_errors'].append(prediction_error)
        
        # Limita histórico de erros
        if len(self.stats['prediction_errors']) > 100:
            self.stats['prediction_errors'].pop(0)
    
    def get_position(self) -> Tuple[float, float]:
        """Retorna posição atual."""
        return (self.state[0], self.state[1])
    
    def get_velocity(self) -> Tuple[float, float]:
        """Retorna velocidade atual."""
        return (self.state[2], self.state[3])
    
    def get_acceleration(self) -> Tuple[float, float]:
        """Retorna aceleração atual."""
        return (self.state[4], self.state[5])
    
    def get_uncertainty(self) -> float:
        """Retorna incerteza da posição atual."""
        return np.sqrt(self.covariance[0, 0] + self.covariance[1, 1])
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do filtro."""
        stats = self.stats.copy()
        
        if self.stats['prediction_errors']:
            stats['average_prediction_error'] = np.mean(self.stats['prediction_errors'])
            stats['prediction_error_std'] = np.std(self.stats['prediction_errors'])
        else:
            stats['average_prediction_error'] = 0.0
            stats['prediction_error_std'] = 0.0
        
        stats['current_uncertainty'] = self.get_uncertainty()
        stats['current_config'] = self.current_config
        
        return stats
    
    def reset(self):
        """Reseta o filtro."""
        self.state = np.zeros(6)
        self.covariance = np.eye(6) * 1000
        self.position_history.clear()
        self.velocity_history.clear()
        self.confidence_history.clear()
        self.measurement_history.clear()
        self.initialized = False
        
        # Reseta configuração
        self.current_config = AdaptiveConfig(
            process_noise=self.base_process_noise,
            measurement_noise=self.base_measurement_noise,
            prediction_weight=0.7,
            measurement_weight=0.3,
            adaptation_rate=self.adaptation_rate,
            confidence_threshold=0.5
        )
        
        # Reseta estatísticas
        self.stats = {
            'updates': 0,
            'adaptations': 0,
            'movement_changes': 0,
            'confidence_adaptations': 0,
            'prediction_errors': [],
            'adaptation_history': []
        }


class MovementAnalyzer:
    """Analisador de padrões de movimento."""
    
    def analyze(self, position_history: List[np.ndarray], confidence_history: List[float],
                current_measurement: np.ndarray, current_confidence: float) -> MovementAnalysis:
        """Analisa padrão de movimento."""
        if len(position_history) < 3:
            return MovementAnalysis(
                movement_type=MovementType.STATIC,
                velocity_magnitude=0.0,
                acceleration_magnitude=0.0,
                direction_stability=1.0,
                confidence_level=ConfidenceLevel.MEDIUM,
                noise_estimate=0.08
            )
        
        # === CÁLCULO DE VELOCIDADES ===
        velocities = []
        for i in range(1, len(position_history)):
            vel = position_history[i] - position_history[i-1]
            velocities.append(np.linalg.norm(vel))
        
        # === CÁLCULO DE ACELERAÇÕES ===
        accelerations = []
        for i in range(1, len(velocities)):
            acc = abs(velocities[i] - velocities[i-1])
            accelerations.append(acc)
        
        # === ANÁLISE DE MOVIMENTO ===
        avg_velocity = np.mean(velocities) if velocities else 0.0
        avg_acceleration = np.mean(accelerations) if accelerations else 0.0
        
        # Estabilidade de direção
        direction_stability = self._calculate_direction_stability(position_history)
        
        # Classificação do movimento
        movement_type = self._classify_movement(avg_velocity, avg_acceleration, direction_stability)
        
        # Nível de confiança
        confidence_level = self._classify_confidence(current_confidence)
        
        # Estimativa de ruído
        noise_estimate = self._estimate_noise(position_history, velocities)
        
        return MovementAnalysis(
            movement_type=movement_type,
            velocity_magnitude=avg_velocity,
            acceleration_magnitude=avg_acceleration,
            direction_stability=direction_stability,
            confidence_level=confidence_level,
            noise_estimate=noise_estimate
        )
    
    def _calculate_direction_stability(self, positions: List[np.ndarray]) -> float:
        """Calcula estabilidade da direção do movimento."""
        if len(positions) < 3:
            return 1.0
        
        directions = []
        for i in range(2, len(positions)):
            vec1 = positions[i-1] - positions[i-2]
            vec2 = positions[i] - positions[i-1]
            
            if np.linalg.norm(vec1) > 0 and np.linalg.norm(vec2) > 0:
                # Produto escalar normalizado
                dot_product = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
                directions.append(max(-1, min(1, dot_product)))  # Clamp para [-1, 1]
        
        if not directions:
            return 1.0
        
        # Estabilidade = média dos cossenos dos ângulos
        return np.mean(directions)
    
    def _classify_movement(self, velocity: float, acceleration: float, stability: float) -> MovementType:
        """Classifica tipo de movimento."""
        if velocity < 0.01:
            return MovementType.STATIC
        elif velocity < 0.05 and acceleration < 0.02:
            return MovementType.SLOW
        elif velocity > 0.2 or acceleration > 0.1:
            return MovementType.FAST
        elif stability < 0.3 or acceleration > 0.05:
            return MovementType.ERRATIC
        elif acceleration > 0.08:  # Mudança súbita
            return MovementType.SUDDEN
        else:
            return MovementType.NORMAL
    
    def _classify_confidence(self, confidence: float) -> ConfidenceLevel:
        """Classifica nível de confiança."""
        if confidence < 0.3:
            return ConfidenceLevel.VERY_LOW
        elif confidence < 0.5:
            return ConfidenceLevel.LOW
        elif confidence < 0.7:
            return ConfidenceLevel.MEDIUM
        elif confidence < 0.9:
            return ConfidenceLevel.HIGH
        else:
            return ConfidenceLevel.VERY_HIGH
    
    def _estimate_noise(self, positions: List[np.ndarray], velocities: List[float]) -> float:
        """Estima nível de ruído nas medições."""
        if len(velocities) < 3:
            return 0.08
        
        # Variabilidade da velocidade como proxy para ruído
        velocity_std = np.std(velocities)
        
        # Normaliza para range típico de ruído
        noise_estimate = min(0.2, max(0.01, velocity_std * 2))
        
        return noise_estimate


# === FUNÇÃO DE CONVENIÊNCIA ===
def create_adaptive_kalman_filter(landmark_id: int, config: Dict = None):
    """Cria uma instância do filtro de Kalman adaptativo."""
    return AdaptiveKalmanFilter(landmark_id, config)


# === EXEMPLO DE USO ===
if __name__ == "__main__":
    # Teste básico do filtro adaptativo
    filter_kalman = create_adaptive_kalman_filter(0)
    
    # Simula sequência de medições
    measurements = [
        (0.5, 0.5, 0.9),  # (x, y, confidence)
        (0.51, 0.51, 0.8),
        (0.52, 0.52, 0.7),
        (0.6, 0.6, 0.3),   # Mudança súbita com baixa confiança
        (0.61, 0.61, 0.9),
        (0.62, 0.62, 0.95),
    ]
    
    for i, (x, y, conf) in enumerate(measurements):
        predicted = filter_kalman.predict()
        filtered = filter_kalman.update((x, y), conf)
        
        print(f"Frame {i}: Medição=({x:.3f}, {y:.3f}) Conf={conf:.2f}")
        print(f"         Predição=({predicted[0]:.3f}, {predicted[1]:.3f})")
        print(f"         Filtrado=({filtered[0]:.3f}, {filtered[1]:.3f})")
        print(f"         Incerteza={filter_kalman.get_uncertainty():.4f}")
        print()
    
    # Estatísticas
    stats = filter_kalman.get_stats()
    print(f"Adaptações realizadas: {stats['adaptations']}")
    print(f"Erro médio de predição: {stats['average_prediction_error']:.4f}")