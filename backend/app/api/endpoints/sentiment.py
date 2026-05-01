from __future__ import annotations

from dataclasses import replace

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status

from app.api import deps
from app.models.user import User
from app.nlp.inference.postprocess import PostprocessError, PostprocessRuleSet, postprocess_predictions
from app.schemas.sentiment import (
	PostprocessRules,
	SentimentBatchPredictRequest,
	SentimentBatchPredictResponse,
	SentimentJobCreateResponse,
	SentimentJobDetailResponse,
	SentimentJobListResponse,
	SentimentJobReprocessRequest,
	SentimentJobResultsResponse,
	SentimentPostprocessRequest,
	SentimentPostprocessResponse,
	SentimentPredictRequest,
	SentimentPredictResponse,
)
from app.services import sentiment_job_service, sentiment_service


router = APIRouter(prefix="/sentiment", tags=["sentiment"])


def _resolve_postprocess_rules(rules: PostprocessRules | None) -> PostprocessRuleSet | None:
	if rules is None:
		return None

	base = sentiment_service.get_default_rules()
	updates = {field: getattr(rules, field) for field in rules.model_fields_set}
	if not updates:
		return base
	return replace(base, **updates)


@router.post("/predict", response_model=SentimentPredictResponse)
async def predict_sentiment(
	payload: SentimentPredictRequest,
	current_user: User = Depends(deps.get_current_user),
):
	_ = current_user
	result = sentiment_service.analyze_text(
		payload.text,
		include_scores=payload.include_scores,
		apply_postprocess=payload.apply_postprocess,
		include_meta=payload.include_meta,
	)
	return result


@router.post("/predict/batch", response_model=SentimentBatchPredictResponse)
async def predict_sentiment_batch(
	payload: SentimentBatchPredictRequest,
	current_user: User = Depends(deps.get_current_user),
):
	_ = current_user
	items = sentiment_service.analyze_texts(
		payload.texts,
		include_scores=payload.include_scores,
		apply_postprocess=payload.apply_postprocess,
		include_meta=payload.include_meta,
	)
	return SentimentBatchPredictResponse(items=items, count=len(items))


@router.post("/postprocess", response_model=SentimentPostprocessResponse)
async def postprocess_sentiment(
	payload: SentimentPostprocessRequest,
	current_user: User = Depends(deps.get_current_user),
):
	_ = current_user
	resolved_rules = _resolve_postprocess_rules(payload.rules) or sentiment_service.get_default_rules()
	predictions = [prediction.model_dump() for prediction in payload.predictions]

	try:
		items = postprocess_predictions(
			predictions,
			rules=resolved_rules,
			include_meta=payload.include_meta,
		)
	except PostprocessError as exc:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Postprocess failed: {exc}",
		) from exc

	return SentimentPostprocessResponse(items=items, count=len(items))


@router.post("/predict/jobs", response_model=SentimentJobCreateResponse)
async def create_sentiment_job(
	payload: SentimentBatchPredictRequest,
	background_tasks: BackgroundTasks,
	current_user: User = Depends(deps.get_current_user),
):
	job = sentiment_job_service.create_job(
		user_id=current_user.id,
		texts=payload.texts,
		include_scores=payload.include_scores,
		apply_postprocess=payload.apply_postprocess,
		include_meta=payload.include_meta,
	)
	background_tasks.add_task(sentiment_job_service.run_job, job.job_id)
	return SentimentJobCreateResponse(job=sentiment_job_service.serialize_job(job))


@router.get("/predict/jobs", response_model=SentimentJobListResponse)
async def list_sentiment_jobs(current_user: User = Depends(deps.get_current_user)):
	jobs = sentiment_job_service.list_jobs(current_user.id)
	items = [sentiment_job_service.serialize_job(job) for job in jobs]
	return SentimentJobListResponse(items=items, count=len(items))


@router.get("/predict/jobs/{job_id}", response_model=SentimentJobDetailResponse)
async def get_sentiment_job(
	job_id: str,
	current_user: User = Depends(deps.get_current_user),
):
	job = sentiment_job_service.get_job(current_user.id, job_id)
	return SentimentJobDetailResponse(job=sentiment_job_service.serialize_job(job))


@router.get("/predict/jobs/{job_id}/results", response_model=SentimentJobResultsResponse)
async def get_sentiment_job_results(
	job_id: str,
	offset: int = Query(0, ge=0),
	limit: int = Query(50, ge=1, le=1000),
	current_user: User = Depends(deps.get_current_user),
):
	items, total = sentiment_job_service.get_job_results(
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
	job_id: str,
	payload: SentimentJobReprocessRequest,
	background_tasks: BackgroundTasks,
	current_user: User = Depends(deps.get_current_user),
):
	resolved_rules = _resolve_postprocess_rules(payload.rules) or sentiment_service.get_default_rules()
	job = sentiment_job_service.reprocess_job(
		current_user.id,
		job_id,
		include_scores=payload.include_scores,
		apply_postprocess=payload.apply_postprocess,
		include_meta=payload.include_meta,
		rules=resolved_rules,
	)
	background_tasks.add_task(sentiment_job_service.run_job, job.job_id)
	return SentimentJobDetailResponse(job=sentiment_job_service.serialize_job(job))
