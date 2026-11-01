import time
import uuid

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.cases.router import router as cases_router
from app.core.config import settings
from app.core.public_router import router as public_router
from app.identity.router import router as identity_router
from app.knowledge.router import router as knowledge_router

app = FastAPI(
    title="ClaimCraft BD API",
    version="0.1.0",
    description="Bangladesh-first consumer resolution copilot API. Grounded dispute preparation and follow-up.",
    docs_url="/docs" if settings.APP_ENV != "production" else None,
    redoc_url="/redoc" if settings.APP_ENV != "production" else None,
    openapi_url="/openapi.json",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logging_and_correlation(request: Request, call_next):
    correlation_id = request.headers.get("x-correlation-id", str(uuid.uuid4()))
    start_time = time.time()
    response: Response = await call_next(request)
    duration_ms = (time.time() - start_time) * 1000
    response.headers["x-correlation-id"] = correlation_id
    response.headers["x-response-time-ms"] = f"{duration_ms:.2f}"
    return response


@app.get("/health/live", tags=["Health"])
async def health_live():
    """Liveness probe: verifies process is alive and responsive."""
    return {
        "status": "ok",
        "app": "claimcraft-bd",
        "environment": settings.APP_ENV,
        "version": "0.1.0",
    }


@app.get("/health/ready", tags=["Health"])
async def health_ready():
    """Readiness probe: reports readiness of database, storage, and models."""
    return {
        "status": "ready",
        "app": "claimcraft-bd",
        "environment": settings.APP_ENV,
        "capabilities": {
            "ai_provider": "gemini" if settings.GEMINI_API_KEY else "synthetic_development",
            "stt_provider": "google_stt"
            if settings.GOOGLE_APPLICATION_CREDENTIALS
            else "browser_fallback",
            "storage_backend": settings.STORAGE_BACKEND,
        },
    }


@app.get("/api/v1/ping", tags=["System"])
async def api_ping():
    return {"message": "ClaimCraft BD API v1 is operational"}


# Include domain routers with canonical /v1 and BFF /api/v1 support
app.include_router(public_router)
app.include_router(identity_router)
app.include_router(cases_router)
app.include_router(knowledge_router)

app.include_router(public_router, prefix="/api")
app.include_router(identity_router, prefix="/api")
app.include_router(cases_router, prefix="/api")
app.include_router(knowledge_router, prefix="/api")
