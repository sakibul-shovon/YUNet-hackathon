from fastapi import APIRouter

from app.copilot.schemas import CopilotChatRequest, CopilotChatResponse
from app.copilot.service import CopilotService

router = APIRouter(prefix="/v1/copilot", tags=["AI Consumer Resolution Copilot"])


@router.post("/chat", response_model=CopilotChatResponse)
async def chat_with_copilot(req: CopilotChatRequest):
    """Conversational AI Copilot grounded in Bangladesh Consumer Law."""
    return await CopilotService.chat(req)

