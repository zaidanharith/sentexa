from __future__ import annotations

from collections.abc import Iterable as IterableABC
from typing import Iterable, List, Optional, Tuple

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer


class TfidfFeatureError(ValueError):
	pass


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


def _identity(value: object) -> object:
	return value


def _prepare_corpus(texts: Iterable[object], *, pretokenized: bool) -> List[object]:
	if pretokenized:
		return [_coerce_tokens(text) for text in texts]
	return [_coerce_text(text) for text in texts]


def _resolve_pretokenized(
	vectorizer: TfidfVectorizer,
	pretokenized: Optional[bool],
) -> bool:
	if pretokenized is not None:
		return pretokenized
	return bool(getattr(vectorizer, "_sentexa_pretokenized", False))


def create_tfidf_vectorizer(
	*,
	pretokenized: bool = False,
	lowercase: bool = True,
	max_features: Optional[int] = None,
	ngram_range: Tuple[int, int] = (1, 1),
	min_df: int | float = 1,
	max_df: int | float = 1.0,
	use_idf: bool = True,
	smooth_idf: bool = True,
	sublinear_tf: bool = False,
	norm: Optional[str] = "l2",
	stop_words: Optional[Iterable[str]] = None,
	token_pattern: Optional[str] = None,
) -> TfidfVectorizer:
	if ngram_range[0] < 1 or ngram_range[1] < ngram_range[0]:
		raise TfidfFeatureError("ngram_range must be a tuple like (1, 2).")

	vectorizer_kwargs = {
		"lowercase": lowercase and not pretokenized,
		"max_features": max_features,
		"ngram_range": ngram_range,
		"min_df": min_df,
		"max_df": max_df,
		"use_idf": use_idf,
		"smooth_idf": smooth_idf,
		"sublinear_tf": sublinear_tf,
		"norm": norm,
		"stop_words": list(stop_words) if stop_words else None,
	}

	if pretokenized:
		vectorizer_kwargs.update(
			{
				"tokenizer": _identity,
				"preprocessor": _identity,
				"token_pattern": None,
			}
		)
	elif token_pattern:
		vectorizer_kwargs["token_pattern"] = token_pattern

	vectorizer = TfidfVectorizer(**vectorizer_kwargs)
	setattr(vectorizer, "_sentexa_pretokenized", pretokenized)
	return vectorizer


def fit_tfidf_vectorizer(
	texts: Iterable[object],
	*,
	pretokenized: bool = False,
	**kwargs: object,
) -> TfidfVectorizer:
	vectorizer = create_tfidf_vectorizer(pretokenized=pretokenized, **kwargs)
	corpus = _prepare_corpus(texts, pretokenized=pretokenized)
	vectorizer.fit(corpus)
	return vectorizer


def tfidf_fit_transform(
	texts: Iterable[object],
	*,
	pretokenized: bool = False,
	**kwargs: object,
):
	vectorizer = create_tfidf_vectorizer(pretokenized=pretokenized, **kwargs)
	corpus = _prepare_corpus(texts, pretokenized=pretokenized)
	features = vectorizer.fit_transform(corpus)
	return vectorizer, features


def tfidf_transform(
	vectorizer: TfidfVectorizer,
	texts: Iterable[object],
	*,
	pretokenized: Optional[bool] = None,
):
	resolved = _resolve_pretokenized(vectorizer, pretokenized)
	corpus = _prepare_corpus(texts, pretokenized=resolved)
	return vectorizer.transform(corpus)


def tfidf_fit_transform_series(
	series: pd.Series,
	*,
	pretokenized: bool = False,
	**kwargs: object,
):
	return tfidf_fit_transform(series.tolist(), pretokenized=pretokenized, **kwargs)


def tfidf_transform_series(
	vectorizer: TfidfVectorizer,
	series: pd.Series,
	*,
	pretokenized: Optional[bool] = None,
):
	return tfidf_transform(vectorizer, series.tolist(), pretokenized=pretokenized)


def tfidf_fit_transform_dataframe(
	df: pd.DataFrame,
	*,
	text_column: str = "text",
	pretokenized: bool = False,
	**kwargs: object,
):
	if text_column not in df.columns:
		raise TfidfFeatureError(
			f"Input column '{text_column}' not found. Available columns: {list(df.columns)}"
		)
	return tfidf_fit_transform(df[text_column].tolist(), pretokenized=pretokenized, **kwargs)


def tfidf_transform_dataframe(
	vectorizer: TfidfVectorizer,
	df: pd.DataFrame,
	*,
	text_column: str = "text",
	pretokenized: Optional[bool] = None,
):
	if text_column not in df.columns:
		raise TfidfFeatureError(
			f"Input column '{text_column}' not found. Available columns: {list(df.columns)}"
		)
	return tfidf_transform(vectorizer, df[text_column].tolist(), pretokenized=pretokenized)


def get_feature_names(vectorizer: TfidfVectorizer) -> List[str]:
	return [str(value) for value in vectorizer.get_feature_names_out()]
