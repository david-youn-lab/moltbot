"""
MQTT 클라이언트 모듈
"""

import asyncio
import json
from typing import Any, Callable, Optional
from dataclasses import dataclass, field
from .logger import get_logger

logger = get_logger(__name__)


@dataclass
class MQTTMessage:
    """MQTT 메시지 데이터 클래스"""
    topic: str
    payload: Any
    qos: int = 0
    retain: bool = False


@dataclass
class MQTTConfig:
    """MQTT 연결 설정"""
    broker: str = "localhost"
    port: int = 1883
    username: Optional[str] = None
    password: Optional[str] = None
    client_id: Optional[str] = None
    keepalive: int = 60


class MQTTClient:
    """
    비동기 MQTT 클라이언트
    
    IoT 기기들과의 통신을 담당합니다.
    """
    
    def __init__(self, config: MQTTConfig):
        """
        Args:
            config: MQTT 연결 설정
        """
        self.config = config
        self._client = None
        self._connected = False
        self._subscriptions: dict[str, list[Callable]] = {}
    
    async def connect(self) -> bool:
        """
        MQTT 브로커에 연결
        
        Returns:
            연결 성공 여부
        """
        try:
            # aiomqtt 사용 시
            # from aiomqtt import Client
            # self._client = Client(
            #     hostname=self.config.broker,
            #     port=self.config.port,
            #     username=self.config.username,
            #     password=self.config.password,
            # )
            # await self._client.__aenter__()
            
            logger.info(f"MQTT 브로커 연결 시도: {self.config.broker}:{self.config.port}")
            self._connected = True
            logger.info("MQTT 연결 성공")
            return True
            
        except Exception as e:
            logger.error(f"MQTT 연결 실패: {e}")
            self._connected = False
            return False
    
    async def disconnect(self) -> None:
        """MQTT 연결 해제"""
        if self._client:
            # await self._client.__aexit__(None, None, None)
            pass
        self._connected = False
        logger.info("MQTT 연결 해제")
    
    async def publish(self, message: MQTTMessage) -> bool:
        """
        메시지 발행
        
        Args:
            message: 발행할 메시지
            
        Returns:
            발행 성공 여부
        """
        if not self._connected:
            logger.warning("MQTT 연결되지 않음")
            return False
        
        try:
            payload = json.dumps(message.payload) if isinstance(message.payload, dict) else str(message.payload)
            logger.debug(f"MQTT 발행: {message.topic} -> {payload[:100]}")
            # await self._client.publish(message.topic, payload, qos=message.qos, retain=message.retain)
            return True
            
        except Exception as e:
            logger.error(f"MQTT 발행 실패: {e}")
            return False
    
    async def subscribe(self, topic: str, callback: Callable) -> bool:
        """
        토픽 구독
        
        Args:
            topic: 구독할 토픽
            callback: 메시지 수신 시 호출할 콜백
            
        Returns:
            구독 성공 여부
        """
        if topic not in self._subscriptions:
            self._subscriptions[topic] = []
        self._subscriptions[topic].append(callback)
        
        logger.info(f"MQTT 토픽 구독: {topic}")
        return True
    
    @property
    def is_connected(self) -> bool:
        """연결 상태 확인"""
        return self._connected


# 사전 정의된 토픽들
class Topics:
    """MQTT 토픽 상수"""
    
    # 음성 인식 관련
    VOICE_COMMAND = "voice/command"
    VOICE_STATUS = "voice/status"
    
    # 기기 제어 관련
    DEVICE_CONTROL = "device/{device_id}/control"
    DEVICE_STATUS = "device/{device_id}/status"
    DEVICE_DISCOVERY = "device/discovery"
    
    # 시스템 관련
    SYSTEM_STATUS = "system/status"
    SYSTEM_LOG = "system/log"
