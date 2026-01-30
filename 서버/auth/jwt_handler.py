"""
JWT 토큰 생성 및 검증
"""

from datetime import datetime, timedelta
from typing import Optional, Any
from jose import jwt, JWTError
from pydantic import BaseModel

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import get_server_settings

settings = get_server_settings()


class TokenPayload(BaseModel):
    """토큰 페이로드"""
    sub: str  # 사용자 ID
    exp: datetime
    iat: datetime
    type: str  # "access" or "refresh"
    jti: Optional[str] = None  # JWT ID (토큰 고유 식별자)


class TokenPair(BaseModel):
    """토큰 쌍"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # 초


def create_access_token(
    subject: str | int,
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[dict[str, Any]] = None,
) -> str:
    """
    액세스 토큰 생성
    
    Args:
        subject: 토큰 주체 (보통 사용자 ID)
        expires_delta: 만료 시간
        additional_claims: 추가 클레임
        
    Returns:
        JWT 액세스 토큰
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access",
    }
    
    if additional_claims:
        to_encode.update(additional_claims)
    
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(
    subject: str | int,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    리프레시 토큰 생성
    
    Args:
        subject: 토큰 주체
        expires_delta: 만료 시간
        
    Returns:
        JWT 리프레시 토큰
    """
    import secrets
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh",
        "jti": secrets.token_hex(16),  # 고유 ID
    }
    
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def create_token_pair(subject: str | int) -> TokenPair:
    """
    액세스 토큰과 리프레시 토큰 쌍 생성
    
    Args:
        subject: 토큰 주체
        
    Returns:
        토큰 쌍
    """
    access_token = create_access_token(subject)
    refresh_token = create_refresh_token(subject)
    
    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


def verify_token(token: str, token_type: str = "access") -> Optional[TokenPayload]:
    """
    토큰 검증
    
    Args:
        token: JWT 토큰
        token_type: 토큰 타입 ("access" or "refresh")
        
    Returns:
        토큰 페이로드 (실패 시 None)
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        
        # 토큰 타입 확인
        if payload.get("type") != token_type:
            return None
        
        return TokenPayload(**payload)
        
    except JWTError:
        return None


def get_current_user(token: str):
    """
    토큰에서 현재 사용자 추출
    
    Args:
        token: JWT 토큰
        
    Returns:
        사용자 ID (실패 시 None)
    """
    payload = verify_token(token, "access")
    if payload is None:
        return None
    return payload.sub
