"""Bounded private PDF previews for source highlighting."""
import io
import threading

import pypdfium2 as pdfium

_PDFIUM_LOCK = threading.Lock()


def render_page(data: bytes, page_number: int, scale_cap: float = 1.6, max_edge: int = 1500) -> bytes:
    # PDFium is not thread safe; keep its document/page/bitmap lifetime serialized.
    with _PDFIUM_LOCK, pdfium.PdfDocument(data) as document:
        if page_number < 1 or page_number > len(document):
            raise ValueError('Page not found')
        page = document[page_number-1]
        try:
            width, height = page.get_size()
            if width <= 0 or height <= 0:
                raise ValueError('Invalid page')
            scale = min(scale_cap, max_edge/max(width, height))
            bitmap = page.render(scale=scale)
            try:
                image = bitmap.to_pil()
                output = io.BytesIO()
                image.save(output, format='PNG')
                return output.getvalue()
            finally:
                bitmap.close()
        finally:
            page.close()
