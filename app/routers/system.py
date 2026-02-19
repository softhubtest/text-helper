from fastapi import APIRouter
from datetime import datetime
from app.services.ai import transformer_predictor, REAL_TRANSFORMER_AVAILABLE, transformer_model
from app.services.search import elasticsearch_predictor, large_dictionary, LARGE_DICT_AVAILABLE, es_manager, ES_MANAGER_AVAILABLE
from app.core.config import settings

router = APIRouter()

@router.get("/")
async def root():
    return {
        "message": "TextHelper ULTIMATE API",
        "version": "2.0.0",
        "status": "running",
        "architecture": "Hybrid: Transformer + Elasticsearch + FastAPI",
    }

@router.get("/health")
async def health():
    """Sistem sağlık kontrolü - Detaylı Durum"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.1.0",
        "components": {}
    }
    
    # Dictionary
    dict_size = 0
    if elasticsearch_predictor.local_dictionary:
        dict_size = len(elasticsearch_predictor.local_dictionary)
    
    if LARGE_DICT_AVAILABLE and large_dictionary:
        try:
            dict_size = large_dictionary.get_word_count()
        except:
            pass
    health_status["components"]["dictionary"] = {"status": "ok", "size": dict_size}
    
    # Transformer
    if REAL_TRANSFORMER_AVAILABLE and transformer_model:
        try:
            info = transformer_model.get_model_info()
            health_status["components"]["transformer"] = {
                "status": "active" if info.get("loaded") else "standby",
                "details": info
            }
        except Exception as e:
            health_status["components"]["transformer"] = {"status": "error", "error": str(e)}
    else:
        health_status["components"]["transformer"] = {"status": "disabled"}
    
    # Elasticsearch
    if elasticsearch_predictor.es_client:
         health_status["components"]["elasticsearch"] = {"status": "connected"}
    else:
         health_status["components"]["elasticsearch"] = {"status": "disconnected"}
         
    return health_status

@router.post("/index_words")
async def index_words_to_elasticsearch():
    """Kelimeleri Elasticsearch'e index'le"""
    if not ES_MANAGER_AVAILABLE or not es_manager or not hasattr(es_manager, 'available') or not es_manager.available:
        return {"status": "error", "message": "Elasticsearch kullanılamıyor"}
    
    words_data = []
    if LARGE_DICT_AVAILABLE and large_dictionary:
        for word in large_dictionary.words:
            words_data.append({
                'word': word,
                'frequency': large_dictionary.word_frequencies.get(word.lower(), 1),
                'category': 'general'
            })
    else:
        for word in elasticsearch_predictor.local_dictionary:
            words_data.append({
                'word': word,
                'frequency': 1,
                'category': 'general'
            })
    
    success = False
    if hasattr(es_manager, 'index_words'):
        try:
            success = await es_manager.index_words(words_data)
        except Exception:
            pass
            
    return {
        "status": "success" if success else "error",
        "words_indexed": len(words_data) if success else 0
    }
