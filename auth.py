# -*- coding: utf-8 -*-
"""نظام المصادقة والجلسات"""
import hashlib
import hmac
import time
import base64
import json
from typing import Optional
from config import SECRET_KEY, ADMIN_PASSWORD, SESSION_TIMEOUT


def _sign(data: str) -> str:
    """توقيع البيانات بـ HMAC"""
    sig = hmac.new(SECRET_KEY.encode(), data.encode(), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(sig).decode().rstrip("=")


def create_session_token(username: str) -> str:
    """إنشاء توكن جلسة"""
    payload = {
        "user": username,
        "exp": int(time.time()) + SESSION_TIMEOUT,
        "iat": int(time.time()),
    }
    data = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    return f"{data}.{_sign(data)}"


def verify_session_token(token: Optional[str]) -> Optional[dict]:
    """التحقق من صحة التوكن"""
    if not token or "." not in token:
        return None
    try:
        data, sig = token.rsplit(".", 1)
        expected = _sign(data)
        if not hmac.compare_digest(sig, expected):
            return None
        # فك التشفير
        padded = data + "=" * (-len(data) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded))
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:
        return None


def check_password(password: str) -> bool:
    """التحقق من كلمة السر"""
    return hmac.compare_digest(password, ADMIN_PASSWORD)
