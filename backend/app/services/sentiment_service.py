from __future__ import annotations

from typing import Iterable, List, Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ml.model.predict import PredictionError, predict_text, predict_texts
from app.models.user import User


class SentimentServiceError(ValueError):
	pass


def _ensure_text(value: object, *, index: Optional[int] = None) -> str:
	if value is None:
		message = "Text is required."
	else:
		text = str(value)
		if text.strip():
			return text
		message = "Text is empty."

	if index is not None:
		message = f"Text at index {index} is empty."

	raise HTTPException(
		status_code=status.HTTP_400_BAD_REQUEST,
		detail=message,
	)


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
		resolved.append(_ensure_text(item, index=idx))
	return resolved


def analyze_text(
	text: object,
	*,
	include_scores: bool = True,
	db: Optional[AsyncSession] = None,
	user: Optional[User] = None,
) -> dict[str, object]:
	validated = _ensure_text(text)
	try:
		result = predict_text(
			validated,
			include_scores=include_scores,
		)
		return result
	except PredictionError as exc:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Prediction failed: {exc}",
		) from exc


def analyze_texts(
	texts: Iterable[object],
	*,
	include_scores: bool = True,
	db: Optional[AsyncSession] = None,
	user: Optional[User] = None,
) -> list[dict[str, object]]:
	validated = _coerce_texts(texts)
	try:
		result = predict_texts(
			validated,
			include_scores=include_scores,
		)
		return result
	except PredictionError as exc:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Prediction failed: {exc}",
		) from exc
