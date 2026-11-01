import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import get_current_principal
from app.identity.models import Principal
from app.operations.pipeline_service import PipelineRunOut, PipelineRunService

router = APIRouter(tags=["Case Operations & Pipeline History"])


@router.get(
    "/v1/cases/{case_id}/pipeline-runs",
    response_model=list[PipelineRunOut],
)
async def get_case_pipeline_runs(
    case_id: uuid.UUID,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    """P08.6 & T53: Returns durable execution receipts and technology inventory for a case."""
    return await PipelineRunService.get_pipeline_runs(case_id, principal, db)

