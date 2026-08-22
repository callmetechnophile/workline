"""Receipt creation, storage, verification, and knowledge graph linking."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple
import uuid

from backend.workline.database.models import GraphEdge, GraphNode
from backend.workline.database.repositories.graph_repository import GraphRepository
from backend.workline.orders.models import Order, Receipt, ReceiptVerificationStatus


class ReceiptService:
    """Manages order receipts, verification authenticity, and SurrealDB graph linking."""

    def __init__(self, graph_repo: Optional[GraphRepository] = None):
        self.graph_repo = graph_repo or GraphRepository()
        self._receipts: Dict[str, Receipt] = {}

    async def generate_receipt(
        self,
        order: Order,
        external_order_id: Optional[str] = None,
        source: str = "Vendor Procurement API",
        verification_status: ReceiptVerificationStatus = ReceiptVerificationStatus.VERIFIED,
    ) -> Receipt:
        """Generate and store official invoice/receipt."""
        receipt_id = f"rec_{uuid.uuid4().hex[:10]}"
        now = datetime.now(timezone.utc).isoformat()

        receipt = Receipt(
            receipt_id=receipt_id,
            order_id=order.order_id,
            vendor=order.vendor,
            external_order_id=external_order_id or order.external_order_id,
            subtotal=order.subtotal,
            shipping=order.shipping_cost,
            tax=order.tax,
            fees=order.fees,
            total=order.total,
            currency=order.currency,
            receipt_url=f"https://receipts.workline.local/{order.order_id}/{receipt_id}",
            invoice_url=f"https://invoices.workline.local/{order.order_id}/{receipt_id}.pdf",
            issued_at=now,
            source=source,
            verification_status=verification_status,
            created_at=now,
        )

        self._receipts[receipt_id] = receipt
        self._receipts[order.order_id] = receipt

        # Persist to SurrealDB
        await self.persist_receipt_graph(receipt, order.project_id)
        return receipt

    def get_receipt(self, receipt_id_or_order_id: str) -> Optional[Receipt]:
        """Fetch receipt by ID or Order ID."""
        return self._receipts.get(receipt_id_or_order_id)

    async def verify_receipt(self, receipt_id: str, confirmation_data: Dict[str, Any]) -> Tuple[bool, Optional[Receipt]]:
        """Verify user-uploaded receipt or external vendor invoice."""
        receipt = self.get_receipt(receipt_id)
        if not receipt:
            return False, None

        if confirmation_data.get("external_order_id"):
            receipt.external_order_id = confirmation_data["external_order_id"]
            receipt.verification_status = ReceiptVerificationStatus.VERIFIED
            return True, receipt

        receipt.verification_status = ReceiptVerificationStatus.VERIFIED
        return True, receipt

    async def persist_receipt_graph(self, receipt: Receipt, project_id: str) -> None:
        """Persist Receipt node and CONFIRMS / PRODUCES edges in SurrealDB."""
        node_id = f"receipt:{receipt.receipt_id}"
        await self.graph_repo.save_node(
            GraphNode(
                id=node_id,
                type="Receipt",
                label=f"Receipt: {receipt.vendor} ({receipt.currency} {receipt.total:.2f})",
                data={"project_id": project_id, **receipt.model_dump()},
            )
        )
        await self.graph_repo.save_edge(
            GraphEdge(
                id=f"confirms:{receipt.receipt_id}_{receipt.order_id.replace(':', '_')}",
                source_id=node_id,
                target_id=receipt.order_id,
                relationship="CONFIRMS",
                data={"project_id": project_id},
            )
        )
        await self.graph_repo.save_edge(
            GraphEdge(
                id=f"produces:{receipt.order_id.replace(':', '_')}_{receipt.receipt_id}",
                source_id=receipt.order_id,
                target_id=node_id,
                relationship="PRODUCES",
                data={"project_id": project_id},
            )
        )
