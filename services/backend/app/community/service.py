import uuid
from typing import Any

from app.community.schemas import (
    CommunityCommentCreate,
    CommunityCommentOut,
    CommunityPostCreate,
    CommunityPostOut,
)

# Realistic community dataset representing Bangladesh consumer disputes
COMMUNITY_POSTS_STORE: list[dict[str, Any]] = [
    {
        "id": "post-daraz-1",
        "title": "দারাজে স্মার্টওয়াচ অর্ডার করে সাবান পেয়েছি, ১৫ দিনেও রিফান্ডের কোনো খবর নেই",
        "story": (
            "গত ২০ অক্টোবর দারাজের একটি ভেরিফাইড সেলার (Gadget Zone BD) থেকে ৩,৪৫০ টাকার একটি স্মার্টওয়াচ "
            "অর্ডার করেছিলাম। ২৫ অক্টোবর পার্সেল খুলে দেখি ভেতরে দুটি কাপড় কাচার সাবান। সাথে সাথে ডেলিভারি বয়কে "
            "জানিয়েছিলাম কিন্তু সে বলল দারাজ অ্যাপে রিটার্ন রিকোয়েস্ট করতে। অ্যাপে ছবি ও ভিডিও সহ রিটার্ন "
            "সাবমিট করার পর ১৫ দিন পার হয়ে গেছে, কাস্টমার কেয়ার শুধু বলছে 'আমরা তদন্ত করছি'। কোনো সুরাহা হচ্ছে না।"
        ),
        "category": "E-Commerce",
        "merchant_name": "Daraz BD / Gadget Zone",
        "disputed_amount_bdt": 3450.0,
        "author_name": "তানভীর আহমেদ (মিরপুর, ঢাকা)",
        "me_too_count": 42,
        "created_at": "২ দিন আগে",
        "has_converted_case": True,
        "is_pinned": True,
        "is_hidden": False,
        "report_count": 0,
        "comments": [
            {
                "id": "c-dz-01",
                "author_name": "অ্যাডভোকেট মো. রিয়াজ (লিগ্যাল ভলান্টিয়ার)",
                "content": (
                    "ভোক্তা অধিকার সংরক্ষণ আইন ২০০৯ এর ৪৫ ধারা অনুযায়ী প্রতিশ্রুত পণ্য সরবরাহ না করা এবং গ্রাহককে "
                    "প্রতারিত করা সরাসরি দণ্ডনীয়। আপনি দারাজের সাপোর্ট টিকিটের স্ক্রিনশট, আনবক্সিং ভিডিও ও ইনভয়েস "
                    "সংরক্ষণ করুন। এবারকি (Ebarki)-র মাধ্যমে লিগ্যাল নোটিশ বা ভোক্তা অধিদপ্তরে অভিযোগের খসড়া তৈরি করে নিন।"
                ),
                "created_at": "১ দিন আগে",
                "is_legal_volunteer": True,
            },
            {
                "id": "c-dz-02",
                "author_name": "রাকিবুল হাসান",
                "content": "আমার সাথেও সেইম ঘটনা ঘটেছিল। ফেসবুক গ্রুপে পোস্ট করার পর কাস্টমার কেয়ার দ্রুত সমাধান করেছিল।",
                "created_at": "২০ ঘণ্টা আগে",
                "is_legal_volunteer": False,
            },
        ],
    },
    {
        "id": "post-bkash-2",
        "title": "অনলাইন মার্চেন্ট পেমেন্টে টাকা কেটে নিলেও অর্ডারে ফেইল্ড দেখাল, ৭ দিনেও রিভার্সাল নেই",
        "story": (
            "অনলাইনে একটি পোশাকের শপে কেনাকাটার সময় বিকাশ অনলাইন পেমেন্ট গেটওয়ে দিয়ে ৫,২০০ টাকা পে করি। "
            "আমার বিকাশ ব্যালেন্স থেকে ৫,২০০ টাকা কেটে নেয় এবং সফল ট্রানজেকশন আইডি চলে আসে। কিন্তু মার্চেন্ট সাইটে "
            "অর্ডার স্ট্যাটাস 'Payment Failed' দেখায়। মার্চেন্ট বলছে তাদের একাউন্টে টাকা ঢোকেনি, আর বিকাশ হেল্পলাইনে "
            "ফোন দিলে বলছে ৭২ ঘণ্টার মধ্যে অটো-রিভার্স হবে। আজ ৭ দিন পার হলেও কোনো টাকা ফেরত আসেনি।"
        ),
        "category": "MFS / Fintech",
        "merchant_name": "bKash Online Merchant Gateway",
        "disputed_amount_bdt": 5200.0,
        "author_name": "সাদিয়া জাহান (উত্তরা)",
        "me_too_count": 67,
        "created_at": "৪ দিন আগে",
        "has_converted_case": True,
        "is_pinned": False,
        "is_hidden": False,
        "report_count": 0,
        "comments": [
            {
                "id": "c-bk-01",
                "author_name": "ব্যাংকিং কনসালট্যান্ট (ভলান্টিয়ার)",
                "content": (
                    "বাংলাদেশ ব্যাংকের পেমেন্ট সিস্টেমস ডিপার্টমেন্টের সার্কুলার অনুযায়ী MFS ট্রানজেকশন ফেইল্ড হলে "
                    "নির্দিষ্ট মেয়াদের মধ্যে টাকা সেটেলমেন্ট করতে হবে। বিকাশের লাইভ চ্যাটে ট্রান্সফারের ট্রানজেকশন আইডি সহ "
                    "আনুষ্ঠানিক কমপ্লেইন টিকিট নাম্বার নিন।"
                ),
                "created_at": "৩ দিন আগে",
                "is_legal_volunteer": True,
            },
            {
                "id": "c-bk-02",
                "author_name": "মেহেদী হাসান",
                "content": "আমারও এরকম হয়েছিল। বিকাশ সেন্টারে গিয়ে লিখিত ফর্ম জমা দেওয়ার ৩ দিনের মাথায় রিভার্স পেয়েছি।",
                "created_at": "২ দিন আগে",
                "is_legal_volunteer": False,
            },
        ],
    },
    {
        "id": "post-showroom-3",
        "title": "শোরুম থেকে নেওয়া ইনভার্টার এসি ৩ দিনের মাথায় গ্যাস লিক, ফ্রি ওয়ারেন্টিতে সার্ভিস দিতে অস্বীকৃতি",
        "story": (
            "একটি ইলেকট্রনিক্স শোরুম থেকে ৪৮,০০০ টাকা দিয়ে ১.৫ টন ইনভার্টার এসি কিনি। টেকনিশিয়ান ইন্সটল করে যাওয়ার "
            "৩ দিনের মধ্যে ঠান্ডা হওয়া সম্পূর্ণ বন্ধ হয়ে যায়। স্থানীয় মেকানিক ডেকে দেখালে সে জানায় পাইপের জয়েন্ট "
            "খারাপভাবে ফিটিং করায় সব গ্যাস বের হয়ে গেছে। শোরুমের কাস্টমার কেয়ারে জানালে তারা বলে ইন্সটলেশনের দায় "
            "তাদের নয় এবং গ্যাস রিফিলের জন্য ৪,৫০০ টাকা সার্ভিস চার্জ দাবি করছে, অথচ আমার ১ বছরের কমপ্লিট ফ্রি সার্ভিস ওয়ারেন্টি রয়েছে।"
        ),
        "category": "Retail",
        "merchant_name": "Elite Electronics Showroom",
        "disputed_amount_bdt": 48000.0,
        "author_name": "ইমতিয়াজ মাহমুদ (ধানমন্ডি, ঢাকা)",
        "me_too_count": 29,
        "created_at": "১ সপ্তাহ আগে",
        "has_converted_case": False,
        "is_pinned": False,
        "is_hidden": False,
        "report_count": 0,
        "comments": [
            {
                "id": "c-sr-01",
                "author_name": "ভোক্তা অধিকার কর্মী",
                "content": (
                    "ওয়ারেন্টি কার্ডে যদি স্পষ্টভাবে পার্টস ও সার্ভিস ফ্রি উল্লেখ থাকে, তবে এই অতিরিক্ত চার্জ দাবি করা "
                    "আইন পরিপন্থী। ক্রয় রশিদ ও ওয়ারেন্টি কার্ডের কপি সংযুক্ত করে শোরুম ম্যানেজারের বরাবরে লিখিত অভিযোগ দিন।"
                ),
                "created_at": "৫ দিন আগে",
                "is_legal_volunteer": True,
            },
        ],
    },
    {
        "id": "post-telecom-4",
        "title": "গ্রাহকের সম্মতি ছাড়াই প্রতি সপ্তাহে স্বয়ংক্রিয়ভাবে অপ্রয়োজনীয় VAS চার্জ কেটে নেওয়া হচ্ছে",
        "story": (
            "গত তিন মাস ধরে খেয়াল করছি আমার প্রিপেইড সিম থেকে প্রতি সপ্তাহে ৩৫ টাকা করে কেটে নেওয়া হচ্ছে। মাই-টেলকো "
            "অ্যাপে চেক করে দেখি একটি মিউজিক স্ট্রিমিং ও স্পোর্টস অ্যালার্ট সার্ভিস চালু আছে যা আমি কখনোই চালু করিনি। "
            "কাস্টমার কেয়ারে কল করলে তারা দায় এড়িয়ে বলে 'হ্যান্ডসেট থেকে ভুলবশত চাপ লেগে অ্যাক্টিভ হয়েছে'। কোনো ওটিপি বা "
            "কনফার্মেশন ছাড়াই এভাবে নিয়মিত টাকা কাটা অনৈতিক।"
        ),
        "category": "Telecom",
        "merchant_name": "Mobile Telecom Operator",
        "disputed_amount_bdt": 420.0,
        "author_name": "নাবিল চৌধুরী (চট্টগ্রাম)",
        "me_too_count": 114,
        "created_at": "১ সপ্তাহ আগে",
        "has_converted_case": False,
        "is_pinned": False,
        "is_hidden": False,
        "report_count": 0,
        "comments": [
            {
                "id": "c-tc-01",
                "author_name": "আইনি উপদেষ্টা",
                "content": "বিটিআরসির কলসেন্টার ১০০ নম্বরে ডায়াল করে অনাকাঙ্ক্ষিত ভিএএস সার্ভিস ডিডাকশনের বিরুদ্ধে সরাসরি অভিযোগ জানাতে পারেন।",
                "created_at": "৬ দিন আগে",
                "is_legal_volunteer": True,
            },
        ],
    },
    {
        "id": "post-fbpage-5",
        "title": "ফেসবুক পেজ 'Trendy Footwear BD' প্রি-পেমেন্ট নিয়ে পেজ ব্লক এবং ফোন বন্ধ",
        "story": (
            "একটি ফেসবুক পেজ থেকে প্রিমিয়াম লেদার সুজ অর্ডার করি ২,১৫০ টাকায়। ক্যাশ অন ডেলিভারি চাইলে তারা জানায় ৫০% "
            "টাকা ও কুরিয়ার চার্জ অগ্রিম দিতে হবে। তাদের রিভিউ দেখে বিশ্বাস করে বিকাশে পুরো ২,১৫০ টাকা সেন্ড মানি করি। "
            "এরপর ৩ দিন পার হলেও মেমো দেয়নি। গতকাল ফোন দিলে নম্বর বন্ধ পাই এবং ফেসবুকে নক দিতে গিয়ে দেখি পেজ থেকে ব্লক করে দেওয়া হয়েছে।"
        ),
        "category": "E-Commerce",
        "merchant_name": "Trendy Footwear BD (Facebook Page)",
        "disputed_amount_bdt": 2150.0,
        "author_name": "মাহমুদুল হাসান (রাজশাহী)",
        "me_too_count": 89,
        "created_at": "২ সপ্তাহ আগে",
        "has_converted_case": True,
        "is_pinned": False,
        "is_hidden": False,
        "report_count": 0,
        "comments": [
            {
                "id": "c-fb-01",
                "author_name": "সাইবার সহায়তা সহকারী",
                "content": "বিকাশ হেল্পলাইনে ট্রানজেকশন আইডি দিয়ে অবিলম্বে ওই মার্চেন্ট/পার্সোনাল ওয়ালেটটি রিপোর্ট করুন যেন প্রতারক টাকা ক্যাশ আউট করতে না পারে।",
                "created_at": "১০ দিন আগে",
                "is_legal_volunteer": True,
            },
        ],
    },
]


