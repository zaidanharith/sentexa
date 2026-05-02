from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Text, Integer, Float, DateTime, ForeignKey, Identity, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.upload import Upload

if TYPE_CHECKING:
	from app.models.user import User


class AnalysisHistory(Base):
	__tablename__ = "analysis_history"

	id: Mapped[int] = mapped_column(
		Integer,
		Identity(start=1),
		primary_key=True,
	)
	user_id: Mapped[int] = mapped_column(
		Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
	)
	source_type: Mapped[str] = mapped_column(String(50), nullable=False)
	source_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
	input_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
	upload_id: Mapped[Optional[int]] = mapped_column(
		Integer, ForeignKey("uploads.id", ondelete="SET NULL"), nullable=True
	)
	job_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True)
	status: Mapped[str] = mapped_column(String(50), nullable=False, default="completed")
	include_scores: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
	apply_postprocess: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
	include_meta: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
	item_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
	result_label: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
	result_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
	label_counts: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
	result_payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
	error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), default=datetime.utcnow, nullable=False
	)
	updated_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
	)

	user: Mapped["User"] = relationship("User")
	upload: Mapped[Optional["Upload"]] = relationship("Upload")