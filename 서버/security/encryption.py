"""
데이터 암호화
민감한 데이터 보호
"""

import base64
import os
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import get_server_settings

settings = get_server_settings()


def _get_fernet() -> Fernet:
    """Fernet 인스턴스 생성"""
    # 시크릿 키에서 암호화 키 파생
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"voicecontrol_salt",  # 프로덕션에서는 환경변수로
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(settings.secret_key.encode()))
    return Fernet(key)


def encrypt_data(data: str) -> str:
    """
    문자열 데이터 암호화
    
    Args:
        data: 암호화할 문자열
        
    Returns:
        암호화된 문자열 (base64)
    """
    fernet = _get_fernet()
    encrypted = fernet.encrypt(data.encode())
    return encrypted.decode()


def decrypt_data(encrypted_data: str) -> Optional[str]:
    """
    암호화된 데이터 복호화
    
    Args:
        encrypted_data: 암호화된 문자열
        
    Returns:
        복호화된 문자열 (실패 시 None)
    """
    try:
        fernet = _get_fernet()
        decrypted = fernet.decrypt(encrypted_data.encode())
        return decrypted.decode()
    except Exception:
        return None


def generate_api_key() -> tuple[str, str]:
    """
    API 키 생성
    
    Returns:
        (평문 키, 해시된 키)
    """
    import secrets
    import hashlib
    
    # 32바이트 랜덤 키 생성
    raw_key = secrets.token_hex(32)
    prefix = raw_key[:8]
    
    # 표시용: vc_xxxxxxxx...
    display_key = f"vc_{raw_key}"
    
    # 저장용: SHA256 해시
    key_hash = hashlib.sha256(display_key.encode()).hexdigest()
    
    return display_key, key_hash


def hash_api_key(api_key: str) -> str:
    """API 키 해시"""
    import hashlib
    return hashlib.sha256(api_key.encode()).hexdigest()
