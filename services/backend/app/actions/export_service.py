import datetime
import hashlib
import io
import uuid

from PIL import Image
from pydantic import BaseModel, ConfigDict, Field

from app.actions.document_ast import EditableDocumentAST


class CaseExportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    export_id: uuid.UUID
    case_id: uuid.UUID
    format: str  # 'markdown', 'html', 'pdf_ready'
    document_title: str
    content: str
    sha256_hash: str
    disclaimer_notice: str = (
        "PREPARATION MATERIAL ONLY — NOT SUBMITTED BY CLAIMCRAFT BD. "
        "Generating or downloading this document does not constitute official submission (T27)."
    )
    is_filed: bool = False
    is_sent: bool = False
    created_at: str


class RasterRedactionRequest(BaseModel):
    bounding_boxes: list[dict[str, int]] = Field(
        ...,
        description="List of pixel coordinate boxes to permanently overwrite: [{'x': 10, 'y': 20, 'w': 100, 'h': 40}]",
    )


class ExportService:
    """P09.4 & P09.5: Multi-format document export, provenance metadata,

    and true raster redaction (T34, T35).
    """

    @classmethod
    def export_as_markdown(
        cls,
        doc: EditableDocumentAST,
    ) -> CaseExportOut:
        is_bn = doc.locale == "bn"
        lines = []

        lines.append(f"# {doc.title}")
        lines.append(f"**Date:** {doc.created_at} | **Status:** {doc.lifecycle_state.upper()}\n")

        lines.append("> [!IMPORTANT]")
        lines.append(
            f"> {doc.unsubmitted_disclaimer_bn if is_bn else doc.unsubmitted_disclaimer_en}\n"
        )

        for sec in doc.sections:
            title = sec.section_title_bn if is_bn else sec.section_title_en
            lines.append(f"## {title}")
            for sent in sec.sentences:
                badge = (
                    f" `[{sent.statement_type}]`" if sent.statement_type != "reviewed_fact" else ""
                )
                citation = (
                    f" *(Statutory Ref: {sent.supporting_citation})*"
                    if sent.supporting_citation
                    else ""
                )
                lines.append(f"- {sent.text}{citation}{badge}")
            lines.append("")

        if doc.evidence_index:
            lines.append("## " + ("সংযুক্ত প্রমাণাদির তালিকা" if is_bn else "Attached Evidence Index"))
            for ev in doc.evidence_index:
                lines.append(f"- **{ev['filename']}** ({ev['mime_type']}) — Verified")
            lines.append("")

        lines.append(
            "## " + ("দাখিল পূর্ববর্তী চেকলিস্ট" if is_bn else "Pre-Filing Verification Checklist")
        )
        for chk in doc.preparation_checklist:
            lines.append(f"- [ ] {chk}")
        lines.append("")

        content_str = "\n".join(lines)
        content_hash = hashlib.sha256(content_str.encode("utf-8")).hexdigest()

        return CaseExportOut(
            export_id=uuid.uuid4(),
            case_id=doc.case_id,
            format="markdown",
            document_title=doc.title,
            content=content_str,
            sha256_hash=content_hash,
            is_filed=False,  # Invariant T27: Export never marks filed!
            is_sent=False,
            created_at=datetime.date.today().isoformat(),
        )

    @classmethod
    def export_as_html(
        cls,
        doc: EditableDocumentAST,
    ) -> CaseExportOut:
        is_bn = doc.locale == "bn"
        html_parts = []

        html_parts.append("<!DOCTYPE html>")
        html_parts.append(f"<html lang='{doc.locale}'>")
        html_parts.append("<head>")
        html_parts.append("<meta charset='utf-8'/>")
        html_parts.append(f"<title>{doc.title}</title>")
        html_parts.append("""<style>
          body { font-family: 'SolaimanLipi', 'Noto Sans Bengali', system-ui, sans-serif; line-height: 1.6; padding: 40px; color: #1e293b; max-width: 800px; margin: auto; }
          .disclaimer { border: 2px solid #f59e0b; background: #fffbeb; color: #b45309; padding: 16px; border-radius: 8px; margin-bottom: 24px; font-weight: bold; font-size: 13px; }
          h1 { color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; font-size: 24px; }
          h2 { color: #1e293b; margin-top: 24px; font-size: 18px; }
          ul { padding-left: 20px; }
          li { margin-bottom: 8px; }
          .tag { font-size: 11px; background: #e2e8f0; padding: 2px 6px; border-radius: 4px; font-family: monospace; }
          .footer { margin-top: 40px; border-top: 1px solid #e2e8f0; padding-top: 16px; font-size: 11px; color: #64748b; }
        </style>""")
        html_parts.append("</head>")
        html_parts.append("<body>")

        disclaimer = doc.unsubmitted_disclaimer_bn if is_bn else doc.unsubmitted_disclaimer_en
        html_parts.append(f"<div class='disclaimer'>⚠️ {disclaimer}</div>")
        html_parts.append(f"<h1>{doc.title}</h1>")
        html_parts.append(
            f"<p><small>Date: {doc.created_at} | Status: {doc.lifecycle_state.upper()}</small></p>"
        )

        for sec in doc.sections:
            title = sec.section_title_bn if is_bn else sec.section_title_en
            html_parts.append(f"<h2>{title}</h2><ul>")
            for sent in sec.sentences:
                badge = (
                    f" <span class='tag'>{sent.statement_type}</span>"
                    if sent.statement_type != "reviewed_fact"
                    else ""
                )
                citation = (
                    f" <em>({sent.supporting_citation})</em>" if sent.supporting_citation else ""
                )
                html_parts.append(f"<li>{sent.text}{citation}{badge}</li>")
            html_parts.append("</ul>")

        html_parts.append(
            "<div class='footer'>ClaimCraft BD — Deterministic Consumer Resolution Copilot.</div>"
        )
        html_parts.append("</body></html>")

        content_str = "\n".join(html_parts)
        content_hash = hashlib.sha256(content_str.encode("utf-8")).hexdigest()

        return CaseExportOut(
            export_id=uuid.uuid4(),
            case_id=doc.case_id,
            format="html",
            document_title=doc.title,
            content=content_str,
            sha256_hash=content_hash,
            is_filed=False,
            is_sent=False,
            created_at=datetime.date.today().isoformat(),
        )

    @classmethod
    def apply_raster_redaction(
        cls,
        image_bytes: bytes,
        bounding_boxes: list[dict[str, int]],
    ) -> bytes:
        """T35 Invariant: True raster redaction permanently replaces sensitive pixels

        with solid black blocks and strips all EXIF metadata.
        Cannot be reversed via CSS removal or alpha channel manipulation.
        """
        img = Image.open(io.BytesIO(image_bytes))
        # Convert to RGB to ensure alpha manipulation cannot unmask pixels
        img = img.convert("RGB")
        width, height = img.size

        # Create drawing context
        from PIL import ImageDraw

        draw = ImageDraw.Draw(img)

        for box in bounding_boxes:
            x = max(0, box.get("x", 0))
            y = max(0, box.get("y", 0))
            w = max(1, box.get("w", 1))
            h = max(1, box.get("h", 1))

            x2 = min(width, x + w)
            y2 = min(height, y + h)

            # Draw permanent opaque black rectangle directly overwriting pixel buffer
            draw.rectangle([x, y, x2, y2], fill=(0, 0, 0))

        # Output stripped bytes without metadata
        out_buf = io.BytesIO()
        img.save(out_buf, format="PNG", optimize=True)
        return out_buf.getvalue()
