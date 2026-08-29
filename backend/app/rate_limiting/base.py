# base.py
# Common interface for every rate limiter.
# Factory returns objects that follow this shape,
# so your code can call the same methods everywhere.

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class RateLimitResult:
    """
    Result of one rate-limit check.

    allowed: True if the request may continue
    retry_after_seconds: how long to wait if blocked (0 if allowed)
    remaining: how many requests/tokens are left in the current window
    """

    allowed: bool
    retry_after_seconds: float = 0.0
    remaining: int = 0


class RateLimiter(ABC):
    """
    Base class (interface) for rate limiters.

    key examples:
      - "user:42"
      - "ip:127.0.0.1"
      - "gemini:global"
      - "search_foods"
    """

    @abstractmethod
    def allow(self, key: str) -> RateLimitResult:
        """
        Check whether this key is allowed RIGHT NOW.
        If allowed, this call usually also consumes 1 request/token.
        """

    def is_allowed(self, key: str) -> bool:
        """Shortcut: True/False only."""
        return self.allow(key).allowed
