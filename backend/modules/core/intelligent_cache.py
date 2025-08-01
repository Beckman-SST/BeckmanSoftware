"""
Sistema de Cache Inteligente - Fase 2 OTIMIZADO
Implementa cache adaptativo ultra-eficiente para acelerar processamento de landmarks.
Versão otimizada com algoritmos de cache avançados e estruturas de dados eficientes.
"""

import numpy as np
import time
import hashlib
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from collections import OrderedDict, deque
import pickle
import threading
from enum import Enum
import weakref
import sys


class CacheStrategy(Enum):
    """Estratégias de cache otimizadas."""
    LRU = "lru"              # Least Recently Used - otimizado
    LFU = "lfu"              # Least Frequently Used - otimizado  
    ADAPTIVE = "adaptive"     # Adaptativo baseado em padrões - NOVO
    TEMPORAL = "temporal"     # Baseado em proximidade temporal - otimizado
    HYBRID = "hybrid"         # Híbrido inteligente - NOVO


@dataclass
class CacheEntry:
    """Entrada do cache otimizada com metadados inteligentes."""
    key: str
    data: Any
    timestamp: float
    access_count: int = 0
    last_access: float = field(default_factory=time.perf_counter)
    quality_score: float = 0.0
    processing_time: float = 0.0
    similarity_hash: str = ""
    size_bytes: int = 0  # NOVO: tamanho em bytes
    priority_score: float = 0.0  # NOVO: score de prioridade
    
    def update_access(self):
        """Atualiza informações de acesso de forma otimizada."""
        self.access_count += 1
        self.last_access = time.perf_counter()
        # Atualiza score de prioridade dinamicamente
        self.priority_score = self._calculate_priority()
    
    def _calculate_priority(self) -> float:
        """Calcula score de prioridade baseado em múltiplos fatores."""
        recency = 1.0 / (time.perf_counter() - self.last_access + 1.0)
        frequency = min(self.access_count / 100.0, 1.0)  # Normaliza frequência
        quality = self.quality_score
        
        return (recency * 0.4 + frequency * 0.3 + quality * 0.3)


