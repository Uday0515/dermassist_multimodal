from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    groq_api_key: str | None = None
    deepgram_api_key: str | None = None
    deepgram_tts_model: str = "aura-2-asteria-en"
    groq_transcription_model: str = "whisper-large-v3-turbo"
    groq_vision_model: str = "qwen/qwen3.8-27b"
    allowed_origins: str = "http://localhost:8501"
    max_image_bytes: int = 10 * 1024 * 1024
    max_audio_bytes: int = 25 * 1024 * 1024
    enable_tts: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
