"""
입력 검증 및 정제
보안을 위한 데이터 검증
"""

import re
import html
from typing import Optional


def validate_email(email: str) -> tuple[bool, Optional[str]]:
    """
    이메일 주소 검증
    
    Args:
        email: 이메일 주소
        
    Returns:
        (유효 여부, 오류 메시지)
    """
    if not email:
        return False, "이메일을 입력하세요"
    
    # 기본 형식 검사
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "유효한 이메일 형식이 아닙니다"
    
    # 길이 검사
    if len(email) > 255:
        return False, "이메일이 너무 깁니다"
    
    return True, None


def validate_phone(phone: str) -> tuple[bool, Optional[str]]:
    """
    전화번호 검증 (한국 형식)
    
    Args:
        phone: 전화번호
        
    Returns:
        (유효 여부, 오류 메시지)
    """
    if not phone:
        return True, None  # 선택 항목
    
    # 숫자와 하이픈만 허용
    cleaned = re.sub(r'[^\d]', '', phone)
    
    # 한국 휴대폰 번호 형식 (010, 011, 016, 017, 018, 019)
    if not re.match(r'^01[0-9]\d{7,8}$', cleaned):
        return False, "유효한 전화번호 형식이 아닙니다"
    
    return True, None


def validate_username(username: str) -> tuple[bool, Optional[str]]:
    """
    사용자명 검증
    
    Args:
        username: 사용자명
        
    Returns:
        (유효 여부, 오류 메시지)
    """
    if not username:
        return False, "사용자명을 입력하세요"
    
    if len(username) < 3:
        return False, "사용자명은 최소 3자 이상이어야 합니다"
    
    if len(username) > 50:
        return False, "사용자명은 50자 이하여야 합니다"
    
    # 영문, 숫자, 언더스코어만 허용
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "사용자명은 영문, 숫자, 언더스코어만 사용 가능합니다"
    
    # 숫자로 시작 불가
    if username[0].isdigit():
        return False, "사용자명은 숫자로 시작할 수 없습니다"
    
    return True, None


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    입력 텍스트 정제
    XSS 및 인젝션 방지
    
    Args:
        text: 입력 텍스트
        max_length: 최대 길이
        
    Returns:
        정제된 텍스트
    """
    if not text:
        return ""
    
    # HTML 이스케이프
    sanitized = html.escape(text)
    
    # 제어 문자 제거
    sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', sanitized)
    
    # 연속 공백 정리
    sanitized = re.sub(r'\s+', ' ', sanitized)
    
    # 길이 제한
    sanitized = sanitized[:max_length]
    
    return sanitized.strip()


def sanitize_filename(filename: str) -> str:
    """
    파일명 정제
    경로 탐색 공격 방지
    
    Args:
        filename: 파일명
        
    Returns:
        안전한 파일명
    """
    if not filename:
        return "unnamed"
    
    # 경로 구분자 제거
    filename = filename.replace("/", "_").replace("\\", "_")
    
    # 위험한 문자 제거
    filename = re.sub(r'[<>:"|?*]', '', filename)
    
    # 점으로 시작하는 파일 방지
    filename = filename.lstrip('.')
    
    # 길이 제한
    if len(filename) > 200:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:195] + ('.' + ext if ext else '')
    
    return filename or "unnamed"
