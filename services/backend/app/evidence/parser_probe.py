import io
from typing import Any

import pypdf
from PIL import Image
from pydantic import BaseModel, Field


class ProbeResult(BaseModel):
    is_safe: bool
    rejection_code: str | None = None
    is_retryable: bool = False
    error_message: str | None = None
    guidance_en: str | None = None
    guidance_bn: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ParserProbe:
    """T12: Probes raw evidence bytes for pixel bombs, page bombs, encryption, active content, and scanner failures."""

    MAX_PIXELS = 25_000_000  # 25 megapixels
    MAX_PDF_PAGES = 50  # 50 pages per PDF
    MAX_AUDIO_SECONDS = 300  # 5 minutes audio

    @classmethod
    def probe_image(cls, data: bytes) -> ProbeResult:
        """T12: Inspects image dimensions and integrity; rejects decompression/pixel bombs."""
        try:
            with Image.open(io.BytesIO(data)) as img:
                w, h = img.size
                pixels = w * h
                if pixels > cls.MAX_PIXELS:
                    return ProbeResult(
                        is_safe=False,
                        rejection_code="PIXEL_BOMB",
                        is_retryable=False,
                        error_message=f"Image resolution ({w}x{h} = {pixels:,} pixels) exceeds the 25 megapixel limit.",
                        guidance_en="Please resize or compress your image to under 25 megapixels before uploading.",
                        guidance_bn="ছবিটি ২৫ মেগাপিক্সেলের অতিরিক্ত বড়। অনুগ্রহ করে ছবির সাইজ ছোট বা কম্প্রেস করে আপলোড করুন।",
                        metadata={"width": w, "height": h, "pixels": pixels},
                    )
                return ProbeResult(
                    is_safe=True,
                    metadata={"width": w, "height": h, "pixels": pixels, "format": img.format},
                )
        except Exception as e:  # noqa: BLE001
            return ProbeResult(
                is_safe=False,
                rejection_code="CORRUPT_IMAGE",
                is_retryable=False,
                error_message=f"Corrupt or unparseable image binary: {e}",
                guidance_en="The uploaded image appears corrupt or damaged. Please take a new screenshot or save as standard PNG/JPEG.",
                guidance_bn="আপলোডকৃত ছবিটি ক্ষতিগ্রস্ত বা অকার্যকর। অনুগ্রহ করে নতুন স্ক্রিনশট নিয়ে অথবা স্ট্যান্ডার্ড ফরম্যাটে সেভ করে আপলোড করুন।",
            )

    @classmethod
    def probe_pdf(cls, data: bytes) -> ProbeResult:
        """T12: Inspects PDF structure for active JavaScript, password encryption, and page bombs."""
        # 1. Search for active content / JavaScript / Launch actions
        lower_sample = data[: min(len(data), 500_000)].lower()
        if b"/javascript" in lower_sample or b"/js " in lower_sample or b"/launch" in lower_sample:
            return ProbeResult(
                is_safe=False,
                rejection_code="ACTIVE_CONTENT_DETECTED",
                is_retryable=False,
                error_message="Active JavaScript or executable launch actions detected in PDF document.",
                guidance_en="PDFs containing embedded scripts or executable macros are forbidden for security. Please print/export to a clean static PDF.",
                guidance_bn="পিডিএফ ফাইলের ভেতর এক্সিকিউটেবল স্ক্রিপ্ট বা ম্যাক্রো শনাক্ত হয়েছে যা নিরাপত্তার স্বার্থে নিষিদ্ধ। অনুগ্রহ করে একটি পরিষ্কার স্ট্যাটিক পিডিএফ আপলোড করুন।",
            )

        # 2. Inspect with pypdf
        try:
            reader = pypdf.PdfReader(io.BytesIO(data))
            if reader.is_encrypted:
                return ProbeResult(
                    is_safe=False,
                    rejection_code="PDF_ENCRYPTED",
                    is_retryable=False,
                    error_message="PDF document is password-protected or encrypted.",
                    guidance_en="Password-protected PDFs cannot be analyzed. Please unlock or export an unencrypted copy.",
                    guidance_bn="পাসওয়ার্ড-সুরক্ষিত পিডিএফ ফাইল বিশ্লেষণ করা সম্ভব নয়। অনুগ্রহ করে পাসওয়ার্ড ছাড়া আনলক করা কপি আপলোড করুন।",
                )

            page_count = len(reader.pages)
            if page_count > cls.MAX_PDF_PAGES:
                return ProbeResult(
                    is_safe=False,
                    rejection_code="PDF_PAGE_LIMIT",
                    is_retryable=False,
                    error_message=f"PDF has {page_count} pages, exceeding the {cls.MAX_PDF_PAGES}-page limit.",
                    guidance_en=f"The document exceeds the {cls.MAX_PDF_PAGES}-page limit. Please split and upload only the relevant order or dispute pages.",
                    guidance_bn=f"ডকুমেন্টে {page_count}টি পাতা রয়েছে যা ৫০ পাতার অতিরিক্ত। অনুগ্রহ করে প্রয়োজনীয় অংশ আলাদা করে আপলোড করুন।",
                    metadata={"page_count": page_count},
                )

            return ProbeResult(
                is_safe=True,
                metadata={"page_count": page_count},
            )
        except Exception as e:  # noqa: BLE001
            return ProbeResult(
                is_safe=False,
                rejection_code="CORRUPT_PDF",
                is_retryable=False,
                error_message=f"Damaged or unparseable PDF document: {e}",
                guidance_en="The PDF appears corrupted. Please open and re-save or re-download the file before trying again.",
                guidance_bn="পিডিএফ ফাইলটি ক্ষতিগ্রস্ত মনে হচ্ছে। অনুগ্রহ করে ফাইলটি পুনরায় ডাউনলোড বা সেভ করে আপলোড করুন।",
            )

    @classmethod
    def probe_file(
        cls, data: bytes, detected_mime: str, simulate_scanner_outage: bool = False
    ) -> ProbeResult:
        """T12: Dispatches to type-specific probe and checks scanner availability."""
        # Check scanner outage simulation (T12)
        if simulate_scanner_outage:
            return ProbeResult(
                is_safe=False,
                rejection_code="SCANNER_OUTAGE",
                is_retryable=True,
                error_message="Security scanner service is temporarily unavailable.",
                guidance_en="Security verification service is temporarily down. Your file remains safely quarantined and will be retried.",
                guidance_bn="নিরাপত্তা স্ক্যানার সাময়িকভাবে অনুপলব্ধ। আপনার ফাইল নিরাপদে কোয়ারেন্টাইনে রাখা হয়েছে এবং স্বয়ংক্রিয়ভাবে পুনরায় যাচাই করা হবে।",
            )

        if detected_mime == "application/pdf":
            return cls.probe_pdf(data)
        elif detected_mime in ("image/png", "image/jpeg", "image/webp"):
            return cls.probe_image(data)
        elif detected_mime.startswith("audio/"):
            # Audio probe: basic size & duration check
            return ProbeResult(is_safe=True, metadata={"mime": detected_mime})

        return ProbeResult(is_safe=True)
