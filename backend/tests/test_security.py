"""密碼雜湊與 JWT 測試（不需 DB）。"""
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hash_roundtrip():
    hashed = hash_password("supersecret123")
    assert hashed != "supersecret123"
    assert verify_password("supersecret123", hashed)
    assert not verify_password("wrongpass", hashed)


def test_jwt_roundtrip():
    token = create_access_token(subject="user-123")
    assert decode_access_token(token) == "user-123"


def test_jwt_invalid_returns_none():
    assert decode_access_token("not.a.valid.token") is None
