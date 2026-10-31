from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["System & Capabilities"])


@router.get("/v1/capabilities")
async def get_capabilities():
    """Returns enabled domain packs, supported languages, provider readiness, and release mode."""
    return {
        "release_mode": settings.APP_ENV,
        "languages": ["en", "bn"],
        "default_language": "en",
        "domain_packs": [
            {
                "id": "consumer_ecommerce",
                "name": "E-commerce & Retail Goods",
                "status": "active",
                "statutory_act": "Consumer Rights Protection Act, 2009",
            },
            {
                "id": "financial_services",
                "name": "MFS & Digital Banking",
                "status": "candidate",
                "statutory_act": "Bangladesh Bank MFS Guidelines",
            },
            {
                "id": "telecom_isp",
                "name": "Telecom & Internet Service",
                "status": "candidate",
                "statutory_act": "BTRC Directives",
            },
        ],
        "providers": {
            "ai_multimodal": "gemini" if settings.GEMINI_API_KEY else "synthetic_development",
            "speech_to_text": "google_cloud_stt" if settings.GOOGLE_APPLICATION_CREDENTIALS else "browser_native_fallback",
            "dense_embeddings": "intfloat/multilingual-e5-small",
            "lexical_search": "bm25s",
        },
    }


@router.get("/v1/technology")
async def get_technology():
    """Returns sanitized build inventory and capability status without disclosing secrets."""
    return {
        "application": "ClaimCraft BD",
        "version": "0.1.0",
        "stack": {
            "web": "Next.js 15.5 App Router + TypeScript + Tailwind CSS",
            "backend": "FastAPI + Pydantic v2 + SQLAlchemy 2 + Alembic",
            "database": "PostgreSQL with Row Level Security (RLS)",
            "i18n": "next-intl (en-BD / bn-BD 100% parity)",
        },
        "guarantees": {
            "tenant_isolation": "Transaction-local principal context + RLS",
            "optimistic_concurrency": "row_version check with 409 conflict handling",
            "privacy": "Zero client token storage, opaque HttpOnly sessions, Cache-Control: private, no-store",
        },
    }
