"""
데이터베이스 연결 관리
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import get_server_settings

settings = get_server_settings()

# 엔진 생성
engine = create_engine(
    settings.database_url,
    echo=settings.database_echo,
    # SQLite 전용 설정
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    # 커넥션 풀 설정
    pool_pre_ping=True,
    pool_recycle=300,
)

# 세션 팩토리
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 모델 베이스
Base = declarative_base()


def get_db() -> Generator:
    """
    데이터베이스 세션 의존성
    
    FastAPI의 Depends()와 함께 사용합니다.
    
    Yields:
        데이터베이스 세션
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    데이터베이스 초기화
    
    모든 테이블을 생성합니다.
    """
    Base.metadata.create_all(bind=engine)


def drop_db() -> None:
    """
    데이터베이스 삭제 (주의!)
    
    모든 테이블을 삭제합니다. 개발 환경에서만 사용하세요.
    """
    Base.metadata.drop_all(bind=engine)
