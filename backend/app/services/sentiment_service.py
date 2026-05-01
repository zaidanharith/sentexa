from __future__ import annotations

from dataclasses import replace
from typing import Iterable, List, Mapping, Optional, Sequence, Tuple

from fastapi import HTTPException, status

from app.nlp.inference.postprocess import (
	DEFAULT_RULES,
	PostprocessError,
	PostprocessRuleSet,
	postprocess_prediction,
	postprocess_predictions,
)
from app.nlp.inference.predictor import (
	ModelArtifacts,
	PredictionError,
	get_default_artifacts,
	predict_text,
	predict_texts,
)


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


def _build_label_maps(label_map: Mapping[object, str]) -> Tuple[dict[str, object], dict[object, str]]:
	label_to_id: dict[str, object] = {}
	id_to_label: dict[object, str] = {}
	for key, value in label_map.items():
		label = str(value)
		id_to_label[key] = label
		if label not in label_to_id or isinstance(key, int):
			label_to_id[label] = key
	return label_to_id, id_to_label


def _resolve_rules(
	rules: Optional[PostprocessRuleSet],
	artifacts: Optional[ModelArtifacts],
) -> PostprocessRuleSet:
	resolved = rules or DEFAULT_RULES
	if artifacts is None or not artifacts.label_map:
		return resolved

	label_to_id = resolved.label_to_id
	id_to_label = resolved.id_to_label
	if not label_to_id or not id_to_label:
		derived_label_to_id, derived_id_to_label = _build_label_maps(artifacts.label_map)
		label_to_id = label_to_id or derived_label_to_id
		id_to_label = id_to_label or derived_id_to_label
		resolved = replace(resolved, label_to_id=label_to_id, id_to_label=id_to_label)
	return resolved


def get_default_rules(*, artifacts: Optional[ModelArtifacts] = None) -> PostprocessRuleSet:
	resolved_artifacts = artifacts or get_default_artifacts()
	return _resolve_rules(DEFAULT_RULES, resolved_artifacts)


def analyze_text(
	text: object,
	*,
	artifacts: Optional[ModelArtifacts] = None,
	include_scores: bool = True,
	apply_postprocess: bool = True,
	rules: Optional[PostprocessRuleSet] = None,
	include_meta: bool = False,
) -> dict[str, object]:
	validated = _ensure_text(text)
	resolved_artifacts = artifacts or get_default_artifacts()

	try:
		prediction = predict_text(
			validated,
			artifacts=resolved_artifacts,
			include_scores=include_scores,
		)
	except PredictionError as exc:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Prediction failed: {exc}",
		) from exc

	if not apply_postprocess:
		return prediction

	resolved_rules = _resolve_rules(rules, resolved_artifacts)
	try:
		return postprocess_prediction(
			prediction,
			rules=resolved_rules,
			include_meta=include_meta,
		)
	except PostprocessError as exc:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Postprocess failed: {exc}",
		) from exc


def analyze_texts(
	texts: Iterable[object],
	*,
	artifacts: Optional[ModelArtifacts] = None,
	include_scores: bool = True,
	apply_postprocess: bool = True,
	rules: Optional[PostprocessRuleSet] = None,
	include_meta: bool = False,
) -> list[dict[str, object]]:
	validated = _coerce_texts(texts)
	resolved_artifacts = artifacts or get_default_artifacts()

	try:
		predictions = predict_texts(
			validated,
			artifacts=resolved_artifacts,
			include_scores=include_scores,
		)
	except PredictionError as exc:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Prediction failed: {exc}",
		) from exc

	if not apply_postprocess:
		return predictions

	resolved_rules = _resolve_rules(rules, resolved_artifacts)
	try:
		return postprocess_predictions(
			predictions,
			rules=resolved_rules,
			include_meta=include_meta,
		)
	except PostprocessError as exc:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Postprocess failed: {exc}",
		) from exc
