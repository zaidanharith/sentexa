from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Text, Integer, Float, DateTime, ForeignKey, Identity, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
	from app.models.user import User


class Upload(Base):
	__tablename__ = "uploads"

	id: Mapped[int] = mapped_column(
		Integer,
		Identity(start=1),
		primary_key=True,
	)
	user_id: Mapped[int] = mapped_column(
		Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
	)
	filename: Mapped[str] = mapped_column(String(255), nullable=False)
	file_type: Mapped[str] = mapped_column(String(50), nullable=False)
	file_path: Mapped[str] = mapped_column(String(255), nullable=False)
	rows_count: Mapped[int] = mapped_column(Integer, nullable=False)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), default=datetime.utcnow, nullable=False
	)
	status: Mapped[str] = mapped_column(String(50), nullable=False, default="uploaded")
	error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

	user: Mapped["User"] = relationship("User")
