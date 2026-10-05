import httpx


class SpeechSynthesisService:
    def __init__(self, api_key: str | None, enabled: bool, model: str) -> None:
        self._api_key = api_key if enabled else None
        self._model = model

    @property
    def configured(self) -> bool:
        return self._api_key is not None

    def synthesize(self, text: str) -> bytes:
        if not self._api_key:
            raise RuntimeError("Speech synthesis is not configured.")
        response = httpx.post(
            "https://api.deepgram.com/v1/speak",
            params={"model": self._model},
            headers={"Authorization": f"Token {self._api_key}", "Content-Type": "application/json"},
            json={"text": text},
            timeout=60,
        )
        response.raise_for_status()
        return response.content
