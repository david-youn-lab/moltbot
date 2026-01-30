"""
컨트롤타워 메인 서버

음성인식 제어 시스템의 중앙 서버입니다.
모든 모듈과 기기들을 연결하고 조율합니다.
"""

import sys
from pathlib import Path
from contextlib import asynccontextmanager

# 상위 디렉토리를 path에 추가 (공통라이브러리 import용)
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from 공통라이브러리 import get_settings, setup_logger, get_logger
from 공통라이브러리.mqtt_client import MQTTClient, MQTTConfig

# 설정 및 로거 초기화
settings = get_settings()
setup_logger(level=settings.log_level, log_file=settings.log_file)
logger = get_logger(__name__)

# MQTT 클라이언트
mqtt_client: Optional[MQTTClient] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 라이프사이클 관리"""
    global mqtt_client
    
    # 시작 시
    logger.info("컨트롤타워 시작")
    
    # MQTT 연결
    mqtt_config = MQTTConfig(
        broker=settings.mqtt_broker,
        port=settings.mqtt_port,
        username=settings.mqtt_username,
        password=settings.mqtt_password,
    )
    mqtt_client = MQTTClient(mqtt_config)
    await mqtt_client.connect()
    
    yield
    
    # 종료 시
    if mqtt_client:
        await mqtt_client.disconnect()
    logger.info("컨트롤타워 종료")


# FastAPI 앱 생성
app = FastAPI(
    title="음성인식 제어 시스템",
    description="가정 내 IoT 기기를 음성으로 제어하는 통합 시스템",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 모델 ====================

class HealthResponse(BaseModel):
    """헬스체크 응답"""
    status: str
    timestamp: datetime
    version: str
    mqtt_connected: bool


class CommandRequest(BaseModel):
    """음성 명령 요청"""
    text: str
    source: str = "api"


class CommandResponse(BaseModel):
    """음성 명령 응답"""
    success: bool
    message: str
    action: Optional[str] = None
    target: Optional[str] = None


class DeviceInfo(BaseModel):
    """기기 정보"""
    id: str
    name: str
    type: str
    status: str
    location: Optional[str] = None


# ==================== 엔드포인트 ====================

@app.get("/", tags=["시스템"])
async def root():
    """루트 엔드포인트"""
    return {
        "name": "음성인식 제어 시스템",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health", response_model=HealthResponse, tags=["시스템"])
async def health_check():
    """헬스체크"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="0.1.0",
        mqtt_connected=mqtt_client.is_connected if mqtt_client else False,
    )


@app.post("/command", response_model=CommandResponse, tags=["음성"])
async def process_command(request: CommandRequest):
    """
    음성 명령 처리
    
    텍스트 명령을 받아 해당 동작을 수행합니다.
    """
    logger.info(f"명령 수신: {request.text} (소스: {request.source})")
    
    # TODO: 명령어 파싱 및 처리 로직 구현
    text = request.text.lower()
    
    # 간단한 명령어 예시
    if "불" in text and ("켜" in text or "on" in text):
        return CommandResponse(
            success=True,
            message="조명을 켭니다",
            action="turn_on",
            target="light",
        )
    elif "불" in text and ("꺼" in text or "off" in text):
        return CommandResponse(
            success=True,
            message="조명을 끕니다",
            action="turn_off",
            target="light",
        )
    elif "에어컨" in text:
        return CommandResponse(
            success=True,
            message="에어컨 명령을 처리합니다",
            action="control",
            target="aircon",
        )
    else:
        return CommandResponse(
            success=False,
            message="인식할 수 없는 명령입니다",
        )


@app.get("/devices", response_model=list[DeviceInfo], tags=["기기"])
async def list_devices():
    """등록된 기기 목록 조회"""
    # TODO: 실제 기기 목록 조회 구현
    return [
        DeviceInfo(
            id="light-001",
            name="거실 조명",
            type="light",
            status="on",
            location="거실",
        ),
        DeviceInfo(
            id="aircon-001",
            name="거실 에어컨",
            type="aircon",
            status="off",
            location="거실",
        ),
    ]


@app.get("/devices/{device_id}", response_model=DeviceInfo, tags=["기기"])
async def get_device(device_id: str):
    """특정 기기 정보 조회"""
    # TODO: 실제 기기 조회 구현
    devices = {
        "light-001": DeviceInfo(
            id="light-001",
            name="거실 조명",
            type="light",
            status="on",
            location="거실",
        ),
    }
    
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="기기를 찾을 수 없습니다")
    
    return devices[device_id]


@app.post("/devices/{device_id}/control", tags=["기기"])
async def control_device(device_id: str, action: str):
    """기기 제어"""
    logger.info(f"기기 제어: {device_id} -> {action}")
    
    # TODO: MQTT로 기기에 명령 전송
    # await mqtt_client.publish(MQTTMessage(
    #     topic=f"device/{device_id}/control",
    #     payload={"action": action},
    # ))
    
    return {
        "success": True,
        "device_id": device_id,
        "action": action,
        "message": f"{device_id}에 {action} 명령을 전송했습니다",
    }


# ==================== 메인 실행 ====================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
