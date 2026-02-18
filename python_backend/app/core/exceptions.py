from fastapi import Request
from fastapi.responses import ORJSONResponse
from app.models.schemas import StandardErrorResponse
from .logs import logger

async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return ORJSONResponse(
        status_code=500,
        content=StandardErrorResponse(
            code="INTERNAL_SERVER_ERROR",
            message="Beklenmeyen sunucu hatasi",
            details={"error": str(exc)}
        ).model_dump()
    )
