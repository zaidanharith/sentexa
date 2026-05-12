from __future__ import annotations

import re
from functools import lru_cache
from collections.abc import Iterable as IterableABC
from typing import Iterable, List, Optional

from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

import pandas as pd


class TextStemmingError(ValueError):
    pass


_WHITESPACE_PATTERN = re.compile(r"\s+")
_STEMMER = StemmerFactory().create_stemmer()


@lru_cache(maxsize=50000)
def _stem_cached(value: str) -> str:
    return _STEMMER.stem(value)


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


def stem_text(
        text: object,
        *,
        lowercase: bool = True,
        normalize_whitespace: bool = True,
) -> str:
    value = _coerce_text(text).strip()
    if not value:
        return ""

    if lowercase:
        value = value.lower()

    value = _stem_cached(value)

    if normalize_whitespace:
        value = _WHITESPACE_PATTERN.sub(" ", value).strip()

    return value


def stem_texts(
        texts: Iterable[object],
        **kwargs: object,
) -> List[str]:
    return [stem_text(text, **kwargs) for text in texts]


def stem_tokens(
        tokens: Iterable[object],
        *,
        lowercase: bool = True,
        drop_empty: bool = True,
) -> List[str]:
    result: List[str] = []

    for token in tokens:
        value = _coerce_text(token).strip()
        if not value:
            if not drop_empty:
                result.append("")
            continue
        if lowercase:
            value = value.lower()
        stemmed = _stem_cached(value)
        if stemmed or not drop_empty:
            result.append(stemmed)

    return result


def stem_tokens_list(
        items: Iterable[Iterable[object]],
        **kwargs: object,
) -> List[List[str]]:
    return [stem_tokens(tokens, **kwargs) for tokens in items]


def stem_series(
        series: pd.Series,
        **kwargs: object,
) -> pd.Series:
    return series.astype(str).apply(lambda value: stem_text(value, **kwargs))


def stem_tokens_series(
        series: pd.Series,
        **kwargs: object,
) -> pd.Series:
    return series.apply(lambda value: stem_tokens(_coerce_tokens(value), **kwargs))


def stem_dataframe(
        df: pd.DataFrame,
        *,
        text_column: str = "text",
        inplace: bool = False,
        **kwargs: object,
) -> pd.DataFrame:
    if text_column not in df.columns:
        raise TextStemmingError(
            f"Text column '{text_column}' not found. Available columns: {list(df.columns)}")

    result = df if inplace else df.copy()
    result[text_column] = stem_series(result[text_column], **kwargs)
    return result


def stem_tokens_dataframe(
        df: pd.DataFrame,
        *,
        tokens_column: str = "tokens",
        output_column: Optional[str] = "stems",
        inplace: bool = False,
        **kwargs: object,
) -> pd.DataFrame:
    if tokens_column not in df.columns:
        raise TextStemmingError(
            f"Tokens column '{tokens_column}' not found. Available columns: {list(df.columns)}")

    if inplace and output_column and output_column != tokens_column:
        raise TextStemmingError(
            "output_column must match tokens_column when inplace=True.")

    result = df if inplace else df.copy()
    column = output_column or tokens_column
    result[column] = stem_tokens_series(result[tokens_column], **kwargs)
    return result
