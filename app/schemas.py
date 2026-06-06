"""Pydantic 请求/响应 Schema"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator


# ===== Auth =====
class RegisterRequest(BaseModel):
    email: str = Field(..., max_length=255)
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)

class LoginRequest(BaseModel):
    email: str
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    token: str
    refresh_token: str

class UserOut(BaseModel):
    id: int
    email: str
    username: str
    avatar_url: Optional[str] = None
    steam_id: Optional[str] = None
    reputation_score: int = 0
    trade_count: int = 0

    class Config:
        orm_mode = True

class AuthResponse(BaseModel):
    user: UserOut
    token: str
    refresh_token: str


# ===== Inventory =====
class CreateInventoryItemRequest(BaseModel):
    definition_id: int
    quality: str  # FN, MW, FT, WW, BS
    float_value: Optional[float] = None
    pattern: Optional[int] = None
    stat_trak: bool = False
    souvenir: bool = False
    description: Optional[str] = None
    image_url: Optional[str] = None

    @validator("quality")
    def validate_quality(cls, v):
        if v not in ("FN", "MW", "FT", "WW", "BS"):
            raise ValueError("quality 必须是 FN/MW/FT/WW/BS")
        return v

class ItemDefinitionOut(BaseModel):
    id: int
    name: str
    category: str
    weapon_type: Optional[str] = None
    skin_name: Optional[str] = None
    rarity: str
    market_hash_name: str

    class Config:
        orm_mode = True

class InventoryItemOut(BaseModel):
    id: int
    owner_id: int
    definition_id: int
    quality: str
    float_value: Optional[float] = None
    pattern: Optional[int] = None
    stat_trak: bool
    souvenir: bool
    status: str
    description: Optional[str] = None
    definition: Optional[ItemDefinitionOut] = None
    created_at: datetime

    class Config:
        orm_mode = True


# ===== Listing =====
class CreateListingRequest(BaseModel):
    offered_item_id: int
    want_description: Optional[str] = None
    want_category: Optional[str] = None
    want_specific_definition_id: Optional[int] = None
    want_quality: Optional[str] = "any"

class UserBrief(BaseModel):
    id: int
    username: str
    avatar_url: Optional[str] = None
    reputation_score: Optional[int] = 0

    class Config:
        orm_mode = True

class ListingOut(BaseModel):
    id: int
    seller: UserBrief
    offered_item: Optional[InventoryItemOut] = None
    want_description: Optional[str] = None
    want_category: Optional[str] = None
    want_quality: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        orm_mode = True

class ListingListResponse(BaseModel):
    listings: List[ListingOut]
    total: int
    page: int
    limit: int


# ===== Trade Offer =====
class CreateOfferRequest(BaseModel):
    listing_id: int
    proposer_item_ids: List[int] = Field(..., min_items=1)
    note: Optional[str] = None

class OfferItemOut(BaseModel):
    id: int
    inventory_item_id: int
    side: str
    inventory_item: Optional[InventoryItemOut] = None

    class Config:
        orm_mode = True

class TradeOfferOut(BaseModel):
    id: int
    listing_id: int
    proposer: UserBrief
    receiver: UserBrief
    status: str
    proposer_note: Optional[str] = None
    offer_items: List[OfferItemOut] = []
    listing: Optional[ListingOut] = None
    created_at: datetime

    class Config:
        orm_mode = True


# ===== Notification =====
class NotificationOut(BaseModel):
    id: int
    user_id: int
    type: str
    title: str
    body: Optional[str] = None
    data: Optional[dict] = None
    is_read: bool
    created_at: datetime

    class Config:
        orm_mode = True

class NotificationListResponse(BaseModel):
    notifications: List[NotificationOut]
    total: int
    unread_count: int
    page: int
    limit: int


# ===== Generic =====
class MessageResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    error: str
    code: Optional[str] = None
    details: Optional[list] = None
