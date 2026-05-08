from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.user import User
from app.schemas.dashboard import KeywordResponse, SentimentLabel
from app.services import dashboard_service


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/keywords", response_model=KeywordResponse)
async def get_keywords(
	current_user: User = Depends(deps.get_current_user),
	db: AsyncSession = Depends(deps.get_db),
	sentiment: SentimentLabel | None = Query(default=None),
	job_id: str | None = Query(default=None),
	top: int = Query(default=30, ge=1, le=200),
):
	items = await dashboard_service.get_keywords(
		db,
		user_id=current_user.id,
		sentiment=sentiment,
		job_id=job_id,
		top=top,
	)
	return KeywordResponse(items=items, sentiment=sentiment, job_id=job_id)
