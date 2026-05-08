from __future__ import annotations

from datetime import date, datetime, timedelta
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


def _normalize_label(value: object) -> str | None:
	if value is None:
		return None
	label = str(value).strip().lower()
	if not label:
		return None
	if label in {"positif", "positive"}:
		return "positive"
	if label in {"negatif", "negative"}:
		return "negative"
	if label in {"netral", "neutral"}:
		return "neutral"
	return None


async def get_history_summary(
	db: AsyncSession,
	user_id: int,
) -> tuple[int, int, dict[str, int], int]:
	count_query = select(func.count()).select_from(AnalysisHistory).where(AnalysisHistory.user_id == user_id)
	count_result = await db.execute(count_query)
	total_analyses = int(count_result.scalar_one())

	start_today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
	start_yesterday = start_today - timedelta(days=1)
	start_tomorrow = start_today + timedelta(days=1)

	count_today_result = await db.execute(
		select(func.count()).select_from(AnalysisHistory).where(
			AnalysisHistory.user_id == user_id,
			AnalysisHistory.created_at >= start_today,
			AnalysisHistory.created_at < start_tomorrow,
		)
	)
	count_yesterday_result = await db.execute(
		select(func.count()).select_from(AnalysisHistory).where(
			AnalysisHistory.user_id == user_id,
			AnalysisHistory.created_at >= start_yesterday,
			AnalysisHistory.created_at < start_today,
		)
	)
	count_today = int(count_today_result.scalar_one())
	count_yesterday = int(count_yesterday_result.scalar_one())
	delta_from_yesterday = count_today - count_yesterday

	result = await db.execute(
		select(
			AnalysisHistory.source_type,
			AnalysisHistory.result_label,
			AnalysisHistory.label_counts,
			AnalysisHistory.result_payload,
		)
		.where(AnalysisHistory.user_id == user_id)
	)

	counts = {"positive": 0, "negative": 0, "neutral": 0}
	for source_type, result_label, label_counts, result_payload in result.all():
		if source_type == "batch":
			if isinstance(label_counts, dict):
				for key, value in label_counts.items():
					label = _normalize_label(key)
					if label is None:
						continue
					try:
						counts[label] += int(value)
					except (TypeError, ValueError):
						continue
			elif isinstance(result_payload, list):
				for item in result_payload:
					if not isinstance(item, dict):
						continue
					label = _normalize_label(item.get("label"))
					if label is None:
						continue
					counts[label] += 1
		else:
			label = _normalize_label(result_label)
			if label is None:
				continue
			counts[label] += 1

	total_sentiments = sum(counts.values())
	return total_analyses, delta_from_yesterday, counts, total_sentiments


def _normalize_count(value: object) -> int | None:
	try:
		return int(value)
	except (TypeError, ValueError):
		return None


def _ensure_trend_bucket(buckets: dict[date, dict[str, int]], key: date) -> dict[str, int]:
	if key not in buckets:
		buckets[key] = {"positive": 0, "negative": 0}
	return buckets[key]


async def get_history_trend(
	db: AsyncSession,
	user_id: int,
	*,
	days: int = 30,
) -> list[dict[str, int | str]]:
	days = max(1, min(days, 365))
	now = datetime.utcnow()
	start_day = (now - timedelta(days=days - 1)).replace(
		hour=0,
		minute=0,
		second=0,
		microsecond=0,
	)

	result = await db.execute(
		select(
			AnalysisHistory.created_at,
			AnalysisHistory.source_type,
			AnalysisHistory.result_label,
			AnalysisHistory.label_counts,
			AnalysisHistory.result_payload,
		)
		.where(
			AnalysisHistory.user_id == user_id,
			AnalysisHistory.created_at >= start_day,
		)
	)

	buckets: dict[date, dict[str, int]] = {}

	for created_at, source_type, result_label, label_counts, result_payload in result.all():
		if not isinstance(created_at, datetime):
			continue
		bucket = _ensure_trend_bucket(buckets, created_at.date())

		if source_type == "batch":
			if isinstance(label_counts, dict):
				for key, value in label_counts.items():
					label = _normalize_label(key)
					if label not in {"positive", "negative"}:
						continue
					count_value = _normalize_count(value)
					if count_value is None:
						continue
					bucket[label] += count_value
			elif isinstance(result_payload, list):
				for item in result_payload:
					if not isinstance(item, dict):
						continue
					label = _normalize_label(item.get("label"))
					if label in {"positive", "negative"}:
						bucket[label] += 1
		else:
			label = _normalize_label(result_label)
			if label in {"positive", "negative"}:
				bucket[label] += 1

	items: list[dict[str, int | str]] = []
	for day_offset in range(days):
		day = (start_day + timedelta(days=day_offset)).date()
		counts = buckets.get(day, {"positive": 0, "negative": 0})
		items.append(
			{
				"date": day.isoformat(),
				"positive": counts.get("positive", 0),
				"negative": counts.get("negative", 0),
			}
		)

	return items