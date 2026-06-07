"""行程路由：生成、列表、查看、刪除（皆需登入）。"""
import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.itinerary import Itinerary
from app.models.user import User
from app.schemas.itinerary import (
    GenerateRequest,
    ItineraryListItem,
    ItineraryOut,
)
from app.services.ai_planner import generate_itinerary

router = APIRouter(prefix="/itineraries", tags=["itineraries"])


@router.post("/generate", response_model=ItineraryOut, status_code=201)
async def generate(
    payload: GenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        # openai client 為同步，丟到 threadpool 避免阻塞事件迴圈
        plan = await run_in_threadpool(
            generate_itinerary,
            payload.location,
            payload.days,
            payload.budget,
            payload.preferences,
            payload.origin,
            payload.start_date,
            payload.departure_time,
            payload.return_time,
        )
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    title = f"{payload.location} {payload.days} 日遊"
    if payload.origin:
        title = f"{payload.origin} → {title}"

    itinerary = Itinerary(
        user_id=current_user.id,
        title=title,
        origin=payload.origin,
        location=payload.location,
        days=payload.days,
        start_date=payload.start_date,
        departure_time=payload.departure_time,
        return_time=payload.return_time,
        budget=payload.budget,
        preferences=payload.preferences,
        plan=plan,
    )
    db.add(itinerary)
    db.commit()
    db.refresh(itinerary)
    return itinerary


@router.get("", response_model=list[ItineraryListItem])
def list_itineraries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Itinerary)
        .filter(Itinerary.user_id == current_user.id)
        .order_by(Itinerary.created_at.desc())
        .all()
    )


def _get_owned(db: Session, itinerary_id: uuid.UUID, user: User) -> Itinerary:
    itinerary = db.get(Itinerary, itinerary_id)
    if itinerary is None or itinerary.user_id != user.id:
        raise HTTPException(status_code=404, detail="找不到此行程")
    return itinerary


@router.get("/{itinerary_id}", response_model=ItineraryOut)
def get_itinerary(
    itinerary_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _get_owned(db, itinerary_id, current_user)


@router.delete("/{itinerary_id}", status_code=204)
def delete_itinerary(
    itinerary_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    itinerary = _get_owned(db, itinerary_id, current_user)
    db.delete(itinerary)
    db.commit()
