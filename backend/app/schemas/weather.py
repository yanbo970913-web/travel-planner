"""天氣預報的回傳結構。"""
from pydantic import BaseModel


class WeatherDay(BaseModel):
    date: str
    weather_code: int | None = None
    emoji: str
    description: str
    temp_max: float | None = None
    temp_min: float | None = None
    precipitation_probability: int | None = None


class WeatherForecast(BaseModel):
    location: str
    resolved_name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    available: bool
    note: str | None = None
    daily: list[WeatherDay] = []
