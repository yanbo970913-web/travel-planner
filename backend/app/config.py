"""應用程式設定：全部從環境變數讀取，敏感資訊一律不寫死。"""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # --- 基本 ---
    APP_NAME: str = "自動化行程規劃系統"
    ENV: str = "development"  # development | production

    # --- 資料庫 ---
    # Render 會自動注入 DATABASE_URL；本機開發用 docker-compose 的預設值。
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/travel"

    # --- JWT ---
    JWT_SECRET: str = "CHANGE_ME_dev_secret_only"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 天

    # token（信箱驗證/重設密碼）有效時數
    VERIFY_TOKEN_EXPIRE_HOURS: int = 24
    RESET_TOKEN_EXPIRE_HOURS: int = 2

    # --- NVIDIA AI ---
    NVIDIA_API_KEY: str = "dummy_key_for_now"  # 使用者稍後提供真正金鑰
    NVIDIA_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    NVIDIA_MODEL: str = "nvidia/nemotron-3-ultra-550b-a55b"  # 高品質但較慢（雲端常逾時）
    # 主力快速模型（回應快、雲端穩定）；550B 作為次要嘗試
    NVIDIA_FAST_MODEL: str = "meta/llama-3.1-70b-instruct"

    # --- Groq（主力 AI：免費、極快、雲端可連，給真實可靠行程）---
    GROQ_API_KEY: str = ""  # 由使用者於 Render 環境變數設定
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # --- Email（寄信服務）---
    # 未設定 SMTP_HOST 時，寄信改為印出連結到 log（dev fallback）。
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: str = "no-reply@travel-planner.local"
    SMTP_TLS: bool = True

    # --- 前端網址（用於信件連結與 CORS）---
    FRONTEND_URL: str = "http://localhost:5173"

    @property
    def cors_origins(self) -> list[str]:
        # 允許前端來源；多個用逗號分隔也支援
        return [o.strip() for o in self.FRONTEND_URL.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
