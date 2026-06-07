"""FastAPI 入口：CORS、健康檢查、掛載 routers。"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, itineraries, pikmin, users

logging.basicConfig(level=logging.INFO)

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    # 額外放行任何 Render 網域，避免前端網址尾碼變動就壞掉
    allow_origin_regex=r"https://.*\.onrender\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(itineraries.router)
app.include_router(pikmin.router)


@app.get("/", tags=["health"])
def root():
    return {"app": settings.APP_NAME, "status": "ok"}


@app.get("/health", tags=["health"])
def health():
    return {"status": "healthy"}
