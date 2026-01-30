# 공통라이브러리

음성인식 제어 시스템에서 사용되는 공통 유틸리티 모듈

## 모듈 구성

### config.py
환경 설정 관리
- `Settings`: Pydantic 기반 설정 클래스
- `get_settings()`: 설정 싱글톤 반환

### logger.py
로깅 설정
- `setup_logger()`: 로거 초기화
- `get_logger()`: 모듈별 로거 반환

### mqtt_client.py
MQTT 통신 클라이언트
- `MQTTClient`: 비동기 MQTT 클라이언트
- `MQTTMessage`: 메시지 데이터 클래스
- `Topics`: 사전 정의된 토픽 상수

### exceptions.py
사용자 정의 예외
- `VoiceControlError`: 기본 예외
- `DeviceNotFoundError`: 기기 미발견
- `ConnectionError`: 연결 오류
- `ConfigurationError`: 설정 오류

## 사용 예시

```python
from 공통라이브러리 import Settings, get_settings, setup_logger, get_logger

# 설정 로드
settings = get_settings()
print(settings.mqtt_broker)

# 로거 설정
setup_logger(level="DEBUG", log_file="app.log")
logger = get_logger(__name__)
logger.info("애플리케이션 시작")

# MQTT 클라이언트
from 공통라이브러리 import MQTTClient
from 공통라이브러리.mqtt_client import MQTTConfig, MQTTMessage

config = MQTTConfig(broker="localhost", port=1883)
client = MQTTClient(config)
await client.connect()
await client.publish(MQTTMessage(topic="test", payload={"hello": "world"}))
```

## 의존성

- pydantic-settings
- loguru
- aiomqtt (MQTT 사용 시)
