"""皮克敏（Pikmin Bloom）顧問服務。

Pikmin Bloom 無官方公開 API，故此功能採「AI 知識生成」：
用 NVIDIA 模型依地點產生當地的地區限定/裝飾皮克敏與近期活動資訊。
活動資訊反映模型知識，非即時官方資料（前端會明確標示）。
"""
import logging
import time

from app.config import settings
from app.schemas.pikmin import PikminAdvice
from app.services.ai_planner import _get_client, extract_json

logger = logging.getLogger("app.pikmin")

SYSTEM_PROMPT = """你是 Pikmin Bloom（Niantic 的 AR 手遊）的資深玩家顧問。
針對使用者提供的旅遊地點，提供當地玩家會關心的「特別皮克敏」資訊。

請涵蓋：
- regional_pikmin：該地區/國家可獲得的「地區限定」或較特別的皮克敏（例如某些國家/大區限定的裝飾皮克敏）。
- decor_highlights：在該地常見的地點類型可獲得的裝飾皮克敏（place_type 與 decor 對應，例如 餐廳→美食裝飾、車站→車站裝飾）。
- current_events：近期或季節性常見的活動皮克敏（例如社群日、季節大花活動）。請以一般性、概括方式描述。
- tips：給造訪該地玩家的 1～2 句蒐集建議。

輸出格式（極重要）：
- 只回傳一個 JSON 物件，不要有任何說明文字或 markdown。
- 欄位固定為：regional_pikmin (字串陣列)、decor_highlights (物件陣列，每個含 place_type 與 decor 兩個字串欄位)、current_events (字串陣列)、tips (字串)。
範例：
{"regional_pikmin":["範例"],"decor_highlights":[{"place_type":"餐廳","decor":"美食裝飾"}],"current_events":["範例活動"],"tips":"建議內容"}
"""


def _call_model(location: str, today: str, temperature: float) -> str:
    stream = _get_client().chat.completions.create(
        model=settings.NVIDIA_FAST_MODEL,  # 用快速模型，雲端穩定
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"我要去【{location}】旅遊（今天是 {today}）。"
                    "請給我當地的特別皮克敏資訊，只回傳 JSON 物件。"
                ),
            },
        ],
        temperature=temperature,
        top_p=0.95,
        max_tokens=2048,
        stream=True,
        timeout=40.0,
    )
    start = time.monotonic()
    parts: list[str] = []
    for chunk in stream:
        if not chunk.choices:
            continue
        content = getattr(chunk.choices[0].delta, "content", None)
        if content:
            parts.append(content)
        if time.monotonic() - start > 50.0:  # 單次總時長上限
            try:
                stream.close()
            except Exception:
                pass
            break
    return "".join(parts)


def _fallback_advice(location: str, today: str) -> dict:
    """AI 失敗時的保底皮克敏資訊（本地產生，保證有結果）。"""
    return PikminAdvice(
        location=location,
        date=today,
        regional_pikmin=["依所在大區而定的地區限定裝飾皮克敏"],
        decor_highlights=[
            {"place_type": "餐廳／咖啡廳", "decor": "美食類裝飾皮克敏"},
            {"place_type": "車站／機場", "decor": "交通類裝飾皮克敏"},
            {"place_type": "公園／景點", "decor": "葉子／花朵類裝飾皮克敏"},
            {"place_type": "便利商店／商店", "decor": "商店類裝飾皮克敏"},
        ],
        current_events=["季節性大花活動", "每月社群日(通常為週末)"],
        tips=f"在 {location} 多走訪不同類型地點，即可蒐集到對應的裝飾皮克敏。",
    ).model_dump()


def get_pikmin_advice(location: str, today: str) -> dict:
    """同步呼叫（router 內用 run_in_threadpool 包裝）。
    **保證不失敗**：AI 失敗時改回傳本地後備資訊。"""
    last_error: Exception | None = None
    if settings.NVIDIA_API_KEY and settings.NVIDIA_API_KEY != "dummy_key_for_now":
        for attempt, temperature in enumerate((0.7, 0.2)):
            try:
                raw = _call_model(location, today, temperature)
                data = extract_json(raw)
                if not isinstance(data, dict):
                    raise ValueError("皮克敏資訊格式非物件")
                advice = PikminAdvice(
                    location=location,
                    date=today,
                    regional_pikmin=data.get("regional_pikmin", []),
                    decor_highlights=data.get("decor_highlights", []),
                    current_events=data.get("current_events", []),
                    tips=data.get("tips", ""),
                )
                return advice.model_dump()
            except Exception as exc:  # 含 openai 認證/連線等例外
                last_error = exc
                logger.warning("皮克敏建議第 %d 次嘗試失敗：%s", attempt + 1, exc)

    logger.error("皮克敏 AI 生成未成功，改用本地後備（原因：%s）", last_error)
    return _fallback_advice(location, today)
