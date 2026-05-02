from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


AnalysisHistoryStatus = Literal["queued", "processing", "completed", "failed"]


class AnalysisHistoryItem(BaseModel):
	id: int
	user_id: int
	source_type: str
	source_name: str | None = None
	input_text: str | None = None
	upload_id: int | None = None
	job_id: str | None = None
	status: AnalysisHistoryStatus
	include_scores: bool
	apply_postprocess: bool
	include_meta: bool
	item_count: int | None = None
	result_label: str | None = None
	result_score: float | None = None
	label_counts: dict[str, int] | None = None
	result_payload: dict | list | None = None
	error: str | None = None
	created_at: datetime
	updated_at: datetime

	model_config = ConfigDict(from_attributes=True)


class AnalysisHistoryListResponse(BaseModel):
	items: list[AnalysisHistoryItem]
	count: int
	offset: int
	limit: int


class AnalysisHistoryDetailResponse(BaseModel):
	item: AnalysisHistoryItem