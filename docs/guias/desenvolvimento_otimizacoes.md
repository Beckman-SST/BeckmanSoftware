# Guia de Desenvolvimento - Otimizações

## Visão Geral

Este guia fornece instruções detalhadas para desenvolvedores que desejam trabalhar com as otimizações implementadas no sistema BeckmanSoftware, incluindo como estender, modificar e manter o código otimizado.

## Estrutura do Código Otimizado

### Localização dos Arquivos

```
src/
├── core/
│   ├── intelligent_cache.py      # Sistema de cache inteligente
│   ├── hierarchical_processor.py # Processamento hierárquico
│   └── adaptive_kalman.py        # Filtro de Kalman adaptativo
├── optimization/
│   ├── __init__.py
│   ├── cache_strategies.py       # Estratégias de cache
│   ├── performance_monitor.py    # Monitoramento de performance
│   └── memory_optimizer.py       # Otimizações de memória
└── tests/
    ├── test_intelligent_cache.py
    ├── test_hierarchical_processor.py
    └── test_performance.py
```

## 1. Trabalhando com IntelligentCache

### Adicionando Nova Estratégia de Cache

#### Passo 1: Definir a Estratégia
```python
# Em cache_strategies.py
class CustomCacheStrategy(CacheStrategyInterface):
    def __init__(self, custom_param: float = 1.0):
        self.custom_param = custom_param
        self.custom_metrics = {}
    
    def should_evict(self, key: str, metadata: Dict) -> bool:
        """Implementa lógica customizada de evicção."""
        # Sua lógica aqui
        return False
    
    def select_victim(self, cache: Dict) -> str:
        """Seleciona item para remoção."""
        # Sua lógica de seleção
        return list(cache.keys())[0]
    
    def update_on_access(self, key: str, metadata: Dict) -> None:
        """Atualiza métricas no acesso."""
        # Atualiza suas métricas customizadas
        pass
```

#### Passo 2: Registrar no Enum
```python
# Em intelligent_cache.py
class CacheStrategy(Enum):
    LRU = "lru"
    LFU = "lfu"
    ADAPTIVE = "adaptive"
    TEMPORAL = "temporal"
    HYBRID = "hybrid"
    CUSTOM = "custom"  # Nova estratégia
```

#### Passo 3: Implementar na Factory
```python
# Em intelligent_cache.py
def _create_strategy_handler(self) -> None:
    """Cria handler para a estratégia selecionada."""
    if self.strategy == CacheStrategy.CUSTOM:
        self.strategy_handler = CustomCacheStrategy()
    # ... outras estratégias
```

### Exemplo de Uso
```python
# Criando cache com estratégia customizada
cache = IntelligentCache(
    max_size=500,
    strategy=CacheStrategy.CUSTOM,
    enable_compression=True,
    custom_param=2.5
)

# Usando o cache
cache.put("key1", data, metadata={"priority": "high"})
result = cache.get("key1")
```

### Debugging Cache
```python
# Obtendo métricas detalhadas
metrics = cache.get_performance_metrics()
print(f"Hit Rate: {metrics['hit_rate']:.2%}")
print(f"Memory Usage: {metrics['memory_usage_mb']:.1f} MB")

# Verificando estado interno
print(f"Cache Size: {len(cache.cache)}")
print(f"Strategy: {cache.strategy.value}")

# Forçando otimização
cache.optimize_cache()
```

## 2. Trabalhando com HierarchicalProcessor

### Adicionando Novo Nível de Processamento

#### Passo 1: Definir o Nível
```python
# Novo nível customizado
CUSTOM_LEVEL = ProcessingLevel(
    name="NÍVEL CUSTOM: Processamento Específico",
    priority="CUSTOM",
    regions=["CUSTOM_REGION"],
    landmark_indices=[100, 101, 102],  # Seus índices
    processing_budget=8.0,  # ms
    quality_threshold=0.7,
    can_skip=True,
    parallel_safe=True
)
```

#### Passo 2: Adicionar aos Níveis
```python
# Em hierarchical_processor.py
def __init__(self, custom_levels: List[ProcessingLevel] = None):
    self.processing_levels = PROCESSING_LEVELS.copy()
    
    # Adiciona níveis customizados
    if custom_levels:
        self.processing_levels.extend(custom_levels)
    
    # Ordena por prioridade
    self._sort_levels_by_priority()
```

