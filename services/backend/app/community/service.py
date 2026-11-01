import uuid
from typing import Any

from app.community.schemas import (
    CommunityCommentCreate,
    CommunityCommentOut,
    CommunityPostCreate,
    CommunityPostOut,
)

# Seed realistic initial community posts representing common Bangladesh consumer disputes
COMMUNITY_POSTS_STORE: list[dict[str, Any]] = [
    {
        "id": "post-daraz-01",
        "title": "দারাজ থেকে ৫,৫০০ টাকার ঘড়ি কিনে সাবান পেয়েছি, রিটার্ন রিজেক্ট করেছে। কী করব?",
        "story": "গত সপ্তাহে দারাজ থেকে একটি স্মার্টওয়াচ অর্ডার করেছিলাম। ক্যাশ অন ডেলিভারি নেওয়ার পর প্যাকেট খুলে দেখি ভেতরে সাবান। কাস্টমার কেয়ারে জানালে তারা দাবি করে প্যাকিং ঠিক ছিল এবং রিটার্ন রিজেক্ট করে দিয়েছে। মেসেঞ্জারেও কোনো সদুত্তর পাচ্ছি না। কেউ কি এমন সমস্যা থেকে টাকা উদ্ধার করতে পেরেছেন?",
        "category": "E-Commerce",
        "merchant_name": "Daraz Bangladesh (Seller: Tech Zone)",
        "disputed_amount_bdt": 5500.0,
        "author_name": "তানভীর আহমেদ (মিরপুর, ঢাকা)",
        "me_too_count": 27,
        "created_at": "২ ঘণ্টা আগে",
        "has_converted_case": True,
        "comments": [
            {
                "id": "c1",
                "author_name": "সাকিব আল হাসান (ভোক্তা অধিকার সচেতন ফোরাম)",
                "content": "প্যাকেট খোলার আনবক্সিং ভিডিও বা ছবি থাকলে সাথে সাথে ভোক্তা অধিকার অধিদপ্তরে (DNCRP) অভিযোগ দাখিল করুন। ধারা ৪৫ এবং ৭৬ অনুযায়ী ৩০ দিনের মধ্যে আবেদন করলে সম্পূর্ণ টাকা ফেরত সহ জরিমানা আদায় সম্ভব।",
                "created_at": "১ ঘণ্টা আগে",
                "is_legal_volunteer": True,
            },
            {
                "id": "c2",
                "author_name": "রাকিবুল ইসলাম",
                "content": "আমার সাথেও সেইম সেলার করেছিল! দারাজে অভিযোগ করে লাভ হয়নি, ClaimCraft দিয়ে অভিযোগের চিঠি পাঠিয়েছিলাম, ৩ দিনের মধ্যে রিফান্ড দিয়েছে।",
                "created_at": "৪৫ মিনিট আগে",
                "is_legal_volunteer": False,
            },
        ],
    },
    {
        "id": "post-bkash-02",
        "title": "বিকাশে পেমেন্ট কেটেছে কিন্তু মার্চেন্টের একাউন্টে টাকা যায়নি — হেল্পলাইনে সমাধান নেই",
        "story": "অনলাইন গ্রোসারি কেনার সময় বিকাশ কিউআর কোড স্ক্যান করে ৪,২০০ টাকা পেমেন্ট করি। আমার ব্যালেন্স কেটে নিয়েছে এবং ট্রানজেকশন সফল দেখিয়েছে। কিন্তু শপের অ্যাপে অর্ডার পেন্ডিং এবং তারা পণ্য দিতে অস্বীকৃতি জানায়। বিকাশ হেল্পলাইনে কল দিলে ৭২ ঘণ্টা অপেক্ষা করতে বলে ৭ দিন পার করে দিয়েছে।",
        "category": "MFS / Fintech",
        "merchant_name": "bKash Limited",
        "disputed_amount_bdt": 4200.0,
        "author_name": "ফারহানা আফরোজ (ধানমন্ডি)",
        "me_too_count": 19,
        "created_at": "৫ ঘণ্টা আগে",
        "has_converted_case": True,
        "comments": [
            {
                "id": "c3",
                "author_name": "আইনি পরামর্শক রফিকুল ইসলাম",
                "content": "প্রথমে বিকাশের সাপোর্ট টিকিট নম্বরটি সংগ্রহ করুন। এরপর বাংলাদেশ ব্যাংকের Financial Integrity & Customer Complaints Department (CIPC)-এ অনলাইনে অভিযোগ দাখিল করুন।",
                "created_at": "৩ ঘণ্টা আগে",
                "is_legal_volunteer": True,
            },
        ],
    },
    {
        "id": "post-gadget-03",
        "title": "ফেসবুক পেজ 'Gadget Zone BD' বিকাশ অগ্রিম নিয়ে মেসেঞ্জারে ব্লক করে দিয়েছে",
        "story": "ফেসবুকে স্পনসরড অ্যাড দেখে একটি গ্যাজেট অর্ডারের জন্য ৩,০০০ টাকা বিকাশ পার্সোনাল নাম্বারে পাঠাই। তারা বলেছিল ২৪ ঘণ্টায় কুরিয়ারে পাঠাবে। টাকা নেওয়ার পর এখন তাদের পেজে আর মেসেজ যাচ্ছে না, ফোন নাম্বারও বন্ধ। কেউ কি এই পেজের আসল ঠিকানা জানেন?",
        "category": "E-Commerce",
        "merchant_name": "Gadget Zone BD (F-Commerce Page)",
        "disputed_amount_bdt": 3000.0,
        "author_name": "নাজমুল হক (চট্টগ্রাম)",
        "me_too_count": 43,
        "created_at": "১ দিন আগে",
        "has_converted_case": False,
        "comments": [
            {
                "id": "c4",
                "author_name": "সাইবার ক্রাইম ভিক্টিম সাপোর্ট ভলান্টিয়ার",
                "content": "এই পেজের বিরুদ্ধে ইতিমধ্যে আরও ১৪ জন ভোক্তা ক্লেইমক্রাফট বিডি-তে অভিযোগ করেছেন। আপনি দ্রুত বিকাশে ট্রানজেকশন ডিসপিউট রিপোর্ট করুন এবং সিআইডি সাইবার পুলিশে জিডি করুন।",
                "created_at": "১৮ ঘণ্টা আগে",
                "is_legal_volunteer": True,
            },
        ],
    },
]


class CommunityService:
    @classmethod
    def list_posts(cls, category: str | None = None) -> list[CommunityPostOut]:
        results = []
        for p in COMMUNITY_POSTS_STORE:
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
                p["comments"].append(cdata)
                return CommunityCommentOut(**cdata)
        raise ValueError("Post not found")
