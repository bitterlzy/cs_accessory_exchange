"""交换提议路由 (TradeOffers)"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import (
    TradeOffer, OfferStatus, OfferItem, OfferSide,
    Listing, ListingStatus, ListingTracking, TrackingStatus,
    InventoryItem, InventoryStatus, EventLog, Notification, User,
)
from app.schemas import CreateOfferRequest, TradeOfferOut
from app.deps import get_current_user_id
from app.errors import NotFound, BadRequest, Forbidden
from app.socketio_server import send_offer_update, send_notification

router = APIRouter(prefix="/api/offers", tags=["交换提议"])


@router.get("", response_model=list[TradeOfferOut])
def list_offers(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """我收到/发出的提议"""
    offers = db.query(TradeOffer).options(
        joinedload(TradeOffer.listing),
        joinedload(TradeOffer.proposer),
        joinedload(TradeOffer.receiver),
        joinedload(TradeOffer.offer_items).joinedload(OfferItem.inventory_item).joinedload(InventoryItem.definition),
    ).filter(
        (TradeOffer.proposer_id == user_id) | (TradeOffer.receiver_id == user_id)
    ).order_by(TradeOffer.created_at.desc()).all()

    return [TradeOfferOut.from_orm(o) for o in offers]


@router.post("", response_model=TradeOfferOut, status_code=201)
def create_offer(
    req: CreateOfferRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """发起交换提议"""
    listing = db.query(Listing).options(joinedload(Listing.seller)) \
        .filter(Listing.id == req.listing_id).first()
    if not listing or listing.status != ListingStatus.active:
        raise NotFound("交换请求不存在或已关闭")
    if listing.seller_id == user_id:
        raise BadRequest("不能对自己的请求发起交换")

    # 验证提议方物品
    proposer_items = db.query(InventoryItem).filter(
        InventoryItem.id.in_(req.proposer_item_ids),
        InventoryItem.owner_id == user_id,
        InventoryItem.status == InventoryStatus.available,
    ).all()
    if len(proposer_items) != len(req.proposer_item_ids):
        raise BadRequest("部分饰品不存在或状态不可用")

    # ---- 事务操作 ----
    # 锁定提议方物品
    for item in proposer_items:
        item.status = InventoryStatus.locked

    # 创建提议
    offer = TradeOffer(
        listing_id=req.listing_id,
        proposer_id=user_id,
        receiver_id=listing.seller_id,
        proposer_note=req.note,
        status=OfferStatus.pending,
    )
    db.add(offer)
    db.flush()

    # 创建提议物品
    for item_id in req.proposer_item_ids:
        db.add(OfferItem(
            trade_offer_id=offer.id,
            inventory_item_id=item_id,
            side=OfferSide.proposer,
        ))

    # 审计日志
    db.add(EventLog(
        trade_offer_id=offer.id,
        actor_id=user_id,
        event_type="offer_created",
        metadata={"listing_id": req.listing_id, "proposer_item_ids": req.proposer_item_ids},
    ))

    # 通知
    notif = Notification(
        user_id=listing.seller_id,
        type="new_offer",
        title="收到新的交换提议",
        body=f"用户对您的饰品发起了交换",
        data={"offer_id": offer.id, "listing_id": req.listing_id},
    )
    db.add(notif)
    db.flush()
    db.refresh(offer, ["listing", "proposer", "receiver", "offer_items"])

    return TradeOfferOut.from_orm(offer)


@router.post("/{offer_id}/accept", response_model=dict)
def accept_offer(
    offer_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """接受交换提议"""
    offer = db.query(TradeOffer).filter(TradeOffer.id == offer_id).first()
    if not offer:
        raise NotFound("提议不存在")
    if offer.receiver_id != user_id:
        raise Forbidden("无权操作")
    if offer.status != OfferStatus.pending:
        raise BadRequest("提议状态不允许接受")

    offer.status = OfferStatus.accepted

    db.add(EventLog(
        trade_offer_id=offer_id, actor_id=user_id,
        event_type="offer_accepted",
    ))
    db.flush()

    return {"message": "提议已接受，请双方确认交换"}


@router.post("/{offer_id}/reject", response_model=dict)
def reject_offer(
    offer_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """拒绝交换提议"""
    offer = db.query(TradeOffer).options(
        joinedload(TradeOffer.offer_items)
    ).filter(TradeOffer.id == offer_id).first()
    if not offer:
        raise NotFound("提议不存在")
    if offer.receiver_id != user_id:
        raise Forbidden("无权操作")
    if offer.status != OfferStatus.pending:
        raise BadRequest("提议状态不允许拒绝")

    offer.status = OfferStatus.rejected

    # 解锁物品
    for oi in offer.offer_items:
        db.query(InventoryItem).filter(InventoryItem.id == oi.inventory_item_id) \
          .update({"status": InventoryStatus.available})

    db.add(EventLog(
        trade_offer_id=offer_id, actor_id=user_id,
        event_type="offer_rejected",
    ))
    db.flush()

    return {"message": "提议已拒绝"}


@router.post("/{offer_id}/confirm", response_model=dict)
def confirm_trade(
    offer_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """确认交换（物品所有权转移）"""
    offer = db.query(TradeOffer).options(
        joinedload(TradeOffer.offer_items),
        joinedload(TradeOffer.listing),
    ).filter(TradeOffer.id == offer_id).first()
    if not offer:
        raise NotFound("提议不存在")
    if offer.proposer_id != user_id and offer.receiver_id != user_id:
        raise Forbidden("无权操作")
    if offer.status != OfferStatus.accepted:
        raise BadRequest("提议尚未被接受，无法确认")

    # ---- 物品所有权转移 ----
    # 拿出的物品归提议方
    listing_offered_item = db.query(InventoryItem).filter(
        InventoryItem.id == offer.listing.offered_item_id
    ).first()
    if listing_offered_item:
        listing_offered_item.owner_id = offer.proposer_id
        listing_offered_item.status = InventoryStatus.available

    # 提议方物品归接收方
    for oi in offer.offer_items:
        db.query(InventoryItem).filter(InventoryItem.id == oi.inventory_item_id) \
          .update({"owner_id": offer.receiver_id, "status": InventoryStatus.available})

    # 完成提议
    offer.status = OfferStatus.completed

    # 关闭 listing
    db.query(Listing).filter(Listing.id == offer.listing_id) \
      .update({"status": ListingStatus.closed})

    # 更新 tracking
    db.query(ListingTracking).filter(
        ListingTracking.listing_id == offer.listing_id
    ).update({"status": TrackingStatus.inactive})

    # 增加用户交换次数
    db.query(User).filter(User.id == offer.proposer_id).update(
        {User.trade_count: User.trade_count + 1}
    )
    db.query(User).filter(User.id == offer.receiver_id).update(
        {User.trade_count: User.trade_count + 1}
    )

    # 审计
    db.add(EventLog(
        trade_offer_id=offer_id, actor_id=user_id,
        event_type="trade_completed",
    ))
    db.flush()

    return {"message": "交换已完成！"}
