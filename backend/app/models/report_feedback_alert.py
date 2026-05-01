from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Identity, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
	from app.models.user import User


class Report(Base):
	__tablename__ = "reports"

	id: Mapped[int] = mapped_column(
		Integer,
		Identity(start=1),
		primary_key=True,
	)
	user_id: Mapped[int] = mapped_column(
		Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
	)
	title: Mapped[str] = mapped_column(String(255), nullable=False)
	description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
	job_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
	start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
	end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
	status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
	format: Mapped[str] = mapped_column(String(50), nullable=False, default="csv")
	file_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), default=datetime.utcnow, nullable=False
	)
	updated_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
	)

	user: Mapped["User"] = relationship("User")


class Feedback(Base):
	__tablename__ = "feedback"

	id: Mapped[int] = mapped_column(
		Integer,
		Identity(start=1),
		primary_key=True,
	)
	user_id: Mapped[int] = mapped_column(
		Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
	)
	job_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
	text: Mapped[str] = mapped_column(Text, nullable=False)
	original_label: Mapped[str] = mapped_column(String(50), nullable=False)
	corrected_label: Mapped[str] = mapped_column(String(50), nullable=False)
	reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), default=datetime.utcnow, nullable=False
	)

	user: Mapped["User"] = relationship("User")


class Alert(Base):
	__tablename__ = "alerts"

	id: Mapped[int] = mapped_column(
		Integer,
		Identity(start=1),
		primary_key=True,
	)
	user_id: Mapped[int] = mapped_column(
		Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
	)
	job_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
	text: Mapped[str] = mapped_column(Text, nullable=False)
	label: Mapped[str] = mapped_column(String(50), nullable=False)
	severity: Mapped[str] = mapped_column(String(50), nullable=False, default="medium")
	reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
	resolved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), default=datetime.utcnow, nullable=False
	)
	resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

	user: Mapped["User"] = relationship("User")
