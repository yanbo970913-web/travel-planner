"""NVIDIA AI 行程生成服務（由使用者測試碼重構）。

重點：
- 金鑰、base_url、模型名稱全部走 settings（環境變數），不寫死。
- 保留原本 enable_thinking 設定；因此回傳可能夾帶 reasoning 或 markdown
  code fence，需用 extract_json() 穩健解析。
- 用 Pydantic 驗證輸出格式，不符就重試一次（溫度調低）。
"""
import json
import logging
import re
import time

from openai import OpenAI

from app.config import settings
from app.schemas.itinerary import ItinerarySegment

logger = logging.getLogger("app.ai_planner")

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            base_url=settings.NVIDIA_BASE_URL,
            api_key=settings.NVIDIA_API_KEY,
            timeout=80.0,      # 單次請求逾時，避免無限卡住
            max_retries=0,     # 關閉 SDK 內建重試（改由我們自己控制，確保總時長可控）
        )
    return _client


SYSTEM_PROMPT = """你是一位專業的全球旅遊行程規劃師。
請根據使用者提供的地點、天數、預算與偏好，規劃出合理且可執行的每日行程。

規則：
1. 必須涵蓋每一天（day 從 1 編號到指定天數），每天安排數個時段。
2. 行程要符合地理動線，相鄰景點盡量就近，避免不合理的來回奔波。
3. 每個段落的 description 需簡述活動內容，並包含「交通方式與移動邏輯」（例如：搭捷運/步行/開車約幾分鐘）。
4. 若地點位於台灣，請盡量融入當地的「特色老街」與「在地秘境」，而非只有熱門大景點。
5. 若為國際城市，請安排該城市的代表性景點與在地體驗。
6. 請考量使用者的預算與偏好來取捨景點與餐飲等級。

輸出格式（極重要）：
- 只回傳一個 JSON 陣列，不要有任何說明文字、前後綴或 markdown。
- 陣列每個元素為物件，欄位固定為：day (整數), time (字串), location (字串), description (字串)。
範例：
[{"day":1,"time":"09:00","location":"範例景點","description":"活動說明，含交通方式"}]
"""


def _build_user_prompt(
    location: str,
    days: int,
    budget: str | None,
    preferences: str | None,
    origin: str | None = None,
) -> str:
    parts = [f"我要去【{location}】玩【{days}】天。"]
    if origin:
        parts.append(
            f"我的出發地是【{origin}】，請在第一天開頭安排從出發地到目的地的交通"
            "（交通方式、班次/路線與大約耗時），最後一天也可安排返程。"
        )
    if budget:
        parts.append(f"我的預算是：{budget}。")
    if preferences:
        parts.append(f"我的偏好是：{preferences}。")
    parts.append("請依規則幫我規劃完整行程，並只回傳 JSON 陣列。")
    return "".join(parts)


def extract_json(content: str):
    """從模型輸出中穩健萃取 JSON（陣列或物件皆可）。

    處理情況：純 JSON、被 ```json ``` 圍欄包住、前後夾帶 reasoning 文字。
    回傳 list 或 dict（由內容決定）。
    """
    if not content:
        raise ValueError("模型回傳為空")

    text = content.strip()

    # 1) 去除 markdown code fence
    fence = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()

    # 2) 直接嘗試解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 3) 從最先出現的 [ 或 { 抓到對應的結尾（容忍前後雜訊/思考文字）
    opens = [i for i in (text.find("["), text.find("{")) if i != -1]
    if opens:
        start = min(opens)
        close_ch = "]" if text[start] == "[" else "}"
        end = text.rfind(close_ch)
        if end > start:
            return json.loads(text[start : end + 1])

    raise ValueError("無法從模型輸出解析出 JSON")


