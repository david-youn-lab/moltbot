"""
API 라우터 통합
"""

from fastapi import APIRouter
from .auth_routes import router as auth_router
from .user_routes import router as user_router
from .device_routes import router as device_router
from .command_routes import router as command_router

api_router = APIRouter(prefix="/api/v1")

# 라우터 등록
api_router.include_router(auth_router, prefix="/auth", tags=["인증"])
api_router.include_router(user_router, prefix="/users", tags=["사용자"])
api_router.include_router(device_router, prefix="/devices", tags=["기기"])
api_router.include_router(command_router, prefix="/commands", tags=["명령"])
