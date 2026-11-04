import datetime
import uuid
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.actions.portal_field_maps import PortalFieldMapService
from app.cases.models import CaseEvent
from app.core.database import get_db_session
from app.core.security import get_current_principal
from app.evidence.models import EvidenceItem
from app.evidence.storage import get_storage_backend
from app.facts.models import FactAssertion, FactSourceLink
from app.facts.normalization import normalize_bdt_money
from app.facts.service import FactService
from app.identity.models import Principal
from app.operations.connected_records import (
    MONEY,
    append_workspace_event,
    connected_records,
    owned_case,
)
from app.operations.reply_preparation import prepare_reply
from app.policy.engine import ProceduralAssessmentEngine

router = APIRouter(tags=['Connected Evidence & Reply Preparation'])


@router.get('/v1/cases/{case_id}/evidence/{evidence_id}/page-preview')
async def pdf_page_preview(case_id: uuid.UUID, evidence_id: uuid.UUID, page: int = 1,
                           principal: Principal = Depends(get_current_principal), db: AsyncSession = Depends(get_db_session)):
    case = await owned_case(case_id, principal, db)
    item = await db.scalar(select(EvidenceItem).where(EvidenceItem.id == evidence_id,
        EvidenceItem.case_id == case.id, EvidenceItem.principal_id == principal.id, EvidenceItem.status == 'accepted'))
    if not item or (item.detected_mime_type or item.declared_mime_type) != 'application/pdf':
        raise HTTPException(404, 'PDF not found')
    if not 1 <= page <= 100:
        raise HTTPException(404, 'Page not found')
    from app.operations.page_preview import render_page
    try:
        data = await run_in_threadpool(get_storage_backend().read_accepted, item.accepted_path)
        png = await run_in_threadpool(render_page, data, page)
    except (OSError, ValueError, RuntimeError) as error:
        raise HTTPException(422, 'This page could not be previewed. Open the original PDF instead.') from error
    return Response(png, media_type='image/png', headers={'Cache-Control': 'private, no-store', 'X-Content-Type-Options': 'nosniff'})


class SourceInput(BaseModel):
    text: str = Field(min_length=4, max_length=10000)
    label: str = Field(default='A message I provided', min_length=2, max_length=180)
    source_type: Literal['pasted_text', 'pasted_message', 'voice_dictation', 'manual_transcript'] = 'pasted_message'
    evidence_id: uuid.UUID | None = None
    expected_version: int


class ReviewInput(BaseModel):
    item_id: str = Field(min_length=24, max_length=24)
    outcome: Literal['confirmed', 'dismissed', 'proposed']
    corrected_date: datetime.date | None = None
    expected_version: int


class ReplyInput(BaseModel):
    message: str = Field(min_length=4, max_length=6000)
    locale: Literal['en', 'bn'] = 'en'
    expected_version: int


class ReplyEdit(BaseModel):
    draft: str = Field(min_length=4, max_length=4000)
    expected_version: int


async def writable(case, principal, db):
    if case.consent_status == 'withdrawn':
        raise HTTPException(403, 'Processing consent was withdrawn')


@router.get('/v1/cases/{case_id}/connected-records')
async def get_records(case_id: uuid.UUID, response: Response,
                      principal: Principal = Depends(get_current_principal), db: AsyncSession = Depends(get_db_session)):
    case = await owned_case(case_id, principal, db)
    response.headers['Cache-Control'] = 'private, no-store'
    return await connected_records(case, principal, db)


@router.post('/v1/cases/{case_id}/connected-records/sources', status_code=201)
async def add_source(case_id: uuid.UUID, payload: SourceInput,
                     principal: Principal = Depends(get_current_principal), db: AsyncSession = Depends(get_db_session)):
    case = await owned_case(case_id, principal, db)
    await writable(case, principal, db)
    if payload.evidence_id:
        file = await db.scalar(select(EvidenceItem).where(EvidenceItem.id == payload.evidence_id,
            EvidenceItem.case_id == case.id, EvidenceItem.principal_id == principal.id, EvidenceItem.status == 'accepted'))
        if not file:
            raise HTTPException(404, 'Record not found')
    event = await append_workspace_event(case, principal, db, 'workspace.source_added',
        payload.model_dump(mode='json', exclude={'expected_version'}), payload.expected_version, material=True)
    return {'id': str(event.id), 'case_version': case.row_version}


