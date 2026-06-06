"""
API 路由模块包

注册所有子路由模块，供 main.py 导入:
- auth: 用户认证
- users: 用户管理
- kyc: 实名认证
- inventory: 饰品库存
- listings: 交换请求
- offers: 交换建议
- trades: 交换历史
- steam: Steam 账号与交易
- notifications: 通知系统
"""
from app.api import auth, users, kyc, inventory, listings, offers, trades, steam, notifications

__all__ = ["auth", "users", "kyc", "inventory", "listings", "offers", "trades", "steam", "notifications"]
