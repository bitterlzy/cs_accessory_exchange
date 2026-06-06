"""交换历史路由"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import TradeOffer, OfferStatus, OfferItem, InventoryItem
from app.schemas import TradeOfferOut
from app.deps import get_current_user_id
from app.errors import NotFound

router = APIRouter(prefix="/api/trades", tags=["交换历史"])


@router.get("", response_model=list[TradeOfferOut])
def list_trades(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """我的交换历史"""
    trades = db.query(TradeOffer).options(
        joinedload(TradeOffer.listing),
        joinedload(TradeOffer.proposer),
        joinedload(TradeOffer.receiver),
        joinedload(TradeOffer.offer_items).joinedload(OfferItem.inventory_item).joinedload(InventoryItem.definition),
    ).filter(
        TradeOffer.status == OfferStatus.completed,
        (TradeOffer.proposer_id == user_id) | (TradeOffer.receiver_id == user_id),
    ).order_by(TradeOffer.created_at.desc()).all()

    return [TradeOfferOut.from_orm(t) for t in trades]


@router.get("/{offer_id}", response_model=TradeOfferOut)
def get_trade(
    offer_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """交换详情"""
    trade = db.query(TradeOffer).options(
        joinedload(TradeOffer.listing),
        joinedload(TradeOffer.proposer),
        joinedload(TradeOffer.receiver),
        joinedload(TradeOffer.offer_items).joinedload(OfferItem.inventory_item).joinedload(InventoryItem.definition),
    ).filter(TradeOffer.id == offer_id).first()

    if not trade:
        raise NotFound("交换记录不存在")

    return TradeOfferOut.from_orm(trade)
