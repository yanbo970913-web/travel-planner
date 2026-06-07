"""寄送驗證信 / 重設密碼信。

未設定 SMTP_HOST 時自動退回 dev fallback：把連結印到 log，
方便本機開發在沒有寄信服務的情況下完成完整驗證流程。
"""
import logging
import smtplib
from email.message import EmailMessage

from app.config import settings

logger = logging.getLogger("app.email")


def _send(to: str, subject: str, body: str) -> None:
    # dev fallback：未設定 SMTP 就印出內容
    if not settings.SMTP_HOST:
        logger.warning(
            "[EMAIL DEV FALLBACK] 未設定 SMTP，以下為信件內容\n"
            "To: %s\nSubject: %s\n%s",
            to,
            subject,
            body,
        )
        return

    msg = EmailMessage()
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        if settings.SMTP_TLS:
            server.starttls()
        if settings.SMTP_USER and settings.SMTP_PASSWORD:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)
    logger.info("已寄出信件給 %s（%s）", to, subject)


def send_verification_email(to: str, token: str) -> None:
    link = f"{settings.cors_origins[0]}/verify-email?token={token}"
    body = (
        f"歡迎使用{settings.APP_NAME}！\n\n"
        f"請點擊以下連結完成信箱驗證（{settings.VERIFY_TOKEN_EXPIRE_HOURS} 小時內有效）：\n"
        f"{link}\n\n"
        "若您未註冊本服務，請忽略此信。"
    )
    _send(to, f"【{settings.APP_NAME}】請驗證您的信箱", body)


def send_reset_password_email(to: str, token: str) -> None:
    link = f"{settings.cors_origins[0]}/reset-password?token={token}"
    body = (
        f"我們收到您的重設密碼請求。\n\n"
        f"請點擊以下連結設定新密碼（{settings.RESET_TOKEN_EXPIRE_HOURS} 小時內有效）：\n"
        f"{link}\n\n"
        "若您未提出此請求，請忽略此信，您的密碼不會變更。"
    )
    _send(to, f"【{settings.APP_NAME}】重設密碼", body)
