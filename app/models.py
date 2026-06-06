"""SQLAlchemy 数据模型 - 对应 Prisma schema 的 10 张表"""
import enum
from datetime import datetime
from sqlalchemy import (
    Column, BigInteger, String, Boolean, DateTime, Text,
    Enum as SAEnum, ForeignKey, JSON, Numeric, UniqueConstraint, Index, Integer
)
from sqlalchemy.orm import relationship
from app.database import Base


# ==================== Python Enums ====================

class UserStatus(str, enum.Enum):
    active = "active"
    disabled = "disabled"

class ItemCategory(str, enum.Enum):
    weapon = "weapon"
    knife = "knife"
    gloves = "gloves"
    sticker = "sticker"
    agent = "agent"
    case = "case"
    key = "key"
    other = "other"

class ItemRarity(str, enum.Enum):
    consumer = "consumer"
    industrial = "industrial"
    mil_spec = "mil_spec"
    restricted = "restricted"
    classified = "classified"
    covert = "covert"
    special = "special"
    exceedingly_rare = "exceedingly_rare"

class ItemQuality(str, enum.Enum):
    FN = "FN"
    MW = "MW"
    FT = "FT"
    WW = "WW"
    BS = "BS"

class InventoryStatus(str, enum.Enum):
    available = "available"
    locked = "locked"
    traded = "traded"
    removed = "removed"

class ListingStatus(str, enum.Enum):
    active = "active"
    matched = "matched"
    closed = "closed"
    cancelled = "cancelled"

class TrackingStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"

class PriceSource(str, enum.Enum):
    steam = "steam"
    buff = "buff"
    igxe = "igxe"
    youpin = "youpin"
    other = "other"

class OfferStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"
    countered = "countered"
    cancelled = "cancelled"
    confirmed = "confirmed"
    completed = "completed"

class OfferSide(str, enum.Enum):
    proposer = "proposer"
    receiver = "receiver"


