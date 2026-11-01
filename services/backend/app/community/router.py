from fastapi import APIRouter, HTTPException, Query, status

from app.community.schemas import (
    CommunityCommentCreate,
    CommunityCommentOut,
    CommunityPostCreate,
    CommunityPostOut,
)
from app.community.service import CommunityService

router = APIRouter(prefix="/v1/community", tags=["Community Consumer Help Forum"])


@router.get("/posts", response_model=list[CommunityPostOut])
def list_community_posts(
    category: str | None = Query(None, description="Optional category filter (e.g. E-Commerce, MFS / Fintech)"),
):
    """Returns consumer grievance posts with mutual-support discussions."""
    return CommunityService.list_posts(category)


@router.post("/posts", response_model=CommunityPostOut, status_code=status.HTTP_201_CREATED)
def create_community_post(post: CommunityPostCreate):
    """Publishes a consumer dispute help request to the public community board."""
    return CommunityService.create_post(post)


@router.post("/posts/{id}/me-too")
def increment_me_too(id: str):
    """Increments the 'Me Too / আমার সাথেও এমন হয়েছে' counter for a dispute."""
    count = CommunityService.increment_me_too(id)
    if count == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"me_too_count": count}


@router.post("/posts/{id}/comments", response_model=CommunityCommentOut)
def add_community_comment(id: str, comment: CommunityCommentCreate):
    """Adds a consumer or legal volunteer advice comment to a community post."""
    try:
        return CommunityService.add_comment(id, comment)
    except ValueError:
        raise HTTPException(status_code=404, detail="Post not found")

