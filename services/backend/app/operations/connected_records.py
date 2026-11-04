"""Private, source-linked chronology. Reviews are durable case events, never invented facts."""
import datetime
import hashlib
import re
import uuid

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.actions.document_store import PreparedDocument
from app.cases.models import Case, CaseEvent
from app.core.config import settings
from app.evidence.models import EvidenceItem
from app.facts.service import FactService
from app.identity.models import Consent
from app.operations.models import CaseRun

MONTHS = {'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
          'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12,
          'জানুয়ারি': 1, 'ফেব্রুয়ারি': 2, 'মার্চ': 3, 'এপ্রিল': 4, 'মে': 5, 'জুন': 6,
          'জুলাই': 7, 'আগস্ট': 8, 'সেপ্টেম্বর': 9, 'অক্টোবর': 10, 'নভেম্বর': 11, 'ডিসেম্বর': 12}
DIGITS = str.maketrans('০১২৩৪৫৬৭৮৯', '0123456789')
MONEY = re.compile(r'(?:BDT|৳|টাকা|Tk\.?)\s*[\d০-৯,]+(?:\.[\d০-৯]+)?|[\d০-৯,]+(?:\.[\d০-৯]+)?\s*(?:টাকা|BDT|Taka|Tk\.?)', re.IGNORECASE)


async def owned_case(case_id, principal, db):
    case = await FactService.get_authorized_case(case_id, principal, db)
    if case.principal_id != principal.id:
        raise HTTPException(404, 'Case not found')
    return case


async def has_external_consent(case, principal, db):
    return bool(await db.scalar(select(Consent.id).where(
        Consent.principal_id == principal.id, Consent.case_id == case.id,
        Consent.purpose == 'external_ai_processing', Consent.withdrawn_at.is_(None),
    ).limit(1))) and case.consent_status != 'withdrawn'


async def append_workspace_event(case, principal, db, kind, data, expected_version=None, material=False):
    # Row locking serializes the event sequence on PostgreSQL; the unique constraint
    # catches a concurrent SQLite write without silently overwriting either record.
    await db.refresh(case)
    if expected_version is not None and case.row_version != expected_version:
        raise HTTPException(409, 'Your case changed. Refresh before saving this update.')
    await db.execute(select(Case.id).where(Case.id == case.id).with_for_update())
    sequence = await db.scalar(select(func.coalesce(func.max(CaseEvent.event_sequence), 0)).where(CaseEvent.case_id == case.id))
    if material:
        case.row_version += 1
    event = CaseEvent(id=uuid.uuid4(), case_id=case.id, principal_id=principal.id,
                      event_sequence=sequence+1, event_type=kind, actor_type='consumer',
                      actor_id=principal.id, payload={**data, 'case_version': case.row_version})
    db.add(event)
    try:
        await db.commit()
    except IntegrityError as error:
        await db.rollback()
        raise HTTPException(409, 'Another update was saved. Refresh and try again.') from error
    await db.refresh(event)
    return event


