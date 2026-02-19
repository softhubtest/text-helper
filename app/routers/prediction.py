from fastapi import APIRouter, Request, HTTPException, Depends
from app.models.schemas import PredictionResponse, PredictionRequest, CorrectionRequest
from app.services.orchestrator import orchestrator
from app.services.search import elasticsearch_predictor
# We need advanced_fuzzy for correction if available.
# Orchestrator handles dependencies, but /correct endpoint used explicit advanced_fuzzy check in main.py.
# I'll implement /correct logic here using imports similar to orchestrator.

try:
    from app.features.advanced_fuzzy import advanced_fuzzy
    ADVANCED_FUZZY_AVAILABLE = True
except ImportError:
    ADVANCED_FUZZY_AVAILABLE = False
    advanced_fuzzy = None

try:
    from app.features.security import security_manager
    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False
    security_manager = None

router = APIRouter()

# Rate limiting helpers (can be moved to core if reused)
_rate_limit_cache = {}
_rate_limit_window = 60
_rate_limit_max_requests = 100

def _check_rate_limit(user_id: str) -> bool:
    import time
    current_time = time.time()
    _rate_limit_cache[user_id] = [
        t for t in _rate_limit_cache.get(user_id, [])
        if current_time - t < _rate_limit_window
    ]
    if len(_rate_limit_cache.get(user_id, [])) >= _rate_limit_max_requests:
        return False
    if user_id not in _rate_limit_cache:
        _rate_limit_cache[user_id] = []
    _rate_limit_cache[user_id].append(current_time)
    return True

@router.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest, req: Request, user_id: str = "default"):
    """
    Hybrid tahmin endpoint'i
    Transformer + Elasticsearch sonuçlarını birleştirir
    """
    try:
        # Rate limit
        if not _check_rate_limit(user_id):
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit aşıldı. Maksimum {_rate_limit_max_requests} istek/{_rate_limit_window} saniye"
            )
        
        # Security check
        if SECURITY_AVAILABLE and security_manager:
            try:
                # Security logging
                client_ip = req.client.host if req.client else "unknown"
                # Fix: Don't block localhost
                if client_ip not in ["127.0.0.1", "localhost", "::1"]:
                     if not security_manager.check_rate_limit(client_ip):
                         raise HTTPException(status_code=429, detail="Too many requests (IP)")
                
                is_valid, error_msg = security_manager.validate_input(request.text)
                if not is_valid:
                    raise HTTPException(status_code=400, detail=error_msg or "Invalid input")
            except HTTPException:
                raise
            except Exception as e:
                # Security modülü hatası prediction'ı engellememeli
                print(f"Security check ignored error: {e}")

        response = await orchestrator.predict(
            text=request.text,
            context_message=request.context_message,
            max_suggestions=request.max_suggestions,
            use_ai=request.use_ai,
            use_search=request.use_search,
            user_id=user_id
        )
        return response
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.post("/process", response_model=PredictionResponse)
async def process_legacy(request: PredictionRequest, req: Request, user_id: str = "default"):
    """Legacy alias for /predict"""
    return await predict(request, req, user_id)

@router.post("/correct")
async def autocorrect_text(request: CorrectionRequest):
    """
    iPhone/WhatsApp tarzı agresif otomatik düzeltme.
    """
    original = request.text
    corrected = original
    words = original.split()
    
    if not words:
        return {"original": original, "corrected": original, "changed": False}
        
    last_word = words[-1]
    
    if ADVANCED_FUZZY_AVAILABLE and advanced_fuzzy:
        # Dictionary needs to be loaded in search service
        vocab = elasticsearch_predictor.local_dictionary
        # If empty try loading? search service handles loading on first search, but here we access directly.
        # It's better to ensure it's loaded.
        if not vocab:
             vocab = elasticsearch_predictor._load_dictionary()

        suggestions = advanced_fuzzy.match(last_word, vocab, max_results=1)
        if suggestions and suggestions[0]['confidence'] > 0.8:
             words[-1] = suggestions[0]['word']
             corrected = " ".join(words)
             
    changed = corrected != original
    return {"original": original, "corrected": corrected, "changed": changed}
