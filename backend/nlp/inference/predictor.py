from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from ..features.tfidf import tfidf_transform
from ..preprocessing.cleaning import clean_text
from ..preprocessing.normalization import normalize_text
from ..preprocessing.stopwords import remove_stopwords_text
from ..preprocessing.tokenization import tokenize_text
from ..preprocessing.stemming import stem_tokens


class PredictionError(ValueError):
	pass


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
FEATURES_DIR = PROCESSED_DIR / "features"
CLASSIFIER_DIR = PROCESSED_DIR / "models" / "classifier"

DEFAULT_VECTORIZER_PATH = FEATURES_DIR / "tfidf_vectorizer.joblib"


CLEANING_OPTIONS = {
	"lowercase": True,
	"remove_html": True,
	"remove_urls": True,
	"remove_mentions": True,
	"hashtag_mode": "keep",
	"remove_emojis": True,
	"remove_punctuation": True,
	"remove_numbers": False,
	"reduce_repeated_chars": True,
	"normalize_whitespace": True,
}

NORMALIZATION_OPTIONS = {
	"lowercase": True,
	"strip_accents": True,
	"use_default_slang_map": True,
	"reduce_repeated_chars": True,
	"max_repeat": 2,
	"normalize_whitespace": True,
}

STOPWORDS_OPTIONS = {
	"use_default_stopwords": True,
	"lowercase": True,
	"normalize_whitespace": True,
}

TOKENIZATION_OPTIONS = {
	"lowercase": True,
	"keep_numbers": True,
	"min_token_length": 1,
	"custom_pattern": None,
}

STEMMING_OPTIONS = {
	"lowercase": True,
	"drop_empty": True,
}


@dataclass(frozen=True)
class ModelArtifacts:
	model: Any
	vectorizer: TfidfVectorizer
	label_map: Dict[object, str]
	feature_type: str
	metadata: Dict[str, Any]


def _load_json(path: Path) -> Dict[str, Any]:
	if not path.exists():
		return {}
	with path.open("r", encoding="utf-8") as file_obj:
		return json.load(file_obj)


def _rebase_container_path(path: Path, project_root: Path) -> Optional[Path]:
	parts = list(path.parts)
	if "app" not in parts:
		return None
	idx = len(parts) - 1 - list(reversed(parts)).index("app")
	relative = Path(*parts[idx:])
	candidate = project_root / relative
	if candidate.exists():
		return candidate
	return None


def _resolve_artifact_path(
	path_value: Optional[str | Path],
	*,
	default: Path,
	project_root: Path,
) -> Path:
	if path_value:
		candidate = Path(path_value)
		if candidate.exists():
			return candidate
		if not candidate.is_absolute():
			candidate = (project_root / candidate).resolve()
			if candidate.exists():
				return candidate
		rebased = _rebase_container_path(candidate, project_root)
		if rebased is not None:
			return rebased
	return default


def _normalize_label_map(raw: Optional[Mapping[object, object]]) -> Dict[object, str]:
	if not raw:
		return {}

	result: Dict[object, str] = {}
	for key, value in raw.items():
		label = str(value)
		result[key] = label
		if isinstance(key, str):
			if key.isdigit():
				result[int(key)] = label
		else:
			result[str(key)] = label
	return result


def _label_for_id(label_map: Mapping[object, str], label_id: object) -> str:
	if label_id in label_map:
		return label_map[label_id]
	label_str = str(label_id)
	if label_str in label_map:
		return label_map[label_str]
	return label_str


def _sigmoid(values: np.ndarray) -> np.ndarray:
	clipped = np.clip(values, -50.0, 50.0)
	return 1.0 / (1.0 + np.exp(-clipped))


def _softmax(values: np.ndarray) -> np.ndarray:
	values = np.asarray(values, dtype=float)
	if values.ndim == 1:
		values = values.reshape(1, -1)
	max_vals = np.max(values, axis=1, keepdims=True)
	exp_vals = np.exp(values - max_vals)
	return exp_vals / np.sum(exp_vals, axis=1, keepdims=True)


def _resolve_class_labels(model: Any, count: int) -> List[object]:
	if hasattr(model, "classes_"):
		return list(model.classes_)
	return list(range(count))


def _compute_probabilities(model: Any, features) -> Tuple[Optional[np.ndarray], List[object]]:
	if hasattr(model, "predict_proba"):
		probs = np.asarray(model.predict_proba(features), dtype=float)
		return probs, _resolve_class_labels(model, probs.shape[1])

	if hasattr(model, "decision_function"):
		scores = np.asarray(model.decision_function(features), dtype=float)
		if scores.ndim == 1:
			pos = _sigmoid(scores)
			probs = np.column_stack([1.0 - pos, pos])
		else:
			probs = _softmax(scores)
		return probs, _resolve_class_labels(model, probs.shape[1])

	return None, _resolve_class_labels(model, 0)


def _resolve_class_index(class_labels: Sequence[object], pred: object) -> Optional[int]:
	if pred in class_labels:
		return class_labels.index(pred)
	pred_str = str(pred)
	for idx, value in enumerate(class_labels):
		if str(value) == pred_str:
			return idx
	return None


def _build_scores_map(
	probabilities: np.ndarray,
	class_labels: Sequence[object],
	label_map: Mapping[object, str],
) -> Dict[str, float]:
	scores: Dict[str, float] = {}
	for label_id, score in zip(class_labels, probabilities):
		label = _label_for_id(label_map, label_id)
		scores[label] = float(score)
	return scores


