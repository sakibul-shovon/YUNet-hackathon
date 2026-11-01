"""API Router for Judge Scenarios and Evaluation Sandbox."""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import get_current_principal
from app.identity.models import Principal
from app.scenarios.manifests import SyntheticScenarioManifest
from app.scenarios.service import ScenarioService

router = APIRouter(tags=["Judge Scenarios Sandbox"])


@router.get(
    "/v1/scenarios",
    response_model=list[SyntheticScenarioManifest],
    status_code=status.HTTP_200_OK,
)
async def list_scenarios():
    """Section 20.1: Returns eight synthetic dispute scenarios with featured quick starts."""
    return ScenarioService.list_scenarios()


@router.post(
    "/v1/scenarios/{scenario_id}/launch",
    status_code=status.HTTP_201_CREATED,
)
async def launch_scenario(
    scenario_id: str,
    locale: str = Query("en-BD", description="Locale for created case"),
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    """T52: Spawns an isolated synthetic case in the database for the judge to test."""
    return await ScenarioService.launch_scenario(scenario_id, principal, db, locale=locale)


@router.post(
    "/v1/scenarios/{case_id}/reset",
    status_code=status.HTTP_200_OK,
)
async def reset_scenario(
    case_id: uuid.UUID,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    """T52: Resets a demo scenario case back to its original baseline state."""
    return await ScenarioService.reset_scenario_case(case_id, principal, db)
