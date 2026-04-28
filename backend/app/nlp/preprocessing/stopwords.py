from __future__ import annotations

import re
from collections.abc import Iterable as IterableABC
from pathlib import Path
from typing import Iterable, List, Optional, Set

from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

import pandas as pd


class StopwordError(ValueError):
	pass


_WHITESPACE_PATTERN = re.compile(r"\s+")
_DEFAULT_STOPWORDS: Optional[Set[str]] = None

def _coerce_text(value: object) -> str:
	if value is None:
		return ""
	return str(value)


def _coerce_tokens(value: object) -> List[str]:
	if value is None:
		return []
	if isinstance(value, (list, tuple, set)):
		return [str(item) for item in value]
	if isinstance(value, str):
		return value.split()
	if isinstance(value, IterableABC):
		return [str(item) for item in value]
	return str(value).split()


def _get_default_stopwords() -> Set[str]:
	global _DEFAULT_STOPWORDS
	if _DEFAULT_STOPWORDS is not None:
		return set(_DEFAULT_STOPWORDS)

	factory = StopWordRemoverFactory()
	_DEFAULT_STOPWORDS = {word.strip().lower() for word in factory.get_stop_words() if word.strip()}
	return set(_DEFAULT_STOPWORDS)


def _resolve_stopwords(
	*,
	stopwords: Optional[Iterable[str]] = None,
	stopwords_file: Optional[str | Path] = None,
	use_default: bool = True,
	additional_stopwords: Optional[Iterable[str]] = None,
	remove_stopwords: Optional[Iterable[str]] = None,
) -> Set[str]:
	resolved: Set[str] = set()
	if use_default:
		resolved.update(_get_default_stopwords())
	if stopwords:
		resolved.update(str(word).strip().lower() for word in stopwords if str(word).strip())
	if additional_stopwords:
		resolved.update(str(word).strip().lower() for word in additional_stopwords if str(word).strip())
	if remove_stopwords:
		resolved.difference_update(
			{str(word).strip().lower() for word in remove_stopwords if str(word).strip()}
		)
	return resolved


def remove_stopwords_text(
	text: object,
	*,
	stopwords: Optional[Iterable[str]] = None,
	stopwords_file: Optional[str | Path] = None,
	use_default_stopwords: bool = True,
	additional_stopwords: Optional[Iterable[str]] = None,
	remove_stopwords: Optional[Iterable[str]] = None,
	lowercase: bool = True,
	normalize_whitespace: bool = True,
) -> str:
	value = _coerce_text(text).strip()
	if not value:
		return ""

	if lowercase:
		value = value.lower()

	resolved = _resolve_stopwords(
		stopwords=stopwords,
		stopwords_file=stopwords_file,
		use_default=use_default_stopwords,
		additional_stopwords=additional_stopwords,
		remove_stopwords=remove_stopwords,
	)

	tokens = [token for token in value.split() if token not in resolved]
	result = " ".join(tokens)
	if normalize_whitespace:
		result = _WHITESPACE_PATTERN.sub(" ", result).strip()
	return result


def remove_stopwords_texts(
	texts: Iterable[object],
	**kwargs: object,
) -> List[str]:
	return [remove_stopwords_text(text, **kwargs) for text in texts]


def remove_stopwords_tokens(
	tokens: Iterable[object],
	*,
	stopwords: Optional[Iterable[str]] = None,
	stopwords_file: Optional[str | Path] = None,
	use_default_stopwords: bool = True,
	additional_stopwords: Optional[Iterable[str]] = None,
	remove_stopwords: Optional[Iterable[str]] = None,
	lowercase: bool = True,
) -> List[str]:
	resolved = _resolve_stopwords(
		stopwords=stopwords,
		stopwords_file=stopwords_file,
		use_default=use_default_stopwords,
		additional_stopwords=additional_stopwords,
		remove_stopwords=remove_stopwords,
	)

	result: List[str] = []
	for token in tokens:
		value = _coerce_text(token).strip()
		if not value:
			continue
		if lowercase:
			value = value.lower()
		if value not in resolved:
			result.append(value)
	return result


def remove_stopwords_tokens_list(
	items: Iterable[Iterable[object]],
	**kwargs: object,
) -> List[List[str]]:
	return [remove_stopwords_tokens(tokens, **kwargs) for tokens in items]


def remove_stopwords_series(
	series: pd.Series,
	**kwargs: object,
) -> pd.Series:
	return series.astype(str).apply(lambda value: remove_stopwords_text(value, **kwargs))


def remove_stopwords_tokens_series(
	series: pd.Series,
	**kwargs: object,
) -> pd.Series:
	return series.apply(lambda value: remove_stopwords_tokens(_coerce_tokens(value), **kwargs))


def remove_stopwords_dataframe(
	df: pd.DataFrame,
	*,
	text_column: str = "text",
	inplace: bool = False,
	**kwargs: object,
) -> pd.DataFrame:
	if text_column not in df.columns:
		raise StopwordError(f"Text column '{text_column}' not found. Available columns: {list(df.columns)}")

	result = df if inplace else df.copy()
	result[text_column] = remove_stopwords_series(result[text_column], **kwargs)
	return result


def remove_stopwords_tokens_dataframe(
	df: pd.DataFrame,
	*,
	tokens_column: str = "tokens",
	output_column: Optional[str] = "tokens",
	inplace: bool = False,
	**kwargs: object,
) -> pd.DataFrame:
	if tokens_column not in df.columns:
		raise StopwordError(f"Tokens column '{tokens_column}' not found. Available columns: {list(df.columns)}")

	if inplace and output_column and output_column != tokens_column:
		raise StopwordError("output_column must match tokens_column when inplace=True.")

	result = df if inplace else df.copy()
	column = output_column or tokens_column
	result[column] = remove_stopwords_tokens_series(result[tokens_column], **kwargs)
	return result
