"""FastAPI 入口：CORS、健康檢查、掛載 routers。"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, itineraries, pikmin, users, weather
from app.services.ai_planner import has_working_ai

logging.basicConfig(level=logging.INFO)

app = FastAPI(title=settings.APP_NAME)

# 部署輔助：未設 AI 金鑰時於 log 提醒（不中斷啟動，健康檢查仍正常）。
if has_working_ai():
    logging.info("AI 服務已就緒。")
else:
    logging.warning(
        "⚠️ 尚未設定 AI 金鑰（GROQ_API_KEY 或 NVIDIA_API_KEY）："
        "行程生成會回 502。請於環境變數設定後重新部署。天氣功能不受影響。"
    )

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
app.include_router(weather.router)


@app.get("/", tags=["health"])
def root():
    return {"app": settings.APP_NAME, "status": "ok"}


@app.get("/health", tags=["health"])
def health():
    return {"status": "healthy"}
