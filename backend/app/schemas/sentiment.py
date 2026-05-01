from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SentimentPredictRequest(BaseModel):
	text: str
	include_scores: bool = True
	apply_postprocess: bool = True
	include_meta: bool = False


class SentimentPostprocessMeta(BaseModel):
	label_before: str
	label_after: str
	threshold: float | None = None


class SentimentPrediction(BaseModel):
	label: str
	label_id: int | str | None = None
	score: float | None = None
	scores: dict[str, float] | None = None
	postprocess: SentimentPostprocessMeta | None = None

	model_config = ConfigDict(from_attributes=True)


class SentimentPredictResponse(SentimentPrediction):
	pass


class SentimentBatchPredictRequest(BaseModel):
	texts: list[str]
	include_scores: bool = True
	apply_postprocess: bool = True
	include_meta: bool = False


class SentimentBatchPredictResponse(BaseModel):
	items: list[SentimentPrediction]
	count: int


class PostprocessRules(BaseModel):
	min_confidence: float | None = None
	per_label_min_confidence: dict[str, float] = Field(default_factory=dict)
	fallback_label: str = "neutral"
	label_merge: dict[str, str] = Field(default_factory=dict)
	label_aliases: dict[str, str] = Field(default_factory=dict)
	blocked_labels: list[str] = Field(default_factory=list)
	label_priority: list[str] = Field(default_factory=list)
	prefer_scores: bool = True
	normalize_scores: bool = True
	label_to_id: dict[str, int | str] = Field(default_factory=dict)
	id_to_label: dict[str, str] = Field(default_factory=dict)


class SentimentPostprocessRequest(BaseModel):
	predictions: list[SentimentPrediction]
	rules: PostprocessRules | None = None
	include_meta: bool = False


class SentimentPostprocessResponse(BaseModel):
	items: list[SentimentPrediction]
	count: int


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
	apply_postprocess: bool = True
	include_meta: bool = False
	rules: PostprocessRules | None = None
