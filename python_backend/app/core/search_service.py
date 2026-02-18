import os
from elasticsearch import Elasticsearch, AsyncElasticsearch

class SearchService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SearchService, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return
            
        self.es_client = None
        self.available = False
        
        # Try connecting to Elasticsearch (Standard Port 9200)
        try:
            # We use Async client for FastAPI
            self.es_client = AsyncElasticsearch(
                ["http://localhost:9200"],
                request_timeout=1,
                max_retries=0
            ) 
            # We can't easily sync ping an async client in init without await
            # But we will check availability on request or background task.
            # Let's assume unavailable until proven otherwise.
            self.available = False 
        except Exception as e:
            print(f"[SEARCH] ES Init Error: {e}")
            
        self.initialized = True

    async def check_connection(self):
        try:
            if await self.es_client.ping():
                if not self.available:
                    print("[SEARCH] Elasticsearch baglantisi BASARILI.")
                self.available = True
            else:
                self.available = False
        except Exception:
            self.available = False

search_service = SearchService()
