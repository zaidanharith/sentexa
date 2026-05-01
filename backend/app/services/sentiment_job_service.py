from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import Lock
from typing import Iterable, List, Optional, Tuple
from uuid import uuid4

from fastapi import HTTPException, status

from app.nlp.inference.postprocess import PostprocessRuleSet
from app.services import sentiment_service


@dataclass
class SentimentJob:
	job_id: str
	user_id: int
	texts: List[str]
	status: str
	created_at: datetime
	updated_at: datetime
	total: int
	completed: int = 0
	items: List[dict] = field(default_factory=list)
	label_counts: dict[str, int] = field(default_factory=dict)
	error: Optional[str] = None
	include_scores: bool = True
	apply_postprocess: bool = True
	include_meta: bool = False
	rules: Optional[PostprocessRuleSet] = None


_JOB_STORE: dict[str, SentimentJob] = {}
_STORE_LOCK = Lock()


def _now() -> datetime:
	return datetime.now(timezone.utc)


def _coerce_texts(texts: Iterable[object]) -> List[str]:
	if isinstance(texts, (str, bytes)):
		items: List[object] = [texts]
	else:
		items = list(texts)
	if not items:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="texts is empty.",
		)

	resolved: List[str] = []
	for idx, item in enumerate(items):
		if item is None:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail=f"Text at index {idx} is empty.",
			)
		value = str(item)
		if not value.strip():
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail=f"Text at index {idx} is empty.",
			)
		resolved.append(value)
	return resolved


def _store_job(job: SentimentJob) -> None:
	with _STORE_LOCK:
		_JOB_STORE[job.job_id] = job


def _get_job(job_id: str) -> SentimentJob:
	with _STORE_LOCK:
		job = _JOB_STORE.get(job_id)
	if job is None:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Job not found",
		)
	return job


def _ensure_owner(job: SentimentJob, user_id: int) -> None:
	if job.user_id != user_id:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Job not found",
		)


def _build_label_counts(items: List[dict]) -> dict[str, int]:
	counts: dict[str, int] = {}
	for item in items:
		prediction = item.get("prediction", {})
		label = prediction.get("label")
		if label is None:
			continue
		label_str = str(label)
		counts[label_str] = counts.get(label_str, 0) + 1
	return counts


def _build_items(texts: List[str], predictions: List[dict]) -> List[dict]:
	items: List[dict] = []
	for idx, (text, prediction) in enumerate(zip(texts, predictions)):
		items.append(
			{
				"index": idx,
				"text": text,
				"prediction": prediction,
			}
		)
	return items


def create_job(
	*,
	user_id: int,
	texts: Iterable[object],
	include_scores: bool = True,
	apply_postprocess: bool = True,
	include_meta: bool = False,
	rules: Optional[PostprocessRuleSet] = None,
) -> SentimentJob:
	resolved_texts = _coerce_texts(texts)
	now = _now()
	job = SentimentJob(
		job_id=uuid4().hex,
		user_id=user_id,
		texts=resolved_texts,
		status="queued",
		created_at=now,
		updated_at=now,
		total=len(resolved_texts),
		completed=0,
		items=[],
		label_counts={},
		error=None,
		include_scores=include_scores,
		apply_postprocess=apply_postprocess,
		include_meta=include_meta,
		rules=rules,
	)
	_store_job(job)
	return job


def run_job(job_id: str) -> None:
	job = _get_job(job_id)
	job.status = "processing"
	job.updated_at = _now()

	try:
		predictions = sentiment_service.analyze_texts(
			job.texts,
			include_scores=job.include_scores,
			apply_postprocess=job.apply_postprocess,
			include_meta=job.include_meta,
			rules=job.rules,
		)
		items = _build_items(job.texts, predictions)
		job.items = items
		job.completed = len(items)
		job.label_counts = _build_label_counts(items)
		job.status = "completed"
		job.error = None
		job.updated_at = _now()
		_store_job(job)
		return
	except HTTPException as exc:
		job.status = "failed"
		job.error = str(exc.detail)
	except Exception as exc:
		job.status = "failed"
		job.error = str(exc)

	job.updated_at = _now()
	_store_job(job)


def list_jobs(user_id: int) -> List[SentimentJob]:
	with _STORE_LOCK:
		jobs = [job for job in _JOB_STORE.values() if job.user_id == user_id]
	jobs.sort(key=lambda item: item.created_at, reverse=True)
	return jobs


def get_job(user_id: int, job_id: str) -> SentimentJob:
	job = _get_job(job_id)
	_ensure_owner(job, user_id)
	return job


def get_job_results(
	user_id: int,
	job_id: str,
	*,
	offset: int = 0,
	limit: int = 50,
) -> Tuple[List[dict], int]:
	job = get_job(user_id, job_id)
	offset = max(offset, 0)
	limit = max(limit, 1)
	total = len(job.items)
	end = min(offset + limit, total)
	return job.items[offset:end], total


def reprocess_job(
	user_id: int,
	job_id: str,
	*,
	include_scores: bool = True,
	apply_postprocess: bool = True,
	include_meta: bool = False,
	rules: Optional[PostprocessRuleSet] = None,
) -> SentimentJob:
	job = get_job(user_id, job_id)
	job.include_scores = include_scores
	job.apply_postprocess = apply_postprocess
	job.include_meta = include_meta
	job.rules = rules
	job.status = "queued"
	job.completed = 0
	job.items = []
	job.label_counts = {}
	job.error = None
	job.updated_at = _now()
	_store_job(job)
	return job


def serialize_job(job: SentimentJob) -> dict[str, object]:
	return {
		"job_id": job.job_id,
		"status": job.status,
		"total": job.total,
		"completed": job.completed,
		"created_at": job.created_at,
		"updated_at": job.updated_at,
		"label_counts": job.label_counts or None,
		"error": job.error,
	}
