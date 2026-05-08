from fastapi import APIRouter

from app.api.endpoints import analyses, auth, dashboard, health, reports, sentiment, subscription

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(subscription.router)
api_router.include_router(sentiment.router)
api_router.include_router(analyses.router)
api_router.include_router(reports.router)
api_router.include_router(dashboard.router)
