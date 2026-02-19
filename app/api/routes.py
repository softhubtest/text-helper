from fastapi import APIRouter, HTTPException, Depends, WebSocket
from app.api.schemas import ProcessRequest, ResponseModel, SuggestionItem
from app.core.nlp_engine import NLPEngine, nlp_engine
from app.core.cache import cache_manager
import time
import sys
from pathlib import Path

# Phrase completion (improvements) - lazy load
_phrase_completer = None

def _get_phrase_completer():
    global _phrase_completer
    if _phrase_completer is not None:
        return _phrase_completer
    try:
        base = Path(__file__).resolve().parent.parent.parent
        if str(base) not in sys.path:
            sys.path.insert(0, str(base))
        from improvements.phrase_completion import PhraseCompleter
        _phrase_completer = PhraseCompleter(dictionary=None)
        return _phrase_completer
    except Exception as e:
        print(f"[ROUTES] Phrase completion not loaded: {e}")
        return None

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            text = data.get("text", "")
            words = text.strip().split()

            # --- AŞAMA 1: Hızlı yanıt (Trie + user_dict, ~20-50 ms) ---
            fast_start = time.perf_counter()
            fast_suggestions = []
            if words:
                last_word = words[-1]
                prefix_results = nlp_engine.complete_prefix_fast(last_word, max_results=5)
                for res in prefix_results:
                    if res["word"].lower() != last_word.lower():
                        raw_count = res.get("count", 0)
                        score_val = 10.0 + (min(raw_count, 1000) / 100.0)
                        fast_suggestions.append({
                            "text": res["word"],
                            "confidence": 1.0,
                            "type": "completion",
                            "score": score_val,
                            "source": res.get("source", "unknown"),
                            "description": "Tamamlama",
                        })
            fast_ms = (time.perf_counter() - fast_start) * 1000
            await websocket.send_json({
                "phase": "fast",
                "suggestions": fast_suggestions,
                "processing_time_ms": round(fast_ms, 2),
            })

            # --- AŞAMA 2: Arka planda zenginleştirilmiş (N-gram / BERT) ---
            full_start = time.perf_counter()
            suggestions = list(fast_suggestions)
            seen_texts = {s["text"].lower() for s in suggestions}

            predictions = nlp_engine.predict_next(text)
            for pred in predictions[:3]:
                w = pred["word"]
                if w.lower() not in seen_texts:
                    suggestions.append({
                        "text": w,
                        "confidence": pred["score"],
                        "type": "next_word",
                        "score": pred["score"] * 10,
                        "source": pred["source"],
                        "description": "Tahmin",
                    })
                    seen_texts.add(w.lower())

            # Phrase completion (bağlamlı ifade önerileri)
            phrase_completer = _get_phrase_completer()
            if phrase_completer and text.strip():
                try:
                    phrase_results = phrase_completer.complete_phrase(text.strip(), max_results=5)
                    for r in phrase_results:
                        t = (r.get("text") or "").strip()
                        if t and t.lower() not in seen_texts:
                            suggestions.append({
                                "text": t,
                                "confidence": 0.9,
                                "type": "phrase",
                                "score": float(r.get("score", 8.0)),
                                "source": r.get("source", "phrase_completion"),
                                "description": r.get("description", "İfade"),
                            })
                            seen_texts.add(t.lower())
                except Exception as e:
                    print(f"[ROUTES] Phrase completion error: {e}")

            suggestions.sort(key=lambda x: x.get("score", 0), reverse=True)
            full_ms = (time.perf_counter() - full_start) * 1000
            await websocket.send_json({
                "phase": "enhanced",
                "suggestions": suggestions[:15],
                "processing_time_ms": round(full_ms, 2),
            })

    except Exception as e:
        print(f"WebSocket Error: {e}")

async def get_engine():
    if not nlp_engine.initialized:
        await nlp_engine.load_models()
    return nlp_engine

