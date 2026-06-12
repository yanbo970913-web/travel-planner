"""天氣預報服務（Open-Meteo，完全免費、免金鑰）。

設計原則：
- **絕不丟出例外**：任何外部 API 失敗都回傳 available=False + 友善說明，
  讓前端頁面永遠不會因天氣服務而壞掉（符合「完全不出錯」）。
- 兩階段：先用內建熱門地點表 / OpenStreetMap Nominatim 把地名轉經緯度，再查每日預報。
- Open-Meteo 免費預報視窗約為「今天起 16 天」；超出範圍（過去或太遠的未來）
  會誠實標示而非報錯。
"""
from __future__ import annotations

import datetime
import logging

import httpx

logger = logging.getLogger("app.weather")

# Nominatim（OpenStreetMap）對中文/台灣地名遠比 Open-Meteo geocoding 準確，
# 故用它做地理編碼。Open-Meteo geocoding 會把「台南」對到中國的村莊，已棄用。
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
# Nominatim 使用規範要求可辨識的 User-Agent（含聯絡資訊）。
_USER_AGENT = "auto-travel-planner/1.0 (https://github.com/yanbo970913-web/travel-planner)"

# 常見目的地的座標快取表：保證最熱門地點即使 Nominatim 暫時不通也查得到，
# 並省下外部呼叫。座標已對照 Nominatim 結果核對無誤。
_CURATED: dict[str, tuple[float, float, str]] = {
    # ── 台灣縣市 ──
    "台北": (25.04, 121.56, "台北・臺灣"), "臺北": (25.04, 121.56, "台北・臺灣"),
    "台北市": (25.04, 121.56, "台北・臺灣"), "臺北市": (25.04, 121.56, "台北・臺灣"),
    "新北": (25.01, 121.46, "新北・臺灣"), "新北市": (25.01, 121.46, "新北・臺灣"),
    "桃園": (24.99, 121.30, "桃園・臺灣"), "基隆": (25.13, 121.74, "基隆・臺灣"),
    "新竹": (24.80, 120.97, "新竹・臺灣"), "苗栗": (24.56, 120.82, "苗栗・臺灣"),
    "台中": (24.15, 120.67, "台中・臺灣"), "臺中": (24.15, 120.67, "台中・臺灣"),
    "台中市": (24.15, 120.67, "台中・臺灣"), "彰化": (24.08, 120.54, "彰化・臺灣"),
    "南投": (23.91, 120.69, "南投・臺灣"), "雲林": (23.71, 120.43, "雲林・臺灣"),
    "嘉義": (23.48, 120.45, "嘉義・臺灣"), "台南": (22.99, 120.21, "台南・臺灣"),
    "臺南": (22.99, 120.21, "台南・臺灣"), "台南市": (22.99, 120.21, "台南・臺灣"),
    "高雄": (22.62, 120.31, "高雄・臺灣"), "高雄市": (22.62, 120.31, "高雄・臺灣"),
    "屏東": (22.67, 120.49, "屏東・臺灣"), "宜蘭": (24.75, 121.75, "宜蘭・臺灣"),
    "花蓮": (23.98, 121.60, "花蓮・臺灣"), "台東": (22.76, 121.14, "台東・臺灣"),
    "臺東": (22.76, 121.14, "台東・臺灣"), "澎湖": (23.57, 119.58, "澎湖・臺灣"),
    "金門": (24.43, 118.32, "金門・臺灣"), "馬祖": (26.16, 119.95, "馬祖・臺灣"),
    # ── 台灣著名景點 ──
    "墾丁": (21.95, 120.80, "墾丁・臺灣"), "九份": (25.11, 121.84, "九份・臺灣"),
    "日月潭": (23.86, 120.92, "日月潭・臺灣"), "阿里山": (23.51, 120.80, "阿里山・臺灣"),
    "太魯閣": (24.17, 121.49, "太魯閣・臺灣"), "淡水": (25.17, 121.44, "淡水・臺灣"),
    "墾丁國家公園": (21.95, 120.80, "墾丁・臺灣"),
    # ── 常見國際城市 ──
    "東京": (35.68, 139.76, "東京・日本"), "大阪": (34.69, 135.50, "大阪・日本"),
    "京都": (35.01, 135.77, "京都・日本"), "北海道": (43.06, 141.35, "札幌・日本"),
    "札幌": (43.06, 141.35, "札幌・日本"), "沖繩": (26.21, 127.68, "那霸・日本"),
    "首爾": (37.57, 126.98, "首爾・韓國"), "釜山": (35.18, 129.08, "釜山・韓國"),
    "曼谷": (13.75, 100.49, "曼谷・泰國"), "新加坡": (1.35, 103.82, "新加坡"),
    "香港": (22.32, 114.17, "香港"), "澳門": (22.20, 113.54, "澳門"),
    "吉隆坡": (3.14, 101.69, "吉隆坡・馬來西亞"), "峇里島": (-8.41, 115.19, "峇里島・印尼"),
    "巴黎": (48.86, 2.35, "巴黎・法國"), "倫敦": (51.51, -0.13, "倫敦・英國"),
    "羅馬": (41.90, 12.50, "羅馬・義大利"), "紐約": (40.71, -74.01, "紐約・美國"),
    "洛杉磯": (34.05, -118.24, "洛杉磯・美國"), "雪梨": (-33.87, 151.21, "雪梨・澳洲"),
}

