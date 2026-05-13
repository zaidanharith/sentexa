from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.user import User

from app.schemas.sentiment import (
	SentimentBatchPredictRequest,
	SentimentBatchPredictResponse,
	SentimentJobCreateResponse,
	SentimentJobDetailResponse,
	SentimentJobListResponse,
	SentimentJobReprocessRequest,
	SentimentJobResultsResponse,
	SentimentPredictRequest,
	SentimentPredictResponse,
)
from app.services import analysis_history_service, sentiment_job_service, sentiment_service, subscription_service


router = APIRouter(prefix="/sentiment", tags=["sentiment"])


def _build_label_counts(items: list[dict]) -> dict[str, int]:
	counts: dict[str, int] = {}
	for item in items:
		prediction = item.get("prediction", {})
		label = prediction.get("label")
		if label is None:
			continue
		label_str = str(label)
		counts[label_str] = counts.get(label_str, 0) + 1
	return counts


@router.post("/predict", response_model=SentimentPredictResponse)
async def predict_sentiment(
	payload: SentimentPredictRequest,
	db: AsyncSession = Depends(deps.get_db),
	current_user: User = Depends(deps.get_current_user),
):
	await subscription_service.validate_and_reduce_quota(db, current_user, 1)
	
	result = sentiment_service.analyze_text(
		payload.text,
		include_scores=payload.include_scores,
	)
	await analysis_history_service.create_history(
		db,
		user_id=current_user.id,
		source_type="text",
		input_text=payload.text,
		status="completed",
		include_scores=payload.include_scores,
		result_label=result.get("label") if isinstance(result, dict) else None,
		result_score=result.get("score") if isinstance(result, dict) else None,
		result_payload=result,
	)
	await db.commit()
	return result


@router.post("/predict/batch", response_model=SentimentBatchPredictResponse)
async def predict_sentiment_batch(
	payload: SentimentBatchPredictRequest,
	db: AsyncSession = Depends(deps.get_db),
	current_user: User = Depends(deps.get_current_user),
):
	quota_needed = len(payload.texts)
	await subscription_service.validate_and_reduce_quota(db, current_user, quota_needed)
	
	items = sentiment_service.analyze_texts(
		payload.texts,
		include_scores=payload.include_scores,
	)
	await analysis_history_service.create_history(
		db,
		user_id=current_user.id,
		source_type="batch",
		input_text="\n".join(payload.texts),
		status="completed",
		include_scores=payload.include_scores,
		item_count=len(items),
		label_counts=_build_label_counts(items),
		result_payload=items,
	)
	await db.commit()
	return SentimentBatchPredictResponse(items=items, count=len(items))

@router.post("/predict/jobs", response_model=SentimentJobCreateResponse)
async def create_sentiment_job(
    payload: SentimentBatchPredictRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    quota_needed = len(payload.texts)
    await subscription_service.validate_and_reduce_quota(db, current_user, quota_needed)
    
    job = await sentiment_job_service.create_job(
        db,
        user_id=current_user.id,
        texts=payload.texts,
        include_scores=payload.include_scores,
    )
    await db.commit()

    await analysis_history_service.create_history(
        db,
        user_id=current_user.id,
        source_type="job",
        job_id=str(job.id),
        input_text="\n".join([str(t) for t in payload.texts]),
        status="queued",
        include_scores=payload.include_scores,
        item_count=job.total_texts,
    )
    await db.commit()

    background_tasks.add_task(sentiment_job_service.run_job, job.id)

    return SentimentJobCreateResponse(job=sentiment_job_service.serialize_job(job))


@router.get("/predict/jobs", response_model=SentimentJobListResponse)
async def list_sentiment_jobs(
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db),
):
    jobs = await sentiment_job_service.list_jobs(db, current_user.id)
    items = [sentiment_job_service.serialize_job(job) for job in jobs]
    return SentimentJobListResponse(items=items, count=len(items))


@router.get("/predict/jobs/{job_id}", response_model=SentimentJobDetailResponse)
async def get_sentiment_job(
    job_id: int,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db),
):
    job = await sentiment_job_service.get_job(db, current_user.id, job_id)
    return SentimentJobDetailResponse(job=sentiment_job_service.serialize_job(job))


@router.get("/predict/jobs/{job_id}/results", response_model=SentimentJobResultsResponse)
async def get_sentiment_job_results(
    job_id: int,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db),
):
    items, total = await sentiment_job_service.get_job_results(
        db,
        current_user.id,
        job_id,
        offset=offset,
        limit=limit,
    )
    return SentimentJobResultsResponse(
        items=items,
        count=len(items),
        total=total,
        offset=offset,
        limit=limit,
    )


@router.post("/predict/jobs/{job_id}/reprocess", response_model=SentimentJobDetailResponse)
async def reprocess_sentiment_job(
    job_id: int,
    payload: SentimentJobReprocessRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    job = await sentiment_job_service.reprocess_job(db, current_user.id, job_id)
    await db.commit()
    
    await analysis_history_service.upsert_job_history(
        db,
        user_id=current_user.id,
        job_id=str(job.id),
        defaults={
			"source_type": "job",
            "item_count": job.total_texts,
        },
        updates={
            "status": "queued",
            "include_scores": payload.include_scores,
            "error": None,
        },
    )
    await db.commit()
    
    background_tasks.add_task(sentiment_job_service.run_job, job.id)
    
    return SentimentJobDetailResponse(job=sentiment_job_service.serialize_job(job))