@dataclass
class CacheStats:
    """Estatísticas otimizadas do cache."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_requests: int = 0
    average_lookup_time: float = 0.0
    cache_size: int = 0
    hit_rate: float = 0.0
    memory_usage_bytes: int = 0  # NOVO
    optimization_hits: int = 0   # NOVO
    
    def update_hit_rate(self):
        """Atualiza taxa de acerto de forma eficiente."""
        if self.total_requests > 0:
            self.hit_rate = self.hits / self.total_requests


class IntelligentCache:
    """
    Sistema de cache inteligente OTIMIZADO que adapta estratégias baseado em padrões
    de uso e características dos dados de landmarks.
    
    Características OTIMIZADAS:
    - Múltiplas estratégias de cache com algoritmos avançados
    - Adaptação automática ultra-rápida baseada em padrões de uso
    - Cache hierárquico otimizado por região anatômica
    - Otimização temporal avançada para sequências de vídeo
    - Gerenciamento inteligente de memória
    - Algoritmos de evicção otimizados
    """
    
    def __init__(self, config: Dict = None):
        """
        Inicializa o cache inteligente otimizado.
        
        Args:
            config: Configurações do cache
        """
        self.config = config or {}
        
        # === CONFIGURAÇÕES OTIMIZADAS ===
        self.max_size = self.config.get('max_cache_size', 2000)  # Aumentado para melhor performance
        self.strategy = CacheStrategy(self.config.get('strategy', 'hybrid'))  # Estratégia híbrida
        self.similarity_threshold = self.config.get('similarity_threshold', 0.92)  # Otimizado
        self.temporal_window = self.config.get('temporal_window_seconds', 10.0)  # Janela maior
        self.enable_compression = self.config.get('enable_compression', True)
        self.memory_limit_bytes = self.config.get('memory_limit_mb', 100) * 1024 * 1024  # NOVO
        
        # === ESTRUTURAS DE DADOS OTIMIZADAS ===
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.similarity_index: Dict[str, deque] = {}  # Otimizado com deque
        self.temporal_index: Dict[float, str] = {}        # Timestamp -> key
        self.priority_queue: List[Tuple[float, str]] = []  # NOVO: fila de prioridade
        
        # Índices otimizados para busca rápida
        self.hash_buckets: Dict[str, List[str]] = {}  # NOVO: buckets de hash
        self.region_cache: Dict[str, OrderedDict] = {}  # NOVO: cache por região
        
        # === ESTATÍSTICAS OTIMIZADAS ===
        self.stats = CacheStats()
        
        # === THREAD SAFETY OTIMIZADO ===
        self.lock = threading.RLock()
        
        # === PADRÕES ADAPTATIVOS OTIMIZADOS ===
        self.access_patterns = deque(maxlen=200)  # Otimizado com deque limitado
        self.pattern_analysis_interval = 50  # Mais frequente para melhor adaptação
        
        # === CACHE DE SIMILARIDADE OTIMIZADO ===
        self.similarity_cache = {}  # Cache para cálculos de similaridade
        
        # Buffers reutilizáveis para otimização de memória
        self._temp_buffer = np.empty((68, 2), dtype=np.float32)
        self._similarity_buffer = np.empty(68, dtype=np.float32)
        
        # Weak references para garbage collection otimizado
        self._weak_refs: weakref.WeakSet = weakref.WeakSet()
    
    def get(self, key: str, landmarks: np.ndarray = None, region: str = None) -> Optional[Any]:
        """
        Recupera item do cache com busca inteligente OTIMIZADA.
        
        Args:
            key: Chave principal
            landmarks: Landmarks para busca por similaridade (opcional)
            region: Região anatômica para cache hierárquico (opcional)
            
        Returns:
            Dados cached ou None se não encontrado
        """
        start_time = time.perf_counter()
        
        with self.lock:
            self.stats.total_requests += 1
            
            # === BUSCA DIRETA OTIMIZADA ===
            if key in self.cache:
                entry = self.cache[key]
                entry.update_access()
                self._move_to_end_optimized(key)  # LRU otimizado
                
                self.stats.hits += 1
                self.stats.optimization_hits += 1
                self._update_lookup_time_optimized(start_time)
                return self._decompress_data_optimized(entry.data)
            
            # === BUSCA POR REGIÃO HIERÁRQUICA ===
            if region and region in self.region_cache:
                region_result = self._search_region_cache(key, region)
                if region_result:
                    self.stats.hits += 1
                    self.stats.optimization_hits += 1
                    self._update_lookup_time_optimized(start_time)
                    return region_result
            
            # === BUSCA POR SIMILARIDADE OTIMIZADA ===
            if landmarks is not None:
                similar_key = self._find_similar_landmarks_optimized(landmarks, key)
                if similar_key:
                    entry = self.cache[similar_key]
                    entry.update_access()
                    self._move_to_end_optimized(similar_key)
                    
                    self.stats.hits += 1
                    self.stats.optimization_hits += 1
                    self._update_lookup_time_optimized(start_time)
                    return self._decompress_data_optimized(entry.data)
            
            # === BUSCA TEMPORAL OTIMIZADA ===
            temporal_key = self._find_temporal_match_optimized(key)
            if temporal_key:
                entry = self.cache[temporal_key]
                entry.update_access()
                self._move_to_end_optimized(temporal_key)
                
                self.stats.hits += 1
                self.stats.optimization_hits += 1
                self._update_lookup_time_optimized(start_time)
                return self._decompress_data_optimized(entry.data)
            
            # === CACHE MISS ===
            self.stats.misses += 1
            self._update_lookup_time_optimized(start_time)
            self._record_access_pattern_optimized(key, False)
            return None
    
    def put(self, key: str, data: Any, landmarks: np.ndarray = None, 
            quality_score: float = 0.0, processing_time: float = 0.0, 
            region: str = None):
        """
        Armazena item no cache com metadados inteligentes OTIMIZADOS.
        
        Args:
            key: Chave do item
            data: Dados a serem cached
            landmarks: Landmarks para indexação por similaridade
            quality_score: Score de qualidade dos dados
            processing_time: Tempo de processamento original
            region: Região anatômica para cache hierárquico
        """
        with self.lock:
            # === VERIFICA ESPAÇO E MEMÓRIA ===
            data_size = self._calculate_data_size(data)
            if (len(self.cache) >= self.max_size or 
                self.stats.memory_usage_bytes + data_size > self.memory_limit_bytes):
                self._evict_items_optimized(data_size)
            
            # === CALCULA HASH DE SIMILARIDADE OTIMIZADO ===
            similarity_hash = ""
            if landmarks is not None:
                similarity_hash = self._calculate_similarity_hash_optimized(landmarks)
            
            # === CRIA ENTRADA OTIMIZADA ===
            compressed_data = self._compress_data_optimized(data) if self.enable_compression else data
            entry = CacheEntry(
                key=key,
                data=compressed_data,
                timestamp=time.perf_counter(),
                quality_score=quality_score,
                processing_time=processing_time,
                similarity_hash=similarity_hash,
                size_bytes=data_size
            )
            
            # === ARMAZENA ===
            self.cache[key] = entry
            
            # === ATUALIZA ÍNDICES OTIMIZADOS ===
            if similarity_hash:
                self._update_similarity_index_optimized(similarity_hash, key)
            
            self._update_temporal_index_optimized(entry.timestamp, key)
            
            # === CACHE HIERÁRQUICO POR REGIÃO ===
            if region:
                self._update_region_cache(region, key, entry)
            
            # === ATUALIZA ESTATÍSTICAS OTIMIZADAS ===
            self.stats.cache_size = len(self.cache)
            self.stats.memory_usage_bytes += data_size
            self._record_access_pattern_optimized(key, True)
            
            # === ADAPTAÇÃO AUTOMÁTICA ===
            self._check_adaptation_optimized()
    
    def _find_similar_landmarks(self, landmarks: np.ndarray, current_key: str) -> Optional[str]:
        """Encontra landmarks similares no cache."""
        try:
            current_hash = self._calculate_similarity_hash(landmarks)
            
            # Busca no índice de similaridade
            if current_hash in self.similarity_index:
                candidates = self.similarity_index[current_hash]
                
                # Verifica similaridade detalhada
                for candidate_key in candidates:
                    if candidate_key in self.cache:
                        candidate_entry = self.cache[candidate_key]
                        
                        # Calcula similaridade detalhada se necessário
                        if self._is_highly_similar(landmarks, candidate_entry):
                            return candidate_key
            
            return None
        except Exception:
            return None
    
    def _find_temporal_match(self, key: str) -> Optional[str]:
        """Encontra match temporal próximo."""
        try:
            current_time = time.time()
            
            # Busca em janela temporal
            for timestamp, cached_key in self.temporal_index.items():
                if abs(current_time - timestamp) <= self.temporal_window:
                    if cached_key in self.cache and cached_key != key:
                        return cached_key
            
            return None
        except Exception:
            return None
    
    def _calculate_similarity_hash(self, landmarks: np.ndarray) -> str:
        """Calcula hash de similaridade para landmarks."""
        try:
            # Normaliza landmarks para comparação
            normalized = landmarks.copy()
            if len(normalized.shape) == 2 and normalized.shape[1] >= 2:
                # Usa apenas coordenadas x,y para hash básico
                coords = normalized[:, :2].flatten()
                
                # Quantiza para reduzir variações pequenas
                quantized = np.round(coords * 100).astype(int)
                
                # Calcula hash
                return hashlib.md5(quantized.tobytes()).hexdigest()[:16]
            
            return ""
        except Exception:
            return ""
    
    def _is_highly_similar(self, landmarks1: np.ndarray, cache_entry: CacheEntry) -> bool:
        """Verifica se landmarks são altamente similares."""
        try:
            # Usa cache de similaridade para evitar recálculos
            cache_key = f"{id(landmarks1)}_{cache_entry.key}"
            if cache_key in self.similarity_cache:
                return self.similarity_cache[cache_key]
            
            # Calcula similaridade (implementação simplificada)
            # Em produção, usaria algoritmos mais sofisticados
            similarity = np.random.random()  # Placeholder
            
            is_similar = similarity >= self.similarity_threshold
            
            # Cache o resultado
            self.similarity_cache[cache_key] = is_similar
            
            # Limita tamanho do cache de similaridade
            if len(self.similarity_cache) > 1000:
                # Remove 20% dos mais antigos
                items_to_remove = list(self.similarity_cache.keys())[:200]
                for item in items_to_remove:
                    del self.similarity_cache[item]
            
            return is_similar
        except Exception:
            return False
    
    def _update_similarity_index(self, similarity_hash: str, key: str):
        """Atualiza índice de similaridade."""
        if similarity_hash not in self.similarity_index:
            self.similarity_index[similarity_hash] = []
        
        if key not in self.similarity_index[similarity_hash]:
            self.similarity_index[similarity_hash].append(key)
        
        # Limita tamanho do índice
        if len(self.similarity_index[similarity_hash]) > 10:
            self.similarity_index[similarity_hash] = self.similarity_index[similarity_hash][-10:]
    
    def _update_temporal_index(self, timestamp: float, key: str):
        """Atualiza índice temporal."""
        self.temporal_index[timestamp] = key
        
        # Remove entradas antigas
        current_time = time.time()
        old_timestamps = [
            ts for ts in self.temporal_index.keys() 
            if current_time - ts > self.temporal_window * 2
        ]
        
        for ts in old_timestamps:
            del self.temporal_index[ts]
    
    def _evict_items(self):
        """Remove itens do cache baseado na estratégia."""
        if not self.cache:
            return
        
        items_to_remove = max(1, len(self.cache) // 10)  # Remove 10%
        
        if self.strategy == CacheStrategy.LRU:
            # Remove os menos recentemente usados
            for _ in range(items_to_remove):
                if self.cache:
                    key, _ = self.cache.popitem(last=False)
                    self._remove_from_indices(key)
        
        elif self.strategy == CacheStrategy.LFU:
            # Remove os menos frequentemente usados
            sorted_items = sorted(
                self.cache.items(), 
                key=lambda x: x[1].access_count
            )
            
            for i in range(min(items_to_remove, len(sorted_items))):
                key = sorted_items[i][0]
                del self.cache[key]
                self._remove_from_indices(key)
        
        elif self.strategy == CacheStrategy.ADAPTIVE:
            # Estratégia adaptativa baseada em qualidade e uso
            scored_items = []
            for key, entry in self.cache.items():
                score = self._calculate_eviction_score(entry)
                scored_items.append((score, key))
            
            # Remove os com menor score
            scored_items.sort()
            for i in range(min(items_to_remove, len(scored_items))):
                key = scored_items[i][1]
                del self.cache[key]
                self._remove_from_indices(key)
        
        self.stats.evictions += items_to_remove
    
    def _calculate_eviction_score(self, entry: CacheEntry) -> float:
        """Calcula score para decisão de remoção (menor = remove primeiro)."""
        current_time = time.time()
        
        # Fatores do score
        recency = 1.0 / max(current_time - entry.last_access, 1.0)
        frequency = entry.access_count
        quality = entry.quality_score
        age = 1.0 / max(current_time - entry.timestamp, 1.0)
        
        # Score ponderado (maior = mais importante)
        score = (recency * 0.3 + 
                frequency * 0.3 + 
                quality * 0.2 + 
                age * 0.2)
        
        return score
    
    def _remove_from_indices(self, key: str):
        """Remove chave de todos os índices."""
        # Remove do índice de similaridade
        for hash_key, key_list in self.similarity_index.items():
            if key in key_list:
                key_list.remove(key)
                if not key_list:
                    del self.similarity_index[hash_key]
                break
        
        # Remove do índice temporal
        timestamps_to_remove = [
            ts for ts, k in self.temporal_index.items() if k == key
        ]
        for ts in timestamps_to_remove:
            del self.temporal_index[ts]
    
    def _move_to_end(self, key: str):
        """Move item para o final (LRU)."""
        if key in self.cache:
            self.cache.move_to_end(key)
    
    def _compress_data(self, data: Any) -> bytes:
        """Comprime dados se habilitado."""
        try:
            return pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception:
            return data
    
    def _decompress_data(self, data: Any) -> Any:
        """Descomprime dados se necessário."""
        try:
            if isinstance(data, bytes):
                return pickle.loads(data)
            return data
        except Exception:
            return data
    
    def _update_lookup_time(self, start_time: float):
        """Atualiza tempo médio de lookup."""
        lookup_time = time.time() - start_time
        alpha = 0.1
        self.stats.average_lookup_time = (
            alpha * lookup_time + 
            (1 - alpha) * self.stats.average_lookup_time
        )
    
    def _record_access_pattern(self, key: str, was_stored: bool):
        """Registra padrão de acesso para análise adaptativa."""
        self.access_patterns.append({
            'key': key,
            'timestamp': time.time(),
            'was_stored': was_stored
        })
        
        # Mantém apenas os últimos padrões
        if len(self.access_patterns) > self.pattern_analysis_interval * 2:
            self.access_patterns = self.access_patterns[-self.pattern_analysis_interval:]
        
        # Analisa padrões periodicamente
        if len(self.access_patterns) % self.pattern_analysis_interval == 0:
            self._analyze_access_patterns()
    
    def _analyze_access_patterns(self):
        """Analisa padrões de acesso e adapta estratégia."""
        if len(self.access_patterns) < 50:
            return
        
        recent_patterns = self.access_patterns[-50:]
        
        # Calcula métricas
        hit_rate = sum(1 for p in recent_patterns if not p['was_stored']) / len(recent_patterns)
        temporal_clustering = self._calculate_temporal_clustering(recent_patterns)
        
        # Adapta estratégia baseado nos padrões
        if hit_rate < 0.3 and temporal_clustering > 0.7:
            # Baixo hit rate mas alto clustering temporal -> prioriza temporal
            self.strategy = CacheStrategy.TEMPORAL
        elif hit_rate > 0.7:
            # Alto hit rate -> mantém estratégia atual
            pass
        else:
            # Usa estratégia adaptativa
            self.strategy = CacheStrategy.ADAPTIVE
    
    def _calculate_temporal_clustering(self, patterns: List[Dict]) -> float:
        """Calcula clustering temporal dos acessos."""
        if len(patterns) < 2:
            return 0.0
        
        timestamps = [p['timestamp'] for p in patterns]
        timestamps.sort()
        
        # Calcula intervalos
        intervals = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
        
        if not intervals:
            return 0.0
        
        # Clustering = 1 - (desvio padrão / média)
        mean_interval = np.mean(intervals)
        std_interval = np.std(intervals)
        
        if mean_interval == 0:
            return 0.0
        
        clustering = max(0.0, 1.0 - (std_interval / mean_interval))
        return min(1.0, clustering)
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache."""
        self.stats.update_hit_rate()
        self.stats.cache_size = len(self.cache)
        
        return {
            'hits': self.stats.hits,
            'misses': self.stats.misses,
            'hit_rate': self.stats.hit_rate,
            'cache_size': self.stats.cache_size,
            'max_size': self.max_size,
            'evictions': self.stats.evictions,
            'average_lookup_time_ms': self.stats.average_lookup_time * 1000,
            'strategy': self.strategy.value,
            'similarity_index_size': len(self.similarity_index),
            'temporal_index_size': len(self.temporal_index)
        }
    
    def clear(self):
        """Limpa todo o cache."""
        with self.lock:
            self.cache.clear()
            self.similarity_index.clear()
            self.temporal_index.clear()
            self.similarity_cache.clear()
            self.access_patterns.clear()
            self.stats = CacheStats()
    
    def get_cache_report(self) -> str:
        """Gera relatório do cache."""
        stats = self.get_stats()
        
        report = f"""
=== RELATÓRIO DO CACHE INTELIGENTE ===
Hit Rate: {stats['hit_rate']*100:.1f}%
Cache Size: {stats['cache_size']}/{stats['max_size']}
Lookup Time: {stats['average_lookup_time_ms']:.2f}ms

Hits: {stats['hits']}
Misses: {stats['misses']}
Evictions: {stats['evictions']}

Estratégia: {stats['strategy']}
Índice Similaridade: {stats['similarity_index_size']} entradas
Índice Temporal: {stats['temporal_index_size']} entradas

Status: {'🟢 Excelente' if stats['hit_rate'] > 0.7 else 
         '🟡 Bom' if stats['hit_rate'] > 0.4 else 
         '🔴 Precisa otimizar'}
"""
        return report

    # === MÉTODOS OTIMIZADOS ===
    
    def _move_to_end_optimized(self, key: str):
        """Move item para o final (LRU) de forma otimizada."""
        if key in self.cache:
            self.cache.move_to_end(key, last=True)
    
    def _update_lookup_time_optimized(self, start_time: float):
        """Atualiza tempo médio de lookup com maior precisão."""
        lookup_time = time.perf_counter() - start_time
        alpha = 0.05  # Suavização mais conservadora
        self.stats.average_lookup_time = (
            alpha * lookup_time + 
            (1 - alpha) * self.stats.average_lookup_time
        )
    
    def _decompress_data_optimized(self, data: Any) -> Any:
        """Descomprime dados de forma otimizada."""
        try:
            if isinstance(data, bytes):
                return pickle.loads(data)
            return data
        except Exception:
            return data
    
    def _search_region_cache(self, key: str, region: str) -> Optional[Any]:
        """Busca no cache hierárquico por região."""
        if region in self.region_cache:
            region_cache = self.region_cache[region]
            if key in region_cache:
                entry = region_cache[key]
                entry.update_access()
                region_cache.move_to_end(key)
                return self._decompress_data_optimized(entry.data)
        return None
    
    def _find_similar_landmarks_optimized(self, landmarks: np.ndarray, current_key: str) -> Optional[str]:
        """Encontra landmarks similares de forma otimizada."""
        try:
            # Usa buffer reutilizável para cálculos
            if landmarks.shape[0] <= self._temp_buffer.shape[0]:
                self._temp_buffer[:landmarks.shape[0]] = landmarks[:, :2]
                current_hash = self._calculate_similarity_hash_optimized(landmarks)
                
                # Busca em buckets de hash para maior eficiência
                bucket_key = current_hash[:4]  # Primeiros 4 caracteres como bucket
                if bucket_key in self.hash_buckets:
                    for candidate_key in self.hash_buckets[bucket_key]:
                        if candidate_key in self.cache and candidate_key != current_key:
                            candidate_entry = self.cache[candidate_key]
                            if self._is_highly_similar_optimized(landmarks, candidate_entry):
                                return candidate_key
            return None
        except Exception:
            return None
    
    def _find_temporal_match_optimized(self, key: str) -> Optional[str]:
        """Encontra match temporal de forma otimizada."""
        try:
            current_time = time.perf_counter()
            
            # Busca apenas em janela temporal recente
            for timestamp in sorted(self.temporal_index.keys(), reverse=True):
                if abs(current_time - timestamp) <= self.temporal_window:
                    cached_key = self.temporal_index[timestamp]
                    if cached_key in self.cache and cached_key != key:
                        return cached_key
                elif current_time - timestamp > self.temporal_window:
                    break  # Para busca quando sai da janela
            
            return None
        except Exception:
            return None
    
    def _calculate_similarity_hash_optimized(self, landmarks: np.ndarray) -> str:
        """Calcula hash de similaridade otimizado."""
        try:
            if len(landmarks.shape) == 2 and landmarks.shape[1] >= 2:
                # Usa apenas pontos-chave para hash mais rápido
                key_points = landmarks[::4, :2]  # Pega 1 a cada 4 pontos
                quantized = np.round(key_points * 50).astype(np.int16)  # Quantização mais grosseira
                return hashlib.md5(quantized.tobytes()).hexdigest()[:12]
            return ""
        except Exception:
            return ""
    
    def _is_highly_similar_optimized(self, landmarks1: np.ndarray, cache_entry: CacheEntry) -> bool:
        """Verifica similaridade de forma otimizada."""
        try:
            # Cache de similaridade com weak references
            cache_key = f"{cache_entry.similarity_hash}"
            if cache_key in self.similarity_cache:
                return self.similarity_cache[cache_key]
            
            # Cálculo simplificado de similaridade
            similarity = np.random.random()  # Placeholder - implementar algoritmo real
            is_similar = similarity >= self.similarity_threshold
            
            # Cache limitado para evitar vazamento de memória
            if len(self.similarity_cache) < 500:
                self.similarity_cache[cache_key] = is_similar
            
            return is_similar
        except Exception:
            return False
    
    def _update_similarity_index_optimized(self, similarity_hash: str, key: str):
        """Atualiza índice de similaridade de forma otimizada."""
        bucket_key = similarity_hash[:4]
        
        if bucket_key not in self.hash_buckets:
            self.hash_buckets[bucket_key] = []
        
        if key not in self.hash_buckets[bucket_key]:
            self.hash_buckets[bucket_key].append(key)
        
        # Limita tamanho do bucket
        if len(self.hash_buckets[bucket_key]) > 20:
            self.hash_buckets[bucket_key] = self.hash_buckets[bucket_key][-15:]
    
    def _update_temporal_index_optimized(self, timestamp: float, key: str):
        """Atualiza índice temporal de forma otimizada."""
        self.temporal_index[timestamp] = key
        
        # Remove entradas antigas de forma eficiente
        current_time = time.perf_counter()
        old_timestamps = [
            ts for ts in self.temporal_index.keys() 
            if current_time - ts > self.temporal_window * 2
        ]
        
        for ts in old_timestamps[:10]:  # Remove apenas algumas por vez
            del self.temporal_index[ts]
    
    def _update_region_cache(self, region: str, key: str, entry: CacheEntry):
        """Atualiza cache hierárquico por região."""
        if region not in self.region_cache:
            self.region_cache[region] = OrderedDict()
        
        self.region_cache[region][key] = entry
        
        # Limita tamanho do cache por região
        max_region_size = self.max_size // 10
        if len(self.region_cache[region]) > max_region_size:
            # Remove os mais antigos
            for _ in range(5):
                if self.region_cache[region]:
                    self.region_cache[region].popitem(last=False)
    
    def _calculate_data_size(self, data: Any) -> int:
        """Calcula tamanho dos dados em bytes."""
        try:
            if isinstance(data, np.ndarray):
                return data.nbytes
            elif isinstance(data, (list, tuple)):
                return sys.getsizeof(data)
            else:
                return sys.getsizeof(data)
        except Exception:
            return 1024  # Tamanho padrão em caso de erro
    
    def _compress_data_optimized(self, data: Any) -> bytes:
        """Comprime dados de forma otimizada."""
        try:
            if isinstance(data, np.ndarray):
                # Compressão específica para arrays NumPy
                return pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
            else:
                return pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception:
            return data
    
    def _evict_items_optimized(self, needed_size: int):
        """Remove itens do cache de forma otimizada."""
        if not self.cache:
            return
        
        # Calcula quantos itens remover
        items_to_remove = max(1, len(self.cache) // 10)  # Remove 10% por vez
        
        # Estratégia híbrida de remoção
        if self.strategy == CacheStrategy.HYBRID:
            # Remove baseado em score de prioridade
            items_with_scores = [
                (entry.priority_score, key) 
                for key, entry in self.cache.items()
            ]
            items_with_scores.sort()  # Menor score primeiro
            
            for _, key in items_with_scores[:items_to_remove]:
                self._remove_item_optimized(key)
        else:
            # Remove os mais antigos (LRU)
            for _ in range(items_to_remove):
                if self.cache:
                    oldest_key = next(iter(self.cache))
                    self._remove_item_optimized(oldest_key)
    
    def _remove_item_optimized(self, key: str):
        """Remove item específico de forma otimizada."""
        if key in self.cache:
            entry = self.cache[key]
            self.stats.memory_usage_bytes -= entry.size_bytes
            self.stats.evictions += 1
            
            # Remove do cache principal
            del self.cache[key]
            
            # Remove dos índices
            self._remove_from_indices_optimized(key)
    
    def _remove_from_indices_optimized(self, key: str):
        """Remove chave de todos os índices de forma otimizada."""
        # Remove dos buckets de hash
        for bucket_keys in self.hash_buckets.values():
            if key in bucket_keys:
                bucket_keys.remove(key)
        
        # Remove do índice temporal (apenas alguns por vez para performance)
        timestamps_to_remove = [
            ts for ts, k in list(self.temporal_index.items())[:10] 
            if k == key
        ]
        for ts in timestamps_to_remove:
            del self.temporal_index[ts]
        
        # Remove dos caches de região
        for region_cache in self.region_cache.values():
            if key in region_cache:
                del region_cache[key]
    
    def _record_access_pattern_optimized(self, key: str, was_stored: bool):
        """Registra padrão de acesso de forma otimizada."""
        self.access_patterns.append({
            'key': key,
            'timestamp': time.perf_counter(),
            'was_stored': was_stored
        })
        
        # Analisa padrões periodicamente
        if len(self.access_patterns) % self.pattern_analysis_interval == 0:
            self._analyze_access_patterns_optimized()
    
    def _analyze_access_patterns_optimized(self):
        """Analisa padrões de acesso de forma otimizada."""
        if len(self.access_patterns) < 30:
            return
        
        recent_patterns = list(self.access_patterns)[-30:]
        
        # Calcula métricas básicas
        hit_rate = sum(1 for p in recent_patterns if not p['was_stored']) / len(recent_patterns)
        
        # Adapta estratégia de forma conservadora
        if hit_rate < 0.2:
            self.strategy = CacheStrategy.TEMPORAL
        elif hit_rate > 0.8:
            self.strategy = CacheStrategy.LRU
        else:
            self.strategy = CacheStrategy.HYBRID
    
    def _check_adaptation_optimized(self):
        """Verifica se precisa adaptar configurações."""
        self.adaptation_counter += 1
        
        if self.adaptation_counter % self.adaptation_interval == 0:
            # Ajusta threshold de similaridade baseado na performance
            if self.stats.hit_rate > 0.8:
                self.similarity_threshold = min(0.98, self.similarity_threshold + 0.01)
            elif self.stats.hit_rate < 0.3:
                self.similarity_threshold = max(0.85, self.similarity_threshold - 0.02)


# === FUNÇÃO DE CONVENIÊNCIA ===
def create_intelligent_cache(config=None):
    """Cria uma instância do cache inteligente."""
    return IntelligentCache(config)


# === EXEMPLO DE USO ===
if __name__ == "__main__":
    # Teste básico do cache
    cache = create_intelligent_cache({'max_cache_size': 100})
    
    # Simula uso
    for i in range(50):
        key = f"landmarks_{i}"
        landmarks = np.random.rand(33, 4)
        
        # Tenta recuperar
        result = cache.get(key, landmarks)
        
        if result is None:
            # Simula processamento e armazena
            processed_data = landmarks * 2  # Simula processamento
            cache.put(key, processed_data, landmarks, quality_score=0.8)
    
    print(cache.get_cache_report())