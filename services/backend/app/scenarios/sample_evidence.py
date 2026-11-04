"""Real, clearly labeled sample documents for an isolated demonstration case."""
import datetime
import io
import uuid

from reportlab.pdfgen import canvas
from sqlalchemy import select

from app.evidence.document_parser import DocumentParser
from app.evidence.models import EvidenceItem
from app.evidence.storage import get_storage_backend
from app.facts.models import FactAssertion, FactSourceLink


async def add_sample_payment(case, principal, db, second=False):
    filename = 'Ebarki-sample-second-payment.pdf' if second else 'Ebarki-sample-payment.pdf'
    existing = await db.scalar(select(EvidenceItem).where(
        EvidenceItem.case_id == case.id, EvidenceItem.principal_id == principal.id,
        EvidenceItem.original_filename == filename, EvidenceItem.status == 'accepted',
    ).limit(1))
    if existing:
        return existing
    amount = 500 if second else 5000
    buffer = io.BytesIO()
    document = canvas.Canvas(buffer, pagesize=(420, 560))
    document.setTitle('Ebarki fictional sample payment record')
    document.setAuthor('Ebarki')
    document.setFillColorRGB(.68, .24, .17)
    document.setFont('Helvetica-Bold', 23)
    document.drawString(38, 500, 'Ebarki / SAMPLE')
    document.setFillColorRGB(.13, .17, .18)
    document.setFont('Helvetica', 10)
    document.drawString(38, 471, 'FICTIONAL DATA. NOT A REAL TRANSACTION.')
    document.line(38, 450, 382, 450)
    document.setFont('Helvetica-Bold', 17)
    document.drawString(38, 410, 'Sample Electronics')
    document.setFont('Helvetica', 11)
    document.drawString(38, 374, 'Payment for a sample phone order')
    document.drawString(38, 337, 'Reference: SAMPLE-002' if second else 'Reference: SAMPLE-001')
    document.drawString(38, 308, 'Date: ' + str(case.incident_date or datetime.date.today().isoformat()))
    document.line(38, 279, 382, 279)
    document.setFont('Helvetica', 11)
    document.drawString(38, 245, 'Amount paid')
    document.setFont('Helvetica-Bold', 30)
    document.drawString(38, 202, f'BDT {amount:,}')
    document.setFont('Helvetica', 10)
    document.drawString(38, 135, 'For the Ebarki scenario sandbox only.')
    document.drawString(38, 115, 'This document proves no real purchase or payment.')
    document.save()
    data = buffer.getvalue()
    storage = get_storage_backend()
    key = f'{case.id}/{uuid.uuid4().hex}_{filename}'
    quarantine = storage.save_quarantine(key, data)
    accepted, digest, size = storage.promote_to_accepted(quarantine, key)
    evidence = EvidenceItem(
        id=uuid.uuid4(), case_id=case.id, principal_id=principal.id, storage_kind='local_disk',
        quarantine_path=quarantine, accepted_path=accepted, original_filename=filename,
        declared_mime_type='application/pdf', detected_mime_type='application/pdf',
        byte_size=size, quota_reserved_bytes=size, sha256_hash=digest, status='accepted',
        is_quarantined=False, upload_token=uuid.uuid4().hex,
        token_expires_at=datetime.datetime.now(datetime.UTC)+datetime.timedelta(days=1), intent_consumed=True,
    )
    db.add(evidence)
    amount_fact = await db.scalar(select(FactAssertion).where(
        FactAssertion.case_id == case.id, FactAssertion.field_name == 'amount_paid',
        FactAssertion.is_active.is_(True),
    ).limit(1))
    if not amount_fact:
        amount_fact = FactAssertion(
            id=uuid.uuid4(), case_id=case.id, field_name='amount_paid', field_type='money',
            typed_value={'minor_units': 550000, 'currency': 'BDT'}, original_text='BDT 5,500',
            origin='synthetic_scenario_manifest', created_case_version=case.row_version,
            is_active=True,
        )
        db.add(amount_fact)
        await db.flush()
    parsed = DocumentParser.parse_pdf_bytes(evidence.id, data)
    region = next((item for item in parsed.regions if item.critical_token_type == 'money'), None)
    db.add(FactSourceLink(assertion_id=amount_fact.id, source_type='evidence_span', locator_meta={
        'evidence_id': str(evidence.id), 'filename': filename, 'page_number': 1,
        'selected_text': f'BDT {amount:,}',
        'normalized_box': region.normalized_box if region else None,
    }))
    if second:
        case.row_version += 1
    await db.commit()
    await db.refresh(evidence)
    return evidence
