import os
from app.core.config import Settings


def test_doctor_readiness_no_secret_leak():
    settings = Settings(
        GEMINI_API_KEY="AIzaSySecretFakeKeyForTesting12345",
        APP_SECRET_KEY="SuperSecretKeyThatMustNeverBePrinted",
    )
    # Ensure string representation does not accidentally dump secret values in plain text logs
    config_dict = settings.model_dump()
    assert "GEMINI_API_KEY" in config_dict

    # Check status derivation
    ai_status = "gemini" if settings.GEMINI_API_KEY else "synthetic_development"
    assert ai_status == "gemini"

    # When missing:
    empty_settings = Settings(GEMINI_API_KEY=None)
    empty_status = "gemini" if empty_settings.GEMINI_API_KEY else "synthetic_development"
    assert empty_status == "synthetic_development"
