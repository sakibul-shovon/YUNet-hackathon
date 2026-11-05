import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError
from starlette.concurrency import run_in_threadpool

from app.actions.router import router as actions_router
from app.admin.router import router as admin_router
from app.cases.issue_router import router as issue_router
from app.cases.router import router as cases_router
from app.cases.timeline_router import router as timeline_router
from app.community.router import router as community_router
from app.copilot.router import router as copilot_router
from app.core.config import settings
from app.core.database import Base, engine
from app.core.public_router import router as public_router
from app.evidence.router import router as evidence_router
from app.extraction.router import router as extraction_router
from app.facts.router import router as facts_router
from app.identity.router import router as identity_router
from app.knowledge.router import router as knowledge_router
from app.merchants.router import router as merchants_router
from app.multimodal.audio.router import router as audio_router
from app.multimodal.vision.router import router as vision_router
from app.operations.router import router as operations_router
from app.policy.router import router as policy_router
from app.retrieval.router import router as retrieval_router
from app.scenarios.router import router as scenarios_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        if settings.APP_ENV == 'production':
            def schema_ready(connection):
                inspector = inspect(connection)
                tables = set(inspector.get_table_names())
                return all(name in tables and set(table.columns.keys()) <= {
                    column['name'] for column in inspector.get_columns(name)}
                    for name, table in Base.metadata.tables.items())
            if not await conn.run_sync(schema_ready):
                raise RuntimeError('Ebarki production database migrations must be applied before startup.')
        else:
            await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Ebarki API",
    version="0.1.0",
    description="Bangladesh-first consumer resolution copilot API. Grounded dispute preparation and follow-up.",
    docs_url="/docs" if settings.APP_ENV != "production" else None,
    redoc_url="/redoc" if settings.APP_ENV != "production" else None,
    openapi_url="/openapi.json",
    lifespan=lifespan,
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
    # CORS is not a CSRF authorization check. Reject cross-origin browser writes,
    # including login/session bootstrap, before any handler can alter a cookie.
    if request.method not in {'GET', 'HEAD', 'OPTIONS'}:
        origin = request.headers.get('origin')
        if (origin and origin.rstrip('/') not in settings.ALLOWED_ORIGINS) or (
            not origin and request.headers.get('sec-fetch-site') == 'cross-site'
        ):
            from fastapi.responses import JSONResponse
            return JSONResponse({'detail': 'This request origin is not permitted.'}, status_code=403,
                                headers={'Cache-Control': 'private, no-store'})
    correlation_id = request.headers.get("x-correlation-id", str(uuid.uuid4()))
    start_time = time.time()
    response: Response = await call_next(request)
    duration_ms = (time.time() - start_time) * 1000
    response.headers["x-correlation-id"] = correlation_id
    response.headers["x-response-time-ms"] = f"{duration_ms:.2f}"
    if '/auth/' in request.url.path:
        response.headers['Cache-Control'] = 'private, no-store'
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
    def probe_storage():
        import tempfile

        from app.evidence.storage import get_storage_backend
        storage = get_storage_backend()
        with tempfile.TemporaryFile(dir=storage.accepted_dir) as probe:
            probe.write(b'Ebarki readiness probe')
            probe.seek(0)
            return probe.read() == b'Ebarki readiness probe'

    try:
        async with engine.connect() as connection:
            await connection.execute(text('SELECT 1'))
        storage_ready = await run_in_threadpool(probe_storage)
        if not storage_ready:
            raise OSError('Storage probe failed')
    except (SQLAlchemyError, OSError, RuntimeError):
        from fastapi.responses import JSONResponse
        return JSONResponse({'status': 'not_ready', 'app': 'Ebarki',
                             'reason': 'Database or configured evidence storage is unavailable.'}, status_code=503)
    return {
        "status": "ready",
        "app": "claimcraft-bd",
        "environment": settings.APP_ENV,
        "capabilities": {
            "ai_provider": "groq" if settings.GROQ_API_KEY else "gemini" if settings.GEMINI_API_KEY else "manual_workflow",
            "image_reading_configured": bool((settings.GROQ_API_KEY and settings.GROQ_VISION_MODEL) or (settings.GEMINI_API_KEY and settings.GEMINI_RECORD_READER_MODEL)),
            "speech_transcription_configured": bool(settings.GROQ_API_KEY),
            "stt_provider": "groq" if settings.GROQ_API_KEY else "manual",
            "storage_backend": settings.STORAGE_BACKEND,
            "database_probe": "passed",
            "storage_read_write_probe": "passed",
        },
    }


@app.get("/api/v1/ping", tags=["System"])
async def api_ping():
    return {"message": "Ebarki API v1 is operational"}


# Include domain routers with canonical /v1 and BFF /api/v1 support
app.include_router(public_router)
app.include_router(identity_router)
app.include_router(cases_router)
app.include_router(issue_router)
app.include_router(knowledge_router)
app.include_router(facts_router)
app.include_router(extraction_router)
app.include_router(policy_router)
app.include_router(actions_router)
app.include_router(evidence_router)
app.include_router(audio_router)
app.include_router(vision_router)
app.include_router(retrieval_router)
app.include_router(operations_router)
app.include_router(timeline_router)
app.include_router(scenarios_router)
app.include_router(merchants_router)
app.include_router(community_router)
app.include_router(copilot_router)
app.include_router(admin_router)

app.include_router(public_router, prefix="/api")
app.include_router(identity_router, prefix="/api")
app.include_router(cases_router, prefix="/api")
app.include_router(issue_router, prefix="/api")
app.include_router(knowledge_router, prefix="/api")
app.include_router(facts_router, prefix="/api")
app.include_router(extraction_router, prefix="/api")
app.include_router(policy_router, prefix="/api")
app.include_router(actions_router, prefix="/api")
app.include_router(evidence_router, prefix="/api")
app.include_router(audio_router, prefix="/api")
app.include_router(vision_router, prefix="/api")
app.include_router(retrieval_router, prefix="/api")
app.include_router(operations_router, prefix="/api")
app.include_router(timeline_router, prefix="/api")
app.include_router(scenarios_router, prefix="/api")
app.include_router(merchants_router, prefix="/api")
app.include_router(community_router, prefix="/api")
app.include_router(copilot_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