@router.post("/process", response_model=ResponseModel)
async def process_text(request: ProcessRequest, engine: NLPEngine = Depends(get_engine)):
    """
    Main endpoint for text processing.
    """
    start_time = time.time()
    
    # 0. Check Cache
    cache_key = f"process:{request.text}:{request.context or ''}"
    cached_response = cache_manager.get(cache_key)
    if cached_response:
        return ResponseModel(**cached_response)

    suggestions = []
    print(f"[HTTP DEBUG] Processing request: '{request.text}'")
    
    words = request.text.strip().split()
    if not words:
        return ResponseModel(original=request.text, suggestions=[])
        
    last_word = words[-1]
    
    # 1. PREFIX COMPLETION
    prefix_results = engine.complete_prefix(last_word, max_results=5)
    for res in prefix_results:
        if res['word'].lower() != last_word.lower():
            raw_count = res.get('count', 0)
            score_val = 10.0 + (min(raw_count, 1000) / 100.0)
            
            suggestions.append(SuggestionItem(
                text=res['word'],
                confidence=1.0, 
                type='completion',
                score=score_val,
                source=res.get('source', 'unknown'),
                description="Tamamlama"
            ))
        
    # 2. GPT-2 Generation
    context_str = request.text
    if len(context_str.strip()) > 2:
        generations = engine.generate_text(context_str, max_new_tokens=4)
        for gen in generations:
            if len(gen) > len(context_str):
                clean_gen = gen[len(context_str):].strip()
                if clean_gen:
                    suggestions.append(SuggestionItem(
                        text=clean_gen,
                        confidence=0.85,
                        type='ai_generation',
                        score=8.0,
                        source="gpt2",
                        description="AI"
                    ))
    
    # 3. Hybrid Prediction (Next Word)
    predictions = engine.predict_next(context_str)
    existing_texts = {s.text for s in suggestions}
    
    for pred in predictions[:3]:
        if pred['word'] not in existing_texts:
            suggestions.append(SuggestionItem(
                text=pred['word'],
                confidence=pred['score'],
                type='next_word',
                score=pred['score'] * 10,
                source=pred.get('source', 'bert'),
                description="Tahmin"
            ))

    # Phrase completion (bağlamlı ifade önerileri)
    phrase_completer = _get_phrase_completer()
    if phrase_completer and context_str.strip():
        try:
            phrase_results = phrase_completer.complete_phrase(context_str.strip(), max_results=5)
            for r in phrase_results:
                t = (r.get("text") or "").strip()
                if t and t not in existing_texts:
                    suggestions.append(SuggestionItem(
                        text=t,
                        confidence=0.9,
                        type="phrase",
                        score=float(r.get("score", 8.0)),
                        source=r.get("source", "phrase_completion"),
                        description=r.get("description", "İfade")
                    ))
                    existing_texts.add(t)
        except Exception as e:
            print(f"[ROUTES] Phrase completion error: {e}")

    # Sort suggestions by score descending
    suggestions.sort(key=lambda x: x.score, reverse=True)
            
    process_time = (time.time() - start_time) * 1000
    
    final_response = ResponseModel(
        original=request.text,
        suggestions=suggestions,
        sentiment="neutral",
        processing_time_ms=process_time
    )
    
    # Cache
    cache_manager.set(cache_key, final_response.model_dump(), ttl=3600)
    
    print(f"[HTTP DEBUG] Returning {len(suggestions)} suggestions")
    return final_response

@router.post("/learn")
async def learn_feedback(feedback: dict):
    try:
        text = feedback.get('text')
        if text:
            nlp_engine.learn(text)
        return {"status": "success"}
    except Exception as e:
        print(f"[LEARN] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    from app.core.search_service import search_service
    trie_ready = nlp_engine.trie_engine is not None and nlp_engine.trie_engine.word_count > 0
    return {
        "status": "active",
        "transformer_loaded": nlp_engine.initialized,
        "trie_ready": trie_ready,
        "trie_words": nlp_engine.trie_engine.word_count if nlp_engine.trie_engine else 0,
        "elasticsearch_available": search_service.available,
    }