def _call_model(
    location: str,
    days: int,
    budget: str | None,
    preferences: str | None,
    origin: str | None,
    *,
    model: str,
    nemotron: bool,
    temperature: float,
    max_tokens: int,
    timeout: float,
    max_seconds: float,
) -> str:
    """以串流方式呼叫，邊收邊累積；只要持續有資料就不會逾時。
    用 max_seconds 控制單次總時長上限。nemotron 模型才送 thinking 參數。"""
    kwargs = {}
    if nemotron:
        kwargs["extra_body"] = {"chat_template_kwargs": {"enable_thinking": False}}
    stream = _get_client().chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": _build_user_prompt(
                    location, days, budget, preferences, origin
                ),
            },
        ],
        temperature=temperature,
        top_p=0.95,
        max_tokens=max_tokens,
        stream=True,
        timeout=timeout,
        **kwargs,
    )
    start = time.monotonic()
    parts: list[str] = []
    for chunk in stream:
        if not chunk.choices:
            continue
        content = getattr(chunk.choices[0].delta, "content", None)
        if content:
            parts.append(content)
        if time.monotonic() - start > max_seconds:
            try:
                stream.close()
            except Exception:
                pass
            break
    return "".join(parts)


# 多模型嘗試（串流）：先用快速模型，失敗才試 550B Ultra，全失敗再用本地後備。
# 總時長控制在 ~2 分鐘內。
def _attempts() -> tuple[dict, ...]:
    return (
        dict(model=settings.NVIDIA_FAST_MODEL, nemotron=False, temperature=0.7,
             max_tokens=4096, timeout=45.0, max_seconds=48.0),
        dict(model=settings.NVIDIA_MODEL, nemotron=True, temperature=0.5,
             max_tokens=3500, timeout=25.0, max_seconds=25.0),
    )


def _fallback_itinerary(
    location: str, days: int, origin: str | None = None
) -> list[dict]:
    """AI 全部失敗時的保底行程（本地產生，保證有結果、絕不報錯）。"""
    segments: list[dict] = []
    for d in range(1, days + 1):
        if d == 1 and origin:
            segments.append(
                {
                    "day": 1,
                    "time": "08:00",
                    "location": f"從 {origin} 出發",
                    "description": (
                        f"從 {origin} 前往 {location}，可搭乘高鐵／台鐵／客運或自行開車，"
                        "抵達後寄放行李、展開行程。"
                    ),
                }
            )
        slots = [
            ("09:30", f"{location} 代表性景點", "走訪當地最具代表性的景點，認識在地特色。"),
            ("12:00", "在地特色午餐", "品嚐當地特色美食與小吃。"),
            ("14:30", f"{location} 老街／文化景點", "漫步老街或文化景點，體驗在地風情與選購伴手禮。"),
            ("18:00", "夜市／晚餐", "享用晚餐，並逛逛附近夜市或商圈。"),
        ]
        for t, loc, desc in slots:
            segments.append({"day": d, "time": t, "location": loc, "description": desc})
        if d == days and origin:
            segments.append(
                {
                    "day": days,
                    "time": "20:30",
                    "location": f"返回 {origin}",
                    "description": f"行程結束，從 {location} 返回 {origin}。",
                }
            )
    return segments


def generate_itinerary(
    location: str,
    days: int,
    budget: str | None = None,
    preferences: str | None = None,
    origin: str | None = None,
) -> list[dict]:
    """同步呼叫（在 router 內用 run_in_threadpool 包裝）。

    回傳通過 Pydantic 驗證的行程段落 list[dict]。
    **保證不失敗**：AI 全部嘗試失敗時，改回傳本地後備行程（永不報錯）。
    總時長上限約 115 秒，確保不超過 2 分鐘。
    """
    last_error: Exception | None = None
    # 有金鑰才嘗試呼叫 AI；沒金鑰直接走後備（仍給結果）
    if settings.NVIDIA_API_KEY and settings.NVIDIA_API_KEY != "dummy_key_for_now":
        for attempt, cfg in enumerate(_attempts()):
            try:
                raw = _call_model(location, days, budget, preferences, origin, **cfg)
                data = extract_json(raw)
                if not isinstance(data, list) or not data:
                    raise ValueError("行程內容為空或格式非陣列")
                # 逐段驗證並正規化
                segments = [ItinerarySegment(**item).model_dump() for item in data]
                if segments:
                    return segments
            except Exception as exc:  # 含 openai 認證/連線等例外
                last_error = exc
                logger.warning("AI 行程生成第 %d 次嘗試失敗：%s", attempt + 1, exc)

    # 保底：AI 失敗或未設金鑰 → 回傳本地後備行程，確保「絕不生成失敗」
    logger.error("AI 生成未成功，改用本地後備行程（原因：%s）", last_error)
    return _fallback_itinerary(location, days, origin)
