from fastapi import APIRouter
from pydantic import BaseModel

from logger_config import get_logger

router = APIRouter(prefix="/monitoring", tags=["monitoring"])
logger = get_logger(__name__)


class HealthCheckResponse(BaseModel):
    status: str


@router.get("/health")
async def health_check() -> HealthCheckResponse:
    logger.info("Health check endpoint called")
    return HealthCheckResponse(status="healthy")
