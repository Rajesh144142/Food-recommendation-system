# fixed_window.py
# Simple fixed-window counter.
#
# Example:
#   max_requests=5, window_seconds=60
#   → each key may call allow() at most 5 times per 60-second window.

import threading
import time
from collections import defaultdict

from app.rate_limiting.base import RateLimiter, RateLimitResult


class FixedWindowRateLimiter(RateLimiter):
    def __init__(self, max_requests: int, window_seconds: float):
        if max_requests < 1:
            raise ValueError("max_requests must be at least 1")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be greater than 0")

        self.max_requests = max_requests
        self.window_seconds = float(window_seconds)

        # key -> (window_start_timestamp, count)
        self._state: dict[str, tuple[float, int]] = defaultdict(lambda: (0.0, 0))
        self._lock = threading.Lock()

    def allow(self, key: str) -> RateLimitResult:
        now = time.monotonic()

        with self._lock:
            window_start, count = self._state[key]

            # New window? Reset the counter.
            if now - window_start >= self.window_seconds:
                window_start = now
                count = 0

            if count >= self.max_requests:
                retry_after = self.window_seconds - (now - window_start)
                self._state[key] = (window_start, count)
                return RateLimitResult(
                    allowed=False,
                    retry_after_seconds=max(retry_after, 0.0),
                    remaining=0,
                )

            count += 1
            self._state[key] = (window_start, count)
            return RateLimitResult(
                allowed=True,
                retry_after_seconds=0.0,
                remaining=self.max_requests - count,
            )
