from fastapi import APIRouter, BackgroundTasks
from typing import Optional
from app.models.schemas import FeedbackRequest
from app.core.logs import logger
from app.core.config import settings

# Optional Learning Modules
try:
    from app.features.ml_learning import ml_learning
    ML_LEARNING_AVAILABLE = True
except ImportError:
    ML_LEARNING_AVAILABLE = False
    ml_learning = None

try:
    from app.features.advanced_ngram import advanced_ngram
    ADVANCED_NGRAM_AVAILABLE = True
except ImportError:
    ADVANCED_NGRAM_AVAILABLE = False
    advanced_ngram = None

try:
    from app.features.advanced_ranking import advanced_ranking
    ADVANCED_RANKING_AVAILABLE = True
except ImportError:
    ADVANCED_RANKING_AVAILABLE = False
    advanced_ranking = None

router = APIRouter()

def background_learn(user_id: str, text: str, selected_suggestion: str):
    """Arka planda öğrenme işlemi"""
    # 1. ML Learning
    if ML_LEARNING_AVAILABLE and ml_learning:
        try:
            ml_learning.learn_from_interaction(user_id, text, selected_suggestion)
            logger.info(f"[LEARN] ML ogrenme: {text} (kullanici: {user_id})")
        except Exception as e:
            logger.error(f"Background ML learning hatası: {e}")

    # 2. N-gram Learning
    if ADVANCED_NGRAM_AVAILABLE and advanced_ngram and hasattr(advanced_ngram, 'learn_from_text'):
        try:
            advanced_ngram.learn_from_text(text)
            if selected_suggestion:
                full_text = f"{text} {selected_suggestion}"
                advanced_ngram.learn_from_text(full_text)
            logger.info(f"[LEARN] N-gram ogrenme: {text}")
        except Exception as e:
            logger.error(f"Background N-gram learning hatası: {e}")

    # 3. Ranking Learning
    if ADVANCED_RANKING_AVAILABLE and advanced_ranking and selected_suggestion and hasattr(advanced_ranking, 'record_click'):
        try:
            advanced_ranking.record_click(selected_suggestion)
            logger.info(f"[LEARN] Ranking ogrenme: {selected_suggestion}")
        except Exception as e:
            logger.error(f"Background Ranking learning hatası: {e}")

@router.post("/learn")
async def learn_interaction(feedback: FeedbackRequest, background_tasks: BackgroundTasks):
    """Kullanıcı etkileşiminden öğren (Fire-and-Forget)"""
    # Ana thread'i bekletmeden arka plana at
    background_tasks.add_task(
        background_learn,
        feedback.user_id,
        feedback.text,
        feedback.selected_suggestion
    )
    return {"status": "queued"}
