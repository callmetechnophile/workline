"""
Immutable Audit Trail subsystem.
"""

from backend.workline.audit.models import AuditEvent
from backend.workline.audit.logger import AuditTrail, default_audit_trail

__all__ = [
    "AuditEvent",
    "AuditTrail",
    "default_audit_trail",
]
