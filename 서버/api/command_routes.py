"""
음성 명령 API 라우터
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession
from pydantic import BaseModel
from typing import Optional, List
import time

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import get_db, User, Device, CommandLog
from database.models import DeviceStatus
from auth.dependencies import get_current_active_user
from security.validators import sanitize_input

router = APIRouter()


# ==================== 스키마 ====================

class CommandRequest(BaseModel):
    """음성 명령 요청"""
    text: str
    source: str = "api"  # api, voice, app


class CommandResult(BaseModel):
    """명령 처리 결과"""
    success: bool
    message: str
    action: Optional[str] = None
    device: Optional[str] = None
    location: Optional[str] = None
    executed: bool = False


class CommandLogResponse(BaseModel):
    """명령 로그 응답"""
    id: int
    raw_text: Optional[str]
    parsed_action: Optional[str]
    parsed_device: Optional[str]
    success: bool
    response: Optional[str]
    processing_time_ms: Optional[int]
    created_at: str


# ==================== 엔드포인트 ====================

@router.post("", response_model=CommandResult)
async def process_command(
    request: CommandRequest,
    current_user: User = Depends(get_current_active_user),
    db: DBSession = Depends(get_db),
):
    """
    음성/텍스트 명령 처리
    
    명령을 파싱하고 해당 기기를 제어합니다.
    """
    start_time = time.time()
    
    # 입력 정제
    text = sanitize_input(request.text, max_length=500)
    
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="명령어를 입력하세요",
        )
    
    # 명령어 파싱 (간단한 규칙 기반)
    result = _parse_and_execute(text, current_user, db)
    
    # 처리 시간 계산
    processing_time = int((time.time() - start_time) * 1000)
    
    # 로그 저장
    log = CommandLog(
        user_id=current_user.id,
        raw_text=text,
        parsed_action=result.action,
        parsed_device=result.device,
        parsed_location=result.location,
        success=result.success,
        response=result.message,
        processing_time_ms=processing_time,
    )
    db.add(log)
    db.commit()
    
    return result


def _parse_and_execute(text: str, user: User, db: DBSession) -> CommandResult:
    """
    명령어 파싱 및 실행
    
    TODO: 더 정교한 NLP 파싱 적용
    """
    text_lower = text.lower()
    
    # 동작 감지
    action = None
    if any(k in text_lower for k in ["켜", "틀어", "on", "열어"]):
        action = "on"
    elif any(k in text_lower for k in ["꺼", "끄", "off", "닫아"]):
        action = "off"
    elif any(k in text_lower for k in ["높여", "올려", "밝게"]):
        action = "increase"
    elif any(k in text_lower for k in ["낮춰", "내려", "어둡게"]):
        action = "decrease"
    
    # 기기 감지
    device_type = None
    if any(k in text_lower for k in ["불", "조명", "전등", "라이트"]):
        device_type = "light"
    elif any(k in text_lower for k in ["에어컨", "냉방"]):
        device_type = "aircon"
    elif any(k in text_lower for k in ["티비", "tv", "텔레비전"]):
        device_type = "tv"
    
    # 위치 감지
    location = None
    locations = ["거실", "안방", "침실", "주방", "욕실", "현관"]
    for loc in locations:
        if loc in text_lower:
            location = loc
            break
    
    # 실행
    if not action or not device_type:
        return CommandResult(
            success=False,
            message="명령을 이해하지 못했습니다. 예: '거실 불 켜줘'",
            action=action,
            device=device_type,
            location=location,
        )
    
    # 사용자의 기기 찾기
    query = db.query(Device).filter(
        Device.owner_id == user.id,
        Device.device_type == device_type,
    )
    
    if location:
        query = query.filter(
            (Device.location == location) | (Device.room == location)
        )
    
    device = query.first()
    
    if not device:
        loc_msg = f" ({location})" if location else ""
        return CommandResult(
            success=False,
            message=f"등록된 {device_type} 기기{loc_msg}를 찾을 수 없습니다",
            action=action,
            device=device_type,
            location=location,
        )
    
    # 기기 제어
    if device.current_state is None:
        device.current_state = {}
    
    if action == "on":
        device.current_state["power"] = "on"
        msg = f"{device.name}을(를) 켰습니다"
    elif action == "off":
        device.current_state["power"] = "off"
        msg = f"{device.name}을(를) 껐습니다"
    elif action == "increase":
        current = device.current_state.get("brightness", 50)
        device.current_state["brightness"] = min(100, current + 20)
        msg = f"{device.name} 밝기를 높였습니다"
    elif action == "decrease":
        current = device.current_state.get("brightness", 50)
        device.current_state["brightness"] = max(0, current - 20)
        msg = f"{device.name} 밝기를 낮췄습니다"
    else:
        msg = f"{device.name}에 명령을 전송했습니다"
    
    device.last_seen = datetime.utcnow()
    device.status = DeviceStatus.ONLINE
    db.commit()
    
    return CommandResult(
        success=True,
        message=msg,
        action=action,
        device=device_type,
        location=location,
        executed=True,
    )


@router.get("/history", response_model=List[CommandLogResponse])
async def get_command_history(
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: DBSession = Depends(get_db),
):
    """
    명령 기록 조회
    """
    logs = db.query(CommandLog).filter(
        CommandLog.user_id == current_user.id
    ).order_by(CommandLog.created_at.desc()).limit(limit).all()
    
    return [
        CommandLogResponse(
            id=log.id,
            raw_text=log.raw_text,
            parsed_action=log.parsed_action,
            parsed_device=log.parsed_device,
            success=log.success,
            response=log.response,
            processing_time_ms=log.processing_time_ms,
            created_at=log.created_at.isoformat(),
        )
        for log in logs
    ]
