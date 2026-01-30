# 주변기기설정

IoT 기기 통합 모듈

## 역할

- IoT 기기 검색 및 등록
- 기기 상태 모니터링
- 기기 제어 명령 전송
- 프로토콜 추상화

## 지원 프로토콜

### Matter (예정)
- 차세대 스마트홈 표준
- Apple, Google, Amazon 공동 지원
- Thread 네트워크 기반

### MQTT
- 경량 메시지 프로토콜
- Tasmota, ESPHome 기기 지원

### WiFi
- 직접 HTTP/REST 통신
- 제조사별 API 연동

### Bluetooth LE
- 근거리 저전력 기기
- 센서, 웨어러블 등

## 기기 유형

| 유형 | 기능 | 예시 |
|------|------|------|
| 조명 | on/off, 밝기, 색상 | Philips Hue, IKEA TRÅDFRI |
| 에어컨 | on/off, 온도, 모드 | 삼성, LG ThinQ |
| TV | on/off, 볼륨, 채널 | 삼성, LG WebOS |
| 스피커 | on/off, 볼륨, 재생 | Sonos, 에코 |
| 센서 | 온도, 습도, 동작 | Aqara, Xiaomi |

## 구현 예정

```python
from 주변기기설정 import DeviceManager, Device

# 기기 관리자
manager = DeviceManager()

# 기기 검색
devices = await manager.discover()

# 기기 등록
light = Device(
    id="light-001",
    name="거실 조명",
    type="light",
    protocol="mqtt",
    address="zigbee2mqtt/거실조명",
)
manager.register(light)

# 기기 제어
await manager.control("light-001", action="turn_on", brightness=80)
```

## TODO

- [ ] 기기 검색 (mDNS/SSDP)
- [ ] Matter 프로토콜 지원
- [ ] 삼성 SmartThings 연동
- [ ] LG ThinQ 연동
- [ ] 기기 그룹화
- [ ] 자동화 규칙
