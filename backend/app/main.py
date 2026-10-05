from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes.consultations import router as consultations_router
from .core.config import get_settings
from .schemas.consultation import HealthResponse

settings = get_settings()
app = FastAPI(title="DermaAssist Multimodal API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.include_router(consultations_router)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse()
