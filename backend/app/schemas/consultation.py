from pydantic import BaseModel, Field


class ConsultationResponse(BaseModel):
    transcript: str | None = None
    guidance: str
    audio_base64: str | None = None
    audio_media_type: str | None = None
    tts_available: bool = False
    tts_status: str = "unconfigured"


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "dermassist-api"


class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Safe, actionable error message")
