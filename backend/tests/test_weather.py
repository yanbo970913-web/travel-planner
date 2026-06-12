"""天氣服務的純函式測試（不需網路、不需金鑰）。"""
import datetime

from app.services.weather import (
    FORECAST_HORIZON_DAYS,
    _curated_lookup,
    compute_window,
    describe_weather,
    parse_forecast,
)

TODAY = datetime.date(2026, 6, 12)


def test_describe_known_code():
    emoji, text = describe_weather(0)
    assert emoji == "☀️"
    assert text == "晴朗"


def test_describe_unknown_code_is_safe():
    # 未知代碼不應丟例外，給通用值
    emoji, text = describe_weather(123)
    assert emoji and text


def test_describe_none_is_safe():
    emoji, text = describe_weather(None)
    assert emoji and text


def test_window_no_start_date_uses_today():
    w = compute_window(None, 3, TODAY)
    assert w["available"] is True
    assert w["q_start"] == TODAY
    assert w["q_end"] == TODAY + datetime.timedelta(days=2)
    assert w["note"] is None


def test_window_future_within_horizon():
    start = (TODAY + datetime.timedelta(days=5)).isoformat()
    w = compute_window(start, 2, TODAY)
    assert w["available"] is True
    assert w["q_start"] == TODAY + datetime.timedelta(days=5)
    assert w["q_end"] == TODAY + datetime.timedelta(days=6)


def test_window_past_trip_unavailable():
    start = (TODAY - datetime.timedelta(days=10)).isoformat()
    w = compute_window(start, 3, TODAY)
    assert w["available"] is False
    assert "已過" in w["note"]


def test_window_too_far_future_unavailable():
    start = (TODAY + datetime.timedelta(days=40)).isoformat()
    w = compute_window(start, 2, TODAY)
    assert w["available"] is False
    assert str(FORECAST_HORIZON_DAYS) in w["note"]


def test_window_partial_overlap_is_clamped_with_note():
    # 從今天起 30 天，超出視窗 → 夾到視窗末端並附說明
    w = compute_window(TODAY.isoformat(), 30, TODAY)
    assert w["available"] is True
    assert w["q_start"] == TODAY
    assert w["q_end"] == TODAY + datetime.timedelta(days=FORECAST_HORIZON_DAYS - 1)
    assert w["note"] is not None


def test_window_bad_date_falls_back_to_today():
    w = compute_window("not-a-date", 1, TODAY)
    assert w["available"] is True
    assert w["q_start"] == TODAY


def test_window_bad_days_type_never_raises():
    # 守住「絕不丟例外」契約：非數字的 days 應視為 1 天而非報錯
    w = compute_window(TODAY.isoformat(), "abc", TODAY)
    assert w["available"] is True
    assert w["q_start"] == TODAY
    assert w["q_end"] == TODAY


def test_window_none_days_never_raises():
    w = compute_window(TODAY.isoformat(), None, TODAY)
    assert w["available"] is True
    assert w["q_end"] == TODAY


def test_parse_forecast_maps_arrays():
    daily = {
        "time": ["2026-06-12", "2026-06-13"],
        "weather_code": [0, 61],
        "temperature_2m_max": [30.1, 28.0],
        "temperature_2m_min": [24.0, 23.5],
        "precipitation_probability_max": [10, 80],
    }
    out = parse_forecast(daily)
    assert len(out) == 2
    assert out[0]["date"] == "2026-06-12"
    assert out[0]["emoji"] == "☀️"
    assert out[1]["description"] == "小雨"
    assert out[1]["precipitation_probability"] == 80


def test_parse_forecast_tolerates_missing_fields():
    # 只有日期、缺其他欄位也不應炸
    out = parse_forecast({"time": ["2026-06-12"]})
    assert len(out) == 1
    assert out[0]["temp_max"] is None
    assert out[0]["weather_code"] is None


def test_parse_forecast_empty():
    assert parse_forecast({}) == []


def test_curated_lookup_taiwan_city():
    # 台南必須對到台灣（緯度約 23），不可是 Open-Meteo 誤判的中國村莊（緯度約 35）
    hit = _curated_lookup("台南")
    assert hit is not None
    assert 22 < hit["latitude"] < 24
    assert 119 < hit["longitude"] < 121


def test_curated_lookup_strips_city_suffix():
    # 「台北市」應比對到「台北」
    a = _curated_lookup("台北市")
    b = _curated_lookup("台北")
    assert a is not None and a == b


def test_curated_lookup_traditional_variant():
    # 「臺南」(正體) 與「台南」應同樣可查
    assert _curated_lookup("臺南") is not None


def test_curated_lookup_miss_returns_none():
    assert _curated_lookup("某個沒收錄的地方") is None