#### Passo 3: Implementar Processamento Específico
```python
def _process_custom_level(self, landmarks: np.ndarray, 
                         level: ProcessingLevel) -> Dict:
    """Processamento específico para nível customizado."""
    if level.priority != "CUSTOM":
        return self._process_standard_level(landmarks, level)
    
    # Sua lógica de processamento customizada
    custom_result = {
        'landmarks': landmarks,
        'custom_metric': self._calculate_custom_metric(landmarks),
        'processing_time': time.time()
    }
    
    return custom_result
```

### Configuração Avançada
```python
# Configuração para diferentes cenários
realtime_config = {
    'max_processing_time': 16.67,  # 60 FPS
    'skip_low_priority_on_delay': True,
    'enable_parallel_processing': True,
    'cache_strategy': CacheStrategy.TEMPORAL
}

quality_config = {
    'max_processing_time': 100.0,  # Sem pressa
    'skip_low_priority_on_delay': False,
    'enable_parallel_processing': True,
    'cache_strategy': CacheStrategy.HYBRID
}

# Criando processador com configuração
processor = HierarchicalProcessor(**realtime_config)
```

### Monitoramento de Performance
```python
# Obtendo estatísticas detalhadas
stats = processor.get_processing_statistics()
print(f"Níveis Processados: {stats['levels_completed']}")
print(f"Tempo Total: {stats['total_processing_time']:.2f}ms")
print(f"Cache Hit Rate: {stats['cache_hit_rate']:.2%}")

# Monitoramento em tempo real
def monitor_processing():
    while True:
        stats = processor.get_processing_statistics()
        if stats['total_processing_time'] > 50.0:
            print("WARNING: Processamento lento detectado!")
        time.sleep(1.0)
```

## 3. Trabalhando com AdaptiveKalman

### Configuração Personalizada
```python
# Configuração para diferentes tipos de movimento
smooth_config = {
    'process_noise': 0.001,        # Movimento muito suave
    'measurement_noise': 0.05,     # Medições precisas
    'outlier_velocity_threshold': 20.0,
    'outlier_acceleration_threshold': 40.0
}

dynamic_config = {
    'process_noise': 0.01,         # Movimento dinâmico
    'measurement_noise': 0.15,     # Medições menos precisas
    'outlier_velocity_threshold': 50.0,
    'outlier_acceleration_threshold': 100.0
}

# Criando filtro personalizado
kalman = AdaptiveKalman(**smooth_config)
```

### Implementando Filtro Customizado
```python
class CustomKalmanFilter(AdaptiveKalman):
    def __init__(self, custom_param: float = 1.0):
        super().__init__()
        self.custom_param = custom_param
        self.custom_history = deque(maxlen=10)
    
    def filter_landmarks(self, landmarks: np.ndarray, 
                        quality_score: float = 1.0) -> np.ndarray:
        """Filtro customizado com lógica adicional."""
        # Aplica filtro base
        filtered = super().filter_landmarks(landmarks, quality_score)
        
        # Adiciona sua lógica customizada
        custom_filtered = self._apply_custom_logic(filtered)
        
        # Armazena no histórico customizado
        self.custom_history.append(custom_filtered)
        
        return custom_filtered
    
    def _apply_custom_logic(self, landmarks: np.ndarray) -> np.ndarray:
        """Sua lógica de filtro customizada."""
        # Implementa sua lógica aqui
        return landmarks * self.custom_param
```

## 4. Otimizações de Performance

### Profiling e Benchmarking

#### Usando cProfile
```python
import cProfile
import pstats

def profile_processing():
    """Profile do processamento completo."""
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Seu código de processamento
    processor = HierarchicalProcessor()
    result = processor.process_landmarks_hierarchical(landmarks, frame_info)
    
    profiler.disable()
    
    # Análise dos resultados
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 funções
```

#### Benchmarking Customizado
```python
import time
import numpy as np

def benchmark_cache_strategies():
    """Benchmark das estratégias de cache."""
    strategies = [CacheStrategy.LRU, CacheStrategy.LFU, 
                 CacheStrategy.ADAPTIVE, CacheStrategy.TEMPORAL]
    
    results = {}
    
    for strategy in strategies:
        cache = IntelligentCache(max_size=1000, strategy=strategy)
        
        # Simula carga de trabalho
        start_time = time.time()
        for i in range(10000):
            key = f"key_{i % 100}"  # 1% hit rate esperado
            data = np.random.random((68, 2))
            
            if i % 10 == 0:  # 10% puts, 90% gets
                cache.put(key, data)
            else:
                cache.get(key)
        
        end_time = time.time()
        metrics = cache.get_performance_metrics()
        
        results[strategy.value] = {
            'total_time': end_time - start_time,
            'hit_rate': metrics['hit_rate'],
            'memory_usage': metrics['memory_usage_mb']
        }
    
    return results
```

