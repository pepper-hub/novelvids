"""用于认证和授权的安全工具。"""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from novelvids.core.config import settings
from novelvids.core.exceptions import AuthenticationError

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    """使用 argon2 对密码进行哈希。"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码与哈希值是否匹配。"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """创建 JWT 访问令牌。"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.jwt.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.jwt.secret_key, algorithm=settings.jwt.algorithm)


def create_refresh_token(data: dict[str, Any]) -> str:
    """创建 JWT 刷新令牌。"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.jwt.refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.jwt.secret_key, algorithm=settings.jwt.algorithm)


def decode_token(token: str) -> dict[str, Any]:
    """解码并验证 JWT 令牌。"""
    try:
        payload = jwt.decode(token, settings.jwt.secret_key, algorithms=[settings.jwt.algorithm])
        return payload
    except JWTError as e:
        raise AuthenticationError(f"无效的令牌: {e}") from e


def verify_access_token(token: str) -> dict[str, Any]:
    """验证访问令牌并返回负载。"""
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise AuthenticationError("无效的令牌类型")
    return payload


def verify_refresh_token(token: str) -> dict[str, Any]:
    """验证刷新令牌并返回负载。"""
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise AuthenticationError("无效的令牌类型")
    return payload
