"""
Workline AI — Team Join Attempt Brute-Force Rate Limiter.

Protects 6-character alphanumeric join codes against brute-force enumeration.
Enforces per-user and per-IP attempt limits with automatic cooldowns.
"""

import time
from collections import defaultdict
from typing import Dict, List, Tuple
from loguru import logger


class JoinAttemptRateLimiter:
    """
    In-memory rate limiter tracking failed join attempts within a sliding time window.
    """

    def __init__(
        self,
        max_failures: int = 5,
        window_seconds: int = 60,
        cooldown_seconds: int = 120,
    ):
        self.max_failures = max_failures
        self.window_seconds = window_seconds
        self.cooldown_seconds = cooldown_seconds

        # identifier -> list of failure timestamps
        self._failures: Dict[str, List[float]] = defaultdict(list)
        # identifier -> cooldown expiry timestamp
        self._cooldowns: Dict[str, float] = {}

    def is_rate_limited(self, identifier: str) -> Tuple[bool, int]:
        """
        Checks if the given identifier (user_id or IP) is currently blocked.
        Returns: (is_blocked, seconds_remaining)
        """
        now = time.time()

        # 1. Check active cooldown
        if identifier in self._cooldowns:
            cooldown_expiry = self._cooldowns[identifier]
            if now < cooldown_expiry:
                remaining = int(cooldown_expiry - now) + 1
                return True, remaining
            else:
                del self._cooldowns[identifier]
                self._failures[identifier] = []

        # 2. Check failure count in sliding window
        window_start = now - self.window_seconds
        recent_failures = [t for t in self._failures[identifier] if t >= window_start]
        self._failures[identifier] = recent_failures

        if len(recent_failures) >= self.max_failures:
            # Trigger new cooldown
            self._cooldowns[identifier] = now + self.cooldown_seconds
            logger.warning(
                f"[RateLimiter] Cooldown triggered for '{identifier}' after {len(recent_failures)} failed join attempts."
            )
            return True, self.cooldown_seconds

        return False, 0

    def record_attempt(self, identifier: str, success: bool) -> None:
        """Records the outcome of a join attempt."""
        now = time.time()
        if success:
            # Clear failure history on successful join
            if identifier in self._failures:
                del self._failures[identifier]
            if identifier in self._cooldowns:
                del self._cooldowns[identifier]
        else:
            self._failures[identifier].append(now)

    def reset_for_test(self) -> None:
        """Resets all tracking states (useful for testing)."""
        self._failures.clear()
        self._cooldowns.clear()


# Global singleton instance
join_rate_limiter = JoinAttemptRateLimiter()
