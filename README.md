# 음성인식 제어 시스템

가정 내 모든 IoT 기기를 음성으로 제어하는 통합 시스템

## 주요 특징

- **오픈소스 기반**: 법적 문제 없음
- **모듈식 아키텍처**: 병렬 개발 가능
- **로컬 처리 우선**: 개인정보보호
- **다중 플랫폼 지원**: Windows, Linux, macOS

## 프로젝트 구조

```
음성인식/
├── 설치파일/          # 시스템 설치 및 배포
├── 음성제어기능/      # 음성 인식 엔진
├── 주변기기설정/      # IoT 기기 통합
├── 공통라이브러리/    # 공통 유틸리티
├── 컨트롤타워/        # 메인 서버
├── AI비서/            # 대화형 비서
├── 테스트/            # 통합 테스트
└── 문서/              # 프로젝트 문서
```

## 빠른 시작

### 1. 요구사항

- Python 3.10+
- Node.js 18+
- Git
- 최소 8GB RAM (Whisper 사용 시)

### 2. 설치

```bash
# 저장소 클론
git clone <repository-url>
cd 음성인식

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 3. 컨트롤타워 실행

```bash
cd 컨트롤타워
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. API 문서 확인

http://localhost:8000/docs

## 기술 스택

| 영역 | 기술 |
|------|------|
| 백엔드 | Python 3.10+, FastAPI, MQTT |
| 음성인식 | OpenAI Whisper, Vosk |
| IoT | Matter, WiFi, BLE, MQTT |
| 프론트엔드 | React, Electron |

## 개발 로드맵

### Phase 1: 기반 구축 ✅ 진행중
- [x] 프로젝트 구조 설계
- [x] 공통 라이브러리 기본 구축
- [x] 컨트롤타워 기본 서버

### Phase 2: 핵심 모듈 개발
- [ ] 음성제어기능 개발
- [ ] 주변기기설정 개발
- [ ] 설치파일 개발

### Phase 3: 확장 기능
- [ ] AI 비서 기능
- [ ] 웹 대시보드

### Phase 4: 통합 및 테스트
- [ ] 모듈 간 통합
- [ ] 종단간 테스트
- [ ] 배포 준비

## 라이선스

MIT License

## 기여

각 모듈은 독립적으로 개발 가능합니다. PR 환영합니다.

## 주의사항

- 음성 데이터는 로컬에서만 처리
- 개인정보보호 원칙 준수
- 상업적 배포 시 법률 자문 필요