### Otimizações de Memória

#### Memory Profiling
```python
import tracemalloc
import psutil
import os

def monitor_memory_usage():
    """Monitora uso de memória em tempo real."""
    tracemalloc.start()
    process = psutil.Process(os.getpid())
    
    # Seu código aqui
    cache = IntelligentCache(max_size=5000)
    
    # Medição de memória
    current, peak = tracemalloc.get_traced_memory()
    memory_info = process.memory_info()
    
    print(f"Memória atual: {current / 1024 / 1024:.1f} MB")
    print(f"Pico de memória: {peak / 1024 / 1024:.1f} MB")
    print(f"RSS: {memory_info.rss / 1024 / 1024:.1f} MB")
    
    tracemalloc.stop()
```

#### Otimização de Arrays NumPy
```python
def optimize_numpy_operations():
    """Otimizações específicas para NumPy."""
    # Use dtype específico para economizar memória
    landmarks = np.array(data, dtype=np.float32)  # vs float64
    
    # Reutilize buffers quando possível
    if not hasattr(self, '_temp_buffer'):
        self._temp_buffer = np.empty_like(landmarks)
    
    np.copyto(self._temp_buffer, landmarks)
    
    # Use operações in-place
    landmarks *= 0.5  # vs landmarks = landmarks * 0.5
    
    # Evite cópias desnecessárias
    view = landmarks[10:20]  # vs copy = landmarks[10:20].copy()
```

## 5. Testes e Validação

### Testes Unitários
```python
import unittest
import numpy as np

class TestOptimizations(unittest.TestCase):
    def setUp(self):
        """Setup para cada teste."""
        self.cache = IntelligentCache(max_size=100)
        self.processor = HierarchicalProcessor()
        self.landmarks = np.random.random((68, 2))
    
    def test_cache_hit_rate(self):
        """Testa taxa de acerto do cache."""
        # Adiciona dados
        for i in range(50):
            self.cache.put(f"key_{i}", self.landmarks)
        
        # Testa acessos
        hits = 0
        for i in range(25):  # Acessa metade dos dados
            if self.cache.get(f"key_{i}") is not None:
                hits += 1
        
        hit_rate = hits / 25
        self.assertGreater(hit_rate, 0.8, "Hit rate deve ser > 80%")
    
    def test_processing_time(self):
        """Testa tempo de processamento."""
        start_time = time.time()
        
        result = self.processor.process_landmarks_hierarchical(
            self.landmarks, {'frame_id': 1}
        )
        
        end_time = time.time()
        processing_time = (end_time - start_time) * 1000  # ms
        
        self.assertLess(processing_time, 50.0, 
                       "Processamento deve ser < 50ms")
    
    def test_memory_efficiency(self):
        """Testa eficiência de memória."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Operações que devem ser eficientes
        for i in range(1000):
            self.cache.put(f"key_{i}", self.landmarks)
        
        final_memory = process.memory_info().rss
        memory_increase = (final_memory - initial_memory) / 1024 / 1024
        
        self.assertLess(memory_increase, 100.0, 
                       "Aumento de memória deve ser < 100MB")
```

### Testes de Integração
```python
def test_full_pipeline():
    """Testa pipeline completo otimizado."""
    # Setup
    cache = IntelligentCache(strategy=CacheStrategy.ADAPTIVE)
    processor = HierarchicalProcessor(cache_strategy=CacheStrategy.ADAPTIVE)
    kalman = AdaptiveKalman()
    
    # Simula processamento de vídeo
    total_time = 0
    cache_hits = 0
    
    for frame_id in range(100):
        landmarks = generate_test_landmarks(frame_id)
        
        start_time = time.time()
        
        # Processamento hierárquico
        result = processor.process_landmarks_hierarchical(
            landmarks, {'frame_id': frame_id}
        )
        
        # Suavização
        smoothed = kalman.filter_landmarks(
            result['processed_landmarks']
        )
        
        end_time = time.time()
        total_time += (end_time - start_time) * 1000
        
        # Verifica cache
        if result.get('cache_hit'):
            cache_hits += 1
    
    # Validações
    avg_time = total_time / 100
    hit_rate = cache_hits / 100
    
    assert avg_time < 30.0, f"Tempo médio muito alto: {avg_time:.2f}ms"
    assert hit_rate > 0.6, f"Hit rate muito baixo: {hit_rate:.2%}"
    
    print(f"Pipeline completo - Tempo médio: {avg_time:.2f}ms, Hit rate: {hit_rate:.2%}")
```

