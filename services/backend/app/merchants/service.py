"""Public merchant boundary: private disputes are never a public dataset."""
from sqlalchemy.ext.asyncio import AsyncSession

from app.merchants.schemas import MerchantIntelligenceOut, MerchantRadarResponse

# A future public dataset needs sharing consent, moderation and provenance.
KNOWN_OFFENDER_REGISTRY: dict = {}


class MerchantIntelligenceService:
    @classmethod
    async def get_intelligence(cls, merchant_name: str, db: AsyncSession) -> MerchantIntelligenceOut:
        return MerchantIntelligenceOut(
            merchant_name=merchant_name or 'Unknown merchant', risk_level='INSUFFICIENT DATA',
            complaint_count=0, total_disputed_bdt=0, victim_count=0, is_known_offender=False,
            common_patterns=[], platform='Not established', recent_complaints=[],
            recommended_action='Ebarki has no reviewed public reports for this search. Private cases are not published here.',
        )

    @classmethod
    async def get_radar_leaderboard(cls, db: AsyncSession) -> MerchantRadarResponse:
        return MerchantRadarResponse(total_tracked_merchants=0, total_complaints_indexed=0,
                                     total_disputed_amount_bdt=0, top_offenders=[])
