# 설치파일

시스템 설치 및 배포 모듈

## 역할

- 원클릭 설치 스크립트
- 의존성 자동 설치
- 환경 설정 자동화
- 시스템 서비스 등록

## 지원 플랫폼

- Windows 10/11
- Ubuntu 20.04+
- Raspberry Pi OS
- macOS (예정)

## 설치 스크립트

### Windows

```powershell
# PowerShell (관리자)
irm https://raw.githubusercontent.com/.../install.ps1 | iex
```

### Linux

```bash
curl -sSL https://raw.githubusercontent.com/.../install.sh | bash
```

## 설치 내용

1. Python 3.10+ 확인/설치
2. 가상환경 생성
3. 의존성 설치
4. 환경 설정 파일 생성
5. 시스템 서비스 등록 (선택)
6. MQTT 브로커 설치 (선택)

## 구성 파일

```
/opt/voice-control/          # Linux
C:\VoiceControl\             # Windows
├── venv/                    # 가상환경
├── config/
│   ├── .env                 # 환경변수
│   └── devices.yaml         # 기기 설정
├── logs/                    # 로그
└── data/                    # 데이터
```

## TODO

- [ ] Windows 설치 스크립트
- [ ] Linux 설치 스크립트
- [ ] Docker Compose
- [ ] Raspberry Pi 최적화
- [ ] 업데이트 스크립트
- [ ] 언인스톨 스크립트
