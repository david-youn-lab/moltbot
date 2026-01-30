"""
기기 API 라우터
IoT 기기 등록 및 제어
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession
from pydantic import BaseModel, Field
from typing import Optional, List, Any

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import get_db, Device, User
from database.models import DeviceStatus
from auth.dependencies import get_current_active_user

router = APIRouter()


# ==================== 스키마 ====================

class DeviceCreate(BaseModel):
    """기기 등록 요청"""
    device_id: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=200)
    device_type: str = Field(min_length=1, max_length=50)
    protocol: Optional[str] = None
    address: Optional[str] = None
    location: Optional[str] = None
    room: Optional[str] = None


class DeviceUpdate(BaseModel):
    """기기 수정 요청"""
    name: Optional[str] = None
    protocol: Optional[str] = None
    address: Optional[str] = None
    location: Optional[str] = None
    room: Optional[str] = None


class DeviceResponse(BaseModel):
    """기기 응답"""
    id: int
    device_id: str
    name: str
    device_type: str
    protocol: Optional[str]
    address: Optional[str]
    status: str
    location: Optional[str]
    room: Optional[str]
    current_state: Optional[dict]
    last_seen: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True


class DeviceControlRequest(BaseModel):
    """기기 제어 요청"""
    action: str  # on, off, set, toggle
    params: Optional[dict[str, Any]] = None


class MessageResponse(BaseModel):
    """메시지 응답"""
    message: str
    success: bool = True


# ==================== 엔드포인트 ====================

@router.get("", response_model=List[DeviceResponse])
async def list_devices(
    current_user: User = Depends(get_current_active_user),
    db: DBSession = Depends(get_db),
):
    """
    내 기기 목록 조회
    """
    devices = db.query(Device).filter(Device.owner_id == current_user.id).all()
    
    return [
        DeviceResponse(
            id=d.id,
            device_id=d.device_id,
            name=d.name,
            device_type=d.device_type,
            protocol=d.protocol,
            address=d.address,
            status=d.status.value,
            location=d.location,
            room=d.room,
            current_state=d.current_state,
            last_seen=d.last_seen.isoformat() if d.last_seen else None,
            created_at=d.created_at.isoformat(),
        )
        for d in devices
    ]


@router.post("", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def register_device(
    request: DeviceCreate,
    current_user: User = Depends(get_current_active_user),
    db: DBSession = Depends(get_db),
):
    """
    기기 등록
    """
    # 중복 확인
    existing = db.query(Device).filter(
        Device.device_id == request.device_id,
        Device.owner_id == current_user.id,
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 기기 ID입니다",
        )
    
    device = Device(
        device_id=request.device_id,
        name=request.name,
        device_type=request.device_type,
        protocol=request.protocol,
        address=request.address,
        location=request.location,
        room=request.room,
        owner_id=current_user.id,
    )
    
    db.add(device)
    db.commit()
    db.refresh(device)
    
    return DeviceResponse(
        id=device.id,
        device_id=device.device_id,
        name=device.name,
        device_type=device.device_type,
        protocol=device.protocol,
        address=device.address,
        status=device.status.value,
        location=device.location,
        room=device.room,
        current_state=device.current_state,
        last_seen=None,
        created_at=device.created_at.isoformat(),
    )


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: str,
    current_user: User = Depends(get_current_active_user),
    db: DBSession = Depends(get_db),
):
    """
    기기 상세 조회
    """
    device = db.query(Device).filter(
        Device.device_id == device_id,
        Device.owner_id == current_user.id,
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="기기를 찾을 수 없습니다",
        )
    
    return DeviceResponse(
        id=device.id,
        device_id=device.device_id,
        name=device.name,
        device_type=device.device_type,
        protocol=device.protocol,
        address=device.address,
        status=device.status.value,
        location=device.location,
        room=device.room,
        current_state=device.current_state,
        last_seen=device.last_seen.isoformat() if device.last_seen else None,
        created_at=device.created_at.isoformat(),
    )


@router.patch("/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: str,
    request: DeviceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: DBSession = Depends(get_db),
):
    """
    기기 정보 수정
    """
    device = db.query(Device).filter(
        Device.device_id == device_id,
        Device.owner_id == current_user.id,
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="기기를 찾을 수 없습니다",
        )
    
    if request.name is not None:
        device.name = request.name
    if request.protocol is not None:
        device.protocol = request.protocol
    if request.address is not None:
        device.address = request.address
    if request.location is not None:
        device.location = request.location
    if request.room is not None:
        device.room = request.room
    
    db.commit()
    db.refresh(device)
    
    return DeviceResponse(
        id=device.id,
        device_id=device.device_id,
        name=device.name,
        device_type=device.device_type,
        protocol=device.protocol,
        address=device.address,
        status=device.status.value,
        location=device.location,
        room=device.room,
        current_state=device.current_state,
        last_seen=device.last_seen.isoformat() if device.last_seen else None,
        created_at=device.created_at.isoformat(),
    )


@router.delete("/{device_id}", response_model=MessageResponse)
async def delete_device(
    device_id: str,
    current_user: User = Depends(get_current_active_user),
    db: DBSession = Depends(get_db),
):
    """
    기기 삭제
    """
    device = db.query(Device).filter(
        Device.device_id == device_id,
        Device.owner_id == current_user.id,
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="기기를 찾을 수 없습니다",
        )
    
    db.delete(device)
    db.commit()
    
    return MessageResponse(message="기기가 삭제되었습니다")


@router.post("/{device_id}/control", response_model=MessageResponse)
async def control_device(
    device_id: str,
    request: DeviceControlRequest,
    current_user: User = Depends(get_current_active_user),
    db: DBSession = Depends(get_db),
):
    """
    기기 제어
    
    action: on, off, set, toggle
    params: action에 따른 추가 파라미터
    """
    device = db.query(Device).filter(
        Device.device_id == device_id,
        Device.owner_id == current_user.id,
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="기기를 찾을 수 없습니다",
        )
    
    # TODO: 실제 기기 제어 로직 (MQTT, HTTP 등)
    # 현재는 상태만 업데이트
    
    if device.current_state is None:
        device.current_state = {}
    
    if request.action == "on":
        device.current_state["power"] = "on"
    elif request.action == "off":
        device.current_state["power"] = "off"
    elif request.action == "toggle":
        current_power = device.current_state.get("power", "off")
        device.current_state["power"] = "off" if current_power == "on" else "on"
    elif request.action == "set":
        if request.params:
            device.current_state.update(request.params)
    
    device.last_seen = datetime.utcnow()
    device.status = DeviceStatus.ONLINE
    
    db.commit()
    
    return MessageResponse(
        message=f"{device.name}에 {request.action} 명령을 전송했습니다",
        success=True,
    )
