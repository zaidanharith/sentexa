from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Identity, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
	from app.models.user import User


class SentimentJob(Base):
	__tablename__ = "sentiment_jobs"

	id: Mapped[int] = mapped_column(
		Integer,
		Identity(start=1),
		primary_key=True,
	)
	user_id: Mapped[int] = mapped_column(
		Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
	)
	status: Mapped[str] = mapped_column(String(50), nullable=False, default="queued")
	total_texts: Mapped[int] = mapped_column(Integer, nullable=False)
	completed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), default=datetime.utcnow, nullable=False
	)
	updated_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
	)
	label_counts: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
	error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

	user: Mapped["User"] = relationship("User")
	results: Mapped[list["SentimentJobResult"]] = relationship(
		"SentimentJobResult", back_populates="job", cascade="all, delete-orphan"
	)


class SentimentJobResult(Base):
	__tablename__ = "sentiment_job_results"

	id: Mapped[int] = mapped_column(
		Integer,
		Identity(start=1),
		primary_key=True,
	)
	job_id: Mapped[int] = mapped_column(Integer, ForeignKey("sentiment_jobs.id", ondelete="CASCADE"), nullable=False)
	index: Mapped[int] = mapped_column(Integer, nullable=False)
	text: Mapped[str] = mapped_column(Text, nullable=False)
	label: Mapped[str] = mapped_column(String(50), nullable=False)
	label_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
	score: Mapped[Optional[float]] = mapped_column(nullable=True)
	scores: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), default=datetime.utcnow, nullable=False
	)

	job: Mapped["SentimentJob"] = relationship("SentimentJob", back_populates="results")
