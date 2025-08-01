"""
Processamento Hierárquico de Landmarks - Fase 2 OTIMIZADO
Otimiza performance processando landmarks por prioridade e região anatômica.
Versão otimizada com algoritmos mais eficientes e cache inteligente.
"""

import numpy as np
import time
import hashlib
from typing import List, Dict, Tuple, Optional, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import cv2
from collections import deque
import threading


class LandmarkPriority(Enum):
    """Níveis de prioridade para processamento de landmarks."""
    CRITICAL = 1    # Face, pose central - SEMPRE processado
    HIGH = 2        # Mãos, pés - Alta prioridade
    MEDIUM = 3      # Detalhes faciais - Média prioridade
    LOW = 4         # Landmarks auxiliares - Baixa prioridade


class AnatomicalRegion(Enum):
    """Regiões anatômicas para processamento hierárquico."""
    FACE = "face"
    POSE = "pose"
    LEFT_HAND = "left_hand"
    RIGHT_HAND = "right_hand"
    LEFT_FOOT = "left_foot"
    RIGHT_FOOT = "right_foot"


@dataclass
class ProcessingLevel:
    """Define um nível de processamento hierárquico otimizado."""
    priority: LandmarkPriority
    regions: List[AnatomicalRegion]
    landmark_indices: np.ndarray  # Mudança: usar numpy array para performance
    processing_budget: float  # Tempo máximo em ms
    quality_threshold: float  # Qualidade mínima aceitável
    can_skip: bool = True     # Se pode ser pulado em caso de pressão de tempo
    parallel_safe: bool = False  # Se pode ser processado em paralelo


@dataclass
class HierarchicalResult:
    """Resultado do processamento hierárquico otimizado."""
    processed_landmarks: np.ndarray
    processing_levels_completed: int
    total_processing_time: float
    quality_scores_by_level: Dict[int, float]
    skipped_regions: List[AnatomicalRegion]
    performance_metrics: Dict[str, float]
    cache_hits: int = 0
    optimization_applied: List[str] = field(default_factory=list)


