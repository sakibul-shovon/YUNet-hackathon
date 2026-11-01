from pydantic import BaseModel, Field


class CommunityCommentCreate(BaseModel):
    author_name: str = Field(default="Anonymous Consumer")
    content: str = Field(..., min_length=2, max_length=1000)


class CommunityCommentOut(BaseModel):
    id: str
    author_name: str
    content: str
    created_at: str
    is_legal_volunteer: bool = False


class CommunityPostCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    story: str = Field(..., min_length=10, max_length=4000)
    category: str = Field(default="E-Commerce")  # E-Commerce, MFS / Fintech, Retail, Telecom
    merchant_name: str = Field(default="Unknown Merchant")
    disputed_amount_bdt: float = Field(default=0.0)


class CommunityPostOut(BaseModel):
    id: str
    title: str
    story: str
    category: str
    merchant_name: str
    disputed_amount_bdt: float
    author_name: str
    me_too_count: int
    created_at: str
    has_converted_case: bool = False
    comments_count: int
    comments: list[CommunityCommentOut] = Field(default_factory=list)
