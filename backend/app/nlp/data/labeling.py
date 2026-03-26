from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple

import pandas as pd

from .loaders import DataLoaderError


class DataLabelingError(DataLoaderError):
	"""Raised when label normalization or encoding fails."""


DEFAULT_LABEL_ALIASES: Dict[str, str] = {
	"positive": "positive",
	"positif": "positive",
	"pos": "positive",
	"1": "positive",
	"negative": "negative",
	"negatif": "negative",
	"neg": "negative",
	"-1": "negative",
	"neutral": "neutral",
	"netral": "neutral",
	"neu": "neutral",
	"0": "neutral",
}

DEFAULT_LABEL_TO_ID: Dict[str, int] = {
	"negative": 0,
	"neutral": 1,
	"positive": 2,
}

DEFAULT_POSITIVE_KEYWORDS: Set[str] = {
	"bagus",
	"mantap",
	"baik",
	"suka",
	"cepat",
	"recommended",
	"puas",
	"terbaik",
}

DEFAULT_NEGATIVE_KEYWORDS: Set[str] = {
	"buruk",
	"jelek",
	"lambat",
	"kecewa",
	"parah",
	"rusak",
	"mahal",
	"zonk",
}


@dataclass(frozen=True)
class LabelMapping:
	label_to_id: Dict[str, int]
	id_to_label: Dict[int, str]


def _clean_label(value: object) -> str:
	return str(value).strip().lower()


def normalize_label(
	label: object,
	*,
	aliases: Optional[Mapping[str, str]] = None,
) -> str:
	"""Normalize a raw label into canonical label form."""
	raw = _clean_label(label)
	alias_map = dict(DEFAULT_LABEL_ALIASES)
	if aliases:
		alias_map.update({str(k).strip().lower(): str(v).strip().lower() for k, v in aliases.items()})

	if raw in alias_map:
		return alias_map[raw]

	if raw:
		return raw

	raise DataLabelingError("Label value is empty and cannot be normalized.")


def normalize_label_column(
	df: pd.DataFrame,
	*,
	label_column: str = "label",
	aliases: Optional[Mapping[str, str]] = None,
	inplace: bool = False,
) -> pd.DataFrame:
	"""Normalize all label values in dataframe label column."""
	if label_column not in df.columns:
		raise DataLabelingError(
			f"Label column '{label_column}' not found. Available columns: {list(df.columns)}"
		)

	result = df if inplace else df.copy()
	result[label_column] = result[label_column].apply(
		lambda value: normalize_label(value, aliases=aliases)
	)
	return result


def build_label_mapping(
	labels: Iterable[object],
	*,
	preferred_order: Optional[Sequence[str]] = None,
) -> LabelMapping:
	"""Build deterministic label <-> id mapping."""
	normalized = [normalize_label(label) for label in labels]
	unique_labels = sorted(set(normalized))

	if not unique_labels:
		raise DataLabelingError("Cannot build label mapping from empty labels.")

	if preferred_order:
		order_lookup = {label: index for index, label in enumerate(preferred_order)}
		unique_labels = sorted(
			unique_labels,
			key=lambda label: (order_lookup.get(label, len(order_lookup)), label),
		)

	label_to_id = {label: idx for idx, label in enumerate(unique_labels)}
	id_to_label = {idx: label for label, idx in label_to_id.items()}
	return LabelMapping(label_to_id=label_to_id, id_to_label=id_to_label)


def encode_labels(
	labels: Iterable[object],
	*,
	label_to_id: Optional[Mapping[str, int]] = None,
) -> List[int]:
	"""Encode raw labels into integer classes."""
	resolved_map = dict(label_to_id) if label_to_id else dict(DEFAULT_LABEL_TO_ID)
	encoded: List[int] = []

	for value in labels:
		normalized = normalize_label(value)
		if normalized not in resolved_map:
			raise DataLabelingError(
				f"Unknown label '{normalized}'. Known labels: {sorted(resolved_map.keys())}"
			)
		encoded.append(int(resolved_map[normalized]))

	return encoded


def decode_labels(
	encoded_labels: Iterable[int],
	*,
	id_to_label: Optional[Mapping[int, str]] = None,
) -> List[str]:
	"""Decode integer classes back into string labels."""
	resolved_map = dict(id_to_label) if id_to_label else {
		value: key for key, value in DEFAULT_LABEL_TO_ID.items()
	}
	decoded: List[str] = []

	for value in encoded_labels:
		if value not in resolved_map:
			raise DataLabelingError(
				f"Unknown encoded label '{value}'. Known ids: {sorted(resolved_map.keys())}"
			)
		decoded.append(str(resolved_map[value]))

	return decoded


def validate_supported_labels(
	labels: Iterable[object],
	*,
	allowed_labels: Optional[Iterable[str]] = None,
) -> Tuple[bool, List[str]]:
	"""Validate labels against allowed classes and return unknown labels if any."""
	allowed = set(allowed_labels or DEFAULT_LABEL_TO_ID.keys())
	normalized_allowed = {normalize_label(label) for label in allowed}

	unknown = sorted(
		{
			normalize_label(label)
			for label in labels
			if normalize_label(label) not in normalized_allowed
		}
	)

	return len(unknown) == 0, unknown


def auto_label_text(
	text: str,
	*,
	positive_keywords: Optional[Iterable[str]] = None,
	negative_keywords: Optional[Iterable[str]] = None,
) -> str:
	"""Assign a simple sentiment label based on keyword matching."""
	if not text or not str(text).strip():
		return "neutral"

	content = str(text).lower()
	positive = set(positive_keywords or DEFAULT_POSITIVE_KEYWORDS)
	negative = set(negative_keywords or DEFAULT_NEGATIVE_KEYWORDS)

	positive_score = sum(1 for keyword in positive if keyword in content)
	negative_score = sum(1 for keyword in negative if keyword in content)

	if positive_score > negative_score:
		return "positive"
	if negative_score > positive_score:
		return "negative"
	return "neutral"


def auto_label_dataframe(
	df: pd.DataFrame,
	*,
	text_column: str = "text",
	output_label_column: str = "label",
	positive_keywords: Optional[Iterable[str]] = None,
	negative_keywords: Optional[Iterable[str]] = None,
	inplace: bool = False,
) -> pd.DataFrame:
	"""Generate labels from text using simple keyword-based rules."""
	if text_column not in df.columns:
		raise DataLabelingError(
			f"Text column '{text_column}' not found. Available columns: {list(df.columns)}"
		)

	result = df if inplace else df.copy()
	result[output_label_column] = result[text_column].astype(str).apply(
		lambda value: auto_label_text(
			value,
			positive_keywords=positive_keywords,
			negative_keywords=negative_keywords,
		)
	)
	return result
