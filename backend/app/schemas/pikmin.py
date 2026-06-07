from pydantic import BaseModel, Field


class DecorHighlight(BaseModel):
    place_type: str = Field(description="地點類型，例如 餐廳、公園、車站")
    decor: str = Field(description="該類型可獲得的裝飾皮克敏")


class PikminAdvice(BaseModel):
    location: str
    date: str  # 此份資訊對應的日期（ISO，每日更新）
    regional_pikmin: list[str] = Field(
        default_factory=list, description="該地區/國家限定或較特別的皮克敏"
    )
    decor_highlights: list[DecorHighlight] = Field(default_factory=list)
    current_events: list[str] = Field(
        default_factory=list, description="近期/季節性活動皮克敏（依模型知識）"
    )
    tips: str = Field(default="", description="給造訪玩家的蒐集建議")
