import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ItinerarySegment(BaseModel):
    """AI 回傳的單一行程段落，對應 prompt 要求的格式。"""

    day: int = Field(description="第幾天，從 1 開始")
    time: str = Field(description="時間或時段，例如 09:00 或 上午")
    location: str = Field(description="地點名稱")
    description: str = Field(description="活動說明，含交通方式/移動邏輯")


class GenerateRequest(BaseModel):
    origin: str | None = Field(default=None, max_length=255)  # 起始地（選填）
    location: str = Field(min_length=1, max_length=255)
    days: int = Field(ge=1, le=30)
    budget: str | None = Field(default=None, max_length=255)
    preferences: str | None = Field(default=None, max_length=1000)


class ItineraryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    origin: str | None
    location: str
    days: int
    budget: str | None
    preferences: str | None
    plan: list[ItinerarySegment]
    created_at: datetime


class ItineraryListItem(BaseModel):
    """歷史清單用的精簡版（不含完整 plan）。"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    location: str
    days: int
    created_at: datetime