## 6. Debugging e Troubleshooting

### Logging Avançado
```python
import logging
import json

# Configuração de logging para otimizações
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('optimization.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('optimization')

class DebugCache(IntelligentCache):
    def get(self, key: str):
        result = super().get(key)
        logger.debug(f"Cache GET: {key} -> {'HIT' if result else 'MISS'}")
        return result
    
    def put(self, key: str, value: Any, metadata: Dict = None):
        super().put(key, value, metadata)
        logger.debug(f"Cache PUT: {key} (size: {len(self.cache)})")
```

### Ferramentas de Debug
```python
def debug_processing_levels():
    """Debug detalhado dos níveis de processamento."""
    processor = HierarchicalProcessor()
    
    for i, level in enumerate(processor.processing_levels):
        print(f"\nNível {i}: {level.name}")
        print(f"  Prioridade: {level.priority}")
        print(f"  Regiões: {level.regions}")
        print(f"  Landmarks: {level.landmark_indices}")
        print(f"  Budget: {level.processing_budget}ms")
        print(f"  Pode pular: {level.can_skip}")
        print(f"  Thread-safe: {level.parallel_safe}")

def debug_cache_state(cache: IntelligentCache):
    """Debug do estado interno do cache."""
    print(f"\n=== Estado do Cache ===")
    print(f"Estratégia: {cache.strategy.value}")
    print(f"Tamanho atual: {len(cache.cache)}")
    print(f"Tamanho máximo: {cache.max_size}")
    print(f"Compressão habilitada: {cache.enable_compression}")
    
    metrics = cache.get_performance_metrics()
    print(f"\n=== Métricas ===")
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"{key}: {value:.3f}")
        else:
            print(f"{key}: {value}")
```

## 7. Melhores Práticas

### Configuração para Produção
```python
# Configuração otimizada para produção
PRODUCTION_CONFIG = {
    'cache': {
        'max_size': 2000,
        'strategy': CacheStrategy.HYBRID,
        'enable_compression': True,
        'similarity_threshold': 0.90
    },
    'processor': {
        'max_processing_time': 33.33,  # 30 FPS
        'skip_low_priority_on_delay': True,
        'enable_parallel_processing': True
    },
    'kalman': {
        'process_noise': 0.005,
        'measurement_noise': 0.08,
        'outlier_velocity_threshold': 35.0
    }
}
```

### Monitoramento Contínuo
```python
class PerformanceMonitor:
    def __init__(self):
        self.metrics_history = deque(maxlen=1000)
        self.alerts = []
    
    def record_metrics(self, metrics: Dict):
        """Registra métricas com timestamp."""
        timestamped_metrics = {
            'timestamp': time.time(),
            **metrics
        }
        self.metrics_history.append(timestamped_metrics)
        self._check_alerts(metrics)
    
    def _check_alerts(self, metrics: Dict):
        """Verifica condições de alerta."""
        if metrics.get('processing_time', 0) > 50.0:
            self.alerts.append({
                'type': 'SLOW_PROCESSING',
                'message': f"Processamento lento: {metrics['processing_time']:.2f}ms",
                'timestamp': time.time()
            })
        
        if metrics.get('hit_rate', 1.0) < 0.5:
            self.alerts.append({
                'type': 'LOW_HIT_RATE',
                'message': f"Hit rate baixo: {metrics['hit_rate']:.2%}",
                'timestamp': time.time()
            })
```

### Otimização Contínua
```python
def auto_tune_parameters():
    """Auto-ajuste de parâmetros baseado em performance."""
    monitor = PerformanceMonitor()
    cache = IntelligentCache()
    
    # Coleta métricas por período
    for _ in range(100):
        # Simula operações
        metrics = cache.get_performance_metrics()
        monitor.record_metrics(metrics)
    
    # Analisa performance
    avg_hit_rate = np.mean([m['hit_rate'] for m in monitor.metrics_history])
    
    # Ajusta parâmetros automaticamente
    if avg_hit_rate < 0.7:
        cache.similarity_threshold *= 0.95  # Mais permissivo
        print("Ajustando threshold para melhorar hit rate")
    
    if avg_hit_rate > 0.95:
        cache.similarity_threshold *= 1.05  # Mais restritivo
        print("Ajustando threshold para economizar memória")
```

Este guia fornece uma base sólida para trabalhar com as otimizações implementadas. Lembre-se de sempre testar suas modificações e monitorar a performance em ambiente de produção.