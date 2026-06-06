"""Risk control middleware

Provides security and anti-fraud protection:
1. Rate limiting (per-IP, per-endpoint)
2. Account freeze detection
3. Device fingerprint tracking
4. Fraud pattern detection

Usage in main.py:
    from middleware.security import RateLimitMiddleware
    app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)
"""

import time
import logging
from collections import defaultdict
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class InMemoryRateLimiter:
    """Simple in-memory rate limiter (single-instance only)

    For production with multiple instances, replace with Redis-backed implementation.
    """

    def __init__(self):
        self._windows = defaultdict(lambda: defaultdict(list))

    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> bool:
        now = time.time()
        window_key = int(now / window_seconds)
        timestamps = self._windows[key][window_key]
        # Clean old entries
        timestamps = [t for t in timestamps if t > now - window_seconds]
        self._windows[key][window_key] = timestamps
        if len(timestamps) >= max_requests:
            return False
        timestamps.append(now)
        return True


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware

    Limits requests per IP address within a time window.
    Skips swagger/redoc endpoints automatically.
    """

    def __init__(
        self,
        app: ASGIApp,
        max_requests: int = 100,
        window_seconds: int = 60,
        exclude_paths: list = None,
    ):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.exclude_paths = exclude_paths or ["/docs", "/redoc", "/openapi.json", "/api/health"]
        self.limiter = InMemoryRateLimiter()

    async def dispatch(self, request: Request, call_next):
        # Skip excluded paths
        if any(request.url.path.startswith(p) for p in self.exclude_paths):
            return await call_next(request)

        # Rate limit by IP
        client_ip = request.client.host if request.client else "unknown"
        key = f"rate:{client_ip}:{request.url.path}"

        if not self.limiter.is_allowed(key, self.max_requests, self.window_seconds):
            logger.warning(f"Rate limit exceeded: {client_ip} -> {request.url.path}")
            return Response(
                content='{"error": "Too many requests", "code": "RATE_LIMITED"}',
                status_code=429,
                media_type="application/json",
                headers={"Retry-After": str(self.window_seconds)},
            )

        return await call_next(request)


class DeviceFingerprintMiddleware(BaseHTTPMiddleware):
    """Device fingerprint tracking middleware

    Extracts device fingerprint from request headers and attaches it
    to the request state for downstream use in fraud detection.
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # Extract fingerprint from headers
        fingerprint = {
            "user_agent": request.headers.get("user-agent", ""),
            "accept_language": request.headers.get("accept-language", ""),
            "sec_ch_ua": request.headers.get("sec-ch-ua", ""),
            "sec_ch_ua_platform": request.headers.get("sec-ch-ua-platform", ""),
        }

        # Simple hash for device identification
        fp_string = "|".join(f"{k}={v}" for k, v in fingerprint.items() if v)
        request.state.device_fingerprint = hash(fp_string) if fp_string else 0
        request.state.client_ip = request.client.host if request.client else "unknown"

        return await call_next(request)


def get_device_fingerprint(request: Request) -> int:
    """Get the device fingerprint from request state"""
    return getattr(request.state, "device_fingerprint", 0)


def get_client_ip(request: Request) -> str:
    """Get the real client IP from request"""
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
