"""天氣路由：依目的地與日期查每日天氣預報（Open-Meteo，免金鑰）。

天氣服務本身絕不丟例外，所以這裡永遠回 200 + available 旗標，
前端依 available 決定是否顯示，頁面不會因天氣而壞掉。
"""
from fastapi import APIRouter, Depends, Query
from fastapi.concurrency import run_in_threadpool

from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.weather import WeatherForecast
from app.services.weather import get_forecast

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("", response_model=WeatherForecast)
async def weather(
    location: str = Query(..., min_length=1, max_length=255),
    start_date: str | None = Query(default=None, max_length=20),
    days: int = Query(default=1, ge=1, le=30),
    current_user: User = Depends(get_current_user),
):
    # httpx 為同步呼叫，丟到 threadpool 避免阻塞事件迴圈
    data = await run_in_threadpool(get_forecast, location.strip(), start_date, days)
    return data
