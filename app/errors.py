"""错误处理工具"""
from fastapi import HTTPException


class AppError(HTTPException):
    """业务异常"""
    def __init__(self, status_code: int, message: str, code: str = None):
        super().__init__(status_code=status_code, detail={"error": message, "code": code})


class NotFound(AppError):
    def __init__(self, message: str = "资源不存在"):
        super().__init__(404, message)


class BadRequest(AppError):
    def __init__(self, message: str):
        super().__init__(400, message)


class Unauthorized(AppError):
    def __init__(self, message: str = "未授权"):
        super().__init__(401, message)


class Forbidden(AppError):
    def __init__(self, message: str = "无权操作"):
        super().__init__(403, message)
