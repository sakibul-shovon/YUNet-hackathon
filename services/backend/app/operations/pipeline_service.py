import datetime
import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.facts.service import FactService
from app.identity.models import Principal


class PipelineStageReceipt(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    stage_name: str
    status: str  # 'completed', 'skipped', 'not_applicable', 'failed'
    provider: str
    model_or_algorithm: str
    duration_ms: int | None = None
    details: dict[str, Any] = {}


class PipelineRunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pipeline_id: uuid.UUID
    case_id: uuid.UUID
    executed_at: datetime.datetime
    overall_status: str
    stages: list[PipelineStageReceipt]
    technology_inventory: dict[str, str]


class PipelineRunService:
    """P08.6 & T53: Durable owner-scoped processing details and execution receipts.

    Truthfully reflects actual stage, channel, and model usage without fabricated metrics or hidden chain-of-thought.
    """

    @classmethod
    async def get_pipeline_runs(
        cls,
        case_id: uuid.UUID,
        principal: Principal,
        db: AsyncSession,
    ) -> list[PipelineRunOut]:
        from app.operations.models import CaseRun
        case = await FactService.get_authorized_case(case_id, principal, db)
        records = (await db.scalars(select(CaseRun).where(
            CaseRun.case_id == case.id, CaseRun.principal_id == principal.id
        ).order_by(CaseRun.created_at.desc()).limit(30))).all()
        return [PipelineRunOut(
            pipeline_id=run.id, case_id=run.case_id, executed_at=run.created_at,
            overall_status=run.status,
            stages=[PipelineStageReceipt(
                stage_name=stage['stage_name'], status=stage['status'],
                provider=(stage.get('details', {}).get('execution_receipt') or {}).get('provider') or
                         ','.join(stage.get('details', {}).get('providers', [])) or 'local',
                model_or_algorithm=stage.get('details', {}).get('method', stage['method']),
                duration_ms=stage.get('duration_ms'), details=stage.get('details', {}),
            ) for stage in run.stages],
            technology_inventory={'execution': 'Recorded operations; provider acknowledgements and cache use appear in stage details',
                                  'dense_model_executed': 'false'},
        ) for run in records]
