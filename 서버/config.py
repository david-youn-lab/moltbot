"""
서버 설정
프로덕션 환경 설정을 관리합니다.
"""

from functools import lru_cache
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field


class ServerSettings(BaseSettings):
    """서버 설정"""
    
    # === 기본 설정 ===
    app_name: str = Field(default="VoiceControl", description="앱 이름")
    app_version: str = Field(default="0.1.0", description="앱 버전")
    debug: bool = Field(default=False, description="디버그 모드")
    environment: str = Field(default="development", description="환경 (development/staging/production)")
    
    # === 서버 설정 ===
    host: str = Field(default="0.0.0.0", description="서버 호스트")
    port: int = Field(default=8000, description="서버 포트")
    workers: int = Field(default=4, description="워커 수")
    
    # === 보안 설정 ===
    secret_key: str = Field(default="change-this-in-production-use-long-random-string", description="JWT 시크릿 키")
    algorithm: str = Field(default="HS256", description="JWT 알고리즘")
    access_token_expire_minutes: int = Field(default=30, description="액세스 토큰 만료 시간(분)")
    refresh_token_expire_days: int = Field(default=7, description="리프레시 토큰 만료 시간(일)")
    
    # === 데이터베이스 설정 ===
    database_url: str = Field(
        default="sqlite:///./voicecontrol.db",
        description="데이터베이스 URL (SQLite/PostgreSQL/MySQL)"
    )
    database_echo: bool = Field(default=False, description="SQL 쿼리 로깅")
    
    # === CORS 설정 ===
    cors_origins: List[str] = Field(
        default=["*"],
        description="허용된 오리진 목록"
    )
    
    # === API 제한 ===
    rate_limit_requests: int = Field(default=100, description="분당 최대 요청 수")
    rate_limit_window: int = Field(default=60, description="제한 윈도우(초)")
    
    # === 로깅 ===
    log_level: str = Field(default="INFO", description="로그 레벨")
    log_file: Optional[str] = Field(default="logs/server.log", description="로그 파일")
    
    # === 외부 서비스 ===
    supabase_url: Optional[str] = Field(default=None, description="Supabase URL")
    supabase_key: Optional[str] = Field(default=None, description="Supabase API Key")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


@lru_cache()
def get_server_settings() -> ServerSettings:
    """서버 설정 싱글톤"""
    return ServerSettings()
