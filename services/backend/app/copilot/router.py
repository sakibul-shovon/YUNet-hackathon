import json

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.copilot.schemas import CopilotChatRequest, CopilotChatResponse
from app.copilot.service import CopilotService
from app.core.database import get_db_session
from app.core.security import get_current_principal
from app.facts.service import FactService
from app.identity.models import Principal

router = APIRouter(prefix="/v1/copilot", tags=["AI Consumer Resolution Copilot"])


@router.post("/chat", response_model=CopilotChatResponse)
async def chat_with_copilot(req: CopilotChatRequest, principal: Principal = Depends(get_current_principal), db: AsyncSession = Depends(get_db_session)):
    """Conversational AI Copilot grounded in Bangladesh Consumer Law."""
    if req.case_id:
        case = await FactService.get_authorized_case(req.case_id, principal, db)
        if case.consent_status == "withdrawn":
            from fastapi import HTTPException
            raise HTTPException(403, "Processing consent was withdrawn")
        req.case_context = json.dumps({"title": case.title, "story": case.story_narrative}, ensure_ascii=False)
    return await CopilotService.chat(req)

