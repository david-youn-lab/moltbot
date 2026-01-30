"""
인증 API 라우터
회원가입, 로그인, 토큰 갱신
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session as DBSession
from pydantic import BaseModel, EmailStr, Field

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import get_db, User, Session
from auth.password import hash_password, verify_password, check_password_strength
from auth.jwt_handler import create_token_pair, verify_token, TokenPair
from security.validators import validate_email, validate_username

router = APIRouter()


# ==================== 스키마 ====================

class RegisterRequest(BaseModel):
    """회원가입 요청"""
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)
    full_name: str | None = None


class LoginRequest(BaseModel):
    """로그인 요청"""
    username: str  # 이메일 또는 사용자명
    password: str


class RefreshRequest(BaseModel):
    """토큰 갱신 요청"""
    refresh_token: str


class MessageResponse(BaseModel):
    """메시지 응답"""
    message: str


# ==================== 엔드포인트 ====================

@router.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: DBSession = Depends(get_db),
):
    """
    회원가입
    
    새 사용자를 등록합니다.
    """
    # 이메일 중복 확인
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용 중인 이메일입니다",
        )
    
    # 사용자명 중복 확인
    if db.query(User).filter(User.username == request.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용 중인 사용자명입니다",
        )
    
    # 사용자명 검증
    valid, error = validate_username(request.username)
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )
    
    # 비밀번호 강도 검사
    strong, errors = check_password_strength(request.password)
    if not strong:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=errors[0],
        )
    
    # 사용자 생성
    user = User(
        email=request.email,
        username=request.username,
        hashed_password=hash_password(request.password),
        full_name=request.full_name,
    )
    
    db.add(user)
    db.commit()
    
    return MessageResponse(message="회원가입이 완료되었습니다")


@router.post("/login", response_model=TokenPair)
async def login(
    request: LoginRequest,
    http_request: Request,
    db: DBSession = Depends(get_db),
):
    """
    로그인
    
    이메일 또는 사용자명으로 로그인합니다.
    """
    # 사용자 찾기 (이메일 또는 사용자명)
    user = db.query(User).filter(
        (User.email == request.username) | (User.username == request.username)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 올바르지 않습니다",
        )
    
    # 계정 잠금 확인
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="계정이 일시적으로 잠겼습니다. 나중에 다시 시도하세요.",
        )
    
    # 비밀번호 확인
    if not verify_password(request.password, user.hashed_password):
        # 로그인 실패 카운트 증가
        user.failed_login_attempts += 1
        
        # 5회 실패 시 30분 잠금
        if user.failed_login_attempts >= 5:
            from datetime import timedelta
            user.locked_until = datetime.utcnow() + timedelta(minutes=30)
        
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 올바르지 않습니다",
        )
    
    # 로그인 성공 - 카운터 리셋
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login = datetime.utcnow()
    
    # 토큰 생성
    token_pair = create_token_pair(user.id)
    
    # 세션 저장
    client_ip = http_request.client.host if http_request.client else None
    user_agent = http_request.headers.get("User-Agent")
    
    session = Session(
        user_id=user.id,
        refresh_token=token_pair.refresh_token,
        expires_at=datetime.utcnow(),  # TODO: 실제 만료 시간
        client_ip=client_ip,
        user_agent=user_agent,
    )
    db.add(session)
    db.commit()
    
    return token_pair


@router.post("/refresh", response_model=TokenPair)
async def refresh_token(
    request: RefreshRequest,
    db: DBSession = Depends(get_db),
):
    """
    토큰 갱신
    
    리프레시 토큰으로 새 액세스 토큰을 발급받습니다.
    """
    # 리프레시 토큰 검증
    payload = verify_token(request.refresh_token, "refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 리프레시 토큰입니다",
        )
    
    # 세션 확인
    session = db.query(Session).filter(
        Session.refresh_token == request.refresh_token,
        Session.is_active == True,
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="세션이 만료되었습니다. 다시 로그인하세요.",
        )
    
    # 기존 세션 무효화
    session.is_active = False
    session.revoked_at = datetime.utcnow()
    
    # 새 토큰 발급
    token_pair = create_token_pair(payload.sub)
    
    # 새 세션 생성
    new_session = Session(
        user_id=int(payload.sub),
        refresh_token=token_pair.refresh_token,
        expires_at=datetime.utcnow(),
        client_ip=session.client_ip,
        user_agent=session.user_agent,
    )
    db.add(new_session)
    db.commit()
    
    return token_pair


@router.post("/logout", response_model=MessageResponse)
async def logout(
    request: RefreshRequest,
    db: DBSession = Depends(get_db),
):
    """
    로그아웃
    
    현재 세션을 무효화합니다.
    """
    session = db.query(Session).filter(
        Session.refresh_token == request.refresh_token,
    ).first()
    
    if session:
        session.is_active = False
        session.revoked_at = datetime.utcnow()
        db.commit()
    
    return MessageResponse(message="로그아웃되었습니다")
