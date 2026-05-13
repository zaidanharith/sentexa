from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable, List, Optional, Tuple
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.sentiment_job import SentimentJob as SentimentJobModel
from app.models.sentiment_job import SentimentJobResult

from app.services import analysis_history_service
from app.services import sentiment_service


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


async def create_job(
    db: AsyncSession,
    *,
    user_id: int,
    texts: Iterable[object],
    include_scores: bool = True,
) -> SentimentJobModel:
    """Create a new sentiment job in database"""
    resolved_texts = _coerce_texts(texts)
    now = _now()
    
    job = SentimentJobModel(
        user_id=user_id,
        status="queued",
        total_texts=len(resolved_texts),
        completed_count=0,
        created_at=now,
        updated_at=now,
    )
    db.add(job)
    await db.flush()
    await db.refresh(job)
    
    for idx, text in enumerate(resolved_texts):
        result = SentimentJobResult(
            job_id=job.id,
            index=idx,
            text=text,
            label="pending",
        )
        db.add(result)
    
    await db.flush()
    return job


async def get_job(db: AsyncSession, user_id: int, job_db_id: int) -> SentimentJobModel:
    result = await db.execute(
        select(SentimentJobModel).where(
            SentimentJobModel.id == job_db_id,
            SentimentJobModel.user_id == user_id,
        )
    )
    job = result.scalar_one_or_none()
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )
    return job


async def list_jobs(db: AsyncSession, user_id: int) -> List[SentimentJobModel]:
    result = await db.execute(
        select(SentimentJobModel)
        .where(SentimentJobModel.user_id == user_id)
        .order_by(SentimentJobModel.created_at.desc())
    )
    return list(result.scalars().all())


async def get_job_results(
    db: AsyncSession,
    user_id: int,
    job_db_id: int,
    *,
    offset: int = 0,
    limit: int = 50,
) -> Tuple[List[dict], int]:
    job = await get_job(db, user_id, job_db_id)
    
    offset = max(offset, 0)
    limit = max(limit, 1)
    
    count_result = await db.execute(
        select(SentimentJobResult).where(SentimentJobResult.job_id == job_db_id)
    )
    total = len(count_result.scalars().all())
    
    result = await db.execute(
        select(SentimentJobResult)
        .where(SentimentJobResult.job_id == job_db_id)
        .order_by(SentimentJobResult.index.asc())
        .offset(offset)
        .limit(limit)
    )
    results = list(result.scalars().all())
    
    items = [
        {
            "index": r.index,
            "text": r.text,
            "prediction": {
                "label": r.label,
                "label_id": r.label_id,
                "score": r.score,
                "scores": r.scores,
            }
        }
        for r in results
    ]
    
    return items, total


async def run_job(job_db_id: int) -> None:
    async with AsyncSessionLocal() as db:
        try:
            job_result = await db.execute(
                select(SentimentJobModel).where(SentimentJobModel.id == job_db_id)
            )
            job = job_result.scalar_one_or_none()
            if not job:
                return
            
            job.status = "processing"
            job.updated_at = _now()
            await db.flush()
            
            texts_result = await db.execute(
                select(SentimentJobResult)
                .where(SentimentJobResult.job_id == job_db_id)
                .order_by(SentimentJobResult.index.asc())
            )
            job_results = list(texts_result.scalars().all())
            texts = [r.text for r in job_results]
            
            await analysis_history_service.upsert_job_history(
                db,
                user_id=job.user_id,
                job_id=str(job.id),
                defaults={
                    "source_type": "job",
                    "input_text": "\n".join(texts),
                    "item_count": len(texts),
                },
                updates={"status": "processing", "error": None},
            )
            await db.commit()
            
            predictions = sentiment_service.analyze_texts(
                texts,
                include_scores=True,
            )
            
            for idx, (job_result, prediction) in enumerate(zip(job_results, predictions)):
                job_result.label = prediction.get("label", "neutral")
                job_result.label_id = prediction.get("label_id")
                job_result.score = prediction.get("score")
                job_result.scores = prediction.get("scores")
            
            label_counts = _build_label_counts([
                {"prediction": p} for p in predictions
            ])
            
            job.status = "completed"
            job.completed_count = len(predictions)
            job.label_counts = label_counts
            job.error = None
            job.updated_at = _now()
            await db.flush()
            
            await analysis_history_service.upsert_job_history(
                db,
                user_id=job.user_id,
                job_id=str(job.id),
                defaults={
                    "source_type": "job",
                    "input_text": "\n".join(texts),
                    "item_count": len(texts),
                },
                updates={
                    "status": "completed",
                    "label_counts": label_counts,
                    "result_payload": [
                        {
                            "index": idx,
                            "text": text,
                            "prediction": pred,
                        }
                        for idx, (text, pred) in enumerate(zip(texts, predictions))
                    ],
                    "error": None,
                },
            )
            await db.commit()
            
        except Exception as exc:
            async with AsyncSessionLocal() as err_db:
                job_result = await err_db.execute(
                    select(SentimentJobModel).where(SentimentJobModel.id == job_db_id)
                )
                job = job_result.scalar_one_or_none()
                if job:
                    job.status = "failed"
                    job.error = str(exc)
                    job.updated_at = _now()
                    await err_db.flush()
                    
                    await analysis_history_service.upsert_job_history(
                        err_db,
                        user_id=job.user_id,
                        job_id=str(job.id),
                        defaults={"source_type": "job", "item_count": job.total_texts},
                        updates={"status": "failed", "error": str(exc)},
                    )
                    await err_db.commit()


async def reprocess_job(
    db: AsyncSession,
    user_id: int,
    job_db_id: int,
) -> SentimentJobModel:
    job = await get_job(db, user_id, job_db_id)
    
    results_result = await db.execute(
        select(SentimentJobResult).where(SentimentJobResult.job_id == job_db_id)
    )
    results = list(results_result.scalars().all())
    for r in results:
        r.label = "pending"
        r.label_id = None
        r.score = None
        r.scores = None
    
    job.status = "queued"
    job.completed_count = 0
    job.label_counts = {}
    job.error = None
    job.updated_at = _now()
    await db.flush()
    
    return job


def serialize_job(job: SentimentJobModel) -> dict[str, object]:
    return {
        "job_id": str(job.id),
        "status": job.status,
        "total": job.total_texts,
        "completed": job.completed_count,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
        "label_counts": job.label_counts or None,
        "error": job.error,
    }