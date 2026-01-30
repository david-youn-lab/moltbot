"""
설정 관리 모듈
"""

from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # 서버 설정
    host: str = Field(default="0.0.0.0", description="서버 호스트")
    port: int = Field(default=8000, description="서버 포트")
    debug: bool = Field(default=False, description="디버그 모드")
    
    # MQTT 설정
    mqtt_broker: str = Field(default="localhost", description="MQTT 브로커 주소")
    mqtt_port: int = Field(default=1883, description="MQTT 포트")
    mqtt_username: Optional[str] = Field(default=None, description="MQTT 사용자명")
    mqtt_password: Optional[str] = Field(default=None, description="MQTT 비밀번호")
    
    # 음성인식 설정
    whisper_model: str = Field(default="base", description="Whisper 모델 크기")
    whisper_language: str = Field(default="ko", description="인식 언어")
    whisper_device: str = Field(default="cpu", description="처리 장치")
    
    # 로깅 설정
    log_level: str = Field(default="INFO", description="로그 레벨")
    log_file: Optional[str] = Field(default=None, description="로그 파일 경로")
    
    # 보안 설정
    secret_key: str = Field(default="change-me-in-production", description="시크릿 키")
    api_key: Optional[str] = Field(default=None, description="API 키")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """설정 싱글톤 반환"""
    return Settings()
