from fastapi import APIRouter
from datetime import datetime
from app.modals.schemas import HealthResponse
from app.core.config import settings
from app.services.ai_service import AIService

router = APIRouter()
ai_service = AIService()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version=settings.VERSION,
        available_services=ai_service.get_available_services()
    )
