# DermaAssist Multimodal

**A safety-first multimodal skin-concern assistant built with Streamlit, FastAPI, and hosted AI models.**

DermaAssist accepts a skin image plus written or spoken context and returns cautious, general educational guidance. It is an **educational prototype, not a diagnostic or clinical product**.

![DermaAssist dashboard](<AI Skin Specialist Dashboard.png>)

## Why this project

- **Multimodal input:** combines an image with text or an audio recording.
- **Speech pipeline:** transcribes audio with Groq Whisper and can read results aloud with optional Deepgram TTS.
- **Secure architecture:** the Streamlit frontend never handles provider credentials; all AI calls stay behind FastAPI.
- **Defensive API design:** validates MIME types, enforces upload limits, keeps uploads in memory, and exposes explicit error responses.
- **Responsible AI boundaries:** prompts avoid diagnosis, prescriptions, confidence claims, and unsupported video analysis.

## Architecture

```text
Streamlit UI
    │ multipart HTTP request
    ▼
FastAPI API
    ├── validates image, audio, and text
    ├── Groq Whisper ───────────────► optional transcript
    ├── Groq vision model ──────────► written guidance
    └── Deepgram TTS ───────────────► optional MP3 response
```

| Layer | Responsibility |
| --- | --- |
| `frontend/streamlit_app.py` | User interface, image/audio capture, API response rendering |
| `backend/app/api/routes/` | Multipart validation and consultation orchestration |
| `backend/app/services/` | Speech-to-text, vision analysis, and text-to-speech integrations |
| `backend/app/core/config.py` | Environment-backed configuration and upload limits |
| `backend/app/schemas/` | Typed API response contracts |

## Run locally

### Requirements

- Python 3.11+
- A Groq API key for transcription and image analysis
- Optional: a Deepgram API key for spoken responses

### 1. Install

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

### 2. Configure environment variables

Create a `.env` file in the repository root:

```dotenv
GROQ_API_KEY=your_groq_api_key
DEEPGRAM_API_KEY=your_deepgram_api_key
```

`DEEPGRAM_API_KEY` is optional. Written guidance still works without it. Never commit `.env` or expose API keys in frontend code.

### 3. Start the services

Run each command from the repository root in a separate terminal:

```powershell
# Terminal 1: API
.\.venv\Scripts\Activate.ps1
uvicorn backend.app.main:app --reload --port 8000

# Terminal 2: UI
.\.venv\Scripts\Activate.ps1
streamlit run frontend/streamlit_app.py --server.port 8501
```

Open <http://localhost:8501>.

## API

- `GET /health` — service health check
- `POST /api/v1/consultations/analyze` — multipart consultation analysis
- `GET /docs` — interactive FastAPI documentation

The analysis endpoint accepts:

| Field | Required | Accepted values |
| --- | --- | --- |
| `image` | Yes | JPEG, PNG, or WebP |
| `description` | One of `description` or `audio` | Written context |
| `audio` | One of `description` or `audio` | MP3, WAV, M4A, WebM, or OGG |

The response includes `guidance`, an optional `transcript`, and optional base64-encoded MP3 audio. Images and audio are processed in memory and are not persisted by the application.

## Engineering decisions

- **Frontend/backend separation** keeps secrets server-side and creates a testable HTTP boundary.
- **Provider adapters** isolate external AI integrations from request handling.
- **Optional TTS** preserves the core written experience when Deepgram is unavailable.
- **Video is not accepted** because analyzing a single frame should not be presented as full-video analysis.
- **Hosted inference** keeps the prototype lightweight while making provider availability, rate limits, and model changes explicit operational considerations.

## Safety notice

DermaAssist provides general educational information only. It must not be used to diagnose a condition, select treatment, or replace a qualified healthcare professional. For urgent or concerning symptoms, seek professional medical care.

