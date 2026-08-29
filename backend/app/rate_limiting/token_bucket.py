# token_bucket.py
# Token-bucket limiter.
#
# Imagine a bucket that holds tokens.
# - Each allow() uses 1 token
# - Tokens refill slowly over time
# - Bursts are allowed until the bucket is empty
#
# Example:
#   capacity=10, refill_rate_per_second=1
#   → up to 10 quick calls, then about 1 call per second

import threading
import time
from collections import defaultdict

from app.rate_limiting.base import RateLimiter, RateLimitResult


class TokenBucketRateLimiter(RateLimiter):
    def __init__(self, capacity: int, refill_rate_per_second: float):
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        if refill_rate_per_second <= 0:
            raise ValueError("refill_rate_per_second must be greater than 0")

        self.capacity = capacity
        self.refill_rate_per_second = float(refill_rate_per_second)

        # key -> (tokens, last_refill_timestamp)
        self._state: dict[str, tuple[float, float]] = defaultdict(
            lambda: (float(capacity), time.monotonic())
        )
        self._lock = threading.Lock()

    def allow(self, key: str) -> RateLimitResult:
        now = time.monotonic()

        with self._lock:
            tokens, last_refill = self._state[key]

            # Add tokens based on elapsed time
            elapsed = now - last_refill
            tokens = min(self.capacity, tokens + elapsed * self.refill_rate_per_second)

            if tokens < 1:
                # How long until we have 1 full token again?
                missing = 1 - tokens
                retry_after = missing / self.refill_rate_per_second
                self._state[key] = (tokens, now)
                return RateLimitResult(
                    allowed=False,
                    retry_after_seconds=retry_after,
                    remaining=0,
                )

            tokens -= 1
            self._state[key] = (tokens, now)
            return RateLimitResult(
                allowed=True,
                retry_after_seconds=0.0,
                remaining=int(tokens),
            )