class CommunityService:
    @classmethod
    def list_posts(cls, category: str | None = None) -> list[CommunityPostOut]:
        results = []
        # Sort pinned posts first
        sorted_posts = sorted(COMMUNITY_POSTS_STORE, key=lambda p: (not p.get("is_pinned", False)))
        for p in sorted_posts:
            if p.get("is_hidden", False):
                continue
            if category and category.lower() != "all" and p["category"].lower() != category.lower():
                continue
            comments = [
                CommunityCommentOut(
                    id=c["id"],
                    author_name=c["author_name"],
                    content=c["content"],
                    created_at=c["created_at"],
                    is_legal_volunteer=c.get("is_legal_volunteer", False),
                )
                for c in p.get("comments", [])
            ]
            results.append(
                CommunityPostOut(
                    id=p["id"],
                    title=p["title"],
                    story=p["story"],
                    category=p["category"],
                    merchant_name=p["merchant_name"],
                    disputed_amount_bdt=p["disputed_amount_bdt"],
                    author_name=p["author_name"],
                    me_too_count=p["me_too_count"],
                    created_at=p["created_at"],
                    has_converted_case=p["has_converted_case"],
                    comments_count=len(comments),
                    comments=comments,
                )
            )
        return results

    @classmethod
    def create_post(cls, post: CommunityPostCreate) -> CommunityPostOut:
        post_id = f"post-{uuid.uuid4().hex[:8]}"
        new_post = {
            "id": post_id,
            "title": post.title,
            "story": post.story,
            "category": post.category,
            "merchant_name": post.merchant_name,
            "disputed_amount_bdt": post.disputed_amount_bdt,
            "author_name": "সচেতন ভোক্তা (Anonymous)",
            "me_too_count": 1,
            "created_at": "এইমাত্র",
            "has_converted_case": False,
            "is_pinned": False,
            "is_hidden": False,
            "report_count": 0,
            "comments": [],
        }
        COMMUNITY_POSTS_STORE.insert(0, new_post)
        return CommunityPostOut(
            id=new_post["id"],
            title=new_post["title"],
            story=new_post["story"],
            category=new_post["category"],
            merchant_name=new_post["merchant_name"],
            disputed_amount_bdt=new_post["disputed_amount_bdt"],
            author_name=new_post["author_name"],
            me_too_count=new_post["me_too_count"],
            created_at=new_post["created_at"],
            has_converted_case=False,
            comments_count=0,
            comments=[],
        )

    @classmethod
    def increment_me_too(cls, post_id: str) -> int:
        for p in COMMUNITY_POSTS_STORE:
            if p["id"] == post_id:
                p["me_too_count"] += 1
                return p["me_too_count"]
        return 0

    @classmethod
    def add_comment(cls, post_id: str, comment: CommunityCommentCreate) -> CommunityCommentOut:
        for p in COMMUNITY_POSTS_STORE:
            if p["id"] == post_id:
                cid = f"c-{uuid.uuid4().hex[:6]}"
                cdata = {
                    "id": cid,
                    "author_name": comment.author_name or "Anonymous",
                    "content": comment.content,
                    "created_at": "এইমাত্র",
                    "is_legal_volunteer": False,
                }
                p.setdefault("comments", []).append(cdata)
                return CommunityCommentOut(**cdata)
        raise ValueError(f"Post {post_id} not found")
