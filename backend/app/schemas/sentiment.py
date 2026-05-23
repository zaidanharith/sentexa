from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SentimentPredictRequest(BaseModel):
	text: str
	include_scores: bool = True


class SentimentPrediction(BaseModel):
	label: str
	label_id: int | str | None = None
	score: float | None = None
	scores: dict[str, float] | None = None

	model_config = ConfigDict(from_attributes=True)


class SentimentPredictResponse(SentimentPrediction):
	pass


class SentimentBatchPredictRequest(BaseModel):
	texts: list[str]
	include_scores: bool = True


SentimentJobStatus = Literal["queued", "processing", "completed", "failed"]


class SentimentJobSummary(BaseModel):
	job_id: str
	status: SentimentJobStatus
	total: int
	completed: int
	created_at: datetime
	updated_at: datetime
	label_counts: dict[str, int] | None = None
	error: str | None = None


class SentimentJobListResponse(BaseModel):
	items: list[SentimentJobSummary]
	count: int


class SentimentJobCreateResponse(BaseModel):
	job: SentimentJobSummary


class SentimentJobDetailResponse(BaseModel):
	job: SentimentJobSummary


class SentimentJobResult(BaseModel):
	index: int
	text: str
	prediction: SentimentPrediction


class SentimentJobResultsResponse(BaseModel):
	items: list[SentimentJobResult]
	count: int
	total: int
	offset: int
	limit: int


class SentimentJobReprocessRequest(BaseModel):
	include_scores: bool = True
