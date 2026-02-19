import sys
import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

# Path setup to support legacy modules
# Path ayari
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)


from app.core.config import settings
from app.core.logs import logger
from app.core.security import api_key_middleware
from app.core.exceptions import global_exception_handler
from app.routers import prediction, learning, websocket, system
from app.services.ai import transformer_predictor
from app.services.search import elasticsearch_predictor
try:
    from app.features.trie_index import trie_index
    TRIE_AVAILABLE = True
except ImportError:
    TRIE_AVAILABLE = False
    trie_index = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    logger.info("Sistem baslatiliyor...")
    
    # 1. ML Modeli (Arka planda)
    try:
        if settings.USE_TRANSFORMER:
            logger.info("Model yukleniyor...")
            asyncio.create_task(transformer_predictor.load_model())
    except Exception as e:
        logger.warning(f"Model hatasi: {e}")
        
    # 2. Arama Motoru
    try:
        await elasticsearch_predictor.connect_elasticsearch()
        # Sozlugu yukle
        elasticsearch_predictor._load_dictionary()
    except Exception as e:
        logger.warning(f"ES hatasi: {e}")
        
    # 3. Hizli Index (Trie)
    if TRIE_AVAILABLE and trie_index:
        try:
            logger.info("Index olusturuluyor...")
            dict_source = elasticsearch_predictor.local_dictionary
            if dict_source:
                await asyncio.to_thread(trie_index.build_index, dict_source)
                logger.info(f"Index hazir ({trie_index.word_count} kelime)")
        except Exception as e:
            logger.warning(f"Index hatasi: {e}")

    logger.info("Sistem hazir!")
    
    yield
    
    # --- SHUTDOWN ---
    logger.info("Sistem kapatiliyor...")
    if elasticsearch_predictor.es_client:
        try:
            close_res = elasticsearch_predictor.es_client.close()
            # If async client
            if hasattr(close_res, '__await__'):
                await close_res
        except Exception as e:
            logger.warning(f"ES close warning: {e}")

app = FastAPI(
    title="TextHelper ULTIMATE API",
    version="2.1.0",
    description="Hybrid AI Text Completion API",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Guvenlik
from starlette.middleware.base import BaseHTTPMiddleware
app.add_middleware(BaseHTTPMiddleware, dispatch=api_key_middleware)

# Exception Handlers
app.add_exception_handler(Exception, global_exception_handler)

# Routers
# app.include_router(system.router) # Root route cakismasi yapiyor, sadece /api/v1 altinda olsun
app.include_router(prediction.router, tags=["prediction"])
app.include_router(learning.router, tags=["learning"])
app.include_router(websocket.router, tags=["realtime"])

# V1 Prefix Backward Compatibility
app.include_router(prediction.router, prefix="/api/v1", tags=["v1"])
app.include_router(learning.router, prefix="/api/v1", tags=["v1"])
app.include_router(system.router, prefix="/api/v1", tags=["v1"])
app.include_router(websocket.router, prefix="/api/v1", tags=["v1"]) # Fix for frontend

# Frontend Statik Dosyalar (En altta ve Duzgun Sirada)
static_dir = os.path.join(BASE_DIR, "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    # Imports for static moved to top


    # Root -> index.html
    @app.get("/")
    async def read_index():
        return FileResponse(os.path.join(static_dir, "index.html"))

    # JS/CSS klasorleri icin direkt erisim
    app.mount("/js", StaticFiles(directory=os.path.join(static_dir, "js")), name="js")
    app.mount("/css", StaticFiles(directory=os.path.join(static_dir, "css")), name="css")
else:
    logger.warning("Static klasoru bulunamadi (Frontend yuklenmedi)")

if __name__ == "__main__":
    is_dev = os.getenv("DEV_MODE", "false").lower() == "true"
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8080,
        reload=is_dev
    )
