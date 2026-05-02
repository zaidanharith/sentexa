from __future__ import annotations

import csv
import io
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis_history import AnalysisHistory
from app.models.report_feedback_alert import Report


REPORTS_DIR = Path("data/reports")


def _ensure_reports_dir():
	"""Ensure reports directory exists"""
	REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def _get_report_file_path(report_id: int, format: str) -> str:
	"""Generate report file path"""
	_ensure_reports_dir()
	filename = f"report_{report_id}.{format}"
	return str(REPORTS_DIR / filename)


async def get_analysis_history_for_report(
	db: AsyncSession,
	user_id: int,
	*,
	job_id: str | None = None,
	start_date: datetime | None = None,
	end_date: datetime | None = None,
) -> list[AnalysisHistory]:
	"""Query analysis_history based on job_id or date range"""
	filters = [AnalysisHistory.user_id == user_id]
	
	if job_id:
		filters.append(AnalysisHistory.job_id == job_id)
	
	if start_date:
		filters.append(AnalysisHistory.created_at >= start_date)
	
	if end_date:
		filters.append(AnalysisHistory.created_at <= end_date)
	
	result = await db.execute(
		select(AnalysisHistory)
		.where(and_(*filters))
		.order_by(AnalysisHistory.created_at.asc())
	)
	return list(result.scalars().all())


def _generate_csv_content(analyses: list[AnalysisHistory]) -> str:
	"""Generate CSV content from analysis history"""
	output = io.StringIO()
	writer = csv.writer(output)
	
	# Write header
	writer.writerow([
		"ID",
		"Source Type",
		"Source Name",
		"Input Text",
		"Status",
		"Result Label",
		"Result Score",
		"Label Counts",
		"Created At",
	])
	
	# Write data rows
	for analysis in analyses:
		label_counts_str = str(analysis.label_counts) if analysis.label_counts else ""
		writer.writerow([
			analysis.id,
			analysis.source_type,
			analysis.source_name or "",
			analysis.input_text or "",
			analysis.status,
			analysis.result_label or "",
			f"{analysis.result_score:.4f}" if analysis.result_score else "",
			label_counts_str,
			analysis.created_at.isoformat(),
		])
	
	return output.getvalue()


def _save_csv_file(content: str, file_path: str) -> None:
	"""Save CSV content to file"""
	Path(file_path).parent.mkdir(parents=True, exist_ok=True)
	with open(file_path, "w", encoding="utf-8") as f:
		f.write(content)


async def generate_report_file(
	db: AsyncSession,
	report: Report,
	*,
	job_id: str | None = None,
	start_date: datetime | None = None,
	end_date: datetime | None = None,
) -> str:
	"""Generate report file and return file path"""
	# Query analysis data
	analyses = await get_analysis_history_for_report(
		db,
		report.user_id,
		job_id=job_id,
		start_date=start_date,
		end_date=end_date,
	)
	
	if not analyses:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="No analysis data found for this report criteria",
		)
	
	file_path = _get_report_file_path(report.id, report.format)
	
	if report.format == "csv":
		csv_content = _generate_csv_content(analyses)
		_save_csv_file(csv_content, file_path)
	else:
		# PDF support can be added here with reportlab or similar
		raise HTTPException(
			status_code=status.HTTP_501_NOT_IMPLEMENTED,
			detail="PDF format not yet implemented",
		)
	
	return file_path


async def create_report(
	db: AsyncSession,
	*,
	user_id: int,
	title: str,
	description: str | None = None,
	job_id: str | None = None,
	start_date: datetime | None = None,
	end_date: datetime | None = None,
	format: str = "csv",
) -> Report:
	report = Report(
		user_id=user_id,
		title=title,
		description=description,
		job_id=job_id,
		start_date=start_date,
		end_date=end_date,
		format=format,
		status="draft",
	)
	db.add(report)
	await db.flush()
	await db.refresh(report)
	return report


async def get_report(db: AsyncSession, user_id: int, report_id: int) -> Report:
	result = await db.execute(
		select(Report).where(
			Report.id == report_id,
			Report.user_id == user_id,
		)
	)
	report = result.scalar_one_or_none()
	if report is None:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Report not found",
		)
	return report


async def list_reports(
	db: AsyncSession,
	user_id: int,
	*,
	offset: int = 0,
	limit: int = 50,
) -> tuple[list[Report], int]:
	offset = max(offset, 0)
	limit = max(limit, 1)

	count_result = await db.execute(
		select(Report).where(Report.user_id == user_id)
	)
	count = len(count_result.scalars().all())

	result = await db.execute(
		select(Report)
		.where(Report.user_id == user_id)
		.order_by(Report.created_at.desc())
		.offset(offset)
		.limit(limit)
	)
	reports = list(result.scalars().all())
	return reports, count


async def update_report_status(
	db: AsyncSession,
	user_id: int,
	report_id: int,
	*,
	status: str,
	file_path: str | None = None,
) -> Report:
	report = await get_report(db, user_id, report_id)
	report.status = status
	if file_path:
		report.file_path = file_path
	report.updated_at = datetime.utcnow()
	await db.flush()
	await db.refresh(report)
	return report


async def delete_report(db: AsyncSession, user_id: int, report_id: int) -> None:
	report = await get_report(db, user_id, report_id)
	# Delete file if exists
	if report.file_path and os.path.exists(report.file_path):
		os.remove(report.file_path)
	await db.delete(report)
	await db.flush()