# ==================== 数据库模型 ====================

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column("password_hash", String(255), nullable=False)
    avatar_url = Column("avatar_url", String(500))
    steam_id = Column("steam_id", String(64), unique=True)
    reputation_score = Column("reputation_score", Integer, default=0)
    trade_count = Column("trade_count", Integer, default=0)
    status = Column(SAEnum(UserStatus), default=UserStatus.active)
    last_login = Column("last_login", DateTime)
    created_at = Column("created_at", DateTime, default=datetime.utcnow)
    updated_at = Column("updated_at", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    inventory_items = relationship("InventoryItem", back_populates="owner")
    listings = relationship("Listing", back_populates="seller")
    listing_tracking = relationship("ListingTracking", back_populates="user")
    proposed_offers = relationship("TradeOffer", back_populates="proposer", foreign_keys="TradeOffer.proposer_id")
    received_offers = relationship("TradeOffer", back_populates="receiver", foreign_keys="TradeOffer.receiver_id")


class ItemDefinition(Base):
    __tablename__ = "item_definitions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    category = Column(SAEnum(ItemCategory), nullable=False)
    weapon_type = Column("weapon_type", String(100))
    skin_name = Column("skin_name", String(255))
    rarity = Column(SAEnum(ItemRarity), nullable=False)
    rarity_color = Column("rarity_color", String(7))
    collection = Column(String(255))
    market_hash_name = Column("market_hash_name", String(255), unique=True, nullable=False, index=True)
    inspect_url_template = Column("inspect_url_template", Text)
    image_url = Column("image_url", String(500))
    is_tradable = Column("is_tradable", Boolean, default=True)
    created_at = Column("created_at", DateTime, default=datetime.utcnow)
    updated_at = Column("updated_at", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    inventory_items = relationship("InventoryItem", back_populates="definition")
    listing_tracking = relationship("ListingTracking", back_populates="definition")
    item_prices = relationship("ItemPrice", back_populates="definition")


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    owner_id = Column("owner_id", BigInteger, ForeignKey("users.id"), nullable=False)
    definition_id = Column("definition_id", BigInteger, ForeignKey("item_definitions.id"), nullable=False)
    quality = Column(SAEnum(ItemQuality), nullable=False)
    float_value = Column("float_value", Numeric(10, 8))
    pattern = Column(Integer)
    sticker_details = Column("sticker_details", JSON)
    stat_trak = Column("stat_trak", Boolean, default=False)
    souvenir = Column(Boolean, default=False)
    description = Column(Text)
    image_url = Column("image_url", String(500))
    status = Column(SAEnum(InventoryStatus), default=InventoryStatus.available)
    created_at = Column("created_at", DateTime, default=datetime.utcnow)
    updated_at = Column("updated_at", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="inventory_items")
    definition = relationship("ItemDefinition", back_populates="inventory_items")
    listing = relationship("Listing", back_populates="offered_item", uselist=False)
    offer_items = relationship("OfferItem", back_populates="inventory_item")

    __table_args__ = (
        Index("idx_owner_id", "owner_id"),
        Index("idx_definition_id", "definition_id"),
        Index("idx_owner_status", "owner_id", "status"),
    )


class Listing(Base):
    __tablename__ = "listings"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    seller_id = Column("seller_id", BigInteger, ForeignKey("users.id"), nullable=False)
    offered_item_id = Column("offered_item_id", BigInteger, ForeignKey("inventory_items.id"), nullable=False)
    want_description = Column("want_description", Text)
    want_category = Column("want_category", String(50))
    want_specific_definition_id = Column("want_specific_definition_id", BigInteger, ForeignKey("item_definitions.id"))
    want_quality = Column("want_quality", String(10), default="any")
    status = Column(SAEnum(ListingStatus), default=ListingStatus.active)
    created_at = Column("created_at", DateTime, default=datetime.utcnow)
    updated_at = Column("updated_at", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    seller = relationship("User", back_populates="listings")
    offered_item = relationship("InventoryItem", back_populates="listing")
    want_specific_definition = relationship("ItemDefinition")
    trade_offers = relationship("TradeOffer", back_populates="listing")
    listing_tracking = relationship("ListingTracking", back_populates="listing", uselist=False)

    __table_args__ = (
        Index("idx_listing_seller", "seller_id"),
        Index("idx_listing_status", "status"),
    )


class ListingTracking(Base):
    __tablename__ = "listing_tracking"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    definition_id = Column("definition_id", BigInteger, ForeignKey("item_definitions.id"), nullable=False)
    user_id = Column("user_id", BigInteger, ForeignKey("users.id"), nullable=False)
    listing_id = Column("listing_id", BigInteger, ForeignKey("listings.id"), unique=True, nullable=False)
    status = Column(SAEnum(TrackingStatus), default=TrackingStatus.active)
    created_at = Column("created_at", DateTime, default=datetime.utcnow)
    updated_at = Column("updated_at", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    definition = relationship("ItemDefinition", back_populates="listing_tracking")
    user = relationship("User", back_populates="listing_tracking")
    listing = relationship("Listing", back_populates="listing_tracking")

    __table_args__ = (
        Index("idx_tracking_def_status", "definition_id", "status"),
        Index("idx_tracking_user", "user_id", "status"),
    )


class ItemPrice(Base):
    __tablename__ = "item_prices"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    definition_id = Column("definition_id", BigInteger, ForeignKey("item_definitions.id"), nullable=False)
    quality = Column(SAEnum(ItemQuality), nullable=False)
    stat_trak = Column("stat_trak", Boolean, default=False)
    source = Column(SAEnum(PriceSource), nullable=False)
    price_min = Column("price_min", Numeric(12, 2))
    price_max = Column("price_max", Numeric(12, 2))
    price_avg = Column("price_avg", Numeric(12, 2))
    volume_24h = Column("volume_24h", Integer)
    currency = Column(String(3), default="CNY")
    fetched_at = Column("fetched_at", DateTime, nullable=False)
    created_at = Column("created_at", DateTime, default=datetime.utcnow)

    definition = relationship("ItemDefinition", back_populates="item_prices")

    __table_args__ = (
        Index("idx_price_definition", "definition_id"),
        Index("idx_price_source", "source"),
        Index("idx_price_fetched", "fetched_at"),
    )


class TradeOffer(Base):
    __tablename__ = "trade_offers"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    listing_id = Column("listing_id", BigInteger, ForeignKey("listings.id"), nullable=False)
    proposer_id = Column("proposer_id", BigInteger, ForeignKey("users.id"), nullable=False)
    receiver_id = Column("receiver_id", BigInteger, ForeignKey("users.id"), nullable=False)
    status = Column(SAEnum(OfferStatus), default=OfferStatus.pending)
    proposer_note = Column("proposer_note", Text)
    receiver_note = Column("receiver_note", Text)
    expires_at = Column("expires_at", DateTime)
    created_at = Column("created_at", DateTime, default=datetime.utcnow)
    updated_at = Column("updated_at", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    listing = relationship("Listing", back_populates="trade_offers")
    proposer = relationship("User", back_populates="proposed_offers", foreign_keys=[proposer_id])
    receiver = relationship("User", back_populates="received_offers", foreign_keys=[receiver_id])
    offer_items = relationship("OfferItem", back_populates="trade_offer")
    event_logs = relationship("EventLog", back_populates="trade_offer")

    __table_args__ = (
        Index("idx_offer_listing", "listing_id"),
        Index("idx_offer_proposer", "proposer_id"),
        Index("idx_offer_receiver", "receiver_id"),
        Index("idx_offer_status", "status"),
    )


class OfferItem(Base):
    __tablename__ = "offer_items"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    trade_offer_id = Column("trade_offer_id", BigInteger, ForeignKey("trade_offers.id"), nullable=False)
    inventory_item_id = Column("inventory_item_id", BigInteger, ForeignKey("inventory_items.id"), nullable=False)
    side = Column(SAEnum(OfferSide), nullable=False)
    created_at = Column("created_at", DateTime, default=datetime.utcnow)

    trade_offer = relationship("TradeOffer", back_populates="offer_items")
    inventory_item = relationship("InventoryItem", back_populates="offer_items")


class EventLog(Base):
    __tablename__ = "event_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    trade_offer_id = Column("trade_offer_id", BigInteger, ForeignKey("trade_offers.id"))
    actor_id = Column("actor_id", BigInteger, ForeignKey("users.id"), nullable=False)
    event_type = Column("event_type", String(50), nullable=False)
    event_metadata = Column(JSON)
    ip_address = Column("ip_address", String(45))
    created_at = Column("created_at", DateTime, default=datetime.utcnow)

    trade_offer = relationship("TradeOffer", back_populates="event_logs")

    __table_args__ = (
        Index("idx_log_offer", "trade_offer_id"),
        Index("idx_log_event", "event_type"),
    )


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column("user_id", BigInteger, ForeignKey("users.id"), nullable=False)
    type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    body = Column(Text)
    data = Column(JSON)
    is_read = Column("is_read", Boolean, default=False)
    created_at = Column("created_at", DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_notif_user_unread", "user_id", "is_read"),
    )
