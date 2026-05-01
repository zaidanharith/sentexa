from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, Mapping, MutableMapping, Optional, Sequence, Tuple


class PostprocessError(ValueError):
	pass


@dataclass(frozen=True)
class PostprocessRuleSet:
	min_confidence: Optional[float] = None
	per_label_min_confidence: Mapping[str, float] = field(default_factory=dict)
	fallback_label: str = "neutral"
	label_merge: Mapping[str, str] = field(default_factory=dict)
	label_aliases: Mapping[str, str] = field(default_factory=dict)
	blocked_labels: Sequence[str] = field(default_factory=tuple)
	label_priority: Sequence[str] = field(default_factory=tuple)
	prefer_scores: bool = True
	normalize_scores: bool = True
	label_to_id: Mapping[str, object] = field(default_factory=dict)
	id_to_label: Mapping[object, str] = field(default_factory=dict)


DEFAULT_RULES = PostprocessRuleSet(
	label_aliases={
		"positif": "positive",
		"negatif": "negative",
		"netral": "neutral",
	},
)


def _to_float(value: object) -> Optional[float]:
	try:
		return float(value)
	except (TypeError, ValueError):
		return None


def _apply_merge(label: str, label_merge: Mapping[str, str]) -> str:
	seen = set()
	current = label
	while current in label_merge and current not in seen:
		seen.add(current)
		current = label_merge[current]
	return current


def _canonical_label(value: object, rules: PostprocessRuleSet) -> str:
	if value in rules.id_to_label:
		return _apply_merge(rules.id_to_label[value], rules.label_merge)
	value_str = str(value)
	if value_str in rules.id_to_label:
		return _apply_merge(rules.id_to_label[value_str], rules.label_merge)
	label = rules.label_aliases.get(value_str, value_str)
	return _apply_merge(label, rules.label_merge)


def _coerce_scores(
	scores: Mapping[object, object],
	rules: PostprocessRuleSet,
) -> Dict[str, float]:
	result: Dict[str, float] = {}
	for key, value in scores.items():
		score = _to_float(value)
		if score is None:
			continue
		label = _canonical_label(key, rules)
		result[label] = result.get(label, 0.0) + score
	return result


def _normalize_scores(scores: Dict[str, float]) -> Dict[str, float]:
	if not scores:
		return scores
	denom = sum(value for value in scores.values() if value > 0.0)
	if denom <= 0.0:
		return scores
	return {key: value / denom for key, value in scores.items()}


def _resolve_priority_map(priorities: Sequence[str]) -> Dict[str, int]:
	return {label: index for index, label in enumerate(priorities)}


def _pick_label_from_scores(
	scores: Mapping[str, float],
	*,
	priorities: Sequence[str] = (),
) -> Optional[str]:
	if not scores:
		return None
	priority_map = _resolve_priority_map(priorities)
	items = sorted(
		scores.items(),
		key=lambda item: (-item[1], priority_map.get(item[0], 10**6), item[0]),
	)
	return items[0][0]


def _resolve_threshold(label: str, rules: PostprocessRuleSet) -> Optional[float]:
	if label in rules.per_label_min_confidence:
		return rules.per_label_min_confidence[label]
	return rules.min_confidence


def postprocess_prediction(
	prediction: Mapping[str, object],
	*,
	rules: PostprocessRuleSet = DEFAULT_RULES,
	include_meta: bool = False,
) -> Dict[str, object]:
	if not prediction:
		raise PostprocessError("prediction is empty.")

	label_raw = prediction.get("label", "")
	label_id = prediction.get("label_id")
	label = _canonical_label(label_raw, rules) if label_raw else ""
	label_from_id = _canonical_label(label_id, rules) if label_id is not None else ""
	if not label and label_from_id:
		label = label_from_id

	provided_scores = prediction.get("scores")
	if isinstance(provided_scores, Mapping):
		scores = _coerce_scores(provided_scores, rules)
		if rules.normalize_scores:
			scores = _normalize_scores(scores)
	else:
		scores = {}

	selected_label = label
	if rules.prefer_scores:
		picked = _pick_label_from_scores(scores, priorities=rules.label_priority)
		if picked:
			selected_label = picked

	if selected_label in rules.blocked_labels:
		selected_label = rules.fallback_label

	selected_label = _apply_merge(selected_label or rules.fallback_label, rules.label_merge)
	selected_label = rules.label_aliases.get(selected_label, selected_label)

	score_value = _to_float(prediction.get("score"))
	if selected_label in scores:
		score_value = scores[selected_label]

	threshold = _resolve_threshold(selected_label, rules)
	if threshold is not None and score_value is not None and score_value < threshold:
		selected_label = rules.fallback_label
		selected_label = _apply_merge(selected_label, rules.label_merge)
		selected_label = rules.label_aliases.get(selected_label, selected_label)
		if selected_label in scores:
			score_value = scores[selected_label]
		else:
			score_value = 0.0

	resolved_label_id = label_id
	if rules.label_to_id and selected_label in rules.label_to_id:
		resolved_label_id = rules.label_to_id[selected_label]

	result: Dict[str, object] = dict(prediction)
	result["label"] = selected_label
	result["label_id"] = resolved_label_id
	if score_value is not None:
		result["score"] = float(score_value)
	if scores:
		result["scores"] = scores

	if include_meta:
		result["postprocess"] = {
			"label_before": str(label_raw),
			"label_after": selected_label,
			"threshold": threshold,
		}

	return result


def postprocess_predictions(
	predictions: Iterable[Mapping[str, object]],
	*,
	rules: PostprocessRuleSet = DEFAULT_RULES,
	include_meta: bool = False,
) -> list[Dict[str, object]]:
	return [
		postprocess_prediction(prediction, rules=rules, include_meta=include_meta)
		for prediction in predictions
	]


class SentimentPostprocessor:
	def __init__(self, rules: PostprocessRuleSet = DEFAULT_RULES) -> None:
		self._rules = rules

	def apply(self, prediction: Mapping[str, object], *, include_meta: bool = False) -> Dict[str, object]:
		return postprocess_prediction(prediction, rules=self._rules, include_meta=include_meta)

	def apply_batch(
		self,
		predictions: Iterable[Mapping[str, object]],
		*,
		include_meta: bool = False,
	) -> list[Dict[str, object]]:
		return postprocess_predictions(predictions, rules=self._rules, include_meta=include_meta)
