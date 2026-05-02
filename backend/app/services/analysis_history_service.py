from __future__ import annotations

from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis_history import AnalysisHistory


async def create_history(
	db: AsyncSession,
	*,
	user_id: int,
	source_type: str,
	source_name: str | None = None,
	input_text: str | None = None,
	upload_id: int | None = None,
	job_id: str | None = None,
	status: str = "completed",
	include_scores: bool = True,
	apply_postprocess: bool = True,
	include_meta: bool = False,
	item_count: int | None = None,
	result_label: str | None = None,
	result_score: float | None = None,
	label_counts: dict[str, int] | None = None,
	result_payload: dict | list | None = None,
	error: str | None = None,
) -> AnalysisHistory:
	history = AnalysisHistory(
		user_id=user_id,
		source_type=source_type,
		source_name=source_name,
		input_text=input_text,
		upload_id=upload_id,
		job_id=job_id,
		status=status,
		include_scores=include_scores,
		apply_postprocess=apply_postprocess,
		include_meta=include_meta,
		item_count=item_count,
		result_label=result_label,
		result_score=result_score,
		label_counts=label_counts,
		result_payload=result_payload,
		error=error,
	)
	db.add(history)
	await db.flush()
	await db.refresh(history)
	return history


async def get_history_by_id(
	db: AsyncSession,
	user_id: int,
	history_id: int,
) -> AnalysisHistory:
	result = await db.execute(
		select(AnalysisHistory).where(
			AnalysisHistory.id == history_id,
			AnalysisHistory.user_id == user_id,
		)
	)
	history = result.scalar_one_or_none()
	if history is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="History not found")
	return history


async def list_history(
	db: AsyncSession,
	user_id: int,
	*,
	offset: int = 0,
	limit: int = 50,
	source_type: str | None = None,
) -> tuple[list[AnalysisHistory], int]:
	offset = max(offset, 0)
	limit = max(limit, 1)

	count_query = select(func.count()).select_from(AnalysisHistory).where(AnalysisHistory.user_id == user_id)
	if source_type:
		count_query = count_query.where(AnalysisHistory.source_type == source_type)
	count_result = await db.execute(count_query)
	count = int(count_result.scalar_one())

	query = (
		select(AnalysisHistory)
		.where(AnalysisHistory.user_id == user_id)
		.order_by(AnalysisHistory.created_at.desc())
		.offset(offset)
		.limit(limit)
	)
	if source_type:
		query = query.where(AnalysisHistory.source_type == source_type)

	result = await db.execute(query)
	items = list(result.scalars().all())
	return items, count


async def upsert_job_history(
	db: AsyncSession,
	*,
	user_id: int,
	job_id: str,
	defaults: Optional[dict] = None,
	updates: Optional[dict] = None,
) -> AnalysisHistory:
	defaults = defaults or {}
	updates = updates or {}
	result = await db.execute(select(AnalysisHistory).where(AnalysisHistory.job_id == job_id))
	history = result.scalar_one_or_none()
	if history is None:
		history = AnalysisHistory(user_id=user_id, job_id=job_id, **defaults)
		db.add(history)
		await db.flush()
	else:
		if history.user_id != user_id:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="History not found")

	for key, value in updates.items():
		setattr(history, key, value)

	await db.flush()
	await db.refresh(history)
	return history