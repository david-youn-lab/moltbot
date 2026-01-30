"""
데이터베이스 모델
SQLAlchemy ORM 모델 정의
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, 
    ForeignKey, Text, JSON, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from .connection import Base


class UserRole(enum.Enum):
    """사용자 역할"""
    USER = "user"
    ADMIN = "admin"
    DEVELOPER = "developer"


class DeviceStatus(enum.Enum):
    """기기 상태"""
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"


class User(Base):
    """사용자 모델"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # 프로필
    full_name = Column(String(200), nullable=True)
    phone = Column(String(20), nullable=True)
    
    # 상태
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER)
    
    # 보안
    last_login = Column(DateTime, nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    
    # 타임스탬프
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 관계
    devices = relationship("Device", back_populates="owner", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    command_logs = relationship("CommandLog", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.username}>"


class Device(Base):
    """기기 모델"""
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    device_type = Column(String(50), nullable=False)  # light, aircon, tv, etc.
    
    # 연결 정보
    protocol = Column(String(50), nullable=True)  # mqtt, http, ble
    address = Column(String(255), nullable=True)
    
    # 상태
    status = Column(SQLEnum(DeviceStatus), default=DeviceStatus.OFFLINE)
    last_seen = Column(DateTime, nullable=True)
    current_state = Column(JSON, nullable=True)  # {"power": "on", "brightness": 80}
    
    # 위치
    location = Column(String(100), nullable=True)
    room = Column(String(100), nullable=True)
    
    # 소유자
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="devices")
    
    # 타임스탬프
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Device {self.name}>"


class Session(Base):
    """세션 모델 (리프레시 토큰 관리)"""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 토큰 정보
    refresh_token = Column(String(500), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    
    # 클라이언트 정보
    client_ip = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    device_info = Column(String(200), nullable=True)
    
    # 상태
    is_active = Column(Boolean, default=True)
    revoked_at = Column(DateTime, nullable=True)
    
    # 타임스탬프
    created_at = Column(DateTime, server_default=func.now())
    
    # 관계
    user = relationship("User", back_populates="sessions")
    
    def __repr__(self):
        return f"<Session {self.id}>"


class CommandLog(Base):
    """명령 로그 모델"""
    __tablename__ = "command_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 명령 정보
    raw_text = Column(Text, nullable=True)  # 원본 음성 텍스트
    parsed_action = Column(String(50), nullable=True)
    parsed_device = Column(String(50), nullable=True)
    parsed_location = Column(String(100), nullable=True)
    parsed_value = Column(JSON, nullable=True)
    
    # 결과
    success = Column(Boolean, default=False)
    response = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # 처리 시간
    processing_time_ms = Column(Integer, nullable=True)
    
    # 타임스탬프
    created_at = Column(DateTime, server_default=func.now())
    
    # 관계
    user = relationship("User", back_populates="command_logs")
    
    def __repr__(self):
        return f"<CommandLog {self.id}>"


class APIKey(Base):
    """API 키 모델 (개발자용)"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 키 정보
    key_hash = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    prefix = Column(String(10), nullable=False)  # 키 앞부분 (표시용)
    
    # 권한
    scopes = Column(JSON, default=list)  # ["read", "write", "admin"]
    
    # 제한
    rate_limit = Column(Integer, default=1000)  # 시간당 요청 수
    expires_at = Column(DateTime, nullable=True)
    
    # 상태
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime, nullable=True)
    
    # 타임스탬프
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<APIKey {self.prefix}...>"
