import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PikminCache(Base):
    """依 (location, date) 快取皮克敏建議，達成「每日更新」並節省 API 呼叫。"""

    __tablename__ = "pikmin_cache"
    __table_args__ = (
        UniqueConstraint("location", "date", name="uq_pikmin_location_date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    location: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    date: Mapped[str] = mapped_column(String(10), nullable=False)  # ISO yyyy-mm-dd
    data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
