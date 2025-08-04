# Arquitetura de Classes Otimizadas

## Visão Geral

Este documento detalha a arquitetura das classes otimizadas implementadas no sistema BeckmanSoftware, incluindo suas responsabilidades, relacionamentos e padrões de design utilizados.

## Diagrama de Classes

```
┌─────────────────────────────────────────────────────────────────┐
│                    Sistema BeckmanSoftware                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │ IntelligentCache│    │HierarchicalProc│    │AdaptiveKalman│ │
│  │                 │    │                 │    │              │ │
│  │ + get()         │◄───┤ + process()     │◄───┤ + filter()   │ │
│  │ + put()         │    │ + optimize()    │    │ + predict()  │ │
│  │ + optimize()    │    │ + cache_result()│    │ + update()   │ │
│  └─────────────────┘    └─────────────────┘    └──────────────┘ │
│           │                       │                       │     │
│           ▼                       ▼                       ▼     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │  CacheStrategy  │    │ ProcessingLevel │    │ FilterConfig │ │
│  │                 │    │                 │    │              │ │
│  │ + LRU           │    │ + CRITICAL      │    │ + noise      │ │
│  │ + LFU           │    │ + HIGH          │    │ + threshold  │ │
│  │ + ADAPTIVE      │    │ + MEDIUM        │    │ + weights    │ │
│  │ + TEMPORAL      │    │ + LOW           │    │              │ │
│  │ + HYBRID        │    │                 │    │              │ │
│  └─────────────────┘    └─────────────────┘    └──────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 1. IntelligentCache

### Responsabilidades
- **Cache Inteligente**: Armazenamento otimizado de landmarks processados
- **Estratégias Múltiplas**: Suporte a LRU, LFU, Adaptive, Temporal e Hybrid
- **Compressão**: Compressão automática de dados grandes
- **Thread Safety**: Operações thread-safe com RLock
- **Métricas**: Coleta de estatísticas de performance

### Estrutura da Classe

```python
class IntelligentCache:
    """Cache inteligente com múltiplas estratégias de otimização."""
    
    def __init__(self, 
                 max_size: int = 1000,
                 strategy: CacheStrategy = CacheStrategy.ADAPTIVE,
                 enable_compression: bool = True,
                 similarity_threshold: float = 0.95):
        # Inicialização otimizada
        
    # Métodos principais
    def get(self, key: str) -> Optional[Any]
    def put(self, key: str, value: Any, metadata: Dict = None) -> None
    def optimize_cache(self) -> None
    def get_performance_metrics(self) -> Dict[str, float]
    
    # Métodos otimizados
    def _compress_data_optimized(self, data: Any) -> bytes
    def _decompress_data_optimized(self, compressed_data: bytes) -> Any
    def _calculate_performance_metrics_optimized(self) -> Dict[str, float]
    def _remove_items_optimized(self, count: int) -> None
    def _record_access_pattern_optimized(self, key: str) -> None
    def _remove_from_indices_optimized(self, key: str) -> None
```

### Padrões de Design Utilizados

#### Strategy Pattern
```python
class CacheStrategy(Enum):
    LRU = "lru"           # Least Recently Used
    LFU = "lfu"           # Least Frequently Used
    ADAPTIVE = "adaptive"  # Adapta-se ao padrão de uso
    TEMPORAL = "temporal"  # Otimizado para sequências temporais
    HYBRID = "hybrid"      # Combina múltiplas estratégias
```

#### Observer Pattern
```python
def _record_access_pattern_optimized(self, key: str) -> None:
    """Registra padrões de acesso para otimização adaptativa."""
    self.access_patterns.append({
        'key': key,
        'timestamp': time.time(),
        'hit': True
    })
```

#### Template Method Pattern
```python
def get(self, key: str) -> Optional[Any]:
    """Template method para recuperação de dados."""
    # 1. Verificar cache
    # 2. Aplicar estratégia específica
    # 3. Registrar acesso
    # 4. Retornar resultado
