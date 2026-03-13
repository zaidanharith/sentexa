from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text

from app.core.database import engine
from app.core.config import settings
from app.core.metrics import metrics_state

router = APIRouter(tags=["health"])

@router.get("/")
def home():
    return {"message": "Welcome to the Sentexa API"}

@router.get("/health")
def health():
    return {"status": "healthy", "environment": settings.ENVIRONMENT}

@router.get("/ready")
async def ready():
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not ready",
        ) from exc

    return {"status": "ready", "environment": settings.ENVIRONMENT}


@router.get("/metrics")
def metrics():
    data = metrics_state.snapshot()
    data["environment"] = settings.ENVIRONMENT
    return data
