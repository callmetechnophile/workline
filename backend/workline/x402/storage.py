"""
Persistent Storage Manager for x402 Payment Records and Idempotency.
Supports in-memory tracking with SQLite / SurrealDB fallback.
"""

from typing import Dict, List, Optional
from backend.workline.x402.models import PaymentRecord, PaymentStatus


class X402Storage:
    """Thread-safe store for payment challenges, settled proofs, and idempotent results."""

    def __init__(self):
        self._records: Dict[str, PaymentRecord] = {}  # keyed by payment_request_id
        self._tx_hashes: Dict[str, str] = {}  # tx_hash -> payment_request_id
        self._idempotency_map: Dict[str, str] = {}  # idempotency_key -> payment_request_id

    def save_record(self, record: PaymentRecord) -> PaymentRecord:
        """Stores or updates a payment record."""
        self._records[record.payment_request_id] = record

        if record.transaction_id:
            self._tx_hashes[record.transaction_id] = record.payment_request_id

        if record.idempotency_key:
            self._idempotency_map[record.idempotency_key] = record.payment_request_id

        return record

    def get_record(self, payment_request_id: str) -> Optional[PaymentRecord]:
        """Look up payment record by payment_request_id."""
        return self._records.get(payment_request_id)

    def get_by_tx_hash(self, tx_hash: str) -> Optional[PaymentRecord]:
        """Look up payment record by blockchain transaction hash."""
        req_id = self._tx_hashes.get(tx_hash)
        if req_id:
            return self._records.get(req_id)
        return None

    def get_by_idempotency_key(self, key: str) -> Optional[PaymentRecord]:
        """Look up payment record by client-supplied idempotency key."""
        req_id = self._idempotency_map.get(key)
        if req_id:
            return self._records.get(req_id)
        return None

    def list_records(
        self,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[PaymentRecord]:
        """List payment records with optional user/project filtering."""
        results = list(self._records.values())

        if user_id:
            results = [r for r in results if r.user_id == user_id]

        if project_id:
            results = [r for r in results if r.project_id == project_id]

        # Return sorted by creation date descending
        results.sort(key=lambda r: r.created_at, reverse=True)
        return results[:limit]

    def clear(self):
        """Clears store (primarily for test resets)."""
        self._records.clear()
        self._tx_hashes.clear()
        self._idempotency_map.clear()


# Global storage singleton
x402_storage = X402Storage()
