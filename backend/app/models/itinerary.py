import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Itinerary(Base):
    __tablename__ = "itineraries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    origin: Mapped[str | None] = mapped_column(String(255), nullable=True)  # 起始地
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    days: Mapped[int] = mapped_column(Integer, nullable=False)
    start_date: Mapped[str | None] = mapped_column(String(20), nullable=True)  # 出發日期
    departure_time: Mapped[str | None] = mapped_column(String(20), nullable=True)  # 去程時間
    return_time: Mapped[str | None] = mapped_column(String(20), nullable=True)  # 回程時間
    budget: Mapped[str | None] = mapped_column(String(255), nullable=True)
    preferences: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    # AI 回傳的結構化行程（list[dict]，每段含 day/location/time/description）
    plan: Mapped[list] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user = relationship("User", back_populates="itineraries")
