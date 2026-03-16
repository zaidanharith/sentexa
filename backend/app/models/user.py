from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime, Integer, Identity
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.review import Review

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        Identity(start=1),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    subscription: Mapped[str] = mapped_column(
        String(50), nullable=False, default="free", server_default="free"
    )
    subscription_quota_remaining: Mapped[int] = mapped_column(
        Integer, nullable=False, default=100, server_default="100"
    )
    subscription_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    reviews: Mapped[list["Review"]] = relationship(
        "Review", back_populates="user", cascade="all, delete-orphan"
    )

from app.models.review import Review
