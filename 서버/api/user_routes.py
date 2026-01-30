"""
사용자 API 라우터
프로필 조회 및 수정
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession
from pydantic import BaseModel, EmailStr
from typing import Optional

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import get_db, User
from auth.dependencies import get_current_active_user
from auth.password import hash_password, verify_password, check_password_strength

router = APIRouter()


# ==================== 스키마 ====================

class UserProfile(BaseModel):
    """사용자 프로필"""
    id: int
    email: str
    username: str
    full_name: Optional[str]
    phone: Optional[str]
    is_verified: bool
    created_at: str
    
    class Config:
        from_attributes = True


class UpdateProfileRequest(BaseModel):
    """프로필 수정 요청"""
    full_name: Optional[str] = None
    phone: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    """비밀번호 변경 요청"""
    current_password: str
    new_password: str


class MessageResponse(BaseModel):
    """메시지 응답"""
    message: str


# ==================== 엔드포인트 ====================

@router.get("/me", response_model=UserProfile)
async def get_my_profile(
    current_user: User = Depends(get_current_active_user),
):
    """
    내 프로필 조회
    """
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        phone=current_user.phone,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at.isoformat(),
    )


@router.patch("/me", response_model=UserProfile)
async def update_my_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_active_user),
    db: DBSession = Depends(get_db),
):
    """
    내 프로필 수정
    """
    if request.full_name is not None:
        current_user.full_name = request.full_name
    
    if request.phone is not None:
        from security.validators import validate_phone
        valid, error = validate_phone(request.phone)
        if not valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error,
            )
        current_user.phone = request.phone
    
    db.commit()
    db.refresh(current_user)
    
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        phone=current_user.phone,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at.isoformat(),
    )


@router.post("/me/password", response_model=MessageResponse)
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: DBSession = Depends(get_db),
):
    """
    비밀번호 변경
    """
    # 현재 비밀번호 확인
    if not verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="현재 비밀번호가 올바르지 않습니다",
        )
    
    # 새 비밀번호 강도 검사
    strong, errors = check_password_strength(request.new_password)
    if not strong:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=errors[0],
        )
    
    # 비밀번호 변경
    current_user.hashed_password = hash_password(request.new_password)
    db.commit()
    
    return MessageResponse(message="비밀번호가 변경되었습니다")


@router.delete("/me", response_model=MessageResponse)
async def delete_my_account(
    current_user: User = Depends(get_current_active_user),
    db: DBSession = Depends(get_db),
):
    """
    계정 삭제
    
    주의: 이 작업은 되돌릴 수 없습니다.
    """
    db.delete(current_user)
    db.commit()
    
    return MessageResponse(message="계정이 삭제되었습니다")
