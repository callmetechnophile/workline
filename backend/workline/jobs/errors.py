"""
Error classification and taxonomy for Workline asynchronous jobs.

Distinguishes non-retryable fatal faults (e.g. authorization denial, contract validation errors,
missing required attributes) from transient recoverable faults (e.g. network timeout, rate limit).
"""

from typing import Tuple


class JobExecutionError(Exception):
    """Base exception for job execution errors."""
    def __init__(self, message: str, is_retryable: bool = False):
        super().__init__(message)
        self.message = message
        self.is_retryable = is_retryable


class NonRetryableJobError(JobExecutionError):
    """Unrecoverable fault; attempts must NOT be retried."""
    def __init__(self, message: str):
        super().__init__(message, is_retryable=False)


class AuthorizationError(NonRetryableJobError):
    """Permission denied or policy violation."""
    pass


class ContractValidationError(NonRetryableJobError):
    """Input payload does not conform to required schema or contract."""
    pass


class TargetNotFoundError(NonRetryableJobError):
    """Target agent or capability could not be found."""
    pass


class TransientJobError(JobExecutionError):
    """Recoverable failure suitable for backoff and retry."""
    def __init__(self, message: str):
        super().__init__(message, is_retryable=True)


NON_RETRYABLE_SUBSTRINGS: Tuple[str, ...] = (
    "AUTHORIZATION_DENIED",
    "PERMISSION_DENIED",
    "ROUTING_FAILED",
    "NOT_FOUND",
    "VALIDATION_ERROR",
    "VALUE_ERROR",
    "CONTRACT_ERROR",
    "UNAUTHORIZED",
    "FORBIDDEN",
)


def is_error_retryable(exc: BaseException) -> bool:
    """
    Classify whether an exception is retryable.
    Returns False for NonRetryableJobError (and subclasses), or errors containing fatal status markers.
    """
    if isinstance(exc, NonRetryableJobError):
        return False
    if isinstance(exc, JobExecutionError):
        return exc.is_retryable

    err_str = str(exc).upper()
    for marker in NON_RETRYABLE_SUBSTRINGS:
        if marker in err_str:
            return False

    return True
