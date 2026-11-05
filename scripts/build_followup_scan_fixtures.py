"""Additional Ebarki image-only Bangla and hybrid PDF fixtures, not real records."""
import hashlib
import io
import json
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT/'docs/qa/fixtures'
OUT = FIX/'followup'
OUT.mkdir(exist_ok=True)
buffer = io.BytesIO()
document = canvas.Canvas(buffer, pagesize=(600, 780))
document.setTitle('Ebarki FICTIONAL image-only QA')
document.drawImage(ImageReader(str(FIX/'বাংলা রসিদ.png')), 0, 0, width=600, height=780)
document.showPage()
document.save()
scan = buffer.getvalue()
assert not PdfReader(io.BytesIO(scan)).pages[0].extract_text()
(OUT/'Bangla scan.pdf').write_bytes(scan)
writer = PdfWriter()
writer.append(PdfReader(FIX/'receipt text.pdf'))
writer.append(PdfReader(io.BytesIO(scan)))
with (OUT/'Native and Bangla scan.pdf').open('wb') as stream:
    writer.write(stream)
manifest = {'product': 'Ebarki', 'classification': 'FICTIONAL QA ONLY; no real person or transaction',
    'files': {}}
for name in ['Bangla scan.pdf', 'Native and Bangla scan.pdf']:
    data = (OUT/name).read_bytes()
    manifest['files'][name] = {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data),
        'page_count': len(PdfReader(io.BytesIO(data)).pages),
        'scan_page': 2 if name.startswith('Native') else 1,
        'merchant': 'কাল্পনিক পদ্মা টেস্ট শপ', 'amount_minor_units': 700000,
        'reference': 'PADMA-QA-BN24', 'date': '2026-10-24',
        'native_page_1': 'Fictional Padma Test Shop; PADMA-QA-A24; BDT 7,000.00' if name.startswith('Native') else None,
        'note': 'The two representations are not automatically treated as separate payments; explicit review is required.'}
(OUT/'GROUND_TRUTH.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
print('Created two genuine fictional PDF fixtures with page-aware ground truth.')
