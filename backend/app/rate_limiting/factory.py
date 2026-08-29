# factory.py
# Factory = one place that builds rate limiters for you.
#
# You choose the type with a string (or enum-like name),
# and the factory returns a ready-to-use RateLimiter.
#
# Why factory?
#   - Call sites stay simple
#   - You can swap algorithms later without rewriting every feature
#   - Easy to use "however and whenever" you need

from __future__ import annotations

from typing import Any

from app.rate_limiting.base import RateLimiter
from app.rate_limiting.fixed_window import FixedWindowRateLimiter
from app.rate_limiting.token_bucket import TokenBucketRateLimiter

# Supported type names (use these strings in create())
FIXED_WINDOW = "fixed_window"
TOKEN_BUCKET = "token_bucket"


class RateLimiterFactory:
    """
    Create rate limiters without hard-coding the class name everywhere.

    Examples:
        limiter = RateLimiterFactory.create(
            "fixed_window",
            max_requests=5,
            window_seconds=60,
        )

        limiter = RateLimiterFactory.create(
            "token_bucket",
            capacity=10,
            refill_rate_per_second=1,
        )

        result = limiter.allow("user:42")
        if not result.allowed:
            print("Wait", result.retry_after_seconds, "seconds")
    """

    @staticmethod
    def create(limiter_type: str, **kwargs: Any) -> RateLimiter:
        """
        Build a rate limiter.

        limiter_type:
          - "fixed_window"
          - "token_bucket"

        kwargs depend on the type (see examples above).
        """
        normalised = (limiter_type or "").strip().lower()

        if normalised in {FIXED_WINDOW, "fixed", "window"}:
            return FixedWindowRateLimiter(
                max_requests=int(kwargs.get("max_requests", 60)),
                window_seconds=float(kwargs.get("window_seconds", 60)),
            )

        if normalised in {TOKEN_BUCKET, "token", "bucket"}:
            return TokenBucketRateLimiter(
                capacity=int(kwargs.get("capacity", 10)),
                refill_rate_per_second=float(
                    kwargs.get("refill_rate_per_second", kwargs.get("refill_rate", 1.0))
                ),
            )

        raise ValueError(
            f"Unknown rate limiter type: {limiter_type!r}. "
            f"Use '{FIXED_WINDOW}' or '{TOKEN_BUCKET}'."
        )

    @staticmethod
    def available_types() -> list[str]:
        """List the built-in limiter types."""
        return [FIXED_WINDOW, TOKEN_BUCKET]
