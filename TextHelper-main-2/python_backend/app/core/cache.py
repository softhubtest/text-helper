import redis
import json
import logging
from typing import Optional, Any
import time

logger = logging.getLogger("TextHelperCache")

class CacheManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CacheManager, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return
            
        self.use_redis = False
        self.redis_client = None
        self.memory_cache = {}
        self.max_memory_size = 1000
        
        # Try connecting to Redis (Standard Port 6379)
        try:
            self.redis_client = redis.Redis(host='localhost', port=6379, db=0, socket_connect_timeout=1)
            self.redis_client.ping()
            self.use_redis = True
            print("[CACHE] Redis connected successfully.")
        except redis.ConnectionError:
            print("[INFO] Redis sunucusu bulunamadi. Yuksek Performansli 'In-Memory Cache' aktif edildi.")
            self.use_redis = False
        except Exception as e:
            print(f"[INFO] Cache modu: Dahili Bellek (Memory). Hizli erisim aktif.")
            self.use_redis = False
            
        self.initialized = True

    def get(self, key: str) -> Optional[Any]:
        if self.use_redis:
            try:
                val = self.redis_client.get(key)
                if val:
                    return json.loads(val)
            except Exception:
                return None
        else:
            return self.memory_cache.get(key)

    def set(self, key: str, value: Any, ttl: int = 3600):
        if self.use_redis:
            try:
                self.redis_client.setex(key, ttl, json.dumps(value))
            except Exception:
                pass
        else:
            # Automatic cleanup if too big
            if len(self.memory_cache) > self.max_memory_size:
                self.memory_cache.pop(next(iter(self.memory_cache)))
            self.memory_cache[key] = value

cache_manager = CacheManager()
