from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


SentimentLabel = Literal["positive", "negative", "neutral"]


class KeywordItem(BaseModel):
	word: str
	count: int


class KeywordResponse(BaseModel):
	items: list[KeywordItem]
	sentiment: SentimentLabel | None = None
	job_id: str | None = None
