"""皮克敏路由：依地點查詢當地特別皮克敏（每日快取）。"""
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.pikmin import PikminCache
from app.models.user import User
from app.schemas.pikmin import PikminAdvice
from app.services.pikmin import get_pikmin_advice

router = APIRouter(prefix="/pikmin", tags=["pikmin"])


@router.get("/advice", response_model=PikminAdvice)
async def advice(
    location: str = Query(..., min_length=1, max_length=255),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today().isoformat()
    loc = location.strip()

    # 同地點同一天 → 直接回快取（達成「每日更新」並省 API）
    cached = (
        db.query(PikminCache)
        .filter(PikminCache.location == loc, PikminCache.date == today)
        .first()
    )
    if cached:
        return cached.data

    try:
        data = await run_in_threadpool(get_pikmin_advice, loc, today)
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    db.add(PikminCache(location=loc, date=today, data=data))
    try:
        db.commit()
    except IntegrityError:
        # 併發競爭：另一請求已寫入，忽略即可
        db.rollback()
    return data
