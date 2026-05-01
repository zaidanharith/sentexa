from fastapi import APIRouter

from app.api.endpoints import auth, health, sentiment, subscription

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(subscription.router)
api_router.include_router(sentiment.router)
