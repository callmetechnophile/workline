"""Payment session tracking and lifecycle persistence."""

from typing import Dict, Optional
from backend.workline.database.models import GraphEdge, GraphNode
from backend.workline.database.repositories.graph_repository import GraphRepository
from backend.workline.orders.models import PaymentSession, PaymentStatus


class PaymentSessionManager:
    """Manages payment session transitions and SurrealDB graph edges."""

    def __init__(self, graph_repo: Optional[GraphRepository] = None):
        self.graph_repo = graph_repo or GraphRepository()
        self._sessions: Dict[str, PaymentSession] = {}

    def save_session(self, session: PaymentSession) -> None:
        """Store session in memory."""
        self._sessions[session.payment_session_id] = session
        self._sessions[session.order_id] = session

    def get_session(self, session_id_or_order_id: str) -> Optional[PaymentSession]:
        """Fetch session by session ID or Order ID."""
        return self._sessions.get(session_id_or_order_id)

    async def persist_session_graph(self, session: PaymentSession, project_id: str) -> None:
        """Persist PaymentSession node and AUTHORIZES edge in SurrealDB."""
        node_id = f"pay_sess:{session.payment_session_id}"
        await self.graph_repo.save_node(
            GraphNode(
                id=node_id,
                type="PaymentSession",
                label=f"Payment ({session.asset} {session.amount:.2f} - {session.status.value})",
                data={"project_id": project_id, **session.model_dump()},
            )
        )
        await self.graph_repo.save_edge(
            GraphEdge(
                id=f"auth:{session.payment_session_id}_{session.order_id.replace(':', '_')}",
                source_id=node_id,
                target_id=session.order_id,
                relationship="AUTHORIZES",
                data={"project_id": project_id},
            )
        )
        await self.graph_repo.save_edge(
            GraphEdge(
                id=f"paid:{session.order_id.replace(':', '_')}_{session.payment_session_id}",
                source_id=session.order_id,
                target_id=node_id,
                relationship="PAID_BY",
                data={"project_id": project_id},
            )
        )
