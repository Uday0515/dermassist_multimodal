import base64

from groq import Groq


SAFETY_PROMPT = """You are an educational skin-information assistant, not a clinician.
Provide cautious, general information only. Do not diagnose, assign confidence scores,
prescribe medication, or promise a treatment outcome. Describe only visible characteristics
when appropriate, acknowledge image limitations, suggest safe next steps, and recommend a
licensed clinician for concerning, worsening, painful, bleeding, rapidly changing, or urgent
symptoms. Mention emergency care when symptoms could be urgent. Keep the response readable
with headings: What may be visible, General information, Next steps, and When to seek care."""


class SkinAnalysisService:
    def __init__(self, api_key: str | None, model: str) -> None:
        self._client = Groq(api_key=api_key) if api_key else None
        self._model = model

    def analyze(self, image_bytes: bytes, image_media_type: str, description: str) -> str:
        if not self._client:
            raise RuntimeError("Image analysis is not configured. Add GROQ_API_KEY to the backend.")
        encoded = base64.b64encode(image_bytes).decode("ascii")
        prompt = f"{SAFETY_PROMPT}\n\nUser description:\n{description or '(none provided)'}"
        completion = self._client.chat.completions.create(
            model=self._model,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {
                        "url": f"data:{image_media_type};base64,{encoded}",
                    }},
                ],
            }],
            temperature=0.2,
            max_tokens=800,
        )
        return (completion.choices[0].message.content or "").strip()
