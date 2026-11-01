from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.merchants.schemas import MerchantIntelligenceOut, MerchantRadarResponse
from app.merchants.service import MerchantIntelligenceService

router = APIRouter(prefix="/v1/merchants", tags=["Merchant Intelligence & Scam Radar"])


@router.get("/intelligence", response_model=MerchantIntelligenceOut)
async def get_merchant_intelligence(
    query: str = Query(..., min_length=1, description="Merchant, shop, or Facebook page name"),
    db: AsyncSession = Depends(get_db_session),
):
    """Searches prior consumer complaints, risk assessment, fraud patterns, and victim counts."""
    return await MerchantIntelligenceService.get_intelligence(query, db)


@router.get("/radar", response_model=MerchantRadarResponse)
async def get_scam_radar_leaderboard(
    db: AsyncSession = Depends(get_db_session),
):
    """Returns community-indexed repeat offender watchlist and dispute statistics."""
    return await MerchantIntelligenceService.get_radar_leaderboard(db)

