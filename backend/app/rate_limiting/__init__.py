# rate_limiting package
# Separate, reusable rate limiters with a factory.
#
# Quick start:
#   from app.rate_limiting import RateLimiterFactory
#
#   limiter = RateLimiterFactory.create(
#       "fixed_window",
#       max_requests=5,
#       window_seconds=60,
#   )
#   result = limiter.allow("user:1")

from app.rate_limiting.base import RateLimiter, RateLimitResult
from app.rate_limiting.factory import FIXED_WINDOW, TOKEN_BUCKET, RateLimiterFactory
from app.rate_limiting.fixed_window import FixedWindowRateLimiter
from app.rate_limiting.token_bucket import TokenBucketRateLimiter

__all__ = [
    "RateLimiter",
    "RateLimitResult",
    "RateLimiterFactory",
    "FixedWindowRateLimiter",
    "TokenBucketRateLimiter",
    "FIXED_WINDOW",
    "TOKEN_BUCKET",
]