def source_date(text):
    text = text.translate(DIGITS).lower()
    patterns = [r'\b(\d{4})-(\d{2})-(\d{2})\b', r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b']
    for index, pattern in enumerate(patterns):
        match = re.search(pattern, text)
        if match:
            a, b, c = map(int, match.groups())
            try:
                return datetime.date(a, b, c).isoformat() if index == 0 else datetime.date(c, b, a).isoformat()
            except ValueError:
                pass
    match = re.search(r'(\d{1,2})\s+([^\s,]+)[,\s]+(\d{4})', text)
    if match:
        day, month, year = match.groups()
        value = MONTHS.get(month) or next((n for name, n in MONTHS.items() if name[:3] == month), None)
        if value:
            try:
                return datetime.date(int(year), value, int(day)).isoformat()
            except ValueError:
                pass
    return None  # Relative dates and missing years require human clarification.


def chronology(readings):
    events = []
    for source in readings:
        lines = source.get('lines') or [{'text': text} for text in re.split(r'\n|(?<=[.!?।])\s+', source.get('text', '')) if text.strip()]
        dated = next((source_date(line['text']) for line in lines if source_date(line['text'])), None)
        selected = []
        for index, line in enumerate(lines):
            text = line['text'].strip()
            lower = text.lower()
            payment = bool(MONEY.search(text))
            promise = any(word in lower for word in ['will deliver', 'deliver by', 'will refund', 'পৌঁছে দেব', 'ফেরত দেব', 'পাঠিয়ে দেব'])
            message = any(word in lower for word in ['seller:', 'merchant:', 'buyer:', 'you:', 'বিক্রেতা:', 'আমি:'])
            if not (payment or promise or message or source.get('method') == 'groq_transcription'):
                continue
            kind = 'promise' if promise else 'payment' if payment else 'message' if message else 'audio'
            date = source_date(text)
            # A receipt's explicitly printed date can contextualize its amount;
            # an unrelated chat date cannot contextualize all other messages.
            if not date and payment and source.get('method') == 'native_pdf' and len(lines) < 35:
                date = dated
            selected.append((index, line, kind, date))
        if not selected and lines:
            selected = [(0, lines[0], 'account' if source['id'] == 'account' else 'record', source_date(lines[0]['text']))]
        for index, line, kind, date in selected[:16]:
            quote = line['text'][:1600]
            identity = hashlib.sha256(f'{source["id"]}:{index}:{quote}'.encode()).hexdigest()[:24]
            events.append({'id': identity, 'source_id': source['id'], 'kind': kind,
                           'quote': quote, 'occurred_on': date, 'review': 'proposed',
                           'source_line': index, 'page': line.get('page'), 'box': line.get('box'),
                           'start': line.get('start'), 'end': line.get('end'),
                           'requires_date_review': date is None, 'order': len(events)})
    return sorted(events, key=lambda event: (event['occurred_on'] is None, event['occurred_on'] or '', event['order']))


async def connected_records(case, principal, db):
    evidence = list((await db.scalars(select(EvidenceItem).where(
        EvidenceItem.case_id == case.id, EvidenceItem.principal_id == principal.id,
        EvidenceItem.status == 'accepted',
    ).order_by(EvidenceItem.created_at))).all())
    accepted = {str(item.id): item for item in evidence}
    runs = list((await db.scalars(select(CaseRun).where(
        CaseRun.case_id == case.id, CaseRun.principal_id == principal.id,
    ).order_by(CaseRun.created_at.desc()).limit(20))).all())
    readings = {}
    for run in runs:
        for source in run.result.get('readings', []):
            item = accepted.get(source['id'])
            if item and source.get('sha256') == item.sha256_hash and source['id'] not in readings:
                readings[source['id']] = source
    sources = [{'id': 'account', 'filename': 'Your original account', 'mime_type': 'text/plain',
                'text': case.story_narrative or '', 'method': 'user_account', 'model_executed': False}]
    sources += [readings.get(str(item.id), {'id': str(item.id), 'filename': item.original_filename,
                 'mime_type': item.detected_mime_type or item.declared_mime_type, 'text': '',
                 'sha256': item.sha256_hash, 'method': 'not_read', 'model_executed': False, 'lines': []}) for item in evidence]
    audit = list((await db.scalars(select(CaseEvent).where(
        CaseEvent.case_id == case.id, CaseEvent.principal_id == principal.id,
        CaseEvent.event_type.in_(['workspace.source_added', 'workspace.timeline_reviewed']),
    ).order_by(CaseEvent.event_sequence))).all())
    for event in audit:
        if event.event_type == 'workspace.source_added':
            attached = event.payload.get('evidence_id')
            if attached and attached not in accepted:
                continue
            sources.append({'id': str(event.id), 'filename': event.payload['label'],
                            'mime_type': 'text/plain', 'text': event.payload['text'],
                            'method': event.payload.get('source_type', 'pasted_text'),
                            'evidence_id': attached, 'model_executed': False,
                            'is_demo': event.payload.get('is_demo', False)})
    sources = sources[:50]
    timeline = chronology(sources)
    reviews = {event.payload['item_id']: event.payload for event in audit if event.event_type == 'workspace.timeline_reviewed'}
    for item in timeline:
        if item['id'] in reviews:
            review = reviews[item['id']]
            item.update({'review': review['outcome'], 'reviewed_case_version': review['case_version']})
            if review.get('corrected_date'):
                item['occurred_on'] = review['corrected_date']
                item['requires_date_review'] = False
                item['date_origin'] = 'user_correction'
    timeline.sort(key=lambda event: (event['occurred_on'] is None, event['occurred_on'] or '', event['order']))
    latest = await db.scalar(select(PreparedDocument).where(
        PreparedDocument.case_id == case.id, PreparedDocument.principal_id == principal.id,
    ).order_by(PreparedDocument.created_at.desc()).limit(1))
    consent = await has_external_consent(case, principal, db)
    return {'case_version': case.row_version, 'sources': sources[:50], 'timeline': timeline,
            'document': {'id': str(latest.id), 'case_version': latest.case_version,
                         'is_stale': latest.case_version != case.row_version or latest.content.get('template_version', 0) < 2} if latest else None,
            'capabilities': {'external_consent': consent, 'image_reading': bool((settings.GROQ_API_KEY and settings.GROQ_VISION_MODEL) or (settings.GEMINI_API_KEY and settings.GEMINI_RECORD_READER_MODEL)),
                             'audio_transcription': bool(settings.GROQ_API_KEY)}}
