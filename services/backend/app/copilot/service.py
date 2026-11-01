import logging
import os

from app.copilot.schemas import (
    CopilotActionSuggestion,
    CopilotChatRequest,
    CopilotChatResponse,
)
from app.core.config import settings

logger = logging.getLogger(__name__)


class CopilotService:
    @classmethod
    async def chat(cls, req: CopilotChatRequest) -> CopilotChatResponse:
        user_msg = req.message.strip().lower()

        # 1. Groq LLaMA 3.3 Ultra-Fast Inference Plane
        groq_key = settings.GROQ_API_KEY or os.environ.get("GROQ_API_KEY")
        if groq_key:
            try:
                import httpx

                system_prompt = (
                    "You are ClaimCraft BD Agentic Copilot, the official AI Consumer Resolution Assistant for Bangladesh. "
                    "Your role is to help everyday Bangladeshi consumers resolve disputes with e-commerce platforms (Daraz, Facebook shops), "
                    "MFS providers (bKash, Nagad), and telecom/ISP operators. "
                    "Ground your answers strictly in the Bangladesh Consumers' Right Protection Act, 2009 (CRPA 2009), "
                    "Cabinet Division GRS Guidelines 2015, and Bangladesh Bank MFS Directives 2022. "
                    "Security Invariant (T32): NEVER ask for, accept, or process banking passwords, OTP, PIN, or CVV. "
                    "Tone: Empathetic, assertive, legally precise, and practical. "
                    "Always reply in natural, polite Bengali (বাংলা) with specific statutory sections (e.g. ধারা ৪৫, ধারা ৪১, ধারা ৬০) and actionable next steps."
                )

                async with httpx.AsyncClient(timeout=25.0) as client:
                    groq_resp = await client.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {groq_key}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": settings.GROQ_MODEL or "llama-3.3-70b-versatile",
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": req.message},
                            ],
                            "temperature": 0.3,
                            "max_tokens": 1024,
                        },
                    )

                    if groq_resp.status_code == 200:
                        data = groq_resp.json()
                        reply_content = data["choices"][0]["message"]["content"]
                        return CopilotChatResponse(
                            reply_en=reply_content,
                            reply_bn=reply_content,
                            relevant_statute="ভোক্তা অধিকার সংরক্ষণ আইন, ২০০৯ (ধারা ৪৫, ৪১ ও ৭৬)",
                            suggested_actions=[
                                CopilotActionSuggestion(
                                    id="act-new-case",
                                    label_en="File Guided Case with this Info",
                                    label_bn="এই তথ্যে সরাসরি কেস ফাইল করুন",
                                    action_type="new_case",
                                    payload="/cases/new",
                                ),
                                CopilotActionSuggestion(
                                    id="act-search-radar",
                                    label_en="Check Merchant in Scam Radar",
                                    label_bn="চোরের ড্যাশবোর্ডে বিক্রেতাকে যাচাই করুন",
                                    action_type="search_merchant",
                                    payload="/merchants",
                                ),
                            ],
                        )
            except (httpx.HTTPError, RuntimeError, ValueError, OSError) as exc:
                logger.warning("Groq live copilot call failed, falling back to local engine: %s", exc)

        # 2. Check for Gemini API key
        gemini_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")

        if gemini_key:
            try:
                import google.generativeai as genai

                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel("gemini-3.8-flash")
                system_prompt = (
                    "You are ClaimCraft BD Copilot, a Bangladesh-first AI consumer resolution assistant. "
                    "Help consumers with disputes under Bangladesh Consumer Rights Protection Act 2009, "
                    "MFS Regulations 2022, BTRC QoS, and Cabinet Division GRS 2015. "
                    "Answer in both English and natural polite Bengali. Always cite specific legal sections and advise on preserving evidence."
                )
                resp = model.generate_content(
                    f"{system_prompt}\n\nUser Message: {req.message}"
                )
                txt = resp.text
                return CopilotChatResponse(
                    reply_en=txt,
                    reply_bn=txt,
                    relevant_statute="Consumers' Right Protection Act, 2009 (Section 45 & 76)",
                    suggested_actions=[
                        CopilotActionSuggestion(
                            id="act-case",
                            label_en="Start Case with this information",
                            label_bn="এই তথ্যে সরাসরি কেস ফাইল করুন",
                            action_type="new_case",
                            payload="/cases/new",
                        ),
                        CopilotActionSuggestion(
                            id="act-radar",
                            label_en="Search Merchant in Scam Radar",
                            label_bn="চোরের ড্যাশবোর্ডে মার্চেন্ট চেক করুন",
                            action_type="search_merchant",
                            payload="/merchants",
                        ),
                    ],
                )
            except (RuntimeError, ValueError, OSError) as exc:
                logger.warning("Gemini live copilot fallback triggered: %s", exc)

        # Expert Grounded Legal Knowledge Engine (Zero-Latency Rule Grounding)
        if any(w in user_msg for w in ["daraz", "online", "facebook", "delivery", "ডেলিভারি", "পণ্য", "ঘড়ি", "অর্ডার", "বিকাশ"]):
            return CopilotChatResponse(
                reply_en=(
                    "Under Section 45 of the Bangladesh Consumers' Right Protection Act, 2009, failing to deliver promised goods "
                    "after taking payment constitutes an official consumer offense. You are entitled to a 100% full refund and administrative remedy. "
                    "Do not panic: preserve your bKash TrxID, order confirmation SMS, and WhatsApp/Messenger chat screenshots. "
                    "ClaimCraft BD can generate your official DNCRP complaint letter instantly."
                ),
                reply_bn=(
                    "ভোক্তা অধিকার সংরক্ষণ আইন, ২০০৯-এর ধারা ৪৫ অনুযায়ী, অগ্রিম টাকা নিয়ে প্রতিশ্রুত পণ্য সরবরাহ না করা একটি শাস্তিযোগ্য অপরাধ। "
                    "আপনি সম্পূর্ণ মূল্য ফেরত (Full Refund) এবং ক্ষতিপূরণ পাওয়ার অধিকারী। "
                    "উদ্বিগ্ন হবেন না: আপনার বিকাশের TrxID, অর্ডারের নিশ্চিতকরণ মেসেজ এবং বিক্রেতার সাথে চ্যাটের স্ক্রিনশট সংগ্রহে রাখুন। "
                    "ক্লেইমক্রাফট বিডি তাৎক্ষণিকভাবে জাতীয় ভোক্তা অধিকার সংরক্ষণ অধিদপ্তরে (DNCRP) দাখিলের উপযোগী দরখাস্ত প্রস্তুত করে দেবে।"
                ),
                relevant_statute="ভোক্তা অধিকার সংরক্ষণ আইন, ২০০৯ (ধারা ৪৫ ও ৭৬)",
                suggested_actions=[
                    CopilotActionSuggestion(
                        id="act-new-case",
                        label_en="Start Guided Non-Delivery Case",
                        label_bn="ডেলিভারি না পাওয়ার কেস খুলুন",
                        action_type="new_case",
                        payload="/cases/new",
                    ),
                    CopilotActionSuggestion(
                        id="act-check-merchant",
                        label_en="Check Merchant in Scam Radar",
                        label_bn="মার্চেন্ট সতর্কতা রাডারে অনুসন্ধান",
                        action_type="search_merchant",
                        payload="/merchants",
                    ),
                ],
            )
        elif any(w in user_msg for w in ["bkash", "nagad", "mfs", "টাকা কেটেছে", "ব্যালেন্স", "পেমেন্ট"]):
            return CopilotChatResponse(
                reply_en=(
                    "Under Bangladesh Bank MFS Regulations 2022, if a payment gateway timeouts or an unauthorized deduction occurs, "
                    "the MFS provider is obligated to initiate auto-reversal within 72 hours. "
                    "First, lodge a formal ticket with bKash/Nagad helpline (16247). If unresolved within 10 working days, "
                    "escalate directly to Bangladesh Bank CIPC."
                ),
                reply_bn=(
                    "বাংলাদেশ ব্যাংক এমএফএস রেগুলেশন ২০২২ অনুযায়ী, পেমেন্ট ফেইলিউর বা ব্যালেন্স কেটে নেওয়ার পর পণ্য না পেলে "
                    "৭২ ঘণ্টার মধ্যে অটো-রিভার্সালের আইনি বাধ্যবাধকতা রয়েছে। "
                    "প্রথমে বিকাশ হেল্পলাইনে (১৬২৪৭) কল করে একটি আনুষ্ঠানিক অভিযোগ টিকিট নম্বর সংগ্রহ করুন। "
                    "১০ কার্যদিবসে সমাধান না হলে বাংলাদেশ ব্যাংকের সিআইপিসি (CIPC) সেলে অভিযোগ দাখিলের আইনি অধিকার আপনার রয়েছে।"
                ),
                relevant_statute="বাংলাদেশ ব্যাংক এমএফএস রেগুলেশনস ২০২২ ও সিআইপিসি ফ্রেমওয়ার্ক",
                suggested_actions=[
                    CopilotActionSuggestion(
                        id="act-mfs-case",
                        label_en="Prepare MFS Provider Notice",
                        label_bn="এমএফএস প্রোভাইডারের লিগ্যাল নোটিশ প্রস্তুত করুন",
                        action_type="new_case",
                        payload="/cases/new",
                    )
                ],
            )
        elif any(w in user_msg for w in ["defect", "broken", "warranty", "ভাঙা", "নষ্ট", "ওয়ারেন্টি"]):
            return CopilotChatResponse(
                reply_en=(
                    "Private store policies like 'Sold goods cannot be returned' (বিক্রিত মাল ফেরত নেওয়া হয় না) are legally invalid "
                    "under Section 41 and 44 of the Consumer Rights Act if the product has latent defects. "
                    "You are entitled to a replacement or refund within the warranty period."
                ),
                reply_bn=(
                    "দোকানের ব্যক্তিগত শর্ত যেমন 'বিক্রিত মাল ফেরত নেওয়া হয় না' ভোক্তা অধিকার সংরক্ষণ আইনের ধারা ৪১ ও ৪৪ অনুযায়ী আইনিভাবে অকার্যকর। "
                    "পণ্য ত্রুটিপূর্ণ হলে বিক্রেতা ওয়ারেন্টির মেয়াদকালে রিপ্লেসমেন্ট দিতে বাধ্য।"
                ),
                relevant_statute="ভোক্তা অধিকার সংরক্ষণ আইন, ২০০৯ (ধারা ৪১ ও ৪৪)",
                suggested_actions=[
                    CopilotActionSuggestion(
                        id="act-defective",
                        label_en="Generate Warranty Claim",
                        label_bn="ওয়ারেন্টি প্রতিস্থাপন দাবি প্রস্তুত করুন",
                        action_type="new_case",
                        payload="/cases/new",
                    )
                ],
            )
        else:
            return CopilotChatResponse(
                reply_en=(
                    "Hello! I am your ClaimCraft Consumer Resolution Copilot. "
                    "Tell me about your consumer issue (e.g. non-delivery, defective goods, unauthorized MFS charges, or insurance denial), "
                    "and I will help you identify your legal rights under Bangladesh law and generate the necessary legal action materials."
                ),
                reply_bn=(
                    "আসসালামু আলাইকুম! আমি আপনার ক্লেইমক্রাফট ভোক্তা অধিকার কো-পাইলট। "
                    "অনলাইন শপ ডেলিভারি না দিলে, বিকাশে টাকা কেটে নিলে, ত্রুটিপূর্ণ পণ্যের ওয়ারেন্টি না দিলে বা যেকোনো গ্রাহক হয়রানি নিয়ে আমাকে জানান। "
                    "আমি আপনাকে সঠিক আইনি ধারা এবং ক্ষতিপূরণের সমাধান প্রস্তুত করে দেব।"
                ),
                relevant_statute="জাতীয় ভোক্তা অধিকার সংরক্ষণ অধিদপ্তর (DNCRP) অভিযোগ প্রক্রিয়া",
                suggested_actions=[
                    CopilotActionSuggestion(
                        id="act-explore",
                        label_en="Try a Realistic Demo Case",
                        label_bn="বাস্তবসম্মত ডেমো কেস দেখুন",
                        action_type="launch_scenario",
                        payload="/scenarios",
                    ),
                    CopilotActionSuggestion(
                        id="act-scam",
                        label_en="Check Scam Merchant Watchlist",
                        label_bn="চোরের ড্যাশবোর্ড / প্রতারক ওয়াচলিস্ট",
                        action_type="search_merchant",
                        payload="/merchants",
                    ),
                ],
            )
