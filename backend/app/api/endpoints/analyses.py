from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.user import User
from app.schemas.analysis_history import (
	AnalysisHistoryDetailResponse,
	AnalysisHistoryListResponse,
	AnalysisHistorySummaryResponse,
	AnalysisHistoryTrendResponse,
)
from app.services import analysis_history_service


router = APIRouter(prefix="/analyses", tags=["analyses"])


@router.get("", response_model=AnalysisHistoryListResponse)
async def list_analysis_history(
	current_user: User = Depends(deps.get_current_user),
	db: AsyncSession = Depends(deps.get_db),
	offset: int = Query(0, ge=0),
	limit: int = Query(50, ge=1, le=100),
	source_type: str | None = Query(default=None),
):
	items, count = await analysis_history_service.list_history(
		db,
		current_user.id,
		offset=offset,
		limit=limit,
		source_type=source_type,
	)
	return AnalysisHistoryListResponse(
		items=items,
		count=count,
		offset=offset,
		limit=limit,
	)


@router.get("/summary", response_model=AnalysisHistorySummaryResponse)
async def get_analysis_history_summary(
	current_user: User = Depends(deps.get_current_user),
	db: AsyncSession = Depends(deps.get_db),
):
	(
		total_analyses,
		delta_from_yesterday,
		sentiment_counts,
		total_sentiments,
	) = await analysis_history_service.get_history_summary(db, current_user.id)
	return AnalysisHistorySummaryResponse(
		total_analyses=total_analyses,
		delta_from_yesterday=delta_from_yesterday,
		sentiment_counts=sentiment_counts,
		total_sentiments=total_sentiments,
	)


@router.get("/trend", response_model=AnalysisHistoryTrendResponse)
async def get_analysis_history_trend(
	current_user: User = Depends(deps.get_current_user),
	db: AsyncSession = Depends(deps.get_db),
	days: int = Query(30, ge=1, le=365),
):
	items = await analysis_history_service.get_history_trend(
		db,
		current_user.id,
		days=days,
	)
	return AnalysisHistoryTrendResponse(items=items)


@router.get("/{history_id:int}", response_model=AnalysisHistoryDetailResponse)
async def get_analysis_history(
	history_id: int,
	current_user: User = Depends(deps.get_current_user),
	db: AsyncSession = Depends(deps.get_db),
):
	history = await analysis_history_service.get_history_by_id(db, current_user.id, history_id)
	return AnalysisHistoryDetailResponse(item=history)