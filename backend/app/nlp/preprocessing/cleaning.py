from __future__ import annotations

import html
import re
from typing import Iterable, List

import pandas as pd


class TextCleaningError(ValueError):
    pass


_URL_PATTERN = re.compile(r"(https?://\S+|www\.\S+)", re.IGNORECASE)
_MENTION_PATTERN = re.compile(r"@\w+")
_HASHTAG_PATTERN = re.compile(r"#(\w+)")
_HTML_TAG_PATTERN = re.compile(r"<[^>]+>")
_CONTROL_CHARS_PATTERN = re.compile(r"[\x00-\x1f\x7f]")
_REPEAT_CHARS_PATTERN = re.compile(r"(.)\1{2,}")
_WHITESPACE_PATTERN = re.compile(r"\s+")
_NON_ALNUM_PATTERN = re.compile(r"[^0-9A-Za-z\s]")
_NON_ALPHA_PATTERN = re.compile(r"[^A-Za-z\s]")
_NUM_PATTERN = re.compile(r"\d+")
_EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F700-\U0001F77F"
    "\U0001F780-\U0001F7FF"
    "\U0001F800-\U0001F8FF"
    "\U0001F900-\U0001F9FF"
    "\U0001FA00-\U0001FA6F"
    "\U0001FA70-\U0001FAFF"
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "]+",
    flags=re.UNICODE,
)


def _coerce_text(value: object) -> str:
    if value is None:
        return ""
    return str(value)


def clean_text(
        text: object,
        *,
        lowercase: bool = True,
        remove_html: bool = True,
        remove_urls: bool = True,
        remove_mentions: bool = True,
        hashtag_mode: str = "keep",
        remove_emojis: bool = True,
        remove_punctuation: bool = True,
        remove_numbers: bool = False,
        reduce_repeated_chars: bool = True,
        normalize_whitespace: bool = True,
) -> str:
    value = _coerce_text(text).strip()
    if not value:
        return ""

    if remove_html:
        value = html.unescape(value)
        value = _HTML_TAG_PATTERN.sub(" ", value)

    value = _CONTROL_CHARS_PATTERN.sub(" ", value)

    if remove_urls:
        value = _URL_PATTERN.sub(" ", value)

    if remove_mentions:
        value = _MENTION_PATTERN.sub(" ", value)

    if hashtag_mode not in {"keep", "remove"}:
        raise TextCleaningError("hashtag_mode must be 'keep' or 'remove'.")
    if hashtag_mode == "keep":
        value = _HASHTAG_PATTERN.sub(r"\1", value)
    else:
        value = _HASHTAG_PATTERN.sub(" ", value)

    if remove_emojis:
        value = _EMOJI_PATTERN.sub(" ", value)

    if reduce_repeated_chars:
        value = _REPEAT_CHARS_PATTERN.sub(r"\1\1", value)

    if lowercase:
        value = value.lower()

    if remove_punctuation:
        if remove_numbers:
            value = _NON_ALPHA_PATTERN.sub(" ", value)
        else:
            value = _NON_ALNUM_PATTERN.sub(" ", value)
    elif remove_numbers:
        value = _NUM_PATTERN.sub(" ", value)

    if normalize_whitespace:
        value = _WHITESPACE_PATTERN.sub(" ", value).strip()

    return value


def clean_texts(
        texts: Iterable[object],
        **kwargs: object,
) -> List[str]:
    return [clean_text(text, **kwargs) for text in texts]


def clean_series(
        series: pd.Series,
        **kwargs: object,
) -> pd.Series:
    return series.astype(str).apply(lambda value: clean_text(value, **kwargs))


def clean_dataframe(
        df: pd.DataFrame,
        *,
        text_column: str = "text",
        inplace: bool = False,
        **kwargs: object,
) -> pd.DataFrame:
    if text_column not in df.columns:
        raise TextCleaningError(
            f"Text column '{text_column}' not found. Available columns: {list(df.columns)}")

    result = df if inplace else df.copy()
    result[text_column] = clean_series(result[text_column], **kwargs)
    return result
