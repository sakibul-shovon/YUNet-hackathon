import datetime
import io
import uuid

from PIL import Image

from app.multimodal.vision.schemas import (
    ScreenshotAnalysisResult,
)


class ScreenshotAdapter:
    """T23: VLM screenshot layout adapter, bubble-role uncertainty, and OCR disagreement reconciliation."""

    @classmethod
    def analyze_image_bytes(
        cls,
        evidence_id: uuid.UUID,
        case_id: uuid.UUID,
        image_bytes: bytes,
        ocr_extracted_text: str = "",
    ) -> ScreenshotAnalysisResult:
        """T23: Inspects screenshot layout, detects theme, preserves bubble uncertainty, and flags OCR disagreements."""
        now = datetime.datetime.now(datetime.UTC)

        # 1. Load image and detect dark vs light theme
        theme = "light"
        width = 800
        height = 1000
        try:
            with Image.open(io.BytesIO(image_bytes)) as img:
                width, height = img.size
                # Sample corners to determine background luminance
                img_rgb = img.convert("RGB")
                w_mid = width // 2
                h_mid = height // 2
                sample_pixels = [
                    img_rgb.getpixel((10, 10)),
                    img_rgb.getpixel((width - 10, 10)),
                    img_rgb.getpixel((10, height - 10)),
                    img_rgb.getpixel((width - 10, height - 10)),
                    img_rgb.getpixel((w_mid, h_mid)),
                ]
                avg_lum = sum(
                    (r * 0.299 + g * 0.587 + b * 0.114) for r, g, b in sample_pixels
                ) / len(sample_pixels)
                if avg_lum < 110:
                    theme = "dark"
                elif avg_lum > 180:
                    theme = "light"
                else:
                    theme = "mixed"
        except (OSError, ValueError):
            theme = "light"

        # A layout/text model did not execute here. Hints are user input, never OCR.
        # No speaker attribution, coordinates, monetary facts or disagreements can
        # be established from image metadata or a supplied hint.
        return ScreenshotAnalysisResult(
            evidence_id=evidence_id, case_id=case_id, detected_layout="unstructured",
            theme=theme, authenticity_guarantee=False, bubbles=[], proposed_facts=[],
            ocr_disagreements=[], analyzed_at=now,
            disclaimer_en="Ebarki inspected image colors only. No OCR or layout model executed. Read records in Evidence story, or add a manual transcript.",
            disclaimer_bn="Ebarki শুধু ছবির রং দেখেছে। OCR বা লেআউট মডেল চলেনি। সূত্রসহ ঘটনা অংশে নথি পড়ুন বা নিজে লেখা যোগ করুন।",
        )
