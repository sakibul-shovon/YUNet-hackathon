from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ProvisionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    citation_handle: str
    source_id: str
    provision_path: str
    section_number: str
    section_bn: str
    title_en: str
    title_bn: str
    parent_path: str | None = None
    document_type: str
    canonical_text_en: str
    canonical_text_bn: str
    qualifications_and_exceptions: list[str] = Field(default_factory=list)
    key_definitions: dict[str, str] = Field(default_factory=dict)
    penalties: dict[str, Any] | None = None
    aliases: list[str] = Field(default_factory=list)
    effective_from: str | None = None
    effective_to: str | None = None
    parent_provision: dict[str, Any] | None = None


class ProvisionLookupResult(BaseModel):
    query: str
    normalized_query: str
    match_found: bool
    provision: ProvisionOut | None = None
    preserves_qualification: bool = True
    context_note_en: str = "Official statutory reference verified against enacted gazette."
    context_note_bn: str = "গেজেটভুক্ত অফিসিয়াল সংবিধিবদ্ধ বিধানের সাথে যাচাইকৃত।"


class ProvisionTreeItem(BaseModel):
    provision_path: str
    citation_handle: str
    title_en: str
    title_bn: str
    section_number: str
    children: list["ProvisionTreeItem"] = Field(default_factory=list)


class HybridSearchRequest(BaseModel):
    query: str
    allowed_ids: list[str] | None = None
    date_context: str | None = None
    top_k: int = 5
    dense_enabled: bool = True
    lexical_enabled: bool = True


class CitationValidationRequest(BaseModel):
    citation_handles: list[str]
    date_context: str | None = None
    allowed_source_ids: list[str] | None = None


class CitationValidationResponse(BaseModel):
    is_valid: bool
    valid_citations: list[str]
    invalid_citations: list[dict[str, Any]] = Field(default_factory=list)
