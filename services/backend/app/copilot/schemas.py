import uuid

from pydantic import BaseModel, Field


class CopilotChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    locale: str = Field(default="bn")
    case_context: str | None = None
    case_id: uuid.UUID | None = None


class CopilotActionSuggestion(BaseModel):
    id: str
    label_en: str
    label_bn: str
    action_type: str  # navigate, launch_scenario, search_merchant, new_case
    payload: str


class CopilotChatResponse(BaseModel):
    reply_en: str
    reply_bn: str
    relevant_statute: str | None = None
    suggested_actions: list[CopilotActionSuggestion] = Field(default_factory=list)
    mode: str = "workflow_guide"
    citations: list[str] = Field(default_factory=list)

