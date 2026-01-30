# 클라이언트 (트리거)

소비자용 클라이언트 애플리케이션

## 개요

소비자가 다운받아 실행하는 프로그램입니다.
서버와 통신하여 음성 명령을 처리합니다.

## 구조

```
클라이언트/
├── __init__.py
├── config.py       # 설정 관리
├── api_client.py   # 서버 API 클라이언트
├── trigger.py      # 메인 애플리케이션
└── README.md
```

## 실행

```bash
cd 클라이언트
python -m trigger
```

## 기능

### 인증
- 회원가입
- 로그인 (자동 토큰 저장)
- 자동 토큰 갱신
- 로그아웃

### 기기 제어
- 기기 목록 조회
- 기기 제어 (켜기/끄기 등)

### 음성 제어
- 텍스트 명령 (현재)
- 음성 인식 (구현 예정)

## 설정 파일

설정은 자동으로 저장됩니다:
- Windows: `%APPDATA%/VoiceControl/config.json`
- Linux/Mac: `~/.config/voicecontrol/config.json`

```json
{
  "server_url": "http://localhost:8000",
  "access_token": "...",
  "refresh_token": "...",
  "whisper_model": "base",
  "language": "ko"
}
```

## 배포

### PyInstaller로 실행 파일 생성

```bash
pip install pyinstaller
pyinstaller --onefile --name voicecontrol trigger.py
```

### Nuitka로 더 빠른 실행 파일 생성

```bash
pip install nuitka
python -m nuitka --standalone --onefile trigger.py
```

## 보안

- 토큰은 로컬에 암호화 없이 저장됨 (개선 필요)
- HTTPS 사용 권장
- 토큰 자동 갱신으로 보안 강화

## TODO

- [ ] 실제 음성 인식 통합
- [ ] 웨이크워드 감지
- [ ] 시스템 트레이 앱
- [ ] 자동 업데이트
- [ ] 토큰 암호화 저장
