"""
오디오 캡처 모듈

마이크에서 오디오를 캡처하고 처리합니다.
"""

import sys
from pathlib import Path
from typing import Optional, Callable
from dataclasses import dataclass
import asyncio

sys.path.insert(0, str(Path(__file__).parent.parent))
from 공통라이브러리 import get_logger

logger = get_logger(__name__)


@dataclass
class AudioConfig:
    """오디오 설정"""
    sample_rate: int = 16000  # Whisper는 16kHz 사용
    channels: int = 1  # 모노
    chunk_size: int = 1024
    format: str = "int16"


class AudioCapture:
    """
    오디오 캡처
    
    마이크에서 오디오를 캡처하고, VAD(Voice Activity Detection)로
    음성 구간을 감지합니다.
    """
    
    def __init__(self, config: Optional[AudioConfig] = None):
        """
        Args:
            config: 오디오 설정
        """
        self.config = config or AudioConfig()
        self._stream = None
        self._is_recording = False
        self._callbacks: list[Callable] = []
        
        logger.info(f"오디오 캡처 초기화: {self.config.sample_rate}Hz, {self.config.channels}ch")
    
    def list_devices(self) -> list[dict]:
        """
        사용 가능한 오디오 입력 장치 목록
        
        Returns:
            장치 정보 목록
        """
        try:
            import sounddevice as sd
            
            devices = []
            for i, device in enumerate(sd.query_devices()):
                if device["max_input_channels"] > 0:
                    devices.append({
                        "id": i,
                        "name": device["name"],
                        "channels": device["max_input_channels"],
                        "sample_rate": device["default_samplerate"],
                    })
            
            return devices
            
        except ImportError:
            logger.error("sounddevice 패키지가 설치되지 않았습니다")
            return []
    
    def start_recording(self, device_id: Optional[int] = None) -> bool:
        """
        녹음 시작
        
        Args:
            device_id: 장치 ID (None이면 기본 장치)
            
        Returns:
            시작 성공 여부
        """
        if self._is_recording:
            logger.warning("이미 녹음 중입니다")
            return False
        
        try:
            import sounddevice as sd
            import numpy as np
            
            def audio_callback(indata, frames, time, status):
                if status:
                    logger.warning(f"오디오 상태: {status}")
                
                # 콜백 호출
                for callback in self._callbacks:
                    callback(indata.copy())
            
            self._stream = sd.InputStream(
                device=device_id,
                samplerate=self.config.sample_rate,
                channels=self.config.channels,
                blocksize=self.config.chunk_size,
                callback=audio_callback,
            )
            self._stream.start()
            self._is_recording = True
            
            logger.info("녹음 시작")
            return True
            
        except Exception as e:
            logger.error(f"녹음 시작 실패: {e}")
            return False
    
    def stop_recording(self) -> None:
        """녹음 중지"""
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        
        self._is_recording = False
        logger.info("녹음 중지")
    
    def on_audio(self, callback: Callable) -> None:
        """
        오디오 데이터 콜백 등록
        
        Args:
            callback: 오디오 데이터를 받을 콜백 함수
        """
        self._callbacks.append(callback)
    
    def record_to_file(
        self,
        filepath: str,
        duration_seconds: float,
        device_id: Optional[int] = None,
    ) -> bool:
        """
        파일로 녹음
        
        Args:
            filepath: 저장할 파일 경로
            duration_seconds: 녹음 시간 (초)
            device_id: 장치 ID
            
        Returns:
            녹음 성공 여부
        """
        try:
            import sounddevice as sd
            import soundfile as sf
            
            logger.info(f"파일 녹음 시작: {filepath} ({duration_seconds}초)")
            
            frames = int(duration_seconds * self.config.sample_rate)
            recording = sd.rec(
                frames,
                samplerate=self.config.sample_rate,
                channels=self.config.channels,
                device=device_id,
            )
            sd.wait()
            
            sf.write(filepath, recording, self.config.sample_rate)
            
            logger.info(f"파일 녹음 완료: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"파일 녹음 실패: {e}")
            return False
    
    @property
    def is_recording(self) -> bool:
        """녹음 상태"""
        return self._is_recording


class VoiceActivityDetector:
    """
    음성 활동 감지 (VAD)
    
    오디오 스트림에서 음성 구간을 감지합니다.
    """
    
    def __init__(self, aggressiveness: int = 2):
        """
        Args:
            aggressiveness: VAD 민감도 (0-3, 높을수록 엄격)
        """
        self.aggressiveness = aggressiveness
        self._vad = None
        
        try:
            import webrtcvad
            self._vad = webrtcvad.Vad(aggressiveness)
            logger.info(f"VAD 초기화: aggressiveness={aggressiveness}")
        except ImportError:
            logger.warning("webrtcvad 패키지가 설치되지 않았습니다")
    
    def is_speech(self, audio_frame: bytes, sample_rate: int = 16000) -> bool:
        """
        음성 여부 판단
        
        Args:
            audio_frame: 오디오 프레임 (10/20/30ms)
            sample_rate: 샘플레이트 (8000/16000/32000/48000)
            
        Returns:
            음성 여부
        """
        if self._vad is None:
            return True  # VAD 없으면 항상 음성으로 처리
        
        try:
            return self._vad.is_speech(audio_frame, sample_rate)
        except Exception as e:
            logger.error(f"VAD 오류: {e}")
            return True
