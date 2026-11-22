from fastapi import APIRouter, Depends

from app.clients.ai_client import AIClient
from app.config import get_settings
from app.dependencies import get_ai_client
from app.schemas.schemas import DependencyStatus

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    settings = get_settings()
    return {"service": settings.app_name, "status": "UP", "version": settings.app_version}


@router.get("/health/dependencies", response_model=list[DependencyStatus])
async def dependency_health(ai_client: AIClient = Depends(get_ai_client)):
    """Entegrasyon sirasinda bagli servislerin durumunu gormek icin."""
    status, detail = await ai_client.check_health()
    return [DependencyStatus(name="ai-service", url=ai_client.base_url, status=status, detail=detail)]
