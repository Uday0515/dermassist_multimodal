import base64
import os

import httpx
import streamlit as st
from components.press_hold_recorder import press_hold_recorder

st.set_page_config(page_title="DermaAssist", page_icon="🩺", layout="wide")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")

st.markdown(
    """<style>
    .block-container {max-width: 1100px; padding-top: 2rem;}
    .notice {background:#d9edf7; color:#102a43; border-left:4px solid #075985; padding:1rem; border-radius:4px;}
    .notice strong {color:#082f49;}
    </style>""",
    unsafe_allow_html=True,
)
st.title("DermaAssist")
st.caption("Educational multimodal skin-concern information")
st.markdown(
    '<div class="notice"><strong>Medical safety notice:</strong> This tool provides general '
    "information only. It is not a medical diagnosis and does not replace advice from a "
    "licensed dermatologist or other clinician.</div>",
    unsafe_allow_html=True,
)

st.markdown("#### Voice description")
st.caption("Press and hold the microphone control while speaking. Release it to submit the recording.")
recording = press_hold_recorder(key="voice_recorder")
if recording and recording.get("audio_base64"):
    st.session_state["recording"] = recording
    st.success("Voice recording ready.")

with st.form("consultation"):
    left, right = st.columns(2)
    with left:
        description = st.text_area("Describe what you are noticing", height=160, placeholder="When did it start? Has it changed?")
        audio = st.file_uploader("Fallback: upload a recording", type=["mp3", "wav", "m4a", "webm", "ogg"])
    with right:
        image = st.file_uploader("Upload a skin image", type=["jpg", "jpeg", "png", "webp"])
        if image:
            st.image(image, caption="Selected image", use_container_width=True)
    submitted = st.form_submit_button("Get general information", type="primary")

if submitted:
    recording = st.session_state.get("recording")
    if image is None:
        st.error("Please upload a skin image.")
    elif not description.strip() and audio is None and not (recording and recording.get("audio_base64")):
        st.error("Please add a written description or an audio recording.")
    else:
        files = {"image": (image.name, image.getvalue(), image.type)}
        if recording and recording.get("audio_base64"):
            audio_bytes = base64.b64decode(recording["audio_base64"])
            files["audio"] = ("recording.webm", audio_bytes, recording.get("mime_type", "audio/webm"))
        elif audio:
            files["audio"] = (audio.name, audio.getvalue(), audio.type)
        data = {"description": description}
        with st.spinner("Sending the request securely to the backend..."):
            try:
                response = httpx.post(f"{BACKEND_URL}/api/v1/consultations/analyze", files=files, data=data, timeout=90)
                payload = response.json()
                if response.is_error:
                    st.error(payload.get("detail", "The backend could not complete the request."))
                else:
                    st.session_state.pop("recording", None)
                    if payload.get("transcript"):
                        st.subheader("Transcript")
                        st.write(payload["transcript"])
                    st.subheader("General guidance")
                    st.markdown(payload["guidance"])
                    if payload.get("audio_base64"):
                        st.audio(base64.b64decode(payload["audio_base64"]), format=payload.get("audio_media_type", "audio/mpeg"))
                    else:
                        tts_status = payload.get("tts_status", "unavailable")
                        messages = {
                            "disabled": "Written guidance is available. Speech synthesis is disabled in backend configuration.",
                            "unconfigured": "Written guidance is available. Add a Deepgram API key to enable speech synthesis.",
                            "provider_error": "Written guidance is available. Deepgram could not generate audio; check the backend TTS model/account.",
                        }
                        st.info(messages.get(tts_status, "Written guidance is available. Speech synthesis was unavailable."))
            except httpx.RequestError:
                st.error(f"Could not connect to the backend at {BACKEND_URL}. Start FastAPI and try again.")
