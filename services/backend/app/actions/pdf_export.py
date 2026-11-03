"""Private, searchable preparation PDFs with embedded Bangla shaping fonts."""
import io
import re
from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from app.actions.document_ast import EditableDocumentAST

FONT_DIR = Path(__file__).parent / "fonts"


def render_pdf(doc: EditableDocumentAST) -> bytes:
    for name, filename in [("EbarkiText", "EbarkiText.ttf"), ("EbarkiBangla", "EbarkiBangla.ttf")]:
        if name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / filename), shapable=True))
    bn = doc.locale == "bn"
    body = ParagraphStyle("body", fontName="EbarkiBangla" if bn else "EbarkiText",
                          fontSize=10.5, leading=20 if bn else 16, spaceAfter=11,
                          textColor=colors.HexColor("#20262b"), alignment=TA_LEFT,
                          shaping=True, splitLongWords=True)
    heading = ParagraphStyle("heading", parent=body, fontSize=14, leading=25, spaceBefore=21,
                             spaceAfter=12, keepWithNext=True)
    title = ParagraphStyle("title", parent=body, fontSize=21, leading=33, spaceAfter=18)
    small = ParagraphStyle("small", parent=body, fontSize=8, leading=15,
                           textColor=colors.HexColor("#56616a"))

    def markup(text):
        # Preserve complete Bangla runs for HarfBuzz; use Latin font for English identifiers.
        runs = re.split(r"([^\u0980-\u09ff\u200c\u200d]+)", str(text))
        parts = []
        for part in runs:
            if not part:
                continue
            font = "EbarkiBangla" if re.search(r"[\u0980-\u09ff]", part) else "EbarkiText"
            parts.append(f'<font name="{font}">{escape(part)}</font>')
        return "".join(parts).replace("\n", "<br/>")

    story = [Paragraph(markup("EBARKI / " + ("খসড়া" if bn else "PREPARATION COPY")), small), Spacer(1, 16),
             Paragraph(markup(doc.title), title),
             Paragraph(markup(doc.unsubmitted_disclaimer_bn if bn else doc.unsubmitted_disclaimer_en), body),
             Paragraph(markup(f'{doc.created_at} · {"সংস্করণ" if bn else "Revision"} {doc.revision}'), small)]
    for section in doc.sections:
        story.append(Paragraph(markup(section.section_title_bn if bn else section.section_title_en), heading))
        for sentence in section.sentences:
            story.append(Paragraph(markup(sentence.text), body))
            if sentence.supporting_citation:
                story.append(Paragraph(markup(("সূত্র: " if bn else "Reference: ") + sentence.supporting_citation), small))
    if doc.evidence_index:
        story.append(Paragraph(markup("নথির তালিকা" if bn else "Evidence index"), heading))
        for index, evidence in enumerate(doc.evidence_index, 1):
            story.append(Paragraph(markup(f'{index}. {evidence["filename"]}'), body))
    story.append(Paragraph(markup("জমা দেওয়ার আগে মিলিয়ে নিন" if bn else "Before submitting"), heading))
    for index, item in enumerate(doc.preparation_checklist, 1):
        story.append(Paragraph(markup(f'{index}. {item}'), body))
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=52, leftMargin=52,
                           topMargin=45, bottomMargin=48, title=doc.title, author="Ebarki")

    def footer(canvas, document):
        canvas.setStrokeColor(colors.HexColor("#d8d8d0"))
        canvas.line(52, 37, A4[0]-52, 37)
        canvas.setFont("EbarkiText", 7)
        canvas.setFillColor(colors.HexColor("#56616a"))
        canvas.drawString(52, 25, "Ebarki · Preparation copy · Not submitted")
        canvas.drawRightString(A4[0]-52, 25, str(document.page))

    pdf.build(story, onFirstPage=footer, onLaterPages=footer)
    return buffer.getvalue()
