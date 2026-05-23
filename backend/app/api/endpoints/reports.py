from datetime import datetime
import os
from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.user import User
from app.schemas.report import (
	GenerateReportRequest,
	ReportDetailResponse,
	ReportListResponse,
	ReportOut,
	UpdateReportRequest,
)
from app.services import report_service


router = APIRouter(prefix="/reports", tags=["reports"])


async def _process_report_generation(
	db: AsyncSession,
	report_id: int,
	user_id: int,
	*,
	job_id: str | None = None,
	start_date: datetime | None = None,
	end_date: datetime | None = None,
):
	try:
		from app.core.database import AsyncSessionLocal
		async with AsyncSessionLocal() as session:
			report = await report_service.get_report(session, user_id, report_id)
			file_path = await report_service.generate_report_file(
				session,
				report,
				job_id=job_id,
				start_date=start_date,
				end_date=end_date,
			)
			await report_service.update_report_status(
				session,
				user_id,
				report_id,
				status="completed",
				file_path=file_path,
			)
			await session.commit()
	except Exception as e:
		from app.core.database import AsyncSessionLocal
		async with AsyncSessionLocal() as session:
			await report_service.update_report_status(
				session,
				user_id,
				report_id,
				status="failed",
			)
			await session.commit()


@router.get("", response_model=ReportListResponse)
async def list_reports(
	current_user: User = Depends(deps.require_premium_subscription),
	db: AsyncSession = Depends(deps.get_db),
	offset: int = Query(0, ge=0),
	limit: int = Query(50, ge=1, le=100),
):
	reports, count = await report_service.list_reports(
		db,
		current_user.id,
		offset=offset,
		limit=limit,
	)
	return ReportListResponse(
		items=[ReportOut.model_validate(r) for r in reports],
		count=count,
		offset=offset,
		limit=limit,
	)


@router.post("/generate", response_model=ReportDetailResponse, status_code=201)
async def generate_report(
	payload: GenerateReportRequest,
	background_tasks: BackgroundTasks,
	current_user: User = Depends(deps.require_premium_subscription),
	db: AsyncSession = Depends(deps.get_db),
):
	if not payload.job_id and not (payload.start_date or payload.end_date):
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Either job_id or date range (start_date/end_date) must be provided",
		)
	
	report = await report_service.create_report(
		db,
		user_id=current_user.id,
		title=payload.title,
		description=payload.description,
		job_id=payload.job_id,
		start_date=payload.start_date,
		end_date=payload.end_date,
		format=payload.format,
	)
	await db.commit()
	
	background_tasks.add_task(
		_process_report_generation,
		db,
		report.id,
		current_user.id,
		job_id=payload.job_id,
		start_date=payload.start_date,
		end_date=payload.end_date,
	)
	
	return ReportDetailResponse(report=ReportOut.model_validate(report))


@router.get("/{report_id}", response_model=ReportDetailResponse)
async def get_report(
	report_id: int,
	current_user: User = Depends(deps.require_premium_subscription),
	db: AsyncSession = Depends(deps.get_db),
):
	report = await report_service.get_report(db, current_user.id, report_id)
	return ReportDetailResponse(report=ReportOut.model_validate(report))


@router.get("/{report_id}/download")
async def download_report(
	report_id: int,
	current_user: User = Depends(deps.require_premium_subscription),
	db: AsyncSession = Depends(deps.get_db),
):
	report = await report_service.get_report(db, current_user.id, report_id)
	
	if report.status != "completed":
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Report is not ready for download",
		)
	
	if report.format != "pdf":
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Only PDF report downloads are supported",
		)

	if not report.file_path or not os.path.exists(report.file_path):
		file_path = await report_service.generate_report_file(
			db,
			report,
			job_id=report.job_id,
			start_date=report.start_date,
			end_date=report.end_date,
		)
		report = await report_service.update_report_status(
			db,
			current_user.id,
			report.id,
			status="completed",
			file_path=file_path,
		)
		await db.commit()

	return FileResponse(
		path=report.file_path,
		media_type="application/pdf",
		filename=f"{report.title}.pdf",
	)


@router.patch("/{report_id}", response_model=ReportDetailResponse)
async def update_report(
	report_id: int,
	payload: UpdateReportRequest,
	current_user: User = Depends(deps.require_premium_subscription),
	db: AsyncSession = Depends(deps.get_db),
):
	report = await report_service.update_report(
		db,
		current_user.id,
		report_id,
		title=payload.title,
		description=payload.description,
	)
	await db.commit()
	return ReportDetailResponse(report=ReportOut.model_validate(report))


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
	report_id: int,
	current_user: User = Depends(deps.require_premium_subscription),
	db: AsyncSession = Depends(deps.get_db),
):
	await report_service.delete_report(db, current_user.id, report_id)
	await db.commit()

