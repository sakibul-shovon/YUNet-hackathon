import json

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.copilot.schemas import CopilotChatRequest, CopilotChatResponse
from app.copilot.service import CopilotService
from app.core.database import get_db_session
from app.core.security import get_current_principal
from app.facts.service import FactService
from app.identity.models import Principal
from app.operations.connected_records import has_external_consent

router = APIRouter(prefix="/v1/copilot", tags=["AI Consumer Resolution Copilot"])


@router.post("/chat", response_model=CopilotChatResponse)
async def chat_with_copilot(req: CopilotChatRequest, principal: Principal = Depends(get_current_principal), db: AsyncSession = Depends(get_db_session)):
    """Conversational AI Copilot grounded in Bangladesh Consumer Law."""
    if req.case_id:
        case = await FactService.get_authorized_case(req.case_id, principal, db)
        if case.consent_status == "withdrawn":
            from fastapi import HTTPException
            raise HTTPException(403, "Processing consent was withdrawn")
        if case.principal_id != principal.id:
            from fastapi import HTTPException
            raise HTTPException(404, 'Case not found')
        if not await has_external_consent(case, principal, db):
            return CopilotChatResponse(mode='consent_required',
                reply_en='Enable AI processing for this case to ask about its information. You can still inspect records, review facts, and explore the source-linked next steps.',
                reply_bn='এই অভিযোগের তথ্য নিয়ে AI-এর সাহায্য পেতে আগে অনুমতি দিন। এর মধ্যেও নথি দেখা, তথ্য মিলিয়ে নেওয়া ও সূত্রসহ করণীয় দেখার কাজ করতে পারেন।')
        req.case_context = json.dumps({"title": case.title, "story": case.story_narrative}, ensure_ascii=False)
    return await CopilotService.chat(req)

