from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.metrics import metrics_state
from app.core.database import get_db

router = APIRouter(tags=["health"])

@router.get("/")
def home():
    return {"message": "Welcome to the Sentexa API"}

@router.get("/health")
def health():
    return {"status": "healthy", "environment": settings.ENVIRONMENT}

@router.get("/api/ready")
async def ready(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable"
        )

@router.get("/metrics")
def metrics():
    data = metrics_state.snapshot()
    data["environment"] = settings.ENVIRONMENT
    return data