# Open-Meteo 免費預報可取得的天數（含今天）。超過此範圍就沒有資料。
FORECAST_HORIZON_DAYS = 16
# 單次外部呼叫逾時：Open-Meteo / Nominatim 平時 <1s，8s 足夠且避免前端等太久。
_HTTP_TIMEOUT = 8.0

# WMO weather code → (emoji, 中文描述)
# 參考 https://open-meteo.com/en/docs（WMO Weather interpretation codes）
_WMO: dict[int, tuple[str, str]] = {
    0: ("☀️", "晴朗"),
    1: ("🌤️", "晴時多雲"),
    2: ("⛅", "多雲"),
    3: ("☁️", "陰天"),
    45: ("🌫️", "有霧"),
    48: ("🌫️", "霧凇"),
    51: ("🌦️", "毛毛雨"),
    53: ("🌦️", "毛毛雨"),
    55: ("🌧️", "毛毛雨（密）"),
    56: ("🌧️", "凍毛雨"),
    57: ("🌧️", "凍毛雨（密）"),
    61: ("🌦️", "小雨"),
    63: ("🌧️", "中雨"),
    65: ("🌧️", "大雨"),
    66: ("🌧️", "凍雨"),
    67: ("🌧️", "強凍雨"),
    71: ("🌨️", "小雪"),
    73: ("🌨️", "中雪"),
    75: ("❄️", "大雪"),
    77: ("🌨️", "雪粒"),
    80: ("🌦️", "陣雨"),
    81: ("🌧️", "強陣雨"),
    82: ("⛈️", "暴雨"),
    85: ("🌨️", "陣雪"),
    86: ("❄️", "強陣雪"),
    95: ("⛈️", "雷雨"),
    96: ("⛈️", "雷雨夾冰雹"),
    99: ("⛈️", "強雷雨冰雹"),
}


def describe_weather(code: int | None) -> tuple[str, str]:
    """WMO 代碼轉 (emoji, 中文)。未知代碼給通用值，不丟例外。"""
    if code is None:
        return ("🌡️", "—")
    return _WMO.get(int(code), ("🌡️", "天氣"))


def compute_window(
    start_date: str | None, days: int, today: datetime.date
) -> dict:
    """計算實際可查詢的日期區間（與預報視窗交集）。

    回傳 dict：available(bool)、q_start/q_end(date|None)、note(str|None)。
    純函式，方便單元測試；絕不丟例外。
    """
    horizon = today + datetime.timedelta(days=FORECAST_HORIZON_DAYS - 1)

    start = today
    if start_date:
        try:
            start = datetime.date.fromisoformat(start_date.strip()[:10])
        except (ValueError, AttributeError):
            start = today

    try:
        span = max(1, int(days)) if days else 1
    except (ValueError, TypeError):
        span = 1  # 守住「絕不丟例外」契約：非數字一律當 1 天
    end = start + datetime.timedelta(days=span - 1)

    q_start = max(start, today)
    q_end = min(end, horizon)

    if q_start > q_end:
        if end < today:
            note = "此行程日期已過，無天氣預報。"
        else:
            note = f"出發日超過 {FORECAST_HORIZON_DAYS} 天預報範圍，靠近出發日再查即可看到天氣。"
        return {"available": False, "q_start": None, "q_end": None, "note": note}

    note = None
    if q_start > start or q_end < end:
        note = f"僅顯示未來 {FORECAST_HORIZON_DAYS} 天內可預報的日期。"
    return {"available": True, "q_start": q_start, "q_end": q_end, "note": note}


