import base64
import logging
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from ...core.config import get_settings
from ...schemas.consultation import ConsultationResponse
from ...services.skin_analysis import SkinAnalysisService
from ...services.speech_synthesis import SpeechSynthesisService
from ...services.speech_transcription import TranscriptionService

router = APIRouter(prefix="/api/v1/consultations", tags=["consultations"])
logger = logging.getLogger(__name__)
IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
AUDIO_TYPES = {"audio/mpeg", "audio/wav", "audio/x-wav", "audio/mp4", "audio/webm", "audio/ogg"}


async def _read_limited(upload: UploadFile, limit: int, label: str) -> bytes:
    data = await upload.read(limit + 1)
    if len(data) > limit:
        raise HTTPException(status_code=413, detail=f"{label} is too large. Maximum is {limit // 1024 // 1024} MB.")
    return data


@router.post("/analyze", response_model=ConsultationResponse)
async def analyze_consultation(
    image: Annotated[UploadFile, File(description="JPEG, PNG, or WebP skin image")],
    description: Annotated[str | None, Form()] = None,
    audio: Annotated[UploadFile | None, File()] = None,
) -> ConsultationResponse:
    settings = get_settings()
    if image.content_type not in IMAGE_TYPES:
        raise HTTPException(status_code=415, detail="Use a JPEG, PNG, or WebP image.")
    image_bytes = await _read_limited(image, settings.max_image_bytes, "Image")
    if not image_bytes:
        raise HTTPException(status_code=400, detail="The image file is empty.")
    if not (description or "").strip() and audio is None:
        raise HTTPException(status_code=422, detail="Add a written description or an audio recording.")

    transcript: str | None = None
    if audio is not None:
        audio_media_type = (audio.content_type or "").split(";", 1)[0].lower()
        if audio_media_type not in AUDIO_TYPES:
            raise HTTPException(status_code=415, detail="Use a supported audio file such as MP3, WAV, M4A, WebM, or OGG.")
        audio_bytes = await _read_limited(audio, settings.max_audio_bytes, "Audio")
        try:
            transcript = TranscriptionService(settings.groq_api_key, settings.groq_transcription_model).transcribe(
                audio_bytes, audio.filename or "recording"
            )
        except Exception as exc:
            raise HTTPException(status_code=502, detail="Audio transcription failed. Check the backend provider configuration or try again.") from exc

    combined_description = "\n".join(part for part in [description, transcript] if part)
    try:
        guidance = SkinAnalysisService(settings.groq_api_key, settings.groq_vision_model).analyze(
            image_bytes, image.content_type, combined_description
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Image analysis failed. Check the backend provider configuration or try again.") from exc

    audio_base64 = None
    if not settings.enable_tts:
        tts_status = "disabled"
    elif not settings.deepgram_api_key:
        tts_status = "unconfigured"
    else:
        try:
            audio_base64 = base64.b64encode(
                SpeechSynthesisService(
                    settings.deepgram_api_key, settings.enable_tts, settings.deepgram_tts_model
                ).synthesize(guidance)
            ).decode("ascii")
            tts_status = "generated"
        except Exception as exc:
            logger.warning("Deepgram TTS request failed: %s", type(exc).__name__)
            tts_status = "provider_error"
    return ConsultationResponse(
        transcript=transcript,
        guidance=guidance,
        audio_base64=audio_base64,
        audio_media_type="audio/mpeg" if audio_base64 else None,
        tts_available=audio_base64 is not None,
        tts_status=tts_status,
    )