@router.post('/v1/cases/{case_id}/connected-records/review')
async def review_moment(case_id: uuid.UUID, payload: ReviewInput,
                        principal: Principal = Depends(get_current_principal), db: AsyncSession = Depends(get_db_session)):
    case = await owned_case(case_id, principal, db)
    await writable(case, principal, db)
    records = await connected_records(case, principal, db)
    item = next((item for item in records['timeline'] if item['id'] == payload.item_id), None)
    if not item:
        raise HTTPException(404, 'Moment not found')
    event = await append_workspace_event(case, principal, db, 'workspace.timeline_reviewed',
        {**payload.model_dump(mode='json', exclude={'expected_version'}), 'source_id': item['source_id'],
         'quote': item['quote']}, payload.expected_version, material=True)
    source = next((source for source in records['sources'] if source['id'] == item['source_id']), None)
    if source and source['mime_type'].startswith(('image/', 'application/pdf')):
        amount = await db.scalar(select(FactAssertion).where(FactAssertion.case_id == case.id,
            FactAssertion.field_name == 'amount_paid', FactAssertion.is_active.is_(True))
            .order_by(FactAssertion.created_at.desc()).limit(1))
        if amount:
            links = (await db.scalars(select(FactSourceLink).where(FactSourceLink.assertion_id == amount.id))).all()
            for link in links:
                meta = link.locator_meta or {}
                if meta.get('timeline_item_id') == item['id'] or (
                    meta.get('evidence_id') == source['id'] and not meta.get('timeline_item_id')
                ):
                    await db.delete(link)
            matches = list(MONEY.finditer(item['quote']))
            if payload.outcome == 'confirmed' and len(matches) == 1:
                value = normalize_bdt_money(matches[0].group()).minor_units
                db.add(FactSourceLink(assertion_id=amount.id, source_type='evidence_span', locator_meta={
                    'evidence_id': source['id'], 'evidence_sha256': source.get('sha256'),
                    'page_number': item.get('page'), 'normalized_box': item.get('box'),
                    'selected_text': item['quote'], 'timeline_item_id': item['id'],
                    'reviewed_money_minor_units': value, 'reviewed_by': str(principal.id),
                }))
            await db.commit()
    return {'id': str(event.id), 'case_version': case.row_version}


@router.get('/v1/cases/{case_id}/reply-preparations')
async def saved_replies(case_id: uuid.UUID, response: Response,
                        principal: Principal = Depends(get_current_principal), db: AsyncSession = Depends(get_db_session)):
    case = await owned_case(case_id, principal, db)
    response.headers['Cache-Control'] = 'private, no-store'
    events = list((await db.scalars(select(CaseEvent).where(CaseEvent.case_id == case.id,
        CaseEvent.principal_id == principal.id, CaseEvent.event_type.in_(['workspace.reply_prepared', 'workspace.reply_edited']))
        .order_by(CaseEvent.event_sequence))).all())
    records = {}
    for event in events:
        identity = event.payload.get('reply_id', str(event.id))
        records[identity] = {**event.payload, 'id': identity, 'created_at': event.created_at.isoformat(),
                             'is_stale': event.payload['case_version'] != case.row_version}
    return list(records.values())[::-1][:25]


