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
    """
    获取当前用户的所有完成交换记录
    
    过滤条件:
    - status = OfferStatus.completed（只返回完成的交换）
    - proposer_id == user_id OR receiver_id == user_id（作为发起方或接收方）
    
    预加载:
    - listing: 关联的交换请求
    - proposer/receiver: 双方用户信息
    - offer_items -> inventory_item -> definition: 交换的饰品详情
    """
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
    """
    获取单条交换记录的详细信息
    
    返回交易的完整快照，包括:
    - 交易双方信息
    - 所有涉及的物品及磨损值
    - 关联的 listing 信息
    """
    trade = db.query(TradeOffer).options(
        joinedload(TradeOffer.listing),
        joinedload(TradeOffer.proposer),
        joinedload(TradeOffer.receiver),
        joinedload(TradeOffer.offer_items).joinedload(OfferItem.inventory_item).joinedload(InventoryItem.definition),
    ).filter(TradeOffer.id == offer_id).first()

    if not trade:
        raise NotFound("交换记录不存在")

    return TradeOfferOut.from_orm(trade)
