import datetime
import re
import secrets
import uuid
from pathlib import Path
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.cases.models import CaseEvent
from app.evidence.document_parser import DocumentParser, DocumentParseResult
from app.evidence.mime_validation import (
    ALLOWED_MIME_TYPES,
    validate_file_signature,
)
from app.evidence.models import EvidenceItem
from app.evidence.parser_probe import ParserProbe
from app.evidence.schemas import (
    EvidenceItemOut,
    EvidenceSpanLinkCreate,
    EvidenceSpanLinkOut,
    PaymentReconciliationResult,
    ReconciliationItem,
    UploadIntentCreate,
    UploadIntentOut,
)
from app.evidence.storage import get_storage_backend
from app.facts.models import FactAssertion, FactSourceLink
from app.facts.service import FactService
from app.identity.models import Principal


def ensure_utc(dt: datetime.datetime) -> datetime.datetime:
    """Ensures datetime is timezone-aware in UTC for database compatibility across SQLite and PostgreSQL."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=datetime.UTC)
    return dt


class EvidenceService:
    """T10, T11: Manages evidence upload intents, quarantine verification, quotas, and accepted storage."""

    MAX_ITEM_BYTES = 20 * 1024 * 1024  # 20 MB per file
    MAX_CASE_BYTES = 100 * 1024 * 1024  # 100 MB aggregate per case
    MAX_CASE_ITEMS = 20  # Max 20 items per case
    TOKEN_EXPIRY_MINUTES = 120  # 2-hour signed upload token lifespan (T11)

    @classmethod
    async def get_case_quota_usage(cls, case_id: uuid.UUID, db: AsyncSession) -> tuple[int, int]:
        """Returns (aggregate_reserved_and_accepted_bytes, active_item_count)."""
        stmt = select(
            func.coalesce(func.sum(EvidenceItem.quota_reserved_bytes), 0),
            func.count(EvidenceItem.id),
        ).where(
            EvidenceItem.case_id == case_id,
            EvidenceItem.status.in_(["intent_created", "quarantined", "validating", "accepted"]),
        )
        res = await db.execute(stmt)
        total_bytes, count = res.one()
        return int(total_bytes), int(count)

    @classmethod
    async def create_upload_intent(
        cls,
        intent_in: UploadIntentCreate,
        principal: Principal,
        db: AsyncSession,
    ) -> UploadIntentOut:
        """T10/T11: Checks case ownership and quotas, creates upload intent, and returns unpredictable token."""
        # 1. Authorize case ownership
        case = await FactService.get_authorized_case(intent_in.case_id, principal, db)

        # 2. Validate declared MIME type
        norm_mime = intent_in.declared_mime_type.strip().lower()
        if norm_mime not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Declared MIME type '{intent_in.declared_mime_type}' is not supported.",
            )

        # 3. Validate declared item size
        if intent_in.declared_byte_size > cls.MAX_ITEM_BYTES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"File exceeds maximum allowed size of {cls.MAX_ITEM_BYTES // (1024 * 1024)} MB.",
            )

        # 4. Check case quota limits (T11)
        current_bytes, current_items = await cls.get_case_quota_usage(case.id, db)
        if current_items >= cls.MAX_CASE_ITEMS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Case item limit of {cls.MAX_CASE_ITEMS} items reached.",
            )

        if current_bytes + intent_in.declared_byte_size > cls.MAX_CASE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Upload would exceed the case aggregate quota of {cls.MAX_CASE_BYTES // (1024 * 1024)} MB.",
            )

        # 5. Sanitize original filename (T10: prevent path traversal)
        safe_filename = Path(intent_in.declared_filename).name
        if not safe_filename or safe_filename.startswith("."):
            safe_filename = f"upload_{uuid.uuid4().hex[:8]}"

        # 6. Generate unpredictable upload token and quarantine key
        upload_token = secrets.token_urlsafe(32)
        token_expires_at = datetime.datetime.now(datetime.UTC) + datetime.timedelta(
            minutes=cls.TOKEN_EXPIRY_MINUTES
        )
        quarantine_key = f"q_{case.id.hex[:8]}_{uuid.uuid4().hex}_{secrets.token_hex(4)}"

        # 7. Record EvidenceItem in DB
        evidence = EvidenceItem(
            id=uuid.uuid4(),
            case_id=case.id,
            principal_id=principal.id,
            storage_kind="local_disk",
            quarantine_path=quarantine_key,
            original_filename=safe_filename,
            declared_mime_type=norm_mime,
            byte_size=0,
            status="intent_created",
            is_quarantined=True,
            upload_token=upload_token,
            token_expires_at=token_expires_at,
            intent_consumed=False,
            quota_reserved_bytes=intent_in.declared_byte_size,
        )
        db.add(evidence)
        await db.commit()
        await db.refresh(evidence)

        upload_url = f"/v1/uploads/{evidence.id}/raw?token={upload_token}"

        return UploadIntentOut(
            intent_id=evidence.id,
            case_id=case.id,
            upload_url=upload_url,
            upload_token=upload_token,
            token_expires_at=evidence.token_expires_at,
            max_byte_size=cls.MAX_ITEM_BYTES,
            storage_kind="local_disk",
        )

    @classmethod
    async def receive_quarantine_data(
        cls,
        intent_id: uuid.UUID,
        upload_token: str,
        file_bytes: bytes,
        db: AsyncSession,
    ) -> None:
        """T10, T11: Receives direct upload to quarantine using one-path token."""
        stmt = select(EvidenceItem).where(
            EvidenceItem.id == intent_id,
            EvidenceItem.upload_token == upload_token,
        )
        res = await db.execute(stmt)
        item = res.scalar_one_or_none()
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Upload intent not found or invalid token.",
            )

        # Invariant T10: Intent cannot be reused
        if item.intent_consumed:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Upload intent has already been consumed.",
            )

        # Invariant T11: Expired token rejected
        now = datetime.datetime.now(datetime.UTC)
        if ensure_utc(item.token_expires_at) < now:
            item.status = "quarantine_expired"
            item.quota_reserved_bytes = 0
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Upload token has expired.",
            )

        # Check actual upload size against item limit
        actual_size = len(file_bytes)
        if actual_size > cls.MAX_ITEM_BYTES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Uploaded file exceeds maximum limit of {cls.MAX_ITEM_BYTES // (1024 * 1024)} MB.",
            )

        # Write data to storage backend under quarantine
        storage = get_storage_backend()
        quarantine_file_path = storage.save_quarantine(item.quarantine_path, file_bytes)

        # Update EvidenceItem
        item.quarantine_path = quarantine_file_path
        item.byte_size = actual_size
        item.status = "quarantined"
        await db.commit()

    @classmethod
    async def complete_upload(
        cls,
        intent_id: uuid.UUID,
        principal: Principal,
        db: AsyncSession,
        simulate_scanner_outage: bool = False,
    ) -> EvidenceItemOut:
        """T10, T11: Consumes intent once, validates server actual bytes, and moves to accepted storage."""
        stmt = select(EvidenceItem).where(
            EvidenceItem.id == intent_id,
            EvidenceItem.principal_id == principal.id,
        )
        res = await db.execute(stmt)
        item = res.scalar_one_or_none()
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Upload intent not found.",
            )

        # Invariant T10: Reused upload-completion intent rejected (409)
        if item.intent_consumed:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Upload intent has already been consumed.",
            )

        storage = get_storage_backend()
        now = datetime.datetime.now(datetime.UTC)

        # Invariant T11: Late write past expiry rejected
        if ensure_utc(item.token_expires_at) < now:
            item.status = "quarantine_expired"
            item.quota_reserved_bytes = 0
            storage.delete_quarantine(item.quarantine_path)
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Upload token has expired before completion was confirmed.",
            )

        if item.status != "quarantined":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot complete upload with status '{item.status}'. File data missing in quarantine.",
            )

        # Mark intent as consumed immediately (T10)
        item.intent_consumed = True

        # Read actual bytes from quarantine
        try:
            raw_data = storage.read_quarantine(item.quarantine_path)
        except FileNotFoundError:
            item.status = "rejected"
            item.rejection_reason = "Quarantine data missing on storage volume"
            item.quota_reserved_bytes = 0
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Quarantine file not found.",
            )

        # Invariant T10: Validate actual byte size vs limit
        if len(raw_data) > cls.MAX_ITEM_BYTES:
            item.status = "rejected"
            item.rejection_reason = f"File exceeds maximum size {cls.MAX_ITEM_BYTES}"
            item.quota_reserved_bytes = 0
            storage.delete_quarantine(item.quarantine_path)
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="File exceeds maximum allowable size.",
            )

        # Invariant T10: Validate file signature against declared MIME
        is_valid, detected_mime, error_msg = validate_file_signature(
            item.declared_mime_type, raw_data
        )
        if not is_valid:
            item.status = "rejected"
            item.rejection_code = "MIME_SPOOF"
            item.rejection_reason = error_msg or "Binary signature mismatch"
            item.detected_mime_type = detected_mime
            item.is_retryable = False
            item.quota_reserved_bytes = 0
            storage.delete_quarantine(item.quarantine_path)
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=error_msg
                or "MIME spoof detected: file contents do not match declared type.",
            )

        # Invariant T12: Deep parser probe (pixel bombs, page bombs, encryption, active content, scanner outage)
        probe = ParserProbe.probe_file(
            raw_data, detected_mime, simulate_scanner_outage=simulate_scanner_outage
        )
        if not probe.is_safe:
            item.rejection_code = probe.rejection_code
            item.rejection_reason = probe.error_message
            item.is_retryable = probe.is_retryable
            item.guidance_en = probe.guidance_en
            item.guidance_bn = probe.guidance_bn

            if probe.is_retryable:
                # T12: Scanner outage keeps file quarantined and retryable; never promoted to accepted
                item.status = "quarantined"
                item.is_quarantined = True
                await db.commit()
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail={
                        "code": probe.rejection_code,
                        "message": probe.error_message,
                        "retryable": True,
                        "guidance_en": probe.guidance_en,
                        "guidance_bn": probe.guidance_bn,
                    },
                )
            else:
                # T12: Non-retryable rejection (pixel bomb, active content, encrypted PDF)
                item.status = "rejected"
                item.is_quarantined = True
                item.quota_reserved_bytes = 0
                storage.delete_quarantine(item.quarantine_path)
                await db.commit()
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={
                        "code": probe.rejection_code,
                        "message": probe.error_message,
                        "retryable": False,
                        "guidance_en": probe.guidance_en,
                        "guidance_bn": probe.guidance_bn,
                    },
                )

        # Invariant T11: Promote verified bytes to separate accepted location
        accepted_key = f"acc_{item.case_id.hex[:8]}_{uuid.uuid4().hex}"
        accepted_path, sha256_hash, actual_bytes = storage.promote_to_accepted(
            item.quarantine_path, accepted_key
        )

        item.accepted_path = accepted_path
        item.detected_mime_type = detected_mime
        item.sha256_hash = sha256_hash
        item.byte_size = actual_bytes
        item.status = "accepted"
        item.is_quarantined = False
        item.quota_reserved_bytes = actual_bytes
        item.rejection_reason = None

        await db.commit()
        await db.refresh(item)

        return EvidenceItemOut(
            id=item.id,
            case_id=item.case_id,
            original_filename=item.original_filename,
            declared_mime_type=item.declared_mime_type,
            detected_mime_type=item.detected_mime_type,
            byte_size=item.byte_size,
            sha256_hash=item.sha256_hash,
            status=item.status,
            is_quarantined=item.is_quarantined,
            rejection_reason=item.rejection_reason,
            created_at=item.created_at,
        )

    @classmethod
    async def list_case_evidence(
        cls,
        case_id: uuid.UUID,
        principal: Principal,
        db: AsyncSession,
    ) -> list[EvidenceItemOut]:
        """Lists evidence for the authorized case owner."""
        await FactService.get_authorized_case(case_id, principal, db)

        stmt = (
            select(EvidenceItem)
            .where(
                EvidenceItem.case_id == case_id,
                EvidenceItem.status.in_(["accepted", "quarantined", "validating", "rejected"]),
            )
            .order_by(EvidenceItem.created_at.desc())
        )
        res = await db.execute(stmt)
        items = res.scalars().all()
        return [
            EvidenceItemOut(
                id=i.id,
                case_id=i.case_id,
                original_filename=i.original_filename,
                declared_mime_type=i.declared_mime_type,
                detected_mime_type=i.detected_mime_type,
                byte_size=i.byte_size,
                sha256_hash=i.sha256_hash,
                status=i.status,
                is_quarantined=i.is_quarantined,
                rejection_reason=i.rejection_reason,
                rejection_code=i.rejection_code,
                is_retryable=i.is_retryable,
                guidance_en=i.guidance_en,
                guidance_bn=i.guidance_bn,
                created_at=i.created_at,
            )
            for i in items
        ]

    @classmethod
    async def get_evidence_item(
        cls,
        case_id: uuid.UUID,
        evidence_id: uuid.UUID,
        principal: Principal,
        db: AsyncSession,
    ) -> EvidenceItemOut:
        """T01: Returns evidence item details if authorized for case owner."""
        await FactService.get_authorized_case(case_id, principal, db)
        stmt = select(EvidenceItem).where(
            EvidenceItem.id == evidence_id,
            EvidenceItem.case_id == case_id,
        )
        res = await db.execute(stmt)
        item = res.scalar_one_or_none()
        if not item or item.status == "deleted":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evidence item not found.",
            )
        return EvidenceItemOut(
            id=item.id,
            case_id=item.case_id,
            original_filename=item.original_filename,
            declared_mime_type=item.declared_mime_type,
            detected_mime_type=item.detected_mime_type,
            byte_size=item.byte_size,
            sha256_hash=item.sha256_hash,
            status=item.status,
            is_quarantined=item.is_quarantined,
            rejection_reason=item.rejection_reason,
            rejection_code=item.rejection_code,
            is_retryable=item.is_retryable,
            guidance_en=item.guidance_en,
            guidance_bn=item.guidance_bn,
            created_at=item.created_at,
        )

    @classmethod
    async def get_evidence_preview_bytes(
        cls,
        case_id: uuid.UUID,
        evidence_id: uuid.UUID,
        principal: Principal,
        db: AsyncSession,
    ) -> tuple[bytes, str, str]:
        """T15: Returns private preview bytes with bounded read lease and no public bucket path."""
        await FactService.get_authorized_case(case_id, principal, db)
        stmt = select(EvidenceItem).where(
            EvidenceItem.id == evidence_id,
            EvidenceItem.case_id == case_id,
        )
        res = await db.execute(stmt)
        item = res.scalar_one_or_none()
        if not item or item.status == "deleted":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evidence item not found.",
            )
        if item.status != "accepted" or not item.accepted_path:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Evidence item is not in accepted status (current status: {item.status}).",
            )
        storage = get_storage_backend()
        data = storage.read_accepted(item.accepted_path)
        mime = item.detected_mime_type or item.declared_mime_type
        return data, mime, item.original_filename

    @classmethod
    async def create_span_link(
        cls,
        case_id: uuid.UUID,
        evidence_id: uuid.UUID,
        payload: EvidenceSpanLinkCreate,
        principal: Principal,
        db: AsyncSession,
    ) -> EvidenceSpanLinkOut:
        """T14, T15: Links an evidence region or page to an asserted case fact."""
        await FactService.get_authorized_case(case_id, principal, db)

        # Validate evidence
        ev_stmt = select(EvidenceItem).where(
            EvidenceItem.id == evidence_id,
            EvidenceItem.case_id == case_id,
            EvidenceItem.status == "accepted",
        )
        ev_res = await db.execute(ev_stmt)
        item = ev_res.scalar_one_or_none()
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Accepted evidence item not found in case.",
            )

        # Validate assertion
        fa_stmt = select(FactAssertion).where(
            FactAssertion.id == payload.assertion_id,
            FactAssertion.case_id == case_id,
            FactAssertion.is_active == True,
        )
        fa_res = await db.execute(fa_stmt)
        assertion = fa_res.scalar_one_or_none()
        if not assertion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Active fact assertion not found in case.",
            )

        locator = {
            "evidence_id": str(evidence_id),
            "filename": item.original_filename,
            "page_number": payload.page_number,
            "normalized_box": payload.normalized_box,
            "selected_text": payload.selected_text,
        }
        link = FactSourceLink(
            assertion_id=assertion.id,
            source_type="evidence_span",
            locator_meta=locator,
        )
        db.add(link)
        await db.commit()
        await db.refresh(link)

        return EvidenceSpanLinkOut(
            id=link.id,
            assertion_id=assertion.id,
            evidence_id=evidence_id,
            source_type=link.source_type,
            page_number=payload.page_number,
            normalized_box=payload.normalized_box,
            selected_text=payload.selected_text,
            created_at=link.created_at,
        )

    @classmethod
    async def get_evidence_spans(
        cls,
        case_id: uuid.UUID,
        evidence_id: uuid.UUID,
        principal: Principal,
        db: AsyncSession,
    ) -> list[EvidenceSpanLinkOut]:
        """T14, T15: Returns all linked spans for an evidence item."""
        await FactService.get_authorized_case(case_id, principal, db)

        stmt = (
            select(FactSourceLink)
            .join(FactAssertion, FactSourceLink.assertion_id == FactAssertion.id)
            .where(
                FactAssertion.case_id == case_id,
                FactAssertion.is_active == True,
                FactSourceLink.source_type == "evidence_span",
            )
        )
        res = await db.execute(stmt)
        links = res.scalars().all()

        matching = []
        target_str = str(evidence_id)
        for link in links:
            meta = link.locator_meta or {}
            if meta.get("evidence_id") == target_str:
                matching.append(
                    EvidenceSpanLinkOut(
                        id=link.id,
                        assertion_id=link.assertion_id,
                        evidence_id=evidence_id,
                        source_type=link.source_type,
                        page_number=meta.get("page_number"),
                        normalized_box=meta.get("normalized_box"),
                        selected_text=meta.get("selected_text"),
                        created_at=link.created_at,
                    )
                )
        return matching

    @classmethod
    async def reconcile_case_payments(
        cls,
        case_id: uuid.UUID,
        principal: Principal,
        db: AsyncSession,
    ) -> PaymentReconciliationResult:
        """T21: Reconciles narrated amount vs linked evidence receipts; detects duplicates and excludes unrelated."""
        await FactService.get_authorized_case(case_id, principal, db)

        # 1. Fetch narrated amount from fact assertions
        stmt_facts = select(FactAssertion).where(
            FactAssertion.case_id == case_id,
            FactAssertion.is_active == True,
            FactAssertion.field_name.in_(["claimed_amount", "transaction_amount", "goods_value"]),
        )
        facts_res = await db.execute(stmt_facts)
        amount_facts = facts_res.scalars().all()

        narrated_minor = 0
        if amount_facts:
            for af in amount_facts:
                val = af.typed_value
                if isinstance(val, dict) and "minor_units" in val:
                    narrated_minor = int(val["minor_units"])
                    break
                elif isinstance(val, (int, float)):
                    narrated_minor = int(val)
                    break

        # 2. Fetch all accepted evidence items for this case
        stmt_ev = select(EvidenceItem).where(
            EvidenceItem.case_id == case_id,
            EvidenceItem.status == "accepted",
        )
        ev_res = await db.execute(stmt_ev)
        accepted_items = {item.id: item for item in ev_res.scalars().all()}

        # 3. Fetch linked spans for this case
        stmt_links = (
            select(FactSourceLink)
            .join(FactAssertion, FactSourceLink.assertion_id == FactAssertion.id)
            .where(
                FactAssertion.case_id == case_id,
                FactAssertion.is_active == True,
                FactSourceLink.source_type == "evidence_span",
            )
        )
        links_res = await db.execute(stmt_links)
        all_links = links_res.scalars().all()

        linked_evidence_ids = set()
        for l in all_links:
            meta = l.locator_meta or {}
            ev_id_str = meta.get("evidence_id")
            if ev_id_str:
                try:
                    linked_evidence_ids.add(uuid.UUID(ev_id_str))
                except ValueError:
                    pass

        # 4. Extract amount for each evidence item from parsed regions/meta or document text
        storage = get_storage_backend()
        reconciled_items: list[ReconciliationItem] = []
        unlinked_items: list[ReconciliationItem] = []
        seen_hashes = set()
        total_linked_minor = 0

        for item_id, item in accepted_items.items():
            if not item.accepted_path:
                continue
            item_bytes = storage.read_accepted(item.accepted_path)
            parsed = (
                DocumentParser.parse_pdf_bytes(item.id, item_bytes)
                if item.detected_mime_type == "application/pdf"
                else None
            )

            extracted_minor = 0
            if parsed and parsed.regions:
                for r in parsed.regions:
                    if r.is_critical_token and r.critical_token_type == "money":
                        nums = re.findall(r"\d+", r.text.replace(",", ""))
                        if nums:
                            val = int(nums[0])
                            extracted_minor = val * 100
                            break

            is_dup = item.sha256_hash in seen_hashes if item.sha256_hash else False
            if item.sha256_hash:
                seen_hashes.add(item.sha256_hash)

            rec_entry = ReconciliationItem(
                evidence_id=item.id,
                filename=item.original_filename,
                amount_minor_units=extracted_minor,
                is_duplicate=is_dup,
                is_linked=(item_id in linked_evidence_ids),
            )

            if item_id in linked_evidence_ids:
                reconciled_items.append(rec_entry)
                if not is_dup:
                    total_linked_minor += extracted_minor
            else:
                unlinked_items.append(rec_entry)

        # 5. Determine reconciliation state and prompts (T21)
        discrepancy = narrated_minor - total_linked_minor
        is_reconciled = (discrepancy == 0) and (narrated_minor > 0)

        if not accepted_items:
            status_str = "no_receipts"
            prompt_en = "No receipts uploaded. Please upload official proof of payment."
            prompt_bn = "কোনো রসিদ আপলোড করা হয়নি। অনুগ্রহ করে লেনদেনের দালিলিক প্রমাণ আপলোড করুন।"
        elif is_reconciled:
            status_str = "reconciled"
            prompt_en = f"All amounts reconciled (BDT {narrated_minor / 100:,.2f})."
            prompt_bn = f"টাকার পরিমাণ সম্পূর্ণভাবে মিলে গেছে (৳{narrated_minor / 100:,.2f})।"
        elif unlinked_items and discrepancy > 0:
            status_str = "unlinked_evidence_available"
            prompt_en = f"Discrepancy: Narrated amount (BDT {narrated_minor / 100:,.2f}) exceeds linked receipts (BDT {total_linked_minor / 100:,.2f}). Link available unlinked receipt to reconcile."
            prompt_bn = f"বর্ণনাকৃত টাকার পরিমাণ (৳{narrated_minor / 100:,.2f}) এবং যুক্ত রশিদের (৳{total_linked_minor / 100:,.2f}) মধ্যে পার্থক্য রয়েছে। অতিরিক্ত রসিদ যুক্ত করে সমাধান করুন।"
        else:
            status_str = "discrepancy"
            prompt_en = f"Discrepancy: Narrated amount (BDT {narrated_minor / 100:,.2f}) vs linked receipts (BDT {total_linked_minor / 100:,.2f}). Please clarify or upload missing proof."
            prompt_bn = f"বর্ণনাকৃত টাকার পরিমাণ (৳{narrated_minor / 100:,.2f}) এবং যুক্ত রশিদের (৳{total_linked_minor / 100:,.2f}) মধ্যে অমিল রয়েছে। অনুগ্রহ করে তথ্য স্পষ্ট করুন বা প্রমাণ আপলোড করুন।"

        return PaymentReconciliationResult(
            case_id=case_id,
            narrated_amount_minor_units=narrated_minor,
            linked_evidence_total_minor_units=total_linked_minor,
            discrepancy_minor_units=discrepancy,
            is_reconciled=is_reconciled,
            status=status_str,
            reconciled_items=reconciled_items,
            unlinked_items=unlinked_items,
            prompt_en=prompt_en,
            prompt_bn=prompt_bn,
        )

    @classmethod
    async def delete_evidence_item(
        cls,
        case_id: uuid.UUID,
        evidence_id: uuid.UUID,
        principal: Principal,
        db: AsyncSession,
    ) -> dict[str, Any]:
        """T36: Cascading removal and invalidation of evidence, private files, linked spans and derived assertions."""
        case = await FactService.get_authorized_case(case_id, principal, db)

        stmt = select(EvidenceItem).where(
            EvidenceItem.id == evidence_id,
            EvidenceItem.case_id == case_id,
        )
        res = await db.execute(stmt)
        item = res.scalar_one_or_none()
        if not item or item.status == "deleted":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evidence item not found.",
            )

        storage = get_storage_backend()

        # 1. Purge physical files from quarantine and accepted
        if item.quarantine_path:
            storage.delete_quarantine(item.quarantine_path)
        if item.accepted_path:
            storage.delete_accepted(item.accepted_path)

        # 2. Delete linked spans
        target_str = str(evidence_id)
        stmt_links = (
            select(FactSourceLink)
            .join(FactAssertion, FactSourceLink.assertion_id == FactAssertion.id)
            .where(FactAssertion.case_id == case_id)
        )
        links_res = await db.execute(stmt_links)
        all_links = links_res.scalars().all()

        deleted_links_count = 0
        for l in all_links:
            meta = l.locator_meta or {}
            if meta.get("evidence_id") == target_str:
                await db.delete(l)
                deleted_links_count += 1

        # 3. Mark evidence status as deleted and release quota
        item.status = "deleted"
        item.quota_reserved_bytes = 0
        item.accepted_path = None

        # 4. Bump case version to invalidate stale cached assessments and drafts (T36)
        case.row_version += 1

        # 5. Record case event
        seq_res = await db.execute(
            select(func.coalesce(func.max(CaseEvent.event_sequence), 0)).where(
                CaseEvent.case_id == case_id
            )
        )
        next_seq = int(seq_res.scalar_one()) + 1

        event = CaseEvent(
            case_id=case_id,
            principal_id=principal.id,
            event_sequence=next_seq,
            event_type="evidence_deleted",
            actor_type="consumer",
            actor_id=principal.id,
            schema_version=1,
            payload={"evidence_id": target_str, "filename": item.original_filename},
            created_at=datetime.datetime.now(datetime.UTC),
        )
        db.add(event)

        await db.commit()

        return {
            "status": "deleted",
            "evidence_id": str(evidence_id),
            "deleted_links_count": deleted_links_count,
            "case_version": case.row_version,
        }

    @classmethod
    async def sweep_expired_intents(cls, db: AsyncSession) -> int:
        """T11: Sweeps expired upload tokens and releases quota reservations."""
        now = datetime.datetime.now(datetime.UTC)
        stmt = select(EvidenceItem).where(
            EvidenceItem.status.in_(["intent_created", "quarantined"]),
        )
        res = await db.execute(stmt)
        candidate_items = res.scalars().all()

        storage = get_storage_backend()
        count = 0
        for item in candidate_items:
            if ensure_utc(item.token_expires_at) < now:
                storage.delete_quarantine(item.quarantine_path)
                item.status = "quarantine_expired"
                item.quota_reserved_bytes = 0
                count += 1

        if count > 0:
            await db.commit()

        return count

    @classmethod
    async def get_evidence_regions(
        cls,
        case_id: uuid.UUID,
        evidence_id: uuid.UUID,
        principal: Principal,
        db: AsyncSession,
    ) -> DocumentParseResult:
        """T13, T14: Returns parsed document regions with normalized bounding boxes and quality flags."""
        await FactService.get_authorized_case(case_id, principal, db)

        stmt = select(EvidenceItem).where(
            EvidenceItem.id == evidence_id,
            EvidenceItem.case_id == case_id,
            EvidenceItem.principal_id == principal.id,
        )
        res = await db.execute(stmt)
        item = res.scalar_one_or_none()
        if not item or item.status != "accepted" or not item.accepted_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Accepted evidence item not found.",
            )

        storage = get_storage_backend()
        data = storage.read_accepted(item.accepted_path)

        if item.detected_mime_type == "application/pdf":
            return DocumentParser.parse_pdf_bytes(item.id, data)
        else:
            return DocumentParseResult(
                evidence_id=item.id,
                page_count=1,
                has_native_text=False,
                ocr_applied=False,
                regions=[],
                full_text="",
                quality_flags=["NON_PDF_IMAGE"],
            )
