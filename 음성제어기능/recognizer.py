"""
음성 인식기 모듈

OpenAI Whisper 또는 Vosk를 사용하여 음성을 텍스트로 변환합니다.
"""

import sys
from pathlib import Path
from typing import Optional, Union
from dataclasses import dataclass
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent))
from 공통라이브러리 import get_logger, get_settings

logger = get_logger(__name__)
settings = get_settings()


class RecognizerType(Enum):
    """인식 엔진 종류"""
    WHISPER = "whisper"
    VOSK = "vosk"


@dataclass
class RecognitionResult:
    """인식 결과"""
    text: str
    confidence: float
    language: str
    duration_ms: int
    
    @property
    def is_valid(self) -> bool:
        """유효한 결과인지 확인"""
        return len(self.text.strip()) > 0 and self.confidence > 0.5


class VoiceRecognizer:
    """
    음성 인식기
    
    Whisper 또는 Vosk를 사용하여 음성을 텍스트로 변환합니다.
    """
    
    def __init__(
        self,
        engine: RecognizerType = RecognizerType.WHISPER,
        model_size: str = "base",
        language: str = "ko",
        device: str = "cpu",
    ):
        """
        Args:
            engine: 인식 엔진 (whisper/vosk)
            model_size: 모델 크기 (tiny/base/small/medium/large)
            language: 인식 언어
            device: 처리 장치 (cpu/cuda)
        """
        self.engine = engine
        self.model_size = model_size
        self.language = language
        self.device = device
        self._model = None
        
        logger.info(f"음성 인식기 초기화: engine={engine.value}, model={model_size}, lang={language}")
    
    def load_model(self) -> bool:
        """
        모델 로드
        
        Returns:
            로드 성공 여부
        """
        try:
            if self.engine == RecognizerType.WHISPER:
                return self._load_whisper()
            elif self.engine == RecognizerType.VOSK:
                return self._load_vosk()
            else:
                logger.error(f"지원하지 않는 엔진: {self.engine}")
                return False
                
        except Exception as e:
            logger.error(f"모델 로드 실패: {e}")
            return False
    
    def _load_whisper(self) -> bool:
        """Whisper 모델 로드"""
        try:
            import whisper
            
            logger.info(f"Whisper 모델 로드 중: {self.model_size}")
            self._model = whisper.load_model(self.model_size, device=self.device)
            logger.info("Whisper 모델 로드 완료")
            return True
            
        except ImportError:
            logger.error("whisper 패키지가 설치되지 않았습니다: pip install openai-whisper")
            return False
    
    def _load_vosk(self) -> bool:
        """Vosk 모델 로드"""
        try:
            # from vosk import Model
            # self._model = Model(model_path)
            logger.warning("Vosk 모델 로드: 아직 구현되지 않음")
            return False
            
        except ImportError:
            logger.error("vosk 패키지가 설치되지 않았습니다: pip install vosk")
            return False
    
    def recognize(self, audio_path: Union[str, Path]) -> Optional[RecognitionResult]:
        """
        오디오 파일에서 음성 인식
        
        Args:
            audio_path: 오디오 파일 경로
            
        Returns:
            인식 결과 (실패 시 None)
        """
        if self._model is None:
            logger.error("모델이 로드되지 않았습니다")
            return None
        
        try:
            import time
            start_time = time.time()
            
            if self.engine == RecognizerType.WHISPER:
                result = self._model.transcribe(
                    str(audio_path),
                    language=self.language,
                    fp16=False if self.device == "cpu" else True,
                )
                
                duration_ms = int((time.time() - start_time) * 1000)
                
                return RecognitionResult(
                    text=result["text"].strip(),
                    confidence=1.0,  # Whisper는 confidence를 직접 제공하지 않음
                    language=result.get("language", self.language),
                    duration_ms=duration_ms,
                )
            
        except Exception as e:
            logger.error(f"음성 인식 실패: {e}")
            return None
    
    def recognize_stream(self, audio_stream) -> Optional[RecognitionResult]:
        """
        실시간 오디오 스트림에서 음성 인식
        
        Args:
            audio_stream: 오디오 스트림
            
        Returns:
            인식 결과
        """
        # TODO: 실시간 스트리밍 인식 구현
        logger.warning("스트리밍 인식: 아직 구현되지 않음")
        return None
    
    @property
    def is_loaded(self) -> bool:
        """모델 로드 여부"""
        return self._model is not None
