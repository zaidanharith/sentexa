from __future__ import annotations

import re
from typing import Iterable, List, Optional

import pandas as pd


class TokenizationError(ValueError):
	pass


_WHITESPACE_PATTERN = re.compile(r"\s+")


def _coerce_text(value: object) -> str:
	if value is None:
		return ""
	return str(value)


def _build_pattern(keep_numbers: bool, custom_pattern: Optional[str]) -> re.Pattern[str]:
	if custom_pattern:
		return re.compile(custom_pattern, flags=re.UNICODE)
	if keep_numbers:
		return re.compile(r"[^\W_]+", flags=re.UNICODE)
	return re.compile(r"[^\W\d_]+", flags=re.UNICODE)


def tokenize_text(
	text: object,
	*,
	lowercase: bool = True,
	keep_numbers: bool = True,
	min_token_length: int = 1,
	custom_pattern: Optional[str] = None,
) -> List[str]:
	if min_token_length < 1:
		raise TokenizationError("min_token_length must be at least 1.")

	value = _coerce_text(text)
	value = _WHITESPACE_PATTERN.sub(" ", value).strip()
	if not value:
		return []

	if lowercase:
		value = value.lower()

	pattern = _build_pattern(keep_numbers, custom_pattern)
	tokens = [token for token in pattern.findall(value) if len(token) >= min_token_length]
	return tokens


def tokenize_texts(
	texts: Iterable[object],
	**kwargs: object,
) -> List[List[str]]:
	return [tokenize_text(text, **kwargs) for text in texts]


def tokenize_series(
	series: pd.Series,
	**kwargs: object,
) -> pd.Series:
	return series.astype(str).apply(lambda value: tokenize_text(value, **kwargs))


def tokenize_dataframe(
	df: pd.DataFrame,
	*,
	text_column: str = "text",
	output_column: str = "tokens",
	inplace: bool = False,
	**kwargs: object,
) -> pd.DataFrame:
	if text_column not in df.columns:
		raise TokenizationError(f"Text column '{text_column}' not found. Available columns: {list(df.columns)}")

	result = df if inplace else df.copy()
	result[output_column] = tokenize_series(result[text_column], **kwargs)
	return result
