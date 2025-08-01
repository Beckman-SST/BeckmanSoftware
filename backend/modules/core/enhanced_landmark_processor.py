"""
Processador Aprimorado de Landmarks - Integração das Melhorias da Fase 1
Combina validação anatômica, interpolação inteligente e suavização temporal otimizada.
"""

import numpy as np
import time
from typing import List, Dict, Tuple, Optional, Any, Union
from dataclasses import dataclass
import cv2

# Importa os módulos criados
from .anatomical_validator import AnatomicalValidator, ValidationResult
from .smart_interpolator import SmartInterpolator, InterpolationResult
from .temporal_smoothing import AdvancedTemporalSmoother
from .config import ConfigManager


@dataclass
class ProcessingResult:
    """Resultado do processamento aprimorado de landmarks."""
    landmarks: np.ndarray
    validation_result: ValidationResult
    interpolation_result: Optional[InterpolationResult]
    smoothing_applied: bool
    processing_time: float
    quality_score: float
    notes: List[str]


class EnhancedLandmarkProcessor:
    """
    Processador aprimorado que integra todas as melhorias da Fase 1:
    - Parâmetros otimizados
    - Validação anatômica
    - Interpolação inteligente
    - Suavização temporal avançada
    """
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        Inicializa o processador aprimorado.
        
        Args:
            config_manager: Gerenciador de configurações (opcional)
        """
        self.config_manager = config_manager or ConfigManager()
        self.config = self.config_manager.get_config()
        
        # === INICIALIZA COMPONENTES ===
        self.anatomical_validator = AnatomicalValidator()
        self.smart_interpolator = SmartInterpolator(history_size=10)
        
        # Inicializa suavização temporal apenas se habilitada
        self.temporal_smoother = None
        if self.config.get('enable_advanced_smoothing', True):
            self.temporal_smoother = AdvancedTemporalSmoother(
                kalman_config={
                    'process_noise': self.config.get('kalman_process_noise', 0.005),
                    'measurement_noise': self.config.get('kalman_measurement_noise', 0.08)
                },
                outlier_config={
                    'velocity_threshold': self.config.get('outlier_velocity_threshold', 35.0),
                    'acceleration_threshold': self.config.get('outlier_acceleration_threshold', 75.0)
                },
                weighted_config={
                    'window_size': self.config.get('weighted_window_size', 7),
                    'decay_factor': self.config.get('weighted_decay_factor', 0.85)
                }
            )
        
        # === ESTATÍSTICAS DE PROCESSAMENTO ===
        self.processing_stats = {
            'total_frames': 0,
            'validation_failures': 0,
            'interpolations_performed': 0,
            'smoothing_applied': 0,
            'average_quality_score': 0.0,
            'average_processing_time': 0.0
        }
    
    def process_landmarks(self, landmarks, timestamp=None, image_shape=None) -> ProcessingResult:
        """
        Processa landmarks aplicando todas as melhorias da Fase 1.
        
        Args:
            landmarks: Landmarks de entrada (formato MediaPipe ou numpy array)
            timestamp: Timestamp atual (opcional)
            image_shape: Forma da imagem para normalização (opcional)
            
        Returns:
            ProcessingResult: Resultado completo do processamento
        """
        start_time = time.time()
        notes = []
        
        # === ETAPA 1: NORMALIZAÇÃO DOS LANDMARKS ===
        normalized_landmarks = self._normalize_landmarks(landmarks)
        if normalized_landmarks is None:
            return self._create_error_result("Falha na normalização dos landmarks", start_time)
        
        # === ETAPA 2: VALIDAÇÃO ANATÔMICA ===
        validation_enabled = self.config.get('enable_anatomical_validation', False)
        validation_result = None
        
        if validation_enabled:
            validation_result = self.anatomical_validator.validate_landmarks(
                normalized_landmarks, image_shape
            )
            notes.append(f"Validação anatômica: {'✅' if validation_result.is_valid else '❌'}")
            
            if not validation_result.is_valid:
                self.processing_stats['validation_failures'] += 1
                notes.extend(validation_result.issues[:2])  # Primeiros 2 problemas
        else:
            # Validação básica de qualidade
            validation_result = self._basic_quality_check(normalized_landmarks)
        
        # === ETAPA 3: IDENTIFICAÇÃO DE LANDMARKS AUSENTES/INVÁLIDOS ===
        missing_indices = self._identify_missing_landmarks(normalized_landmarks)
        interpolation_result = None
        
        # === ETAPA 4: INTERPOLAÇÃO INTELIGENTE ===
        if missing_indices and self.config.get('enable_smart_interpolation', False):
            interpolation_result = self.smart_interpolator.interpolate_missing_landmarks(
                normalized_landmarks, missing_indices, timestamp
            )
            
            if interpolation_result.success:
                normalized_landmarks = interpolation_result.interpolated_landmarks
                self.processing_stats['interpolations_performed'] += 1
                notes.append(f"Interpolação: {interpolation_result.method_used}")
            else:
                notes.append("Interpolação falhou")
        
        # === ETAPA 5: SUAVIZAÇÃO TEMPORAL AVANÇADA ===
        smoothing_applied = False
        if self.temporal_smoother is not None:
            try:
                smoothed_landmarks = self.temporal_smoother.smooth_landmarks(normalized_landmarks)
                if smoothed_landmarks is not None:
                    normalized_landmarks = smoothed_landmarks
                    smoothing_applied = True
                    self.processing_stats['smoothing_applied'] += 1
                    notes.append("Suavização temporal aplicada")
            except Exception as e:
                notes.append(f"Erro na suavização: {str(e)[:50]}")
        
        # === ETAPA 6: CÁLCULO DA QUALIDADE FINAL ===
        quality_score = self._calculate_quality_score(
            normalized_landmarks, validation_result, interpolation_result, smoothing_applied
        )
        
        # === ATUALIZA ESTATÍSTICAS ===
        processing_time = time.time() - start_time
        self._update_stats(quality_score, processing_time)
        
        return ProcessingResult(
            landmarks=normalized_landmarks,
            validation_result=validation_result,
            interpolation_result=interpolation_result,
            smoothing_applied=smoothing_applied,
            processing_time=processing_time,
            quality_score=quality_score,
            notes=notes
        )
    
    def _normalize_landmarks(self, landmarks):
        """Normaliza landmarks para formato padrão."""
        try:
            if hasattr(landmarks, 'landmark'):  # MediaPipe format
                return np.array([[lm.x, lm.y, lm.z, lm.visibility] 
                               for lm in landmarks.landmark])
            elif isinstance(landmarks, np.ndarray):
                if landmarks.shape[1] == 3:  # Adiciona coluna de visibilidade se ausente
                    visibility = np.ones((landmarks.shape[0], 1))
                    return np.hstack([landmarks, visibility])
                return landmarks
            elif isinstance(landmarks, list):
                return np.array(landmarks)
            else:
                return None
        except Exception:
            return None
    
    def _basic_quality_check(self, landmarks) -> ValidationResult:
        """Verificação básica de qualidade quando validação anatômica está desabilitada."""
        issues = []
        confidence_score = 1.0
        
        # Verifica thresholds de visibilidade e confiança
        visibility_threshold = self.config.get('landmark_visibility_threshold', 0.5)
        confidence_threshold = self.config.get('landmark_confidence_threshold', 0.7)
        
        low_quality_count = 0
        for i, landmark in enumerate(landmarks):
            if len(landmark) >= 4:  # Tem visibilidade
                if landmark[3] < visibility_threshold:
                    low_quality_count += 1
        
        if low_quality_count > len(landmarks) * 0.3:  # Mais de 30% com baixa qualidade
            issues.append(f"{low_quality_count} landmarks com baixa visibilidade")
            confidence_score *= 0.7
        
        return ValidationResult(
            is_valid=confidence_score > 0.6,
            confidence_score=confidence_score,
            issues=issues
        )
    
    def _identify_missing_landmarks(self, landmarks) -> List[int]:
        """Identifica landmarks ausentes ou de baixa qualidade."""
        missing_indices = []
        visibility_threshold = self.config.get('landmark_visibility_threshold', 0.5)
        
        for i, landmark in enumerate(landmarks):
            # Verifica se landmark está ausente (NaN) ou tem baixa visibilidade
            if (np.isnan(landmark).any() or 
                (len(landmark) >= 4 and landmark[3] < visibility_threshold)):
                missing_indices.append(i)
        
        return missing_indices
    
    def _calculate_quality_score(self, landmarks, validation_result, interpolation_result, smoothing_applied) -> float:
        """Calcula score de qualidade final dos landmarks."""
        base_score = 0.5
        
        # Componente 1: Qualidade básica dos landmarks
        visibility_scores = []
        for landmark in landmarks:
            if len(landmark) >= 4:
                visibility_scores.append(landmark[3])
            else:
                visibility_scores.append(0.5)
        
        avg_visibility = np.mean(visibility_scores)
        base_score += avg_visibility * 0.3
        
        # Componente 2: Resultado da validação anatômica
        if validation_result:
            base_score += validation_result.confidence_score * 0.2
        
        # Componente 3: Sucesso da interpolação
        if interpolation_result and interpolation_result.success:
            base_score += interpolation_result.confidence * 0.1
        
        # Componente 4: Aplicação da suavização
        if smoothing_applied:
            base_score += 0.1
        
        return min(1.0, base_score)
    
    def _update_stats(self, quality_score, processing_time):
        """Atualiza estatísticas de processamento."""
        self.processing_stats['total_frames'] += 1
        
        # Atualiza médias usando média móvel
        alpha = 0.1  # Fator de suavização
        self.processing_stats['average_quality_score'] = (
            alpha * quality_score + 
            (1 - alpha) * self.processing_stats['average_quality_score']
        )
        
        self.processing_stats['average_processing_time'] = (
            alpha * processing_time + 
            (1 - alpha) * self.processing_stats['average_processing_time']
        )
    
    def _create_error_result(self, error_message, start_time) -> ProcessingResult:
        """Cria resultado de erro."""
        return ProcessingResult(
            landmarks=np.zeros((33, 4)),
            validation_result=ValidationResult(False, 0.0, [error_message]),
            interpolation_result=None,
            smoothing_applied=False,
            processing_time=time.time() - start_time,
            quality_score=0.0,
            notes=[error_message]
        )
    
    def get_processing_stats(self) -> Dict:
        """Retorna estatísticas de processamento."""
        stats = self.processing_stats.copy()
        
        if stats['total_frames'] > 0:
            stats['validation_failure_rate'] = stats['validation_failures'] / stats['total_frames']
            stats['interpolation_rate'] = stats['interpolations_performed'] / stats['total_frames']
            stats['smoothing_rate'] = stats['smoothing_applied'] / stats['total_frames']
        else:
            stats['validation_failure_rate'] = 0.0
            stats['interpolation_rate'] = 0.0
            stats['smoothing_rate'] = 0.0
        
        return stats
    
    def reset_stats(self):
        """Reseta estatísticas de processamento."""
        self.processing_stats = {
            'total_frames': 0,
            'validation_failures': 0,
            'interpolations_performed': 0,
            'smoothing_applied': 0,
            'average_quality_score': 0.0,
            'average_processing_time': 0.0
        }
        
        # Reseta histórico do interpolador
        self.smart_interpolator.reset_history()
        
        # Reseta suavização temporal se existir
        if self.temporal_smoother:
            self.temporal_smoother.reset()
    
    def update_config(self, new_config: Dict):
        """Atualiza configurações do processador."""
        self.config_manager.update_config(new_config)
        self.config = self.config_manager.get_config()
        
        # Reinicializa componentes se necessário
        if self.temporal_smoother and self.config.get('enable_advanced_smoothing', True):
            self.temporal_smoother.update_config({
                'kalman': {
                    'process_noise': self.config.get('kalman_process_noise', 0.005),
                    'measurement_noise': self.config.get('kalman_measurement_noise', 0.08)
                },
                'outlier': {
                    'velocity_threshold': self.config.get('outlier_velocity_threshold', 35.0),
                    'acceleration_threshold': self.config.get('outlier_acceleration_threshold', 75.0)
                },
                'weighted': {
                    'window_size': self.config.get('weighted_window_size', 7),
                    'decay_factor': self.config.get('weighted_decay_factor', 0.85)
                }
            })
    
    def get_quality_report(self) -> str:
        """Gera relatório de qualidade em texto."""
        stats = self.get_processing_stats()
        
        report = f"""
