from __future__ import annotations

from dataclasses import replace

from fastapi import APIRouter, Depends, HTTPException, status

from app.api import deps
from app.models.user import User
from app.nlp.inference.postprocess import PostprocessError, PostprocessRuleSet, postprocess_predictions
from app.schemas.sentiment import (
	PostprocessRules,
	SentimentBatchPredictRequest,
	SentimentBatchPredictResponse,
	SentimentPostprocessRequest,
	SentimentPostprocessResponse,
	SentimentPredictRequest,
	SentimentPredictResponse,
)
from app.services import sentiment_service


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