```

### Otimizações Implementadas

#### Buffers Reutilizáveis
```python
def __init__(self):
    self._temp_buffer = None  # Buffer reutilizável
    self._compression_buffer = None
```

#### Índices Otimizados
```python
self.frequency_index = defaultdict(int)  # O(1) access
self.temporal_index = {}  # Timestamp mapping
self.access_patterns = deque(maxlen=200)  # Limited memory
```

#### Compressão Seletiva
```python
def _should_compress(self, data: Any) -> bool:
    """Comprime apenas dados que se beneficiam."""
    return (self.enable_compression and 
            self._estimate_size(data) > self.compression_threshold)
```

## 2. HierarchicalProcessor

### Responsabilidades
- **Processamento Hierárquico**: Processa landmarks por níveis de prioridade
- **Otimização de Tempo**: Gerencia budgets de tempo por nível
- **Cache Integrado**: Utiliza IntelligentCache para otimização
- **Skip Inteligente**: Pula níveis não-críticos quando necessário
- **Paralelização**: Suporte a processamento paralelo

### Estrutura da Classe

```python
class HierarchicalProcessor:
    """Processador hierárquico otimizado para landmarks."""
    
    def __init__(self,
                 max_processing_time: float = 50.0,
                 cache_strategy: CacheStrategy = CacheStrategy.ADAPTIVE,
                 skip_low_priority_on_delay: bool = True,
                 enable_parallel_processing: bool = True):
        # Inicialização com cache integrado
        
    # Métodos principais
    def process_landmarks_hierarchical(self, landmarks: np.ndarray, 
                                     frame_info: Dict) -> Dict
    def optimize_processing_levels(self) -> None
    def get_processing_statistics(self) -> Dict[str, Any]
    
    # Métodos otimizados
    def _extract_landmarks_optimized(self, landmarks: np.ndarray, 
                                   indices: List[int]) -> np.ndarray
    def _process_with_region_cache_optimized(self, level_landmarks: np.ndarray,
                                           level: ProcessingLevel) -> Dict
    def _integrate_results_optimized(self, results: List[Dict]) -> Dict
    def _update_performance_cache_optimized(self, level_idx: int, 
                                          processing_time: float) -> None
```

### Níveis de Processamento

#### ProcessingLevel Dataclass
```python
@dataclass
class ProcessingLevel:
    name: str
    priority: str
    regions: List[str]
    landmark_indices: List[int]
    processing_budget: float  # ms
    quality_threshold: float
    can_skip: bool
    parallel_safe: bool = True
```

#### Níveis Definidos
```python
PROCESSING_LEVELS = [
    ProcessingLevel(
        name="NÍVEL 1: CRÍTICO - Face e pose central",
        priority="CRITICAL",
        regions=["FACE", "POSE"],
        landmark_indices=list(range(17)) + [23, 24],
        processing_budget=15.0,
        quality_threshold=0.8,
        can_skip=False
    ),
    # ... outros níveis
]
```

### Algoritmos de Otimização

#### Skip Inteligente
```python
def _should_skip_level(self, level: ProcessingLevel, 
                      remaining_time: float) -> bool:
    """Determina se um nível deve ser pulado."""
    if not level.can_skip:
        return False
    
    if remaining_time < level.processing_budget:
        if self.skip_low_priority_on_delay:
            return True
    
    return False
```

#### Ajuste Dinâmico de Budget
```python
def _adjust_remaining_budgets(self, start_level: int, 
                            time_factor: float) -> None:
    """Ajusta budgets dos níveis restantes dinamicamente."""
    for i in range(start_level, len(self.processing_levels)):
        if self.processing_levels[i].can_skip:
            self.processing_levels[i].processing_budget *= time_factor
```

#### Cache por Região
```python
def _check_region_cache(self, cache_key: str) -> Optional[Dict]:
    """Verifica cache específico por região anatômica."""
    cached_result = self.cache.get(cache_key)
    if cached_result:
        self.stats['cache_hits'] += 1
        return cached_result
    return None
