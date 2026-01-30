"""
비밀번호 해싱 및 검증
bcrypt를 사용한 안전한 비밀번호 처리
"""

from passlib.context import CryptContext

# bcrypt 컨텍스트 설정
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # 해시 라운드 (높을수록 안전하지만 느림)
)


def hash_password(password: str) -> str:
    """
    비밀번호 해싱
    
    Args:
        password: 평문 비밀번호
        
    Returns:
        해시된 비밀번호
    """
    # bcrypt는 72바이트 제한이 있음
    password_bytes = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return pwd_context.hash(password_bytes)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    비밀번호 검증
    
    Args:
        plain_password: 평문 비밀번호
        hashed_password: 해시된 비밀번호
        
    Returns:
        일치 여부
    """
    # bcrypt는 72바이트 제한이 있음
    password_bytes = plain_password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return pwd_context.verify(password_bytes, hashed_password)


def check_password_strength(password: str) -> tuple[bool, list[str]]:
    """
    비밀번호 강도 검사
    
    Args:
        password: 검사할 비밀번호
        
    Returns:
        (통과 여부, 오류 메시지 목록)
    """
    errors = []
    
    if len(password) < 8:
        errors.append("비밀번호는 최소 8자 이상이어야 합니다")
    
    if not any(c.isupper() for c in password):
        errors.append("대문자를 최소 1개 포함해야 합니다")
    
    if not any(c.islower() for c in password):
        errors.append("소문자를 최소 1개 포함해야 합니다")
    
    if not any(c.isdigit() for c in password):
        errors.append("숫자를 최소 1개 포함해야 합니다")
    
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        errors.append("특수문자를 최소 1개 포함해야 합니다")
    
    return len(errors) == 0, errors
