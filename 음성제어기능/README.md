# 음성제어기능

음성 인식 엔진 모듈

## 구성요소

### recognizer.py - 음성 인식기
- OpenAI Whisper 기반 음성-텍스트 변환
- Vosk 경량 대안 지원 (오프라인)

### audio_capture.py - 오디오 캡처
- 마이크 입력 캡처
- VAD (Voice Activity Detection)
- 파일 녹음

### command_parser.py - 명령어 파서
- 한국어 자연어 명령 분석
- 동작/기기/위치/값 추출

## 지원 명령어 예시

```
"거실 불 켜줘"
"안방 에어컨 꺼"
"에어컨 온도 24도로 맞춰줘"
"거실 조명 밝기 50%로 설정해줘"
"티비 볼륨 높여줘"
```

## 사용 예시

```python
from 음성제어기능 import VoiceRecognizer, AudioCapture, CommandParser

# 음성 인식기 초기화
recognizer = VoiceRecognizer(model_size="base", language="ko")
recognizer.load_model()

# 오디오 캡처
capture = AudioCapture()
capture.record_to_file("recording.wav", duration_seconds=5)

# 음성 인식
result = recognizer.recognize("recording.wav")
print(f"인식 결과: {result.text}")

# 명령어 파싱
parser = CommandParser()
command = parser.parse(result.text)
print(f"동작: {command.action}, 기기: {command.device_type}")
```

## 모델 크기별 특성

| 모델 | 파라미터 | VRAM | 상대 속도 | 정확도 |
|------|----------|------|-----------|--------|
| tiny | 39M | ~1GB | 32x | 낮음 |
| base | 74M | ~1GB | 16x | 보통 |
| small | 244M | ~2GB | 6x | 좋음 |
| medium | 769M | ~5GB | 2x | 매우 좋음 |
| large | 1550M | ~10GB | 1x | 최고 |

## TODO

- [ ] 실시간 스트리밍 인식
- [ ] 웨이크워드 감지 ("아리아", "하이 빅스비" 등)
- [ ] 다중 언어 지원
- [ ] 화자 분리
- [ ] 소음 환경 최적화
