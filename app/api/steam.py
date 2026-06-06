import re
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, SteamAccount, SteamTradeOperation, TradeOffer, OfferStatus
from app.models import SteamOperationType, SteamOpStatus
from app.schemas import LinkSteamRequest, SteamAccountOut, SteamTradeOperationOut
from app.deps import get_current_user_id
from app.errors import NotFound, BadRequest, Forbidden
from app.config import settings

router = APIRouter(prefix="/api/steam", tags=["Steam"])

def _parse_trade_url(url):
    m = re.search(r"partner=(\d+)", url)
    if m:
        return str(int(m.group(1)) + 76561197960265728)
    return None

@router.post("/link", response_model=SteamAccountOut)
def link_account(req: LinkSteamRequest, uid: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    sid = _parse_trade_url(req.trade_url)
    if not sid: raise BadRequest("Invalid trade URL")
    # Check if this Steam account is already bound by someone else
    if db.query(SteamAccount).filter(SteamAccount.steam_id == sid).first():
        raise BadRequest("This Steam account is already bound to another user")
    # LIFETIME BINDING: check user does not already have a Steam account
    existing_acct = db.query(SteamAccount).filter(SteamAccount.user_id == uid).first()
    if existing_acct:
        raise BadRequest("You already have a bound Steam account. Binding is permanent and cannot be changed.")
    acct = SteamAccount(user_id=uid, steam_id=sid, trade_url=req.trade_url, is_primary=True)
    db.add(acct)
    u = db.query(User).filter(User.id == uid).first()
    if u: u.steam_id = sid
    db.flush()
    return SteamAccountOut.from_orm(acct)

@router.get("/accounts", response_model=list[SteamAccountOut])
def list_accounts(uid: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return [SteamAccountOut.from_orm(a) for a in db.query(SteamAccount).filter(SteamAccount.user_id == uid).all()]

def submit_offer(oid: int, steam_offer_id: str, uid: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    offer = db.query(TradeOffer).filter(TradeOffer.id == oid).first()
    if not offer: raise NotFound("Not found")
    if offer.proposer_id != uid and offer.receiver_id != uid: raise Forbidden("Forbidden")
    if offer.status != OfferStatus.accepted: raise BadRequest("Not accepted")
    op = SteamTradeOperation(operation_type=SteamOperationType.trade, trade_offer_id=steam_offer_id,
        from_user_id=uid, to_user_id=offer.receiver_id if offer.proposer_id == uid else offer.proposer_id,
        related_offer_id=offer.id, status=SteamOpStatus.sent, sent_at=datetime.utcnow())
    db.add(op)
    offer.steam_trade_offer_id = steam_offer_id
    db.flush()
    return {"message": "Submitted", "steam_offer_id": steam_offer_id}

@router.post("/offers/{oid}/confirm")
def confirm_delivery(oid: int, uid: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    offer = db.query(TradeOffer).filter(TradeOffer.id == oid).first()
    if not offer: raise NotFound("Not found")
    if offer.receiver_id != uid: raise Forbidden("Only receiver can confirm")
    if offer.status != OfferStatus.accepted: raise BadRequest("Not accepted")
    offer.status = OfferStatus.completed
    db.query(User).filter(User.id == offer.proposer_id).update({User.trade_count: User.trade_count + 1})
    db.query(User).filter(User.id == offer.receiver_id).update({User.trade_count: User.trade_count + 1})
    db.flush()
    return {"message": "Trade completed!"}