def parse_forecast(daily: dict) -> list[dict]:
    """把 Open-Meteo 的每日陣列轉成前端好用的列表。容錯：缺欄位就給 None。"""
    times = daily.get("time") or []
    codes = daily.get("weather_code") or []
    tmax = daily.get("temperature_2m_max") or []
    tmin = daily.get("temperature_2m_min") or []
    pop = daily.get("precipitation_probability_max") or []

    out: list[dict] = []
    for i, day in enumerate(times):
        code = codes[i] if i < len(codes) else None
        emoji, desc = describe_weather(code)
        out.append(
            {
                "date": day,
                "weather_code": code,
                "emoji": emoji,
                "description": desc,
                "temp_max": tmax[i] if i < len(tmax) else None,
                "temp_min": tmin[i] if i < len(tmin) else None,
                "precipitation_probability": pop[i] if i < len(pop) else None,
            }
        )
    return out


def _curated_lookup(location: str) -> dict | None:
    """先查內建熱門地點表（含去除「市/縣」後綴的寬鬆比對）。"""
    key = location.strip()
    hit = _CURATED.get(key)
    if hit is None and key and key[-1] in "市縣":
        hit = _CURATED.get(key[:-1])
    if hit is None:
        return None
    lat, lon, name = hit
    return {"name": name, "latitude": lat, "longitude": lon}


def _nominatim(location: str) -> dict | None:
    """用 OpenStreetMap Nominatim 把地名轉座標（對中文/台灣地名準確）。"""
    try:
        resp = httpx.get(
            NOMINATIM_URL,
            params={
                "q": location,
                "format": "json",
                "limit": 1,
                "accept-language": "zh-TW",
                "addressdetails": 1,
            },
            headers={"User-Agent": _USER_AGENT},
            timeout=_HTTP_TIMEOUT,
        )
        resp.raise_for_status()
        results = resp.json()
        if not results:
            return None
        top = results[0]
        addr = top.get("address") or {}
        local = (
            addr.get("city")
            or addr.get("town")
            or addr.get("county")
            or addr.get("state")
            or (top.get("display_name", "").split(",")[0])
        )
        country = addr.get("country")
        name = "・".join(p for p in (local, country) if p) or location
        return {
            "name": name,
            "latitude": float(top["lat"]),
            "longitude": float(top["lon"]),
        }
    except Exception as exc:  # 網路/解析等任何錯誤
        logger.warning("天氣 Nominatim geocode 失敗（%s）：%s", location, exc)
        return None


# 只快取「成功」的地理編碼結果：避免把暫時性的網路失敗（None）永久記住，
# 否則 Nominatim 一次抖動就會讓該地點之後永遠查不到天氣。
_geo_cache: dict[str, dict] = {}


def _geocode(location: str) -> dict | None:
    """地名 → {name, latitude, longitude}；找不到或失敗回 None。

    順序：內建熱門地點表（快、保證正確）→ Nominatim（通用）。
    成功結果快取於行程內記憶體，減少外部呼叫並尊重 Nominatim 用量規範。
    """
    key = location.strip()
    if key in _geo_cache:
        return _geo_cache[key]
    result = _curated_lookup(key) or _nominatim(key)
    # 只快取成功結果，且設上限避免記憶體無限成長
    if result and len(_geo_cache) < 2048:
        _geo_cache[key] = result
    return result


def get_forecast(location: str, start_date: str | None, days: int) -> dict:
    """取得目的地的每日天氣預報。**絕不丟例外**。

    回傳：{location, resolved_name, latitude, longitude, available, note, daily[]}
    """
    base = {
        "location": location,
        "resolved_name": None,
        "latitude": None,
        "longitude": None,
        "available": False,
        "note": None,
        "daily": [],
    }

    geo = _geocode(location)
    if not geo or geo.get("latitude") is None:
        base["note"] = f"找不到「{location}」的位置座標，暫無天氣預報。"
        return base

    base["resolved_name"] = geo["name"]
    base["latitude"] = geo["latitude"]
    base["longitude"] = geo["longitude"]

    today = datetime.date.today()
    window = compute_window(start_date, days, today)
    if not window["available"]:
        base["note"] = window["note"]
        return base

    try:
        resp = httpx.get(
            FORECAST_URL,
            params={
                "latitude": geo["latitude"],
                "longitude": geo["longitude"],
                "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
                "timezone": "auto",
                "start_date": window["q_start"].isoformat(),
                "end_date": window["q_end"].isoformat(),
            },
            timeout=_HTTP_TIMEOUT,
        )
        resp.raise_for_status()
        daily = parse_forecast(resp.json().get("daily") or {})
    except Exception as exc:
        logger.warning("天氣預報查詢失敗（%s）：%s", location, exc)
        base["note"] = "天氣服務暫時無法使用，稍後再試。"
        return base

    base["available"] = bool(daily)
    base["daily"] = daily
    base["note"] = window["note"] if daily else "查無此區間的天氣資料。"
    return base
