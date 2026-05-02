from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


ReportStatus = Literal["draft", "processing", "completed", "failed"]
ReportFormat = Literal["csv", "pdf"]


class ReportOut(BaseModel):
	id: int
	user_id: int
	title: str
	description: str | None = None
	job_id: str | None = None
	start_date: datetime | None = None
	end_date: datetime | None = None
	status: ReportStatus
	format: ReportFormat
	file_path: str | None = None
	created_at: datetime
	updated_at: datetime

	model_config = ConfigDict(from_attributes=True)


class ReportListResponse(BaseModel):
	items: list[ReportOut]
	count: int
	offset: int
	limit: int


class ReportDetailResponse(BaseModel):
	report: ReportOut


class GenerateReportRequest(BaseModel):
	title: str = Field(..., min_length=1, max_length=255)
	description: str | None = Field(default=None, max_length=1000)
	job_id: str | None = None
	start_date: datetime | None = None
	end_date: datetime | None = None
	format: ReportFormat = Field(default="csv")
