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
)
from app.services import report_service


router = APIRouter(prefix="/reports", tags=["reports"])


async def _process_report_generation(
	db: AsyncSession,
	report_id: int,
	user_id: int,
	*,
	job_id: str | None = None,
	start_date: None = None,
	end_date: None = None,
):
	"""Background task to generate report file"""
	try:
		# Fetch fresh session for background task
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
	current_user: User = Depends(deps.get_current_user),
	db: AsyncSession = Depends(deps.get_db),
	offset: int = Query(0, ge=0),
	limit: int = Query(50, ge=1, le=100),
):
	"""Mengambil daftar laporan yang pernah dibuat oleh pengguna"""
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
	current_user: User = Depends(deps.get_current_user),
	db: AsyncSession = Depends(deps.get_db),
):
	"""Membuat laporan baru berdasarkan hasil analisis job tertentu atau rentang waktu yang dipilih"""
	# Validate that either job_id or date range is provided
	if not payload.job_id and not (payload.start_date or payload.end_date):
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Either job_id or date range (start_date/end_date) must be provided",
		)
	
	# Create report in draft status
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
	
	# Queue background task to generate report file
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
	current_user: User = Depends(deps.get_current_user),
	db: AsyncSession = Depends(deps.get_db),
):
	"""Mengambil metadata dan ringkasan isi laporan tertentu"""
	report = await report_service.get_report(db, current_user.id, report_id)
	return ReportDetailResponse(report=ReportOut.model_validate(report))


@router.get("/{report_id}/download")
async def download_report(
	report_id: int,
	format: str = Query("csv", regex="^(csv|pdf)$"),
	current_user: User = Depends(deps.get_current_user),
	db: AsyncSession = Depends(deps.get_db),
):
	"""Mengunduh laporan dalam format CSV atau PDF (fitur Premium)"""
	report = await report_service.get_report(db, current_user.id, report_id)
	
	if report.status != "completed":
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Report is not ready for download",
		)
	
	if not report.file_path:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Report file not found",
		)
	
	if format != report.format:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=f"Report format is {report.format}, not {format}",
		)
	
	return FileResponse(
		path=report.file_path,
		media_type="text/csv" if report.format == "csv" else "application/pdf",
		filename=f"{report.title}.{report.format}",
	)
