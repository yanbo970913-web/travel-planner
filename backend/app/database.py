"""SQLAlchemy engine / Session / Base 與 FastAPI 依賴。"""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


def _normalize_db_url(url: str) -> str:
    # Render / Heroku 有時提供 postgres://，SQLAlchemy 2.x 需要 postgresql://
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


engine = create_engine(
    _normalize_db_url(settings.DATABASE_URL),
    pool_pre_ping=True,   # 每次取用前 ping，避開 Neon 閒置斷線後的 stale 連線
    pool_recycle=300,     # Neon 免費方案閒置約 5 分鐘會睡眠；定期回收連線更穩
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
