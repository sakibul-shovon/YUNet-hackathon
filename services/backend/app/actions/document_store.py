"""Versioned, owner-authorized preparation documents. Editing never files a case."""

import datetime
import uuid

from fastapi import HTTPException
from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Uuid, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.actions.document_ast import (
    DocumentASTService,
    DocumentSectionAST,
    DocumentSentenceAST,
    EditableDocumentAST,
)
from app.core.database import Base
from app.evidence.models import EvidenceItem
from app.facts.service import FactService
from app.identity.models import Principal
from app.policy.engine import ProceduralAssessmentEngine


class PreparedDocument(Base):
    __tablename__ = "prepared_document_versions"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("cases.id", ondelete="CASCADE"), index=True)
    principal_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("principals.id", ondelete="CASCADE"), index=True)
    document_type: Mapped[str] = mapped_column(String(64))
    locale: Mapped[str] = mapped_column(String(8))
    case_version: Mapped[int] = mapped_column(Integer)
    revision: Mapped[int] = mapped_column(Integer, default=1)
    content: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.UTC))


async def load_document(
    case_id: uuid.UUID, principal: Principal, db: AsyncSession,
    document_type: str = "dncrp_ccms_complaint", locale: str = "en",
    document_id: uuid.UUID | None = None,
) -> EditableDocumentAST:
    case = await FactService.get_authorized_case(case_id, principal, db)
    query = select(PreparedDocument).where(
        PreparedDocument.case_id == case.id, PreparedDocument.principal_id == principal.id,
    )
    if document_id:
        saved = await db.scalar(query.where(PreparedDocument.id == document_id))
        if not saved:
            raise HTTPException(404, "Document not found")
        if saved.content.get('template_version', 0) < 2:
            raise HTTPException(409, 'Ebarki retired this preparation template. Prepare a current document before using it.')
    else:
        saved = await db.scalar(query.where(
            PreparedDocument.document_type == document_type, PreparedDocument.locale == locale,
            PreparedDocument.case_version == case.row_version,
        ).order_by(PreparedDocument.revision.desc(), PreparedDocument.created_at.desc()).limit(1))
    if saved and saved.content.get('template_version', 0) >= 2:
        return EditableDocumentAST.model_validate(saved.content)
    assertions = await FactService.get_assertions(case.id, principal, db)
    evidence = list((await db.scalars(select(EvidenceItem).where(
        EvidenceItem.case_id == case.id, EvidenceItem.status == "accepted"
    ))).all())
    facts = ProceduralAssessmentEngine.extract_facts_from_db_records(assertions, case)
    doc = DocumentASTService.generate_document_ast(
        case, facts, assertions, evidence_items=evidence,
        document_type=document_type, locale=locale,
    )
    doc.case_version = case.row_version
    doc.revision = 1
    from app.operations.connected_records import connected_records
    records = await connected_records(case, principal, db)
    moments = [item for item in records['timeline'] if item['review'] == 'confirmed']
    if moments:
        doc.sections.append(DocumentSectionAST(section_id='reviewed_chronology',
            section_title_en='Chronology reviewed by the consumer', section_title_bn='ভোক্তার মিলিয়ে দেখা ঘটনাক্রম',
            sentences=[DocumentSentenceAST(sentence_id=f'moment_{item["id"]}',
                text=f'{item["occurred_on"] + " — " if item["occurred_on"] else ""}{item["quote"]}',
                statement_type='user_allegation', supporting_record={
                    key: item[key] for key in ('source_id', 'source_line', 'quote', 'page', 'box', 'start', 'end')
                }) for item in moments[:20]]))
    await save_document(doc, principal.id, db)
    return doc


async def save_document(doc: EditableDocumentAST, principal_id: uuid.UUID, db: AsyncSession):
    db.add(PreparedDocument(
        id=doc.document_id, case_id=doc.case_id, principal_id=principal_id,
        document_type=doc.document_type, locale=doc.locale,
        case_version=doc.case_version, revision=doc.revision,
        content=doc.model_dump(mode="json"),
    ))
    await db.commit()
