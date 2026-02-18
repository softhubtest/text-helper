from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.orchestrator import orchestrator
from app.core.logs import logger

router = APIRouter()

_ws_rate_limit = {}
_ws_rate_limit_window = 60
_ws_rate_limit_max_requests = 1000

def _check_ws_rate_limit(user_id: str) -> bool:
    import time
    current_time = time.time()
    _ws_rate_limit[user_id] = [
        t for t in _ws_rate_limit.get(user_id, [])
        if current_time - t < _ws_rate_limit_window
    ]
    if len(_ws_rate_limit.get(user_id, [])) >= _ws_rate_limit_max_requests:
        return False
    if user_id not in _ws_rate_limit:
        _ws_rate_limit[user_id] = []
    _ws_rate_limit[user_id].append(current_time)
    return True

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Real-time oneriler"""
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_json()
            user_id = data.get("user_id", "default")
            
            if not _check_ws_rate_limit(user_id):
                await websocket.send_json({
                    "error": f"Rate limit aşıldı."
                })
                continue
            
            text = data.get("text", "").strip()
            context_message = data.get("context_message", None)
            max_suggestions = data.get("max_suggestions", 80)
            use_ai = data.get("use_ai", True)
            use_search = data.get("use_search", True)
            
            try:
                # logger.debug(f"WS Request: text='{text}'") 
                # Avoid excessive logging in production loop
                
                response = await orchestrator.predict(
                    text=text,
                    context_message=context_message,
                    max_suggestions=max_suggestions,
                    use_ai=use_ai,
                    use_search=use_search,
                    user_id=user_id
                )
                
                response_dict = response.model_dump() if hasattr(response, 'model_dump') else response.dict()
                await websocket.send_json(response_dict)
                
            except Exception as e:
                logger.error(f"Prediction loop hatasi: {e}")
                await websocket.send_json({"suggestions": [], "error": str(e)})
                
    except WebSocketDisconnect:
        logger.info("WS connection closed (normal)")
    except Exception as e:
        # Check standard disconnect codes
        if "disconnect" in str(e).lower():
             logger.info("WS connection closed (normal)")
        else:
            logger.error(f"WebSocket error: {e}")
            try:
                await websocket.close()
            except:
                pass