@router.post('/v1/cases/{case_id}/reply-preparations', status_code=201)
async def make_reply(case_id: uuid.UUID, payload: ReplyInput,
                      principal: Principal = Depends(get_current_principal), db: AsyncSession = Depends(get_db_session)):
    case = await owned_case(case_id, principal, db)
    await writable(case, principal, db)
    if case.row_version != payload.expected_version:
        raise HTTPException(409, 'Case changed. Refresh before preparing your reply.')
    source = await append_workspace_event(case, principal, db, 'workspace.source_added', {
        'text': payload.message, 'label': 'Reported seller response' if payload.locale == 'en' else 'আপনার দেওয়া বিক্রেতার উত্তর',
        'source_type': 'pasted_message'}, payload.expected_version, material=True)
    result = await prepare_reply(case, principal, db, payload.message, payload.locale)
    result['source_id'] = str(source.id)
    event = await append_workspace_event(case, principal, db, 'workspace.reply_prepared', result,
                                         expected_version=case.row_version)
    return {**event.payload, 'id': str(event.id), 'created_at': event.created_at.isoformat(), 'is_stale': False}


@router.put('/v1/cases/{case_id}/reply-preparations/{reply_id}')
async def edit_reply(case_id: uuid.UUID, reply_id: uuid.UUID, payload: ReplyEdit,
                      principal: Principal = Depends(get_current_principal), db: AsyncSession = Depends(get_db_session)):
    case = await owned_case(case_id, principal, db)
    await writable(case, principal, db)
    original = await db.scalar(select(CaseEvent).where(CaseEvent.id == reply_id, CaseEvent.case_id == case.id,
        CaseEvent.principal_id == principal.id, CaseEvent.event_type == 'workspace.reply_prepared'))
    if not original:
        raise HTTPException(404, 'Reply not found')
    if original.payload['case_version'] != case.row_version:
        raise HTTPException(409, 'New information is available. Prepare a current reply before editing.')
    event = await append_workspace_event(case, principal, db, 'workspace.reply_edited',
        {**original.payload, 'reply_id': str(reply_id), 'draft': payload.draft, 'user_edited': True}, payload.expected_version)
    return {**event.payload, 'id': str(reply_id), 'created_at': event.created_at.isoformat(), 'is_stale': False}


@router.get('/v1/cases/{case_id}/filing-handoff')
async def filing_handoff(case_id: uuid.UUID, response: Response, portal_id: str = 'dncrp_ccms',
                         principal: Principal = Depends(get_current_principal), db: AsyncSession = Depends(get_db_session)):
    case = await owned_case(case_id, principal, db)
    response.headers['Cache-Control'] = 'private, no-store'
    assertions = list((await db.scalars(select(FactAssertion).where(FactAssertion.case_id == case.id,
        FactAssertion.is_active.is_(True)))).all())
    facts = ProceduralAssessmentEngine.extract_facts_from_db_records(assertions, case)
    try:
        mapping = PortalFieldMapService.get_field_map(portal_id, {'merchant_name': case.merchant_name,
            'story_narrative': case.story_narrative, 'desired_outcomes': case.desired_outcomes,
            'incident_date': case.incident_date}, facts)
    except ValueError as error:
        raise HTTPException(404, 'Channel not found') from error
    reviewed = await FactService.get_assertions(case.id, principal, db)
    by_field = {fact.field_name: fact for fact in reviewed}
    fields = []
    for field in mapping.fields:
        fact = by_field.get(field.fact_source)
        fields.append({**field.model_dump(), 'fact_id': str(fact.id) if fact else None,
                       'review': fact.review_outcome if fact else 'user_provided' if field.prepared_value else None})
    files = list((await db.scalars(select(EvidenceItem).where(EvidenceItem.case_id == case.id,
        EvidenceItem.principal_id == principal.id, EvidenceItem.status == 'accepted'))).all())
    latest = await connected_records(case, principal, db)
    return {**mapping.model_dump(), 'fields': fields, 'case_version': case.row_version,
            'document': latest['document'], 'evidence': [{'id': str(f.id), 'filename': f.original_filename,
             'mime_type': f.detected_mime_type or f.declared_mime_type} for f in files], 'is_submitted': False}
