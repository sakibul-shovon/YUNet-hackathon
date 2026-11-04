import uuid
from typing import Any

from app.community.schemas import (
    CommunityCommentCreate,
    CommunityCommentOut,
    CommunityPostCreate,
    CommunityPostOut,
)

# Public data is never fabricated or copied from private cases.
COMMUNITY_POSTS_STORE: list[dict[str, Any]] = []


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
