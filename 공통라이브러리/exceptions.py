"""
사용자 정의 예외 클래스
"""


class VoiceControlError(Exception):
    """음성 제어 시스템 기본 예외"""
    
    def __init__(self, message: str, code: str = "UNKNOWN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class DeviceNotFoundError(VoiceControlError):
    """기기를 찾을 수 없는 경우"""
    
    def __init__(self, device_id: str):
        super().__init__(
            message=f"기기를 찾을 수 없습니다: {device_id}",
            code="DEVICE_NOT_FOUND"
        )
        self.device_id = device_id


class ConnectionError(VoiceControlError):
    """연결 오류"""
    
    def __init__(self, target: str, reason: str = ""):
        message = f"연결 실패: {target}"
        if reason:
            message += f" ({reason})"
        super().__init__(message=message, code="CONNECTION_ERROR")
        self.target = target
        self.reason = reason


class ConfigurationError(VoiceControlError):
    """설정 오류"""
    
    def __init__(self, message: str):
        super().__init__(message=message, code="CONFIGURATION_ERROR")


class AudioProcessingError(VoiceControlError):
    """오디오 처리 오류"""
    
    def __init__(self, message: str):
        super().__init__(message=message, code="AUDIO_PROCESSING_ERROR")


class RecognitionError(VoiceControlError):
    """음성 인식 오류"""
    
    def __init__(self, message: str):
        super().__init__(message=message, code="RECOGNITION_ERROR")


class CommandError(VoiceControlError):
    """명령 처리 오류"""
    
    def __init__(self, command: str, reason: str = ""):
        message = f"명령 처리 실패: {command}"
        if reason:
            message += f" ({reason})"
        super().__init__(message=message, code="COMMAND_ERROR")
        self.command = command
        self.reason = reason
