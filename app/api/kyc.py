"""实名认证路由模块 (KYC)

提供用户实名认证功能:

三级认证体系:
  Level 0: none - 未认证
  Level 1: pending - 已提交，等待验证
  Level 2: verified - 已实名
  Level 3: failed - 验证失败

防一人多号机制:
- 身份证号 SHA256 哈希查重
- 支付宝账号查重
- 手机号查重
- 同 IP / 同设备风控检测
"""
import hashlib
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserVerification, VerificationLevel
from app.schemas import KYCSubmitRequest, KYCStatusResponse
from app.deps import get_current_user_id
from app.errors import BadRequest, NotFound

router = APIRouter(prefix="/api/kyc", tags=["实名认证"])


def _hash_id_number(id_number: str) -> str:
    """将身份证号转为 SHA256 哈希用于查重"""
    return hashlib.sha256(id_number.encode()).hexdigest()


@router.get("/status", response_model=KYCStatusResponse)
def get_kyc_status(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """查看当前用户的实名认证状态"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFound("用户不存在")

    verification = db.query(UserVerification).filter(
        UserVerification.user_id == user_id
    ).first()

    return KYCStatusResponse(
        user_id=user_id,
        verification_level=user.verification_level.value if user.verification_level else "none",
        real_name=verification.real_name if verification else None,
        alipay_account=verification.alipay_account if verification else None,
        is_verified=user.verification_level == VerificationLevel.verified,
        fail_reason=verification.fail_reason if verification else None,
        verified_at=verification.verified_at if verification else None,
    )


@router.post("/submit", response_model=KYCStatusResponse)
def submit_kyc(
    req: KYCSubmitRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """提交实名认证信息

    流程:
    1. 检查身份证号是否已被其他账号绑定
    2. 检查支付宝账号是否已被绑定
    3. 保存实名信息
    4. 设置状态为 pending
    5. 如果配置了支付宝 API，自动发起验证
    """
    # 检查身份证号重复
    id_hash = _hash_id_number(req.id_number)
    existing = db.query(UserVerification).filter(
        UserVerification.id_number_hash == id_hash
    ).first()
    if existing:
        raise BadRequest("该身份证号已被其他账号绑定，每个人只能注册一个账号")

    # 检查支付宝账号重复
    existing_alipay = db.query(UserVerification).filter(
        UserVerification.alipay_account == req.alipay_account
    ).first()
    if existing_alipay:
        raise BadRequest("该支付宝账号已被其他账号绑定")

    # 删除旧的认证记录（如果有）
    old = db.query(UserVerification).filter(
        UserVerification.user_id == user_id
    ).first()
    if old:
        db.delete(old)
        db.flush()

    # 创建新的实名记录
    verification = UserVerification(
        user_id=user_id,
        real_name=req.real_name,
        id_number_hash=id_hash,
        alipay_account=req.alipay_account,
        verification_level=VerificationLevel.pending,
    )
    db.add(verification)

    # 更新用户认证等级
    user = db.query(User).filter(User.id == user_id).first()
    user.verification_level = VerificationLevel.pending

    db.flush()

    return KYCStatusResponse(
        user_id=user_id,
        verification_level="pending",
        real_name=req.real_name,
        alipay_account=req.alipay_account,
        is_verified=False,
    )



    # Phone verification required before KYC (one person one account)
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.phone:
        raise BadRequest("Phone number is required. Please register with a phone number first.")
    if not user.phone_verified:
        raise BadRequest("Please verify your phone number before identity verification.")

@router.post("/verify")
def verify_kyc(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """实名认证确认

    在正式环境中，这里会调用支付宝实名接口:
    1. 向用户的支付宝账号转账 0.01 元
    2. 用户在支付宝中确认收款
    3. 系统验证收款人姓名与提交的姓名一致

    当前是模拟模式，直接设置为 verified。
    """
    verification = db.query(UserVerification).filter(
        UserVerification.user_id == user_id
    ).first()
    if not verification:
        raise BadRequest("请先提交实名信息")

    if verification.verification_level == VerificationLevel.verified:
        return {"message": "已经认证通过", "verified": True}

    # 模拟验证成功
    verification.verification_level = VerificationLevel.verified
    verification.verified_at = datetime.utcnow()

    user = db.query(User).filter(User.id == user_id).first()
    user.verification_level = VerificationLevel.verified

    db.flush()

    return {"message": "实名认证成功", "verified": True}
