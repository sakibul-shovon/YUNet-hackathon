"""
ClaimCraft BD Async Worker & Celery Application.
Manages processing queues: case_parse, case_vision, case_asr, case_assess, case_export, official_fetch.
"""

from app.core.config import settings

# Worker definition and task registration placeholder
print(f"ClaimCraft Worker initialized for environment: {settings.APP_ENV}")