class HierarchicalProcessor:
    """
    Processador hierárquico OTIMIZADO que maximiza performance processando landmarks
    por ordem de prioridade e importância anatômica com algoritmos eficientes.
    """
    
    def __init__(self, config: Dict = None):
        """
        Inicializa o processador hierárquico otimizado.
        
        Args:
            config: Configurações do processador
        """
        self.config = config or {}
        
        # === CONFIGURAÇÕES DE PERFORMANCE OTIMIZADAS ===
        self.max_processing_time = self.config.get('max_processing_time_ms', 33.0)  # 33ms para 30 FPS
        self.adaptive_quality = self.config.get('adaptive_quality', True)
        self.skip_low_priority_on_delay = self.config.get('skip_low_priority_on_delay', True)
        self.enable_parallel_processing = self.config.get('enable_parallel', False)
        self.enable_smart_caching = self.config.get('enable_smart_caching', True)
        
        # === DEFINIÇÃO DOS NÍVEIS HIERÁRQUICOS OTIMIZADOS ===
        self.processing_levels = self._define_optimized_processing_levels()
        
        # === CACHE INTELIGENTE DE PERFORMANCE ===
        self.performance_history = deque(maxlen=50)  # Circular buffer mais eficiente
        self.region_performance_cache = {}
        self.result_cache = {}  # Cache de resultados similares
        self.cache_hit_threshold = 0.95  # Threshold para similaridade de cache
        
        # === OTIMIZAÇÕES DE MEMÓRIA ===
        self._landmark_buffer = None  # Buffer reutilizável
        self._result_buffer = None    # Buffer para resultados
        
        # === ESTATÍSTICAS OTIMIZADAS ===
        self.stats = {
            'total_frames': 0,
            'levels_completed_avg': 0.0,
            'skipped_regions_count': 0,
            'performance_adaptations': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'optimization_hits': 0,
            'parallel_executions': 0,
            'memory_optimizations': 0
        }
        
        # === THREAD SAFETY ===
        self.lock = threading.RLock() if self.enable_parallel_processing else None
    
    def _define_optimized_processing_levels(self) -> List[ProcessingLevel]:
        """Define os níveis de processamento hierárquico OTIMIZADOS."""
        return [
            # NÍVEL 1: CRÍTICO - Face e pose central (NUNCA pode ser pulado)
            ProcessingLevel(
                priority=LandmarkPriority.CRITICAL,
                regions=[AnatomicalRegion.FACE, AnatomicalRegion.POSE],
                landmark_indices=np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 23, 24]),
                processing_budget=15.0,  # Reduzido para 15ms
                quality_threshold=0.8,
                can_skip=False,  # NUNCA pode ser pulado
                parallel_safe=False
            ),
            
            # NÍVEL 2: ALTO - Mãos (importante para gestos, pode ser processado em paralelo)
            ProcessingLevel(
                priority=LandmarkPriority.HIGH,
                regions=[AnatomicalRegion.LEFT_HAND, AnatomicalRegion.RIGHT_HAND],
                landmark_indices=np.array([17, 18, 19, 20, 21, 22, 25, 26, 27, 28, 29, 30]),
                processing_budget=10.0,  # Reduzido para 10ms
                quality_threshold=0.7,
                can_skip=True,
                parallel_safe=True  # Pode ser processado em paralelo
            ),
            
            # NÍVEL 3: MÉDIO - Detalhes faciais (pode ser pulado sob pressão)
            ProcessingLevel(
                priority=LandmarkPriority.MEDIUM,
                regions=[AnatomicalRegion.FACE],
                landmark_indices=np.array([31, 32]) if hasattr(np, 'array') else np.array([]),
                processing_budget=5.0,   # Reduzido para 5ms
                quality_threshold=0.6,
                can_skip=True,
                parallel_safe=True
            ),
            
            # NÍVEL 4: BAIXO - Auxiliares (primeiro a ser pulado)
            ProcessingLevel(
                priority=LandmarkPriority.LOW,
                regions=[AnatomicalRegion.LEFT_FOOT, AnatomicalRegion.RIGHT_FOOT],
                landmark_indices=np.array([]),  # Preenchido dinamicamente
                processing_budget=3.0,   # Apenas 3ms
                quality_threshold=0.5,
                can_skip=True,
                parallel_safe=True
            )
        ]
    
    def process_landmarks_hierarchical(self, landmarks, enhanced_processor, timestamp=None) -> HierarchicalResult:
        """
        Processa landmarks usando abordagem hierárquica OTIMIZADA.
        
        Args:
            landmarks: Landmarks de entrada
            enhanced_processor: Processador aprimorado da Fase 1
            timestamp: Timestamp atual
            
        Returns:
            HierarchicalResult: Resultado do processamento hierárquico otimizado
        """
        start_time = time.perf_counter()  # Mais preciso que time.time()
        
        # === OTIMIZAÇÃO DE MEMÓRIA: Reutiliza buffers ===
        if self._landmark_buffer is None or self._landmark_buffer.shape != landmarks.shape:
            self._landmark_buffer = np.empty_like(landmarks)
            self.stats['memory_optimizations'] += 1
        
        np.copyto(self._landmark_buffer, landmarks)
        processed_landmarks = self._landmark_buffer
        
        # === VERIFICAÇÃO DE CACHE INTELIGENTE ===
        cache_key = self._generate_cache_key(landmarks, timestamp)
        cached_result = self._check_cache(cache_key) if self.enable_smart_caching else None
        
        if cached_result is not None:
            self.stats['cache_hits'] += 1
            cached_result.cache_hits = 1
            cached_result.optimization_applied.append("cache_hit")
            return cached_result
        
        # === INICIALIZAÇÃO DE VARIÁVEIS ===
        quality_scores_by_level = {}
        skipped_regions = []
        levels_completed = 0
        optimization_applied = []
        
        # === PROCESSAMENTO OTIMIZADO POR NÍVEIS ===
        for level_idx, level in enumerate(self.processing_levels):
            level_start_time = time.perf_counter()
            
            # === VERIFICAÇÃO INTELIGENTE DE TEMPO ===
            elapsed_time = (time.perf_counter() - start_time) * 1000  # ms
            remaining_time = self.max_processing_time - elapsed_time
            
            # Lógica otimizada de skip
            if remaining_time < level.processing_budget:
                if level.can_skip and self.skip_low_priority_on_delay:
                    skipped_regions.extend(level.regions)
                    optimization_applied.append(f"skipped_level_{level_idx}")
                    continue
                elif not level.can_skip:
                    # Nível crítico - reduz budget dos próximos níveis
                    self._adjust_remaining_budgets(level_idx + 1, remaining_time * 0.8)
                    optimization_applied.append("budget_adjustment")
            
            # === EXTRAÇÃO OTIMIZADA DE LANDMARKS ===
            level_landmarks = self._extract_level_landmarks_optimized(processed_landmarks, level)
            
            if level_landmarks is not None and level_landmarks.size > 0:
                # === PROCESSAMENTO COM CACHE DE REGIÃO ===
                region_cache_key = f"{cache_key}_{level_idx}"
                cached_level_result = self._check_region_cache(region_cache_key) if self.enable_smart_caching else None
                
                if cached_level_result is not None:
                    level_result = cached_level_result
                    optimization_applied.append(f"region_cache_hit_{level_idx}")
                    self.stats['optimization_hits'] += 1
                else:
                    # Processamento normal
                    level_result = enhanced_processor.process_landmarks(
                        level_landmarks, timestamp
                    )
                    
                    # Armazena no cache de região
                    if self.enable_smart_caching:
                        self._store_region_cache(region_cache_key, level_result)
                
                # === INTEGRAÇÃO OTIMIZADA ===
                self._integrate_level_results_optimized(
                    processed_landmarks, level_result.landmarks, level
                )
                
                quality_scores_by_level[level_idx] = level_result.quality_score
                levels_completed += 1
                
                # === OTIMIZAÇÃO ADAPTATIVA DE QUALIDADE ===
                if self._should_skip_remaining_levels(level_result, level, remaining_time):
                    optimization_applied.append("quality_based_skip")
                    break
            
            # === ATUALIZAÇÃO EFICIENTE DE CACHE ===
            level_time = (time.perf_counter() - level_start_time) * 1000
            self._update_performance_cache_optimized(level.regions[0], level_time)
        
        # === CÁLCULO OTIMIZADO DE MÉTRICAS ===
        total_time = (time.perf_counter() - start_time) * 1000
        performance_metrics = self._calculate_performance_metrics_optimized(
            total_time, levels_completed, len(skipped_regions)
        )
        
        # === ATUALIZAÇÃO EFICIENTE DE ESTATÍSTICAS ===
        self._update_stats_optimized(levels_completed, len(skipped_regions), total_time)
        
        # === CRIAÇÃO DO RESULTADO ===
        result = HierarchicalResult(
            processed_landmarks=processed_landmarks.copy(),  # Copia apenas no final
            processing_levels_completed=levels_completed,
            total_processing_time=total_time,
            quality_scores_by_level=quality_scores_by_level,
            skipped_regions=skipped_regions,
            performance_metrics=performance_metrics,
            cache_hits=0,
            optimization_applied=optimization_applied
        )
        
        # === ARMAZENA NO CACHE ===
        if self.enable_smart_caching:
            self._store_cache(cache_key, result)
        
        return result
    
    # === MÉTODOS OTIMIZADOS ===
    
    def _generate_cache_key(self, landmarks: np.ndarray, timestamp: float = None) -> str:
        """Gera chave de cache baseada em landmarks e timestamp."""
        # Hash rápido baseado em posições principais
        key_landmarks = landmarks[::4] if len(landmarks) > 8 else landmarks  # Amostragem
        hash_input = np.round(key_landmarks.flatten(), 3)  # Reduz precisão para melhor cache hit
        return hashlib.md5(hash_input.tobytes()).hexdigest()[:16]
    
    def _check_cache(self, cache_key: str) -> Optional[HierarchicalResult]:
        """Verifica cache de resultados."""
        return self.result_cache.get(cache_key)
    
    def _store_cache(self, cache_key: str, result: HierarchicalResult):
        """Armazena resultado no cache."""
        if len(self.result_cache) > 50:  # Limita tamanho do cache
            # Remove entrada mais antiga
            oldest_key = next(iter(self.result_cache))
            del self.result_cache[oldest_key]
        self.result_cache[cache_key] = result
    
    def _check_region_cache(self, region_key: str):
        """Verifica cache de região específica."""
        return self.region_performance_cache.get(f"result_{region_key}")
    
    def _store_region_cache(self, region_key: str, result):
        """Armazena resultado de região no cache."""
        self.region_performance_cache[f"result_{region_key}"] = result
    
    def _extract_level_landmarks_optimized(self, landmarks: np.ndarray, level: ProcessingLevel) -> Optional[np.ndarray]:
        """Extrai landmarks específicos de um nível de forma otimizada."""
        if level.landmark_indices.size == 0:
            return None
        
        # Usa indexação numpy direta - muito mais rápida
        try:
            valid_mask = level.landmark_indices < len(landmarks)
            if not np.any(valid_mask):
                return None
            
            valid_indices = level.landmark_indices[valid_mask]
            return landmarks[valid_indices]
        except (IndexError, ValueError):
            return None
    
    def _integrate_level_results_optimized(self, base_landmarks: np.ndarray, 
                                         level_landmarks: np.ndarray, level: ProcessingLevel):
        """Integra resultados de um nível de volta aos landmarks base (in-place)."""
        if level_landmarks is None or level.landmark_indices.size == 0:
            return
        
        try:
            valid_mask = level.landmark_indices < len(base_landmarks)
            valid_indices = level.landmark_indices[valid_mask]
            
            # Integração in-place para melhor performance
            min_len = min(len(level_landmarks), len(valid_indices))
            base_landmarks[valid_indices[:min_len]] = level_landmarks[:min_len]
        except (IndexError, ValueError):
            pass
    
    def _should_skip_remaining_levels(self, level_result, level: ProcessingLevel, remaining_time: float) -> bool:
        """Determina se deve pular níveis restantes baseado na qualidade."""
        if not self.adaptive_quality:
            return False
        
        # Qualidade excelente no nível crítico + pouco tempo restante
        if (level.priority == LandmarkPriority.CRITICAL and 
            level_result.quality_score > 0.92 and 
            remaining_time < 10.0):
            return True
        
        # Qualidade muito boa em qualquer nível + tempo muito limitado
        if level_result.quality_score > 0.95 and remaining_time < 5.0:
            return True
        
        return False
    
    def _adjust_remaining_budgets(self, start_level: int, available_time: float):
        """Ajusta budgets dos níveis restantes baseado no tempo disponível."""
        remaining_levels = self.processing_levels[start_level:]
        if not remaining_levels:
            return
        
        # Distribui tempo disponível proporcionalmente
        total_budget = sum(level.processing_budget for level in remaining_levels)
        if total_budget > 0:
            factor = available_time / total_budget
            for level in remaining_levels:
                level.processing_budget *= factor
    
    def _update_performance_cache_optimized(self, region: AnatomicalRegion, processing_time: float):
        """Atualização otimizada do cache de performance."""
        region_key = region.value
        if region_key not in self.region_performance_cache:
            self.region_performance_cache[region_key] = deque(maxlen=10)
        
        self.region_performance_cache[region_key].append(processing_time)
    
    def _calculate_performance_metrics_optimized(self, total_time: float, levels_completed: int, skipped_count: int) -> Dict[str, float]:
        """Cálculo otimizado de métricas de performance."""
        total_regions = sum(len(level.regions) for level in self.processing_levels)
        
        return {
            'fps_estimate': 1000.0 / max(total_time, 1.0),
            'efficiency_ratio': levels_completed / len(self.processing_levels),
            'skip_ratio': skipped_count / max(total_regions, 1),
            'time_utilization': min(total_time / self.max_processing_time, 1.0),
            'performance_score': self._calculate_performance_score_optimized(total_time, levels_completed),
            'optimization_efficiency': self.stats['optimization_hits'] / max(self.stats['total_frames'], 1)
        }
    
    def _calculate_performance_score_optimized(self, total_time: float, levels_completed: int) -> float:
        """Cálculo otimizado do score de performance."""
        # Score baseado em tempo, completude e otimizações
        time_score = max(0, 1.0 - (total_time / self.max_processing_time))
        completeness_score = levels_completed / len(self.processing_levels)
        optimization_bonus = min(0.1, self.stats['optimization_hits'] / max(self.stats['total_frames'], 1))
        
        return (time_score * 0.5 + completeness_score * 0.4 + optimization_bonus * 0.1)
    
    def _update_stats_optimized(self, levels_completed: int, skipped_count: int, processing_time: float):
        """Atualização otimizada de estatísticas."""
        self.stats['total_frames'] += 1
        
        # Média móvel exponencial - mais eficiente
        alpha = 0.1
        self.stats['levels_completed_avg'] = (
            alpha * levels_completed + (1 - alpha) * self.stats['levels_completed_avg']
        )
        
        self.stats['skipped_regions_count'] += skipped_count
        self.performance_history.append(processing_time)
    
    def _extract_level_landmarks(self, landmarks, level: ProcessingLevel) -> Optional[np.ndarray]:
        """Extrai landmarks específicos de um nível (método legado)."""
        return self._extract_level_landmarks_optimized(landmarks, level)
    
    def _integrate_level_results(self, base_landmarks, level_landmarks, level: ProcessingLevel) -> np.ndarray:
        """Integra resultados de um nível de volta aos landmarks base."""
        try:
            result_landmarks = base_landmarks.copy()
            
            if level_landmarks is None or not level.landmark_indices:
                return result_landmarks
            
            # Integra apenas os landmarks válidos
            valid_indices = [i for i in level.landmark_indices if i < len(result_landmarks)]
            
            for i, landmark_idx in enumerate(valid_indices):
                if i < len(level_landmarks):
                    result_landmarks[landmark_idx] = level_landmarks[i]
            
            return result_landmarks
        except Exception:
            return base_landmarks
    
    def _update_performance_cache(self, region: AnatomicalRegion, processing_time: float):
        """Atualiza cache de performance por região."""
        if region not in self.region_performance_cache:
            self.region_performance_cache[region] = []
        
        # Mantém histórico dos últimos 10 tempos
        self.region_performance_cache[region].append(processing_time)
        if len(self.region_performance_cache[region]) > 10:
            self.region_performance_cache[region].pop(0)
    
    def _calculate_performance_metrics(self, total_time: float, levels_completed: int, skipped_count: int) -> Dict[str, float]:
        """Calcula métricas de performance."""
        return {
            'fps_estimate': 1000.0 / max(total_time, 1.0),
            'efficiency_ratio': levels_completed / len(self.processing_levels),
            'skip_ratio': skipped_count / max(sum(len(level.regions) for level in self.processing_levels), 1),
            'time_utilization': min(total_time / self.max_processing_time, 1.0),
            'performance_score': self._calculate_performance_score(total_time, levels_completed)
        }
    
    def _calculate_performance_score(self, total_time: float, levels_completed: int) -> float:
        """Calcula score de performance geral."""
        # Score baseado em tempo e completude
        time_score = max(0, 1.0 - (total_time / self.max_processing_time))
        completeness_score = levels_completed / len(self.processing_levels)
        
        return (time_score * 0.6 + completeness_score * 0.4)
    
    def _update_stats(self, levels_completed: int, skipped_count: int, processing_time: float):
        """Atualiza estatísticas do processador."""
        self.stats['total_frames'] += 1
        
        # Média móvel
        alpha = 0.1
        self.stats['levels_completed_avg'] = (
            alpha * levels_completed + 
            (1 - alpha) * self.stats['levels_completed_avg']
        )
        
        self.stats['skipped_regions_count'] += skipped_count
        
        # Adiciona ao histórico de performance
        self.performance_history.append(processing_time)
        if len(self.performance_history) > 100:  # Mantém últimos 100 frames
            self.performance_history.pop(0)
    
    def get_adaptive_config(self) -> Dict[str, float]:
        """Retorna configurações adaptativas baseadas na performance."""
        if len(self.performance_history) < 10:
            return {}
        
        avg_time = np.mean(self.performance_history[-10:])
        
        # Adapta configurações baseado na performance recente
        adaptive_config = {}
        
        if avg_time > self.max_processing_time * 0.8:  # Muito lento
            adaptive_config.update({
                'kalman_process_noise': 0.008,  # Menos preciso, mais rápido
                'weighted_window_size': 5,      # Janela menor
                'enable_anatomical_validation': False  # Pula validação pesada
            })
            self.stats['performance_adaptations'] += 1
        
        elif avg_time < self.max_processing_time * 0.3:  # Muito rápido
            adaptive_config.update({
                'kalman_process_noise': 0.003,  # Mais preciso
                'weighted_window_size': 9,      # Janela maior
                'enable_anatomical_validation': True  # Ativa validação
            })
        
        return adaptive_config
    
    def get_performance_report(self) -> str:
        """Gera relatório de performance."""
        if not self.performance_history:
            return "Nenhum dado de performance disponível."
        
        avg_time = np.mean(self.performance_history)
        fps_estimate = 1000.0 / avg_time if avg_time > 0 else 0
        
        report = f"""
=== RELATÓRIO DE PERFORMANCE HIERÁRQUICA ===
Frames processados: {self.stats['total_frames']}
Tempo médio: {avg_time:.1f}ms
FPS estimado: {fps_estimate:.1f}

Níveis completados (média): {self.stats['levels_completed_avg']:.1f}/{len(self.processing_levels)}
Regiões puladas: {self.stats['skipped_regions_count']}
Adaptações de performance: {self.stats['performance_adaptations']}

Cache hits: {self.stats['cache_hits']}
Cache misses: {self.stats['cache_misses']}

Status: {'🟢 Excelente' if fps_estimate > 25 else 
         '🟡 Bom' if fps_estimate > 15 else 
         '🔴 Precisa otimizar'}
"""
        return report
    
    def reset(self):
        """Reseta o processador hierárquico."""
        self.performance_history.clear()
        self.region_performance_cache.clear()
        self.stats = {
            'total_frames': 0,
            'levels_completed_avg': 0.0,
            'skipped_regions_count': 0,
            'performance_adaptations': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }


