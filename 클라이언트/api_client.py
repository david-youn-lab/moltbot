"""
API 클라이언트
서버와의 통신을 담당합니다.
"""

import httpx
from typing import Optional, Any
from dataclasses import dataclass

from .config import load_config, save_config, ClientConfig


@dataclass
class APIResponse:
    """API 응답"""
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    status_code: int = 0


class APIClient:
    """
    서버 API 클라이언트
    
    자동 토큰 갱신을 지원합니다.
    """
    
    def __init__(self, config: Optional[ClientConfig] = None):
        self.config = config or load_config()
        self._client = httpx.Client(
            base_url=self.config.server_url,
            timeout=30.0,
        )
    
    def _get_headers(self) -> dict:
        """인증 헤더 생성"""
        headers = {"Content-Type": "application/json"}
        if self.config.access_token:
            headers["Authorization"] = f"Bearer {self.config.access_token}"
        return headers
    
    def _handle_response(self, response: httpx.Response) -> APIResponse:
        """응답 처리"""
        try:
            data = response.json()
        except Exception:
            data = None
        
        if response.status_code >= 400:
            error = data.get("detail") if data else response.text
            return APIResponse(
                success=False,
                error=error,
                status_code=response.status_code,
            )
        
        return APIResponse(
            success=True,
            data=data,
            status_code=response.status_code,
        )
    
    def _refresh_token(self) -> bool:
        """토큰 갱신"""
        if not self.config.refresh_token:
            return False
        
        try:
            response = self._client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": self.config.refresh_token},
            )
            
            if response.status_code == 200:
                data = response.json()
                self.config.access_token = data["access_token"]
                self.config.refresh_token = data["refresh_token"]
                save_config(self.config)
                return True
        except Exception:
            pass
        
        return False
    
    def request(
        self,
        method: str,
        path: str,
        data: Optional[dict] = None,
        retry_auth: bool = True,
    ) -> APIResponse:
        """
        API 요청
        
        401 오류 시 자동으로 토큰 갱신을 시도합니다.
        """
        try:
            response = self._client.request(
                method,
                path,
                json=data,
                headers=self._get_headers(),
            )
            
            # 401이면 토큰 갱신 시도
            if response.status_code == 401 and retry_auth:
                if self._refresh_token():
                    return self.request(method, path, data, retry_auth=False)
            
            return self._handle_response(response)
            
        except httpx.ConnectError:
            return APIResponse(
                success=False,
                error="서버에 연결할 수 없습니다",
            )
        except Exception as e:
            return APIResponse(
                success=False,
                error=str(e),
            )
    
    def get(self, path: str) -> APIResponse:
        """GET 요청"""
        return self.request("GET", path)
    
    def post(self, path: str, data: Optional[dict] = None) -> APIResponse:
        """POST 요청"""
        return self.request("POST", path, data)
    
    def patch(self, path: str, data: Optional[dict] = None) -> APIResponse:
        """PATCH 요청"""
        return self.request("PATCH", path, data)
    
    def delete(self, path: str) -> APIResponse:
        """DELETE 요청"""
        return self.request("DELETE", path)
    
    # === 인증 API ===
    
    def register(self, email: str, username: str, password: str) -> APIResponse:
        """회원가입"""
        return self.post("/api/v1/auth/register", {
            "email": email,
            "username": username,
            "password": password,
        })
    
    def login(self, username: str, password: str) -> APIResponse:
        """로그인"""
        response = self.post("/api/v1/auth/login", {
            "username": username,
            "password": password,
        })
        
        if response.success and response.data:
            self.config.access_token = response.data["access_token"]
            self.config.refresh_token = response.data["refresh_token"]
            save_config(self.config)
        
        return response
    
    def logout(self) -> APIResponse:
        """로그아웃"""
        response = self.post("/api/v1/auth/logout", {
            "refresh_token": self.config.refresh_token,
        })
        
        from .config import clear_tokens
        clear_tokens()
        self.config.access_token = None
        self.config.refresh_token = None
        
        return response
    
    # === 사용자 API ===
    
    def get_profile(self) -> APIResponse:
        """내 프로필"""
        return self.get("/api/v1/users/me")
    
    # === 기기 API ===
    
    def list_devices(self) -> APIResponse:
        """기기 목록"""
        return self.get("/api/v1/devices")
    
    def register_device(self, device_id: str, name: str, device_type: str, **kwargs) -> APIResponse:
        """기기 등록"""
        return self.post("/api/v1/devices", {
            "device_id": device_id,
            "name": name,
            "device_type": device_type,
            **kwargs,
        })
    
    def control_device(self, device_id: str, action: str, params: Optional[dict] = None) -> APIResponse:
        """기기 제어"""
        return self.post(f"/api/v1/devices/{device_id}/control", {
            "action": action,
            "params": params,
        })
    
    # === 명령 API ===
    
    def send_command(self, text: str, source: str = "app") -> APIResponse:
        """음성/텍스트 명령"""
        return self.post("/api/v1/commands", {
            "text": text,
            "source": source,
        })
    
    def get_command_history(self, limit: int = 20) -> APIResponse:
        """명령 기록"""
        return self.get(f"/api/v1/commands/history?limit={limit}")
    
    def close(self):
        """클라이언트 종료"""
        self._client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()