=== RELATÓRIO DE QUALIDADE DOS LANDMARKS ===
Frames processados: {stats['total_frames']}
Qualidade média: {stats['average_quality_score']:.3f}
Tempo médio: {stats['average_processing_time']*1000:.1f}ms

Taxa de falhas na validação: {stats['validation_failure_rate']*100:.1f}%
Taxa de interpolação: {stats['interpolation_rate']*100:.1f}%
Taxa de suavização: {stats['smoothing_rate']*100:.1f}%

Status: {'🟢 Excelente' if stats['average_quality_score'] > 0.8 else 
         '🟡 Bom' if stats['average_quality_score'] > 0.6 else 
         '🔴 Precisa melhorar'}
"""
        return report


# === FUNÇÃO DE CONVENIÊNCIA ===
def create_enhanced_landmark_processor(config_manager=None):
    """Cria uma instância do processador aprimorado."""
    return EnhancedLandmarkProcessor(config_manager)


# === EXEMPLO DE USO ===
if __name__ == "__main__":
    # Teste básico do processador aprimorado
    processor = create_enhanced_landmark_processor()
    
    # Landmarks de exemplo
    test_landmarks = np.random.rand(33, 4)
    test_landmarks[13] = np.nan  # Simula landmark ausente
    
    result = processor.process_landmarks(test_landmarks)
    
    print(f"Qualidade: {result.quality_score:.3f}")
    print(f"Tempo: {result.processing_time*1000:.1f}ms")
    print(f"Notas: {result.notes}")
    print(processor.get_quality_report())