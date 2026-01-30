"""
메인 서버 애플리케이션
프로덕션용 FastAPI 서버
"""

import sys
from pathlib import Path
from contextlib import asynccontextmanager

sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import get_server_settings
from database.connection import init_db
from api.router import api_router

settings = get_server_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 라이프사이클"""
    # 시작 시
    print(f"[START] {settings.app_name} v{settings.app_version}")
    print(f"[ENV] {settings.environment}")
    
    # 데이터베이스 초기화
    init_db()
    print("[OK] Database initialized")
    
    yield
    
    # 종료 시
    print("[STOP] Server shutdown")


# FastAPI 앱 생성
app = FastAPI(
    title=settings.app_name,
    description="음성인식 IoT 제어 시스템 API",
    version=settings.app_version,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 전역 예외 핸들러
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """전역 예외 처리"""
    if settings.debug:
        import traceback
        return JSONResponse(
            status_code=500,
            content={
                "detail": str(exc),
                "traceback": traceback.format_exc(),
            },
        )
    return JSONResponse(
        status_code=500,
        content={"detail": "서버 내부 오류가 발생했습니다"},
    )


# 라우터 등록
app.include_router(api_router)


# 헬스체크
@app.get("/health")
async def health_check():
    """헬스체크"""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.environment,
    }


# 루트
@app.get("/")
async def root():
    """루트"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs" if settings.debug else "disabled",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        workers=1 if settings.debug else settings.workers,
    )
