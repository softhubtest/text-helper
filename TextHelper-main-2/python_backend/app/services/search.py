import os
import asyncio
from typing import List, Optional
from app.models.schemas import Suggestion
from app.core.config import settings
from app.core.logs import logger

# Optional dependencies logic
try:
    from app.features.large_dictionary import large_dictionary
    LARGE_DICT_AVAILABLE = True
except ImportError:
    LARGE_DICT_AVAILABLE = False
    large_dictionary = None

try:
    from app.features.elasticsearch_setup import es_manager
    ES_MANAGER_AVAILABLE = True
except ImportError:
    ES_MANAGER_AVAILABLE = False
    es_manager = None

class ElasticsearchPredictor:
    """Elasticsearch ile hızlı sözlük arama"""
    
    def __init__(self):
        self.es_client = None
        self.use_elasticsearch = settings.USE_ELASTICSEARCH
        self.local_dictionary = [] # Lazy load
        self._dictionary_loaded = False
        
    def _load_dictionary(self) -> List[str]:
        """Yerel sözlük yükle (Elasticsearch yoksa)"""
        if self._dictionary_loaded:
            return self.local_dictionary
            
        # Büyük Türkçe sözlük path
        dictionary_file = os.path.join(settings.BASE_DIR, "turkish_dictionary.txt")
        
        try:
            if os.path.exists(dictionary_file):
                logger.info(f"Sözlük yükleniyor... ({dictionary_file})")
                with open(dictionary_file, 'r', encoding='utf-8') as f:
                    lines = []
                    count = 0
                    for line in f:
                        if line.strip():
                            lines.append(line.strip())
                            count += 1
                            if count >= 500000: # Limit memory usage
                                break
                    
                self._dictionary_loaded = True
                logger.info(f"Sözlük yüklendi ({len(lines)} kelime)")
                return lines
        except MemoryError:
            logger.warning("Yetersiz bellek - Büyük sözlük yüklenemedi. Varsayılan küçük sözlük kullanılacak.")
        except Exception as e:
            logger.warning(f"Sözlük yükleme hatası: {e}")
        
        # Varsayılan sözlük (Fallback)
        self._dictionary_loaded = True
        return [
            'mantık', 'mantıklı', 'merhaba', 'selam', 'teşekkür', 'yardım', 'müşteri', 'sipariş',
            'iyi', 'kötü', 'güzel', 'sorun', 'çözüm', 'iade'
        ]
    
    async def connect_elasticsearch(self):
        """Elasticsearch'e bağlan"""
        if ES_MANAGER_AVAILABLE and es_manager:
            try:
                if hasattr(es_manager, 'connect'):
                    await es_manager.connect()
                if hasattr(es_manager, 'available') and es_manager.available:
                    if hasattr(es_manager, 'es_client'):
                        self.es_client = es_manager.es_client
                    logger.info("Elasticsearch Manager ile baglanti kuruldu")
                    return
            except Exception as e:
                logger.warning(f"ES manager connect hatasi: {e}")
        
        # Fallback: Direkt bağlantı
        try:
            from elasticsearch import Elasticsearch
            
            es_hosts = []
            http_auth = None
            
            if settings.ELASTICSEARCH_URL:
                es_hosts = [settings.ELASTICSEARCH_URL]
            else:
                es_host = settings.ELASTICSEARCH_HOST
                if not es_host.startswith("http://") and not es_host.startswith("https://"):
                    es_host = f"http://{es_host}"
                es_hosts = [es_host]
            
            if settings.ELASTICSEARCH_USERNAME and settings.ELASTICSEARCH_PASSWORD:
                http_auth = (settings.ELASTICSEARCH_USERNAME, settings.ELASTICSEARCH_PASSWORD)
            
            self.es_client = Elasticsearch(
                es_hosts,
                http_auth=http_auth,
                request_timeout=10,
                max_retries=2,
                retry_on_timeout=True
            )
            
            try:
                if self.es_client.ping():
                    logger.info(f"Elasticsearch baglantisi kuruldu: {es_host}")
                else:
                    logger.info("Elasticsearch kullanilamiyor, yerel sozluk kullanilacak (normal)")
                    self.es_client = None
            except Exception:
                logger.info("Elasticsearch kullanilamiyor, yerel sozluk kullanilacak (normal)")
                self.es_client = None
        except ImportError:
            logger.warning("elasticsearch kutuphanesi kurulu degil: pip install elasticsearch")
            self.es_client = None
        except Exception as e:
            logger.info("Elasticsearch kullanilamiyor, yerel sozluk kullanilacak (normal)")
            self.es_client = None
    
    async def search(self, prefix: str, max_results: int = 50) -> List[Suggestion]:
        if self.es_client:
            return await self._elasticsearch_search(prefix, max_results)
        else:
            return await self._local_search(prefix, max_results)
    
    async def _elasticsearch_search(self, prefix: str, max_results: int) -> List[Suggestion]:
        if ES_MANAGER_AVAILABLE and es_manager and hasattr(es_manager, 'available') and es_manager.available:
            try:
                if hasattr(es_manager, 'search'):
                    results = await es_manager.search(prefix, max_results)
                    if results and isinstance(results, list):
                        return [Suggestion(**r) for r in results if isinstance(r, dict)]
            except Exception as e:
                logger.warning(f"ES manager search hatasi: {e}")
        
        if not self.es_client:
            return await self._local_search(prefix, max_results)
        
        try:
            query = {
                "suggest": {
                    "word-suggest": {
                        "prefix": prefix.lower(),
                        "completion": {
                            "field": "word_suggest",
                            "size": max_results
                        }
                    }
                }
            }
            
            response = self.es_client.search(index="turkish_words", body=query)
            suggestions = []
            
            for option in response.get('suggest', {}).get('word-suggest', [{}])[0].get('options', []):
                suggestions.append(Suggestion(
                    text=option['text'],
                    type="dictionary",
                    score=8.0 + (option.get('score', 0) / 100),
                    description="Sözlük (Elasticsearch)",
                    source="elasticsearch"
                ))
            
            return suggestions
        except Exception as e:
            logger.error(f"Elasticsearch arama hatası: {e}")
            return await self._local_search(prefix, max_results)
    
    async def _local_search(self, prefix: str, max_results: int) -> List[Suggestion]:
        suggestions = []
        prefix_lower = prefix.lower().strip()
        
        if not prefix_lower:
            return suggestions
            
        if not self.local_dictionary and not self._dictionary_loaded:
             self.local_dictionary = self._load_dictionary()
        
        if LARGE_DICT_AVAILABLE and large_dictionary:
            try:
                results = large_dictionary.search(prefix_lower, max_results)
                if results:
                    for result in results:
                        suggestions.append(Suggestion(
                            text=result['word'],
                            type="dictionary",
                            score=result.get('score', 8.0),
                            description=f"Sözlük (frekans: {result.get('frequency', 0)})",
                            source="large_dictionary"
                        ))
                    return suggestions
            except Exception as e:
                logger.error(f"Large dictionary search hatası: {e}")
        
        # Fallback local dictionary
        for word in self.local_dictionary:
            word_lower = word.lower()
            if len(prefix_lower) >= 1 and word_lower.startswith(prefix_lower) and word_lower != prefix_lower:
                if len(prefix_lower) == 1:
                    score = 9.5 - (len(word_lower) * 0.02)
                elif len(prefix_lower) == 2:
                    score = 9.0 - (len(word_lower) * 0.01)
                else:
                    score = (len(prefix_lower) / len(word_lower)) * 8.5
                
                suggestions.append(Suggestion(
                    text=word,
                    type="dictionary",
                    score=score,
                    description="Sözlük",
                    source="local_dictionary"
                ))
                
                if len(suggestions) >= max_results * 2:
                    break
        
        suggestions.sort(key=lambda x: x.score, reverse=True)
        return suggestions[:max_results]

elasticsearch_predictor = ElasticsearchPredictor()
