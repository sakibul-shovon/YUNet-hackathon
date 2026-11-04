import asyncio
import json
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.database import get_db_session
from app.core.security import get_current_principal
from app.identity.models import Principal
from app.operations.models import CaseRun
from app.operations.pipeline_service import PipelineRunOut, PipelineRunService
from app.operations.runs import (
    TERMINAL,
    RunRequest,
    create_run,
    execute_run,
    owned_run,
    recover_expired_run,
    serialize_run,
)
from app.operations.workbench_router import router as workbench_router

router = APIRouter(tags=["Case Operations & Pipeline History"])
from app.operations.workspace import router as workspace_router

router.include_router(workspace_router)
router.include_router(workbench_router)


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


@router.post("/v1/cases/{case_id}/runs", status_code=202)
async def start_case_run(
    case_id: uuid.UUID, payload: RunRequest, tasks: BackgroundTasks,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    run = await create_run(case_id, payload, principal, db)
    factory = async_sessionmaker(db.bind, expire_on_commit=False)
    tasks.add_task(execute_run, run.id, factory)
    return serialize_run(run)


@router.get("/v1/cases/{case_id}/runs")
async def list_case_runs(
    case_id: uuid.UUID, principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    from app.facts.service import FactService
    await FactService.get_authorized_case(case_id, principal, db)
    runs = await db.scalars(select(CaseRun).where(
        CaseRun.case_id == case_id, CaseRun.principal_id == principal.id,
    ).order_by(CaseRun.created_at.desc()).limit(30))
    records = list(runs)
    for run in records:
        await recover_expired_run(run, db)
    return [serialize_run(run) for run in records]


@router.get("/v1/cases/{case_id}/runs/{run_id}")
async def get_case_run(
    case_id: uuid.UUID, run_id: uuid.UUID,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    return serialize_run(await owned_run(case_id, run_id, principal, db))


@router.post("/v1/cases/{case_id}/runs/{run_id}/cancel")
async def cancel_case_run(
    case_id: uuid.UUID, run_id: uuid.UUID,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    run = await owned_run(case_id, run_id, principal, db)
    if run.status not in TERMINAL:
        run.cancel_requested = True
        await db.commit()
    return serialize_run(run)


@router.get("/v1/cases/{case_id}/runs/{run_id}/events")
async def stream_case_run(
    case_id: uuid.UUID, run_id: uuid.UUID, request: Request,
    principal: Principal = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db_session),
):
    await owned_run(case_id, run_id, principal, db)
    factory = async_sessionmaker(db.bind, expire_on_commit=False)

    async def events():
        previous = ""
        for _ in range(480):
            if await request.is_disconnected():
                return
            async with factory() as stream_db:
                run = await owned_run(case_id, run_id, principal, stream_db)
                payload = json.dumps(serialize_run(run), ensure_ascii=False)
                if payload != previous:
                    yield f"event: run\ndata: {payload}\n\n"
                    previous = payload
                if run.status in TERMINAL:
                    return
            await asyncio.sleep(.25)
        yield "event: reconnect\ndata: {}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream", headers={
        "Cache-Control": "private, no-store", "X-Accel-Buffering": "no",
    })
