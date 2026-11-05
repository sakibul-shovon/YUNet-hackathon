"""Read real files. Never turn filenames or binary metadata into recognized text."""
import json
from typing import Any

import httpx
from pydantic import ValidationError
from starlette.concurrency import run_in_threadpool

from app.core.config import settings
from app.evidence.document_parser import DocumentParser
from app.evidence.storage import get_storage_backend
from app.operations.understanding import provider_receipt
from app.operations.visual_reader import (
    MAX_OCR_PAGES,
    READER_VERSION,
    prepare_image,
    read_visual,
    render_pdf_page,
    vision_available,
)


def pdf_lines(parsed) -> list[dict]:
    """Group native word coordinates into source lines, retaining real page positions."""
    groups: dict[tuple[int, int], list] = {}
    for region in parsed.regions:
        groups.setdefault((region.page_number, round(region.normalized_box[1]*100)), []).append(region)
    lines = []
    for (page, _), regions in groups.items():
        regions.sort(key=lambda region: region.normalized_box[0])
        lines.append({'text': ' '.join(region.text for region in regions), 'page': page,
                      'box': [min(r.normalized_box[0] for r in regions), min(r.normalized_box[1] for r in regions),
                              max(r.normalized_box[2] for r in regions), max(r.normalized_box[3] for r in regions)]})
    return lines[:240]


async def read_evidence(item, external_consent: bool) -> dict[str, Any]:
    mime = item.detected_mime_type or item.declared_mime_type
    base = {'id': str(item.id), 'filename': item.original_filename, 'mime_type': mime,
            'sha256': item.sha256_hash, 'text': '', 'lines': [], 'model_executed': False,
            'method': 'manual_required', 'reason': 'reader_unavailable', 'reader_version': READER_VERSION}
    try:
        data = await run_in_threadpool(get_storage_backend().read_accepted, item.accepted_path)
        if mime == 'application/pdf':
            parsed = await run_in_threadpool(DocumentParser.parse_pdf_bytes, item.id, data)
            native = pdf_lines(parsed)
            native_pages = {line['page'] for line in native}
            missing = [page for page in range(1, parsed.page_count+1) if page not in native_pages]
            if not missing:
                return {**base, 'method': 'native_pdf', 'reason': None,
                        'text': parsed.full_text[:18000], 'lines': native,
                        'page_count': parsed.page_count, 'pages_read': sorted(native_pages)}
            partial = {**base, 'method': 'native_pdf' if native else 'manual_required',
                       'text': parsed.full_text[:18000], 'lines': native, 'partial': True,
                       'page_count': parsed.page_count, 'pages_read': sorted(native_pages), 'unread_pages': missing}
            if not external_consent or not vision_available():
                return {**partial, 'reason': 'external_consent_required' if not external_consent else 'reader_unavailable'}
            lines, receipts = list(native), []
            method, model, failure = None, None, None
            for page in missing[:MAX_OCR_PAGES]:
                try:
                    image = await run_in_threadpool(render_pdf_page, data, page-1)
                    prepared, mapping = await run_in_threadpool(prepare_image, image)
                    reading = await read_visual(prepared, mapping, page)
                    lines.extend(reading['lines'])
                    receipts.append({**reading['execution_receipt'], 'page': page})
                    method, model = reading['method'], reading['model']
                    # An acknowledged blank page is read, without inventing its content.
                    native_pages.add(page)
                except httpx.HTTPStatusError as error:
                    failure = {'reason': 'provider_unavailable', 'provider_status': error.response.status_code}
                    break
                except (httpx.HTTPError, ValidationError, ValueError, KeyError, IndexError, OSError, TypeError):
                    failure = {'reason': 'reader_unavailable'}
                    break
            unread = [page for page in range(1, parsed.page_count+1) if page not in native_pages]
            lines.sort(key=lambda line: line['page'])
            return {**partial, 'method': method.replace('_vision', '_pdf_vision') if method else partial['method'],
                    'model': model, 'model_executed': bool(receipts),
                    'execution_receipt': receipts[0] if receipts else None, 'execution_receipts': receipts,
                    'text': '\n'.join(line['text'] for line in lines)[:18000], 'lines': lines,
                    'partial': bool(unread), 'pages_read': sorted(native_pages), 'unread_pages': unread,
                    'reason': 'pdf_page_limit' if unread else None, **(failure or {})}
        if not external_consent:
            return {**base, 'reason': 'external_consent_required'}
        if mime.startswith('image/') and vision_available():
            if len(data) > 8*1024*1024:
                return {**base, 'reason': 'image_reader_size_limit'}
            prepared, mapping = await run_in_threadpool(prepare_image, data)
            return {**base, **await read_visual(prepared, mapping)}
        if mime.startswith('audio/') and settings.GROQ_API_KEY:
            if len(data) > 20*1024*1024:
                return {**base, 'reason': 'audio_reader_size_limit'}
            async with httpx.AsyncClient(timeout=55) as client:
                response = await client.post('https://api.groq.com/openai/v1/audio/transcriptions',
                    headers={'Authorization': f'Bearer {settings.GROQ_API_KEY}'},
                    files={'file': (item.original_filename, data, mime)},
                    data={'model': settings.GROQ_TRANSCRIBE_MODEL, 'response_format': 'verbose_json',
                          'timestamp_granularities[]': 'segment', 'temperature': '0',
                          'prompt': 'Ebarki. Bangladesh consumer records. Currency words: taka, poisha. Preserve spoken details; do not infer missing facts.'})
            response.raise_for_status()
            result = response.json()
            lines = []
            for segment in result.get('segments', [])[:160]:
                start, end = float(segment['start']), float(segment['end'])
                if 0 <= start < end and isinstance(segment.get('text'), str):
                    lines.append({'text': segment['text'][:1600], 'start': start, 'end': end})
            return {**base, 'method': 'groq_transcription', 'model_executed': True, 'reason': None,
                    'model': settings.GROQ_TRANSCRIBE_MODEL, 'lines': lines,
                    'execution_receipt': provider_receipt(response, settings.GROQ_TRANSCRIBE_MODEL),
                    'text': str(result.get('text', ''))[:18000]}
    except httpx.HTTPStatusError as error:
        return {**base, 'reason': 'provider_unavailable', 'provider_status': error.response.status_code}
    except (httpx.HTTPError, ValidationError, ValueError, KeyError, IndexError, OSError, TypeError, json.JSONDecodeError):
        return {**base, 'reason': 'reader_unavailable'}
    return base
