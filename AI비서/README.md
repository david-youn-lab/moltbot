# AI비서

대화형 비서 기능 모듈

## 역할

- 자연어 대화 처리
- 컨텍스트 유지
- 다중 턴 대화
- 개인화된 응답

## 기능

### 대화 처리
- 일상 대화
- 질문 응답
- 명령 해석

### 스마트홈 연동
- "거실 불 켜줘" → 기기 제어
- "지금 몇 도야?" → 센서 조회
- "나갈 때 다 꺼줘" → 시나리오 실행

### 정보 제공
- 날씨 정보
- 뉴스 브리핑
- 일정 알림

### 개인화
- 사용자 선호 학습
- 습관 기반 자동화
- 맞춤 응답

## 기술 스택

### LLM 옵션
- OpenAI GPT-4
- Anthropic Claude
- 로컬 LLM (Ollama)

### 음성 합성 (TTS)
- Google TTS
- Edge TTS
- 로컬 TTS

## 구현 예정

```python
from AI비서 import Assistant

# 비서 초기화
assistant = Assistant(
    llm="gpt-4",
    tts="edge-tts",
    language="ko",
)

# 대화
response = await assistant.chat("오늘 날씨 어때?")
print(response.text)

# 음성 출력
await assistant.speak(response.text)
```

## 웨이크워드 후보

- "아리아" (Aria)
- "하윤아"
- 커스텀 웨이크워드

## TODO

- [ ] LLM 연동
- [ ] 대화 컨텍스트 관리
- [ ] 음성 합성 (TTS)
- [ ] 웨이크워드 감지
- [ ] 스킬 시스템
- [ ] 개인화 엔진
