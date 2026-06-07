"""ai_planner 的 JSON 解析測試（不需 API 金鑰）。"""
import pytest

from app.services.ai_planner import extract_json


def test_extract_plain_json():
    raw = '[{"day":1,"time":"09:00","location":"A","description":"x"}]'
    assert extract_json(raw) == [
        {"day": 1, "time": "09:00", "location": "A", "description": "x"}
    ]


def test_extract_json_with_code_fence():
    raw = '```json\n[{"day":1,"time":"09:00","location":"A","description":"x"}]\n```'
    assert extract_json(raw)[0]["location"] == "A"


def test_extract_json_with_reasoning_prefix():
    # 模擬 enable_thinking 夾帶思考文字在 JSON 前後
    raw = (
        "讓我思考一下行程安排...\n"
        '[{"day":1,"time":"09:00","location":"A","description":"x"}]\n'
        "以上是規劃結果。"
    )
    data = extract_json(raw)
    assert len(data) == 1
    assert data[0]["day"] == 1


def test_extract_json_empty_raises():
    with pytest.raises(ValueError):
        extract_json("")


def test_extract_json_no_array_raises():
    with pytest.raises(ValueError):
        extract_json("這裡沒有任何 JSON 內容")
