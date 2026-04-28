from __future__ import annotations

import re
import unicodedata
from typing import Iterable, List, Mapping, Optional

import pandas as pd


class TextNormalizationError(ValueError):
	pass


_WORD_PATTERN = re.compile(r"\b\w+\b")
_WHITESPACE_PATTERN = re.compile(r"\s+")

DEFAULT_SLANG_MAP: Mapping[str, str] = {
	"ga": "tidak",
	"gak": "tidak",
	"gk": "tidak",
	"nggak": "tidak",
	"ngga": "tidak",
	"tdk": "tidak",
	"yg": "yang",
	"bgt": "banget",
	"udh": "sudah",
	"udah": "sudah",
	"dgn": "dengan",
	"krn": "karena",
	"sm": "sama",
	"tp": "tapi",
	"trus": "terus",
	"trs": "terus",
	"aja": "saja",
	"kalo": "kalau",
	"gmn": "gimana",
	"gmana": "gimana",
	"dlm": "dalam",
}


def _coerce_text(value: object) -> str:
	if value is None:
		return ""
	return str(value)


def _strip_accents(value: str) -> str:
	normalized = unicodedata.normalize("NFKD", value)
	return "".join(char for char in normalized if not unicodedata.combining(char))


def _reduce_repeated_chars(value: str, max_repeat: int) -> str:
	if max_repeat < 1:
		raise TextNormalizationError("max_repeat must be at least 1.")
	pattern = re.compile(r"(.)\1{%d,}" % max_repeat)
	return pattern.sub(lambda match: match.group(1) * max_repeat, value)


def _prepare_slang_map(
	custom_map: Optional[Mapping[str, str]],
	*,
	use_default: bool,
) -> Mapping[str, str]:
	resolved: dict[str, str] = {}
	if use_default:
		resolved.update(DEFAULT_SLANG_MAP)
	if custom_map:
		resolved.update(custom_map)
	return {
		str(key).strip().lower(): str(value).strip().lower()
		for key, value in resolved.items()
		if str(key).strip()
	}


def _apply_slang_map(value: str, slang_map: Mapping[str, str]) -> str:
	if not slang_map:
		return value

	def _replace(match: re.Match[str]) -> str:
		word = match.group(0)
		replacement = slang_map.get(word)
		if replacement is None and word.lower() != word:
			replacement = slang_map.get(word.lower())
		return replacement if replacement is not None else word

	return _WORD_PATTERN.sub(_replace, value)


def normalize_text(
	text: object,
	*,
	lowercase: bool = True,
	strip_accents: bool = True,
	slang_map: Optional[Mapping[str, str]] = None,
	use_default_slang_map: bool = True,
	reduce_repeated_chars: bool = True,
	max_repeat: int = 2,
	normalize_whitespace: bool = True,
) -> str:
	value = _coerce_text(text).strip()
	if not value:
		return ""

	if lowercase:
		value = value.lower()

	if strip_accents:
		value = _strip_accents(value)

	resolved_map = _prepare_slang_map(slang_map, use_default=use_default_slang_map)
	if resolved_map:
		value = _apply_slang_map(value, resolved_map)

	if reduce_repeated_chars:
		value = _reduce_repeated_chars(value, max_repeat=max_repeat)

	if normalize_whitespace:
		value = _WHITESPACE_PATTERN.sub(" ", value).strip()

	return value


def normalize_texts(
	texts: Iterable[object],
	**kwargs: object,
) -> List[str]:
	return [normalize_text(text, **kwargs) for text in texts]


def normalize_series(
	series: pd.Series,
	**kwargs: object,
) -> pd.Series:
	return series.astype(str).apply(lambda value: normalize_text(value, **kwargs))


def normalize_dataframe(
	df: pd.DataFrame,
	*,
	text_column: str = "text",
	inplace: bool = False,
	**kwargs: object,
) -> pd.DataFrame:
	if text_column not in df.columns:
		raise TextNormalizationError(
			f"Text column '{text_column}' not found. Available columns: {list(df.columns)}"
		)

	result = df if inplace else df.copy()
	result[text_column] = normalize_series(result[text_column], **kwargs)
	return result