def preprocess_text(text: object) -> List[str]:
	value = clean_text(text, **CLEANING_OPTIONS)
	value = normalize_text(value, **NORMALIZATION_OPTIONS)
	value = remove_stopwords_text(value, **STOPWORDS_OPTIONS)
	tokens = tokenize_text(value, **TOKENIZATION_OPTIONS)
	return stem_tokens(tokens, **STEMMING_OPTIONS)


def preprocess_texts(texts: Iterable[object]) -> List[List[str]]:
	return [preprocess_text(text) for text in texts]


def _prepare_corpus(tokens_list: List[List[str]], vectorizer: TfidfVectorizer) -> List[object]:
	use_pretokenized = bool(getattr(vectorizer, "_sentexa_pretokenized", False))
	if use_pretokenized:
		return tokens_list
	return [" ".join(tokens) for tokens in tokens_list]


def load_classifier_artifacts(
	*,
	model_dir: Optional[str | Path] = None,
	model_path: Optional[str | Path] = None,
	vectorizer_path: Optional[str | Path] = None,
	metadata_path: Optional[str | Path] = None,
) -> ModelArtifacts:
	resolved_dir = Path(model_dir) if model_dir else CLASSIFIER_DIR
	resolved_metadata = Path(metadata_path) if metadata_path else (resolved_dir / "classifier_metadata.json")
	metadata = _load_json(resolved_metadata)

	feature_type = str(metadata.get("best_feature", "tfidf"))
	label_map = _normalize_label_map(metadata.get("label_map"))
	artifact_paths = metadata.get("artifact_paths", {}) if isinstance(metadata, dict) else {}

	resolved_vectorizer = _resolve_artifact_path(
		artifact_paths.get("tfidf_vectorizer") if isinstance(artifact_paths, dict) else None,
		default=Path(vectorizer_path) if vectorizer_path else DEFAULT_VECTORIZER_PATH,
		project_root=PROJECT_ROOT,
	)
	resolved_model = _resolve_artifact_path(
		metadata.get("model_path") if isinstance(metadata, dict) else None,
		default=Path(model_path) if model_path else (resolved_dir / "classifier_model.joblib"),
		project_root=PROJECT_ROOT,
	)

	if not resolved_model.exists():
		raise PredictionError(f"Model file not found: {resolved_model}")
	if not resolved_vectorizer.exists():
		raise PredictionError(f"Vectorizer file not found: {resolved_vectorizer}")

	model = joblib.load(resolved_model)
	vectorizer = joblib.load(resolved_vectorizer)
	if not isinstance(vectorizer, TfidfVectorizer):
		raise PredictionError("Loaded vectorizer is not a TfidfVectorizer.")

	return ModelArtifacts(
		model=model,
		vectorizer=vectorizer,
		label_map=label_map,
		feature_type=feature_type,
		metadata=metadata,
	)


@lru_cache(maxsize=1)
def get_default_artifacts() -> ModelArtifacts:
	return load_classifier_artifacts()


def predict_texts(
	texts: Iterable[object],
	*,
	artifacts: Optional[ModelArtifacts] = None,
	include_scores: bool = True,
) -> List[Dict[str, object]]:
	if isinstance(texts, (str, bytes)):
		text_list = [texts]
	else:
		text_list = list(texts)
	if not text_list:
		raise PredictionError("texts is empty.")

	resolved_artifacts = artifacts or get_default_artifacts()
	tokens_list = preprocess_texts(text_list)
	corpus = _prepare_corpus(tokens_list, resolved_artifacts.vectorizer)
	use_pretokenized = bool(getattr(resolved_artifacts.vectorizer, "_sentexa_pretokenized", False))
	features = tfidf_transform(
		resolved_artifacts.vectorizer,
		corpus,
		pretokenized=use_pretokenized,
	)

	preds = resolved_artifacts.model.predict(features)
	pred_list = preds.tolist() if hasattr(preds, "tolist") else list(preds)
	probabilities, class_labels = _compute_probabilities(resolved_artifacts.model, features)
	label_map = resolved_artifacts.label_map

	results: List[Dict[str, object]] = []
	for idx, pred in enumerate(pred_list):
		label = _label_for_id(label_map, pred)
		item: Dict[str, object] = {
			"label": label,
			"label_id": pred,
		}
		if probabilities is not None:
			class_index = _resolve_class_index(class_labels, pred)
			score = float(probabilities[idx][class_index]) if class_index is not None else float(
				np.max(probabilities[idx])
			)
			item["score"] = score
			if include_scores:
				item["scores"] = _build_scores_map(
					probabilities[idx],
					class_labels,
					label_map,
				)
		results.append(item)

	return results


def predict_text(
	text: object,
	*,
	artifacts: Optional[ModelArtifacts] = None,
	include_scores: bool = True,
) -> Dict[str, object]:
	return predict_texts(
		[text],
		artifacts=artifacts,
		include_scores=include_scores,
	)[0]


class SentimentPredictor:
	def __init__(self, artifacts: Optional[ModelArtifacts] = None) -> None:
		self._artifacts = artifacts or get_default_artifacts()

	def predict(self, text: object, *, include_scores: bool = True) -> Dict[str, object]:
		return predict_text(text, artifacts=self._artifacts, include_scores=include_scores)

	def predict_batch(
		self,
		texts: Iterable[object],
		*,
		include_scores: bool = True,
	) -> List[Dict[str, object]]:
		return predict_texts(texts, artifacts=self._artifacts, include_scores=include_scores)
