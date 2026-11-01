import datetime
import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ChatBubbleProposal(BaseModel):
    bubble_id: str
    text: str
    speaker_role: str = "ambiguous"  # 'consumer', 'counterparty_merchant', 'ambiguous'
    speaker_role_confidence: float = 0.8
    timestamp_text: str | None = None
    normalized_box: list[float] | None = None


class OCRDisagreement(BaseModel):
    field_name: str
    ocr_detected_value: Any
    vlm_detected_value: Any
    ocr_confidence: float
    vlm_confidence: float
    resolution_status: str = "requires_user_review"  # never auto-resolved with fake confidence
    guidance_en: str
    guidance_bn: str


class ScreenshotAnalysisResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    evidence_id: uuid.UUID
    case_id: uuid.UUID
    detected_layout: str  # 'chat_conversation', 'payment_receipt', 'order_status', 'unstructured'
    theme: str  # 'light', 'dark', 'mixed'
    authenticity_guarantee: bool = (
        False  # T23 Invariant: Always False, visually plausible receipt never certified authentic
    )
    bubbles: list[ChatBubbleProposal] = Field(default_factory=list)
    proposed_facts: list[dict[str, Any]] = Field(default_factory=list)
    ocr_disagreements: list[OCRDisagreement] = Field(default_factory=list)
    disclaimer_en: str = "Visually inspected layout proposal. Does not constitute regulatory, banking, or forensic certification of document authenticity."
    disclaimer_bn: str = "দৃশ্যমান লেআউট প্রস্তাবনা। এটি নথির আনুষ্ঠানিক, ব্যাংকিং বা ফরেনসিক সত্যতা প্রমাণ করে না।"
    analyzed_at: datetime.datetime
