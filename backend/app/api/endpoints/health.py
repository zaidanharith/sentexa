from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/")
def home():
    return {"message": "Welcome to the Sentexa API"}


@router.get("/health")
def health():
    return {"status": "healthy", "environment": settings.ENVIRONMENT}
