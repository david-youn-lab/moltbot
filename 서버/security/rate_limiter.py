"""
속도 제한 (Rate Limiting)
API 남용 방지
"""

import time
from collections import defaultdict
from typing import Optional, Callable
from functools import wraps
from fastapi import HTTPException, Request, status


class RateLimiter:
    """
    인메모리 속도 제한기
    
    프로덕션에서는 Redis 사용 권장
    """
    
    def __init__(self, requests: int = 100, window: int = 60):
        """
        Args:
            requests: 윈도우당 최대 요청 수
            window: 윈도우 크기 (초)
        """
        self.requests = requests
        self.window = window
        self._storage: dict[str, list[float]] = defaultdict(list)
    
    def _clean_old_requests(self, key: str) -> None:
        """오래된 요청 기록 제거"""
        current_time = time.time()
        self._storage[key] = [
            t for t in self._storage[key]
            if current_time - t < self.window
        ]
    
    def is_allowed(self, key: str) -> tuple[bool, dict]:
        """
        요청 허용 여부 확인
        
        Args:
            key: 클라이언트 식별자 (IP, 사용자 ID 등)
            
        Returns:
            (허용 여부, 메타 정보)
        """
        self._clean_old_requests(key)
        
        current_count = len(self._storage[key])
        remaining = max(0, self.requests - current_count)
        
        meta = {
            "limit": self.requests,
            "remaining": remaining,
            "reset": int(time.time()) + self.window,
        }
        
        if current_count >= self.requests:
            return False, meta
        
        self._storage[key].append(time.time())
        meta["remaining"] = remaining - 1
        
        return True, meta
    
    def reset(self, key: str) -> None:
        """특정 키의 제한 초기화"""
        self._storage[key] = []


# 전역 제한기
_default_limiter = RateLimiter()


async def rate_limit(
    request: Request,
    limiter: Optional[RateLimiter] = None,
) -> None:
    """
    FastAPI 의존성으로 사용하는 속도 제한
    
    사용법:
        @app.get("/api/endpoint")
        async def endpoint(request: Request, _: None = Depends(rate_limit)):
            ...
    """
    if limiter is None:
        limiter = _default_limiter
    
    # 클라이언트 IP 추출
    client_ip = request.client.host if request.client else "unknown"
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        client_ip = forwarded.split(",")[0].strip()
    
    allowed, meta = limiter.is_allowed(client_ip)
    
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="요청이 너무 많습니다. 잠시 후 다시 시도하세요.",
            headers={
                "X-RateLimit-Limit": str(meta["limit"]),
                "X-RateLimit-Remaining": str(meta["remaining"]),
                "X-RateLimit-Reset": str(meta["reset"]),
                "Retry-After": str(meta["reset"] - int(time.time())),
            },
        )


def rate_limit_decorator(requests: int = 100, window: int = 60):
    """
    데코레이터로 사용하는 속도 제한
    
    사용법:
        @rate_limit_decorator(requests=10, window=60)
        async def my_function():
            ...
    """
    limiter = RateLimiter(requests, window)
    
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 첫 번째 인자에서 request 추출 시도
            request = kwargs.get("request") or (args[0] if args else None)
            if request and hasattr(request, "client"):
                client_ip = request.client.host if request.client else "unknown"
                allowed, _ = limiter.is_allowed(client_ip)
                if not allowed:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="요청이 너무 많습니다",
                    )
            return await func(*args, **kwargs)
        return wrapper
    return decorator
