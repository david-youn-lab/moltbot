# 서버

프로덕션용 백엔드 서버

## 구조

```
서버/
├── main.py              # 메인 애플리케이션
├── config.py            # 서버 설정
├── api/                 # API 라우터
│   ├── auth_routes.py   # 인증 (회원가입/로그인)
│   ├── user_routes.py   # 사용자 관리
│   ├── device_routes.py # 기기 관리
│   └── command_routes.py# 음성 명령
├── auth/                # 인증 모듈
│   ├── jwt_handler.py   # JWT 토큰
│   ├── password.py      # 비밀번호 해싱
│   └── dependencies.py  # FastAPI 의존성
├── database/            # 데이터베이스
│   ├── connection.py    # 연결 관리
│   └── models.py        # ORM 모델
└── security/            # 보안
    ├── rate_limiter.py  # 속도 제한
    ├── encryption.py    # 암호화
    └── validators.py    # 입력 검증
```

## 실행

### 개발 모드

```bash
cd 서버
uvicorn main:app --reload --port 8000
```

### 프로덕션 모드

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API 엔드포인트

### 인증 (/api/v1/auth)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | /register | 회원가입 |
| POST | /login | 로그인 |
| POST | /refresh | 토큰 갱신 |
| POST | /logout | 로그아웃 |

### 사용자 (/api/v1/users)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | /me | 내 프로필 |
| PATCH | /me | 프로필 수정 |
| POST | /me/password | 비밀번호 변경 |
| DELETE | /me | 계정 삭제 |

### 기기 (/api/v1/devices)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | / | 기기 목록 |
| POST | / | 기기 등록 |
| GET | /{id} | 기기 상세 |
| PATCH | /{id} | 기기 수정 |
| DELETE | /{id} | 기기 삭제 |
| POST | /{id}/control | 기기 제어 |

### 명령 (/api/v1/commands)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | / | 명령 처리 |
| GET | /history | 명령 기록 |

## 환경 변수

```env
# 필수
SECRET_KEY=your-super-secret-key-change-in-production

# 데이터베이스
DATABASE_URL=sqlite:///./voicecontrol.db

# 선택
DEBUG=false
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
```

## 보안 기능

- JWT 기반 인증
- bcrypt 비밀번호 해싱
- 속도 제한 (Rate Limiting)
- 입력 검증 및 정제
- 계정 잠금 (5회 실패 시 30분)
- CORS 설정

## 배포

### Oracle Cloud Free Tier (권장)

1. 인스턴스 생성 (Ubuntu)
2. Docker 설치
3. 컨테이너 실행

### Docker

```bash
docker build -t voicecontrol-server .
docker run -d -p 8000:8000 voicecontrol-server
```