```

## 3. AdaptiveKalman

### Responsabilidades
- **Suavização Temporal**: Filtro de Kalman adaptativo para landmarks
- **Detecção de Outliers**: Identifica e corrige anomalias
- **Predição**: Prediz posições futuras baseado no histórico
- **Adaptação**: Ajusta parâmetros baseado na qualidade dos dados

### Estrutura da Classe

```python
class AdaptiveKalman:
    """Filtro de Kalman adaptativo para suavização de landmarks."""
    
    def __init__(self,
                 process_noise: float = 0.005,
                 measurement_noise: float = 0.08,
                 outlier_velocity_threshold: float = 35.0,
                 outlier_acceleration_threshold: float = 75.0):
        # Inicialização otimizada
        
    # Métodos principais
    def filter_landmarks(self, landmarks: np.ndarray, 
                        quality_score: float = 1.0) -> np.ndarray
    def predict_next_frame(self) -> Optional[np.ndarray]
    def reset_filter(self) -> None
    def get_filter_statistics(self) -> Dict[str, float]
    
    # Métodos otimizados
    def _detect_outliers_optimized(self, landmarks: np.ndarray) -> np.ndarray
    def _adaptive_noise_adjustment_optimized(self, quality_score: float) -> None
    def _weighted_average_optimized(self, landmarks: np.ndarray, 
                                  weights: np.ndarray) -> np.ndarray
```

### Algoritmos de Suavização

#### Detecção de Outliers
```python
def _detect_outliers_optimized(self, landmarks: np.ndarray) -> np.ndarray:
    """Detecta outliers baseado em velocidade e aceleração."""
    if len(self.history) < 2:
        return np.zeros(len(landmarks), dtype=bool)
    
    # Cálculo otimizado de velocidade
    velocity = np.linalg.norm(landmarks - self.history[-1], axis=1)
    velocity_outliers = velocity > self.outlier_velocity_threshold
    
    # Cálculo otimizado de aceleração
    if len(self.history) >= 3:
        prev_velocity = np.linalg.norm(self.history[-1] - self.history[-2], axis=1)
        acceleration = np.abs(velocity - prev_velocity)
        acceleration_outliers = acceleration > self.outlier_acceleration_threshold
        return velocity_outliers | acceleration_outliers
    
    return velocity_outliers
```

#### Ajuste Adaptativo de Ruído
```python
def _adaptive_noise_adjustment_optimized(self, quality_score: float) -> None:
    """Ajusta ruído baseado na qualidade dos dados."""
    # Ajuste conservador baseado na qualidade
    noise_factor = 1.0 + (1.0 - quality_score) * 0.5
    self.current_process_noise = self.base_process_noise * noise_factor
    self.current_measurement_noise = self.base_measurement_noise * noise_factor
```

#### Média Móvel Ponderada
```python
def _weighted_average_optimized(self, landmarks: np.ndarray, 
                              weights: np.ndarray) -> np.ndarray:
    """Calcula média ponderada otimizada."""
    if len(self.history) == 0:
        return landmarks
    
    # Pesos adaptativos baseados na qualidade
    total_weight = np.sum(weights)
    if total_weight > 0:
        weights = weights / total_weight
        
    # Média ponderada com histórico
    weighted_sum = landmarks * weights[-1]
    for i, hist_landmarks in enumerate(self.history[-len(weights)+1:]):
        weighted_sum += hist_landmarks * weights[i]
    
    return weighted_sum
```

## 4. Relacionamentos entre Classes

### Composição
```python
class HierarchicalProcessor:
    def __init__(self):
        # Composição: HierarchicalProcessor HAS-A IntelligentCache
        self.cache = IntelligentCache(
            max_size=self.cache_size,
            strategy=cache_strategy,
            enable_compression=True
        )
        
        # Composição: HierarchicalProcessor HAS-A AdaptiveKalman
        self.kalman_filter = AdaptiveKalman(
            process_noise=0.005,
            measurement_noise=0.08
        )
