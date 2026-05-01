from __future__ import annotations

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
