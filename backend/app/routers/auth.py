"""認證路由：註冊、登入、信箱驗證、忘記/重設密碼。"""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.config import settings
from app.core.email import send_reset_password_email, send_verification_email
from app.core.security import (
    create_access_token,
    generate_url_token,
    hash_password,
    verify_password,
)
from app.database import get_db
from app.models.token import TOKEN_TYPE_RESET, TOKEN_TYPE_VERIFY, Token
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    MessageResponse,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _create_token(db: Session, user: User, token_type: str, hours: int) -> Token:
    token = Token(
        user_id=user.id,
        token=generate_url_token(),
        type=token_type,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=hours),
        used=False,
    )
    db.add(token)
    db.commit()
    db.refresh(token)
    return token


def _consume_token(db: Session, raw_token: str, token_type: str) -> Token:
    token = (
        db.query(Token)
        .filter(Token.token == raw_token, Token.type == token_type)
        .first()
    )
    if token is None or token.used:
        raise HTTPException(status_code=400, detail="無效的連結")
    if token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="連結已過期，請重新申請")
    return token


@router.post("/register", response_model=MessageResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="此信箱已被註冊")

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        is_verified=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = _create_token(
        db, user, TOKEN_TYPE_VERIFY, settings.VERIFY_TOKEN_EXPIRE_HOURS
    )
    send_verification_email(user.email, token.token)

    return MessageResponse(message="註冊成功，請至信箱點擊驗證連結後再登入。")


@router.get("/verify-email", response_model=MessageResponse)
def verify_email(token: str = Query(...), db: Session = Depends(get_db)):
    db_token = _consume_token(db, token, TOKEN_TYPE_VERIFY)
    user = db.get(User, db_token.user_id)
    if user is None:
        raise HTTPException(status_code=400, detail="無效的連結")

    user.is_verified = True
    db_token.used = True
    db.commit()
    return MessageResponse(message="信箱驗證成功，您現在可以登入了。")


@router.post("/resend-verification", response_model=MessageResponse)
def resend_verification(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """重寄驗證信。若帳號存在且未驗證，重新產生 token 並寄出。"""
    user = db.query(User).filter(User.email == payload.email).first()
    if user is not None and not user.is_verified:
        token = _create_token(
            db, user, TOKEN_TYPE_VERIFY, settings.VERIFY_TOKEN_EXPIRE_HOURS
        )
        send_verification_email(user.email, token.token)
    # 不洩漏帳號是否存在/是否已驗證
    return MessageResponse(message="若該信箱尚未驗證，我們已重新寄出驗證連結。")


@router.post("/login", response_model=TokenResponse)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # OAuth2 表單用 username 欄位帶 email
    user = db.query(User).filter(User.email == form.username).first()
    if user is None or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="信箱或密碼錯誤",
        )
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="信箱尚未驗證，請先至信箱完成驗證。",
        )

    access_token = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=access_token)


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    # 即使查無此人也回相同訊息，避免洩漏帳號是否存在
    if user is not None:
        token = _create_token(
            db, user, TOKEN_TYPE_RESET, settings.RESET_TOKEN_EXPIRE_HOURS
        )
        send_reset_password_email(user.email, token.token)
    return MessageResponse(message="若該信箱已註冊，我們已寄出重設密碼連結。")


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    db_token = _consume_token(db, payload.token, TOKEN_TYPE_RESET)
    user = db.get(User, db_token.user_id)
    if user is None:
        raise HTTPException(status_code=400, detail="無效的連結")

    user.hashed_password = hash_password(payload.new_password)
    db_token.used = True
    db.commit()
    return MessageResponse(message="密碼已重設，請使用新密碼登入。")
