"""
트리거 애플리케이션
소비자가 실행하는 메인 프로그램
"""

import sys
import time
from pathlib import Path
from typing import Optional

from .config import load_config, save_config, ClientConfig
from .api_client import APIClient


class VoiceControlApp:
    """
    음성 제어 앱
    
    소비자가 다운받아 실행하는 클라이언트 애플리케이션입니다.
    """
    
    def __init__(self):
        self.config = load_config()
        self.api = APIClient(self.config)
        self.recognizer = None
        self.audio_capture = None
        self._running = False
    
    def setup(self, server_url: Optional[str] = None) -> bool:
        """
        초기 설정
        
        서버 URL 설정 및 연결 테스트
        """
        if server_url:
            self.config.server_url = server_url
            save_config(self.config)
            self.api = APIClient(self.config)
        
        # 연결 테스트
        try:
            import httpx
            response = httpx.get(f"{self.config.server_url}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ 서버 연결 성공: {self.config.server_url}")
                return True
        except Exception as e:
            print(f"❌ 서버 연결 실패: {e}")
        
        return False
    
    def login(self, username: str, password: str) -> bool:
        """로그인"""
        response = self.api.login(username, password)
        
        if response.success:
            print(f"✅ 로그인 성공!")
            return True
        else:
            print(f"❌ 로그인 실패: {response.error}")
            return False
    
    def register(self, email: str, username: str, password: str) -> bool:
        """회원가입"""
        response = self.api.register(email, username, password)
        
        if response.success:
            print(f"✅ 회원가입 성공!")
            return True
        else:
            print(f"❌ 회원가입 실패: {response.error}")
            return False
    
    def is_logged_in(self) -> bool:
        """로그인 상태 확인"""
        if not self.config.access_token:
            return False
        
        response = self.api.get_profile()
        return response.success
    
    def send_command(self, text: str) -> dict:
        """
        텍스트 명령 전송
        
        Args:
            text: 명령어 텍스트
            
        Returns:
            처리 결과
        """
        response = self.api.send_command(text, source="app")
        
        if response.success:
            return response.data
        else:
            return {"success": False, "message": response.error}
    
    def list_devices(self) -> list:
        """기기 목록 조회"""
        response = self.api.list_devices()
        
        if response.success:
            return response.data
        return []
    
    def control_device(self, device_id: str, action: str) -> bool:
        """기기 제어"""
        response = self.api.control_device(device_id, action)
        return response.success
    
    def start_voice_control(self):
        """
        음성 제어 시작
        
        마이크에서 음성을 인식하여 명령을 처리합니다.
        """
        print("🎤 음성 제어를 시작합니다...")
        print("💡 Ctrl+C로 종료할 수 있습니다")
        print()
        
        # TODO: 실제 음성 인식 구현
        # 현재는 텍스트 입력으로 대체
        
        self._running = True
        
        try:
            while self._running:
                text = input("명령 입력 (종료: quit): ").strip()
                
                if text.lower() in ["quit", "exit", "종료"]:
                    break
                
                if not text:
                    continue
                
                result = self.send_command(text)
                
                if result.get("success"):
                    print(f"✅ {result.get('message')}")
                else:
                    print(f"❌ {result.get('message')}")
                
                print()
                
        except KeyboardInterrupt:
            print("\n👋 음성 제어를 종료합니다")
        
        self._running = False
    
    def stop(self):
        """중지"""
        self._running = False
    
    def close(self):
        """종료"""
        self.api.close()


def main():
    """메인 함수"""
    app = VoiceControlApp()
    
    print("=" * 50)
    print("🎤 음성인식 IoT 제어 시스템")
    print("=" * 50)
    print()
    
    # 서버 연결 확인
    if not app.setup():
        server_url = input("서버 URL 입력: ").strip()
        if not app.setup(server_url):
            print("서버에 연결할 수 없습니다. 종료합니다.")
            return
    
    # 로그인 확인
    if not app.is_logged_in():
        print("\n로그인이 필요합니다.")
        choice = input("1. 로그인  2. 회원가입: ").strip()
        
        if choice == "2":
            email = input("이메일: ").strip()
            username = input("사용자명: ").strip()
            password = input("비밀번호: ").strip()
            
            if not app.register(email, username, password):
                return
        
        username = input("사용자명 또는 이메일: ").strip()
        password = input("비밀번호: ").strip()
        
        if not app.login(username, password):
            return
    
    # 메인 메뉴
    while True:
        print("\n" + "=" * 30)
        print("1. 음성 제어 시작")
        print("2. 기기 목록")
        print("3. 명령 입력")
        print("4. 로그아웃")
        print("0. 종료")
        print("=" * 30)
        
        choice = input("선택: ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            app.start_voice_control()
        elif choice == "2":
            devices = app.list_devices()
            if devices:
                print("\n📱 등록된 기기:")
                for d in devices:
                    status = "🟢" if d["status"] == "online" else "🔴"
                    print(f"  {status} {d['name']} ({d['device_type']})")
            else:
                print("등록된 기기가 없습니다")
        elif choice == "3":
            text = input("명령 입력: ").strip()
            if text:
                result = app.send_command(text)
                print(f"결과: {result.get('message')}")
        elif choice == "4":
            app.api.logout()
            print("로그아웃되었습니다")
            break
    
    app.close()
    print("\n👋 프로그램을 종료합니다")


if __name__ == "__main__":
    main()