# === FUNÇÃO DE CONVENIÊNCIA ===
def create_hierarchical_processor(config=None):
    """Cria uma instância do processador hierárquico."""
    return HierarchicalProcessor(config)


# === EXEMPLO DE USO ===
if __name__ == "__main__":
    # Teste básico do processador hierárquico
    processor = create_hierarchical_processor()
    
    # Simula landmarks
    test_landmarks = np.random.rand(33, 4)
    
    # Simula processador aprimorado (mock)
    class MockEnhancedProcessor:
        def process_landmarks(self, landmarks, timestamp=None):
            from enhanced_landmark_processor import ProcessingResult
            from anatomical_validator import ValidationResult
            return ProcessingResult(
                landmarks=landmarks,
                validation_result=ValidationResult(True, 0.8, []),
                interpolation_result=None,
                smoothing_applied=True,
                processing_time=0.01,
                quality_score=0.8,
                notes=["Mock processing"]
            )
    
    mock_processor = MockEnhancedProcessor()
    result = processor.process_landmarks_hierarchical(test_landmarks, mock_processor)
    
    print(f"Níveis completados: {result.processing_levels_completed}")
    print(f"Tempo total: {result.total_processing_time:.1f}ms")
    print(f"FPS estimado: {result.performance_metrics['fps_estimate']:.1f}")
    print(processor.get_performance_report())