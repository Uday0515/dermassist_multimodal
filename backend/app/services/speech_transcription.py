from groq import Groq


class TranscriptionService:
    def __init__(self, api_key: str | None, model: str) -> None:
        self._client = Groq(api_key=api_key) if api_key else None
        self._model = model

    @property
    def configured(self) -> bool:
        return self._client is not None

    def transcribe(self, audio_bytes: bytes, filename: str) -> str:
        if not self._client:
            raise RuntimeError("Audio transcription is not configured. Add GROQ_API_KEY to the backend.")
        result = self._client.audio.transcriptions.create(
            file=(filename, audio_bytes),
            model=self._model,
            response_format="text",
        )
        return str(result).strip()
