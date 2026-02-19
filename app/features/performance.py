"""
Performance Optimizations
- Connection pooling
- Query optimization
- Aggressive caching
"""

from typing import Dict, Optional
import asyncio
from functools import lru_cache
import time
import re

class PerformanceOptimizer:
    """Performans optimizasyonu"""
    
    def __init__(self):
        # Connection pool (simulated)
        self.connection_pools = {}
        self.pool_size = 10
        
        # Query cache
        self.query_cache: Dict[str, tuple] = {}  # query -> (result, timestamp)
        self.cache_ttl = 300  # 5 minutes
        
        # Statistics
        self.stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'query_count': 0,
            'avg_response_time': 0.0
        }
    
    def get_connection_pool(self, service: str):
        """Connection pool al"""
        if service not in self.connection_pools:
            self.connection_pools[service] = {
                'connections': [],
                'available': [],
                'in_use': set()
            }
        return self.connection_pools[service]
    
    def get_cached_query(self, query_key: str) -> Optional[any]:
        """Cache'den query sonucu al"""
        if query_key in self.query_cache:
            result, timestamp = self.query_cache[query_key]
            if time.time() - timestamp < self.cache_ttl:
                self.stats['cache_hits'] += 1
                return result
        
        self.stats['cache_misses'] += 1
        return None
    
    def cache_query(self, query_key: str, result: any):
        """Query sonucunu cache'le"""
        self.query_cache[query_key] = (result, time.time())
        
        # Cache size limit
        if len(self.query_cache) > 1000:
            # Remove oldest entries
            sorted_cache = sorted(
                self.query_cache.items(),
                key=lambda x: x[1][1]
            )
            for key, _ in sorted_cache[:100]:
                del self.query_cache[key]
    
    async def parallel_execute(self, tasks: list) -> list:
        """Paralel işlem yap"""
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        elapsed = time.time() - start_time
        
        self.stats['query_count'] += 1
        # Update average
        total_queries = self.stats['query_count']
        current_avg = self.stats['avg_response_time']
        self.stats['avg_response_time'] = (
            (current_avg * (total_queries - 1) + elapsed) / total_queries
        )
        
        return results
    
    def optimize_query(self, query: str) -> str:
        """Query optimize et"""
        # Basit optimizasyonlar
        # Trim whitespace
        query = query.strip()
        # Remove multiple spaces
        query = re.sub(r'\s+', ' ', query)
        return query
    
    def get_stats(self) -> Dict:
        """İstatistikleri al"""
        cache_hit_rate = 0.0
        total = self.stats['cache_hits'] + self.stats['cache_misses']
        if total > 0:
            cache_hit_rate = self.stats['cache_hits'] / total * 100
        
        return {
            'cache_hits': self.stats['cache_hits'],
            'cache_misses': self.stats['cache_misses'],
            'cache_hit_rate': f"{cache_hit_rate:.2f}%",
            'query_count': self.stats['query_count'],
            'avg_response_time_ms': f"{self.stats['avg_response_time'] * 1000:.2f}",
            'cache_size': len(self.query_cache)
        }
    
    def clear_cache(self):
        """Cache'i temizle"""
        self.query_cache.clear()
        self.stats['cache_hits'] = 0
        self.stats['cache_misses'] = 0

# Global instance
performance_optimizer = PerformanceOptimizer()
