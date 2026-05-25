from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.metrics import metrics_state

router = APIRouter(tags=["health"])


@router.get("/")
def home():
    return {"message": "Welcome to the Sentexa API"}


@router.get("/health")
def health():
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }


@router.get("/ready")
async def ready(db: AsyncSession = Depends(get_db)):
    await db.execute(text("SELECT 1"))
    return {
        "status": "ready",
        "environment": settings.ENVIRONMENT
    }


@router.get("/metrics")
def metrics():
    data = metrics_state.snapshot()
    data["environment"] = settings.ENVIRONMENT
    return data