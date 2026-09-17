"""
Job state definitions for Workline asynchronous execution framework.
"""

from enum import Enum


class JobState(str, Enum):
    """Lifecycle states for asynchronous jobs."""
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    RETRYING = "RETRYING"
    DEAD_LETTER = "DEAD_LETTER"

    @property
    def is_terminal(self) -> bool:
        """Return True if state is terminal (no further transitions allowed)."""
        return self in (
            JobState.SUCCEEDED,
            JobState.FAILED,
            JobState.CANCELLED,
            JobState.DEAD_LETTER,
        )

    @property
    def is_active(self) -> bool:
        """Return True if job is currently active or waiting."""
        return self in (
            JobState.PENDING,
            JobState.QUEUED,
            JobState.RUNNING,
            JobState.RETRYING,
        )
