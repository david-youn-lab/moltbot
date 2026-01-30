"""
명령어 파서 모듈

인식된 음성 텍스트를 분석하여 실행 가능한 명령으로 변환합니다.
"""

import sys
import re
from pathlib import Path
from typing import Optional, Any
from dataclasses import dataclass, field
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent))
from 공통라이브러리 import get_logger

logger = get_logger(__name__)


class ActionType(Enum):
    """동작 유형"""
    TURN_ON = "turn_on"
    TURN_OFF = "turn_off"
    SET_VALUE = "set_value"
    INCREASE = "increase"
    DECREASE = "decrease"
    QUERY = "query"
    UNKNOWN = "unknown"


class DeviceType(Enum):
    """기기 유형"""
    LIGHT = "light"
    AIRCON = "aircon"
    TV = "tv"
    FAN = "fan"
    SPEAKER = "speaker"
    CURTAIN = "curtain"
    DOOR = "door"
    UNKNOWN = "unknown"


@dataclass
class ParsedCommand:
    """파싱된 명령"""
    action: ActionType
    device_type: DeviceType
    location: Optional[str] = None
    value: Optional[Any] = None
    raw_text: str = ""
    confidence: float = 1.0
    
    @property
    def is_valid(self) -> bool:
        """유효한 명령인지 확인"""
        return (
            self.action != ActionType.UNKNOWN and
            self.device_type != DeviceType.UNKNOWN
        )
    
    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            "action": self.action.value,
            "device_type": self.device_type.value,
            "location": self.location,
            "value": self.value,
            "raw_text": self.raw_text,
            "confidence": self.confidence,
        }


class CommandParser:
    """
    명령어 파서
    
    한국어 음성 명령을 분석하여 구조화된 명령으로 변환합니다.
    """
    
    # 동작 키워드 매핑
    ACTION_KEYWORDS = {
        ActionType.TURN_ON: ["켜", "켜줘", "켜 줘", "틀어", "틀어줘", "on", "열어", "열어줘"],
        ActionType.TURN_OFF: ["꺼", "꺼줘", "꺼 줘", "끄다", "off", "닫아", "닫아줘"],
        ActionType.INCREASE: ["높여", "높여줘", "올려", "올려줘", "세게", "밝게"],
        ActionType.DECREASE: ["낮춰", "낮춰줘", "내려", "내려줘", "약하게", "어둡게"],
        ActionType.SET_VALUE: ["맞춰", "맞춰줘", "설정", "세팅"],
        ActionType.QUERY: ["뭐야", "어때", "상태", "알려줘", "몇"],
    }
    
    # 기기 키워드 매핑
    DEVICE_KEYWORDS = {
        DeviceType.LIGHT: ["불", "조명", "전등", "라이트", "light", "램프"],
        DeviceType.AIRCON: ["에어컨", "에어콘", "냉방", "aircon", "ac"],
        DeviceType.TV: ["티비", "TV", "텔레비전", "television"],
        DeviceType.FAN: ["선풍기", "팬", "fan"],
        DeviceType.SPEAKER: ["스피커", "speaker", "음악", "볼륨"],
        DeviceType.CURTAIN: ["커튼", "블라인드", "curtain"],
        DeviceType.DOOR: ["문", "door", "현관"],
    }
    
    # 위치 키워드
    LOCATION_KEYWORDS = [
        "거실", "안방", "침실", "주방", "부엌", "욕실", "화장실",
        "현관", "베란다", "발코니", "서재", "아이방", "손님방",
    ]
    
    def __init__(self):
        logger.info("명령어 파서 초기화")
    
    def parse(self, text: str) -> ParsedCommand:
        """
        텍스트 명령 파싱
        
        Args:
            text: 인식된 음성 텍스트
            
        Returns:
            파싱된 명령
        """
        text = text.strip().lower()
        logger.debug(f"명령어 파싱: {text}")
        
        action = self._detect_action(text)
        device_type = self._detect_device(text)
        location = self._detect_location(text)
        value = self._detect_value(text)
        
        command = ParsedCommand(
            action=action,
            device_type=device_type,
            location=location,
            value=value,
            raw_text=text,
        )
        
        logger.info(f"파싱 결과: {command.to_dict()}")
        return command
    
    def _detect_action(self, text: str) -> ActionType:
        """동작 감지"""
        for action, keywords in self.ACTION_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    return action
        return ActionType.UNKNOWN
    
    def _detect_device(self, text: str) -> DeviceType:
        """기기 감지"""
        for device, keywords in self.DEVICE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    return device
        return DeviceType.UNKNOWN
    
    def _detect_location(self, text: str) -> Optional[str]:
        """위치 감지"""
        for location in self.LOCATION_KEYWORDS:
            if location in text:
                return location
        return None
    
    def _detect_value(self, text: str) -> Optional[Any]:
        """값 감지 (온도, 밝기 등)"""
        # 숫자 감지
        numbers = re.findall(r'\d+', text)
        if numbers:
            return int(numbers[0])
        
        # 퍼센트 감지
        percent_match = re.search(r'(\d+)\s*(%|퍼센트|프로)', text)
        if percent_match:
            return {"type": "percent", "value": int(percent_match.group(1))}
        
        # 온도 감지
        temp_match = re.search(r'(\d+)\s*(도|°)', text)
        if temp_match:
            return {"type": "temperature", "value": int(temp_match.group(1))}
        
        return None


# 명령어 예시
COMMAND_EXAMPLES = [
    "거실 불 켜줘",
    "안방 에어컨 꺼",
    "에어컨 온도 24도로 맞춰줘",
    "거실 조명 밝기 50%로 설정해줘",
    "티비 볼륨 높여줘",
    "현관문 열어줘",
    "커튼 닫아줘",
]
