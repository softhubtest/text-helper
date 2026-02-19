"""
Performance Optimizer - CPU/GPU kullanımını minimize eder
"""

import asyncio
from typing import List, Any
from datetime import datetime
import os

class PerformanceOptimizer:
    """Performans optimizasyonu - CPU/GPU kullanımını azaltır"""
    
    def __init__(self):
        # CPU kullanımını azaltmak için paralel task sayısını sınırla
        self.max_parallel_tasks = int(os.getenv("MAX_PARALLEL_TASKS", "3"))  # Varsayılan: 3
        self.task_timeout = float(os.getenv("TASK_TIMEOUT", "5.0"))  # Varsayılan: 5 saniye (arama için yeterli)
        self.enable_heavy_features = os.getenv("ENABLE_HEAVY_FEATURES", "false").lower() == "true"
    
    async def parallel_execute(self, tasks: List[Any], max_workers: int = None) -> List[Any]:
        """Paralel task'ları çalıştır (timeout ile)"""
        if not tasks:
            return []
        
        # Maksimum paralel task sayısını sınırla
        max_workers = max_workers or self.max_parallel_tasks
        if len(tasks) > max_workers:
            # Task'ları gruplara böl
            results = []
            for i in range(0, len(tasks), max_workers):
                batch = tasks[i:i + max_workers]
                batch_results = await asyncio.gather(
                    *[self._execute_with_timeout(task) for task in batch],
                    return_exceptions=True
                )
                results.extend(batch_results)
            return results
        else:
            # Tüm task'ları paralel çalıştır (timeout ile)
            return await asyncio.gather(
                *[self._execute_with_timeout(task) for task in tasks],
                return_exceptions=True
            )
    
    async def _execute_with_timeout(self, task: Any) -> Any:
        """Task'ı timeout ile çalıştır"""
        try:
            return await asyncio.wait_for(task, timeout=self.task_timeout)
        except asyncio.TimeoutError:
            print(f"[PERF] Task timeout ({self.task_timeout}s) - atlaniyor")
            return []
        except Exception as e:
            print(f"[PERF] Task hatasi: {e}")
            return []
    
    def get_stats(self) -> dict:
        """Performans istatistikleri"""
        return {
            "max_parallel_tasks": self.max_parallel_tasks,
            "task_timeout": self.task_timeout,
            "enable_heavy_features": self.enable_heavy_features
        }

# Global instance
performance_optimizer = PerformanceOptimizer()
