from pydantic import BaseModel, Field


class MerchantComplaintSummary(BaseModel):
    id: str
    date: str
    issue_type: str
    amount_bdt: float
    status: str
    summary_preview: str


class MerchantIntelligenceOut(BaseModel):
    merchant_name: str
    risk_level: str  # HIGH RISK, MODERATE, VERIFIED / LOW
    complaint_count: int
    total_disputed_bdt: float
    common_patterns: list[str]
    victim_count: int
    is_known_offender: bool
    platform: str  # Facebook F-Commerce, Marketplace, Website, Physical Store
    recommended_action: str
    recent_complaints: list[MerchantComplaintSummary] = Field(default_factory=list)


class MerchantRadarLeaderboardItem(BaseModel):
    merchant_name: str
    platform: str
    category: str
    complaint_count: int
    total_disputed_bdt: float
    risk_level: str
    primary_allegation: str
    last_reported_date: str


class MerchantRadarResponse(BaseModel):
    total_tracked_merchants: int
    total_complaints_indexed: int
    total_disputed_amount_bdt: float
    top_offenders: list[MerchantRadarLeaderboardItem]
