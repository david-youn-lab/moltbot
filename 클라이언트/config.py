"""
클라이언트 설정
"""

import os
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class ClientConfig:
    """클라이언트 설정"""
    
    # 서버 설정
    server_url: str = "http://localhost:8000"
    
    # 인증
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    
    # 음성인식 설정
    whisper_model: str = "base"
    language: str = "ko"
    use_gpu: bool = False
    
    # 오디오 설정
    sample_rate: int = 16000
    channels: int = 1
    
    # 기타
    auto_reconnect: bool = True
    debug: bool = False


def get_config_path() -> Path:
    """설정 파일 경로"""
    # 사용자 홈 디렉토리에 저장
    if os.name == "nt":  # Windows
        config_dir = Path(os.environ.get("APPDATA", "")) / "VoiceControl"
    else:  # Linux/Mac
        config_dir = Path.home() / ".config" / "voicecontrol"
    
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "config.json"


def load_config() -> ClientConfig:
    """설정 로드"""
    config_path = get_config_path()
    
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return ClientConfig(**data)
        except Exception:
            pass
    
    return ClientConfig()


def save_config(config: ClientConfig) -> None:
    """설정 저장"""
    config_path = get_config_path()
    
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(asdict(config), f, indent=2, ensure_ascii=False)


def clear_tokens() -> None:
    """토큰 삭제 (로그아웃)"""
    config = load_config()
    config.access_token = None
    config.refresh_token = None
    save_config(config)