```

### Agregação
```python
class LandmarkProcessor:
    def __init__(self):
        # Agregação: LandmarkProcessor USES-A HierarchicalProcessor
        self.hierarchical_processor = HierarchicalProcessor()
        
        # Agregação: LandmarkProcessor USES-A IntelligentCache
        self.shared_cache = IntelligentCache()
```

### Dependência
```python
# IntelligentCache depende de CacheStrategy
def __init__(self, strategy: CacheStrategy):
    self.strategy = strategy

# HierarchicalProcessor depende de ProcessingLevel
def process_landmarks_hierarchical(self, landmarks: np.ndarray):
    for level in self.processing_levels:
        # Processa cada nível
```

## 5. Padrões de Design Aplicados

### Factory Pattern
```python
class CacheFactory:
    @staticmethod
    def create_cache(strategy: CacheStrategy, **kwargs) -> IntelligentCache:
        """Factory para criar cache com estratégia específica."""
        return IntelligentCache(strategy=strategy, **kwargs)
```

### Singleton Pattern (para configurações)
```python
class OptimizationConfig:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

### Command Pattern (para operações de cache)
```python
class CacheCommand:
    def execute(self): pass
    def undo(self): pass

class PutCommand(CacheCommand):
    def __init__(self, cache, key, value):
        self.cache = cache
        self.key = key
        self.value = value
    
    def execute(self):
        self.cache.put(self.key, self.value)
```

### Decorator Pattern (para métricas)
```python
def performance_monitor(func):
    """Decorator para monitorar performance de métodos."""
    def wrapper(self, *args, **kwargs):
        start_time = time.time()
        result = func(self, *args, **kwargs)
        end_time = time.time()
        
        self.performance_metrics[func.__name__] = end_time - start_time
        return result
    return wrapper
```

## 6. Extensibilidade

### Interface para Novas Estratégias
```python
class CacheStrategyInterface:
    def should_evict(self, key: str, metadata: Dict) -> bool:
        raise NotImplementedError
    
    def select_victim(self, cache: Dict) -> str:
        raise NotImplementedError
    
    def update_on_access(self, key: str, metadata: Dict) -> None:
        raise NotImplementedError
```

### Plugin System para Processamento
```python
class ProcessingPlugin:
    def process_level(self, landmarks: np.ndarray, 
                     level: ProcessingLevel) -> Dict:
        raise NotImplementedError
    
    def get_plugin_info(self) -> Dict:
        raise NotImplementedError
```

### Configuração Dinâmica
```python
class DynamicConfig:
    def __init__(self):
        self.config = {}
        self.observers = []
    
    def update_config(self, key: str, value: Any) -> None:
        self.config[key] = value
        self._notify_observers(key, value)
    
    def _notify_observers(self, key: str, value: Any) -> None:
        for observer in self.observers:
            observer.on_config_change(key, value)
```

## 7. Testes e Validação

### Testes Unitários
```python
class TestIntelligentCache(unittest.TestCase):
    def test_cache_strategies(self):
        # Testa todas as estratégias de cache
        
    def test_compression_optimization(self):
        # Testa compressão seletiva
        
    def test_thread_safety(self):
        # Testa operações concorrentes
```

### Testes de Performance
```python
class TestPerformanceOptimizations(unittest.TestCase):
    def test_processing_time_improvement(self):
        # Valida ganhos de tempo
        
    def test_memory_usage_optimization(self):
        # Valida redução de memória
        
    def test_cache_hit_rate(self):
        # Valida eficiência do cache
```

### Benchmarks
```python
def benchmark_cache_strategies():
    """Compara performance das estratégias de cache."""
    strategies = [CacheStrategy.LRU, CacheStrategy.LFU, 
                 CacheStrategy.ADAPTIVE, CacheStrategy.TEMPORAL]
    
    for strategy in strategies:
        cache = IntelligentCache(strategy=strategy)
        # Executa benchmark e coleta métricas
```

Esta arquitetura de classes otimizadas fornece uma base sólida e extensível para o sistema BeckmanSoftware, com foco em performance, maintibilidade e escalabilidade.