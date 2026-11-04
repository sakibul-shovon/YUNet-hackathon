"""Build genuine fictional OCR/audio fixtures; no user data or provider credentials."""
import io
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'services' / 'backend'))

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from app.operations.page_preview import render_page

target = ROOT / 'demo' / 'specs' / 'samples'
target.mkdir(parents=True, exist_ok=True)
font = ROOT / 'services' / 'backend' / 'app' / 'actions' / 'fonts' / 'EbarkiBangla.ttf'
pdfmetrics.registerFont(TTFont('EbarkiQABangla', str(font), shapable=True))
style = ParagraphStyle('qa', fontName='Helvetica', fontSize=16, leading=29,
                       textColor=colors.HexColor('#202b2e'), spaceAfter=12, shaping=True)
bn = ParagraphStyle('bn', parent=style, fontName='EbarkiQABangla', fontSize=18, leading=35)
buffer = io.BytesIO()
document = SimpleDocTemplate(buffer, pagesize=(500, 650), topMargin=45, bottomMargin=40,
                              leftMargin=45, rightMargin=45, title='Ebarki QA fictional receipt', author='Ebarki')
document.build([
    Paragraph('Ebarki / TEST RECEIPT', style),
    Paragraph('FICTIONAL DATA. NO REAL PURCHASE.', ParagraphStyle('small', parent=style, fontSize=10)),
    Spacer(1, 20), Paragraph('নমুনা ইলেকট্রনিকস', bn),
    Paragraph('Date: 2026-10-20', style), Paragraph('Reference: EBARKI-QA-5000', style),
    Spacer(1, 18), Paragraph('Paid BDT 5,000', style),
    Paragraph('পরিশোধ করা টাকা <font name="Helvetica">5,000</font>', bn),
    Spacer(1, 24), Paragraph('A clearly labeled test record for Ebarki.', ParagraphStyle('note', parent=style, fontSize=11)),
])
data = buffer.getvalue()
(target / 'ebarki_qa_receipt.pdf').write_bytes(data)
(target / 'ebarki_qa_receipt.png').write_bytes(render_page(data, 1))
if sys.platform == 'win32':
    wave = str(target / 'ebarki_qa_voice.wav').replace("'", "''")
    command = ("Add-Type -AssemblyName System.Speech; "
               "$speech = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
               f"$speech.SetOutputToWaveFile('{wave}'); "
               "$speech.Speak('This is an Ebarki test. I paid five thousand five hundred taka for a phone. The phone has not arrived.'); "
               "$speech.Dispose()")
    subprocess.run(['powershell', '-NoProfile', '-Command', command], check=True,
                   creationflags=subprocess.CREATE_NO_WINDOW, stdout=subprocess.DEVNULL)
print('Built fictional receipt PDF/PNG and local speech WAV (Windows). No provider was called.')
