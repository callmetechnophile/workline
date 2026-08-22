"""Capability-limited tool implementations for Workline ADK agents.

Wraps SurrealDB repositories, Qdrant semantic storage, and Procurement Engine.
Prevents arbitrary shell execution or unchecked SQL queries.
"""

from typing import Any, Dict, List, Optional
from backend.workline.database.models import GraphEdge, GraphNode, ProjectModel
from backend.workline.database.repositories.collaboration_repository import CollaborationRepository
from backend.workline.database.repositories.graph_repository import GraphRepository
from backend.workline.database.repositories.project_repository import ProjectRepository
from backend.workline.procurement.engine import ProcurementEngine, procurement_engine
from backend.workline.procurement.models import (
    BOM,
    ComponentCandidate,
    ComponentRequirement,
    DeterministicValidationReport,
)
from backend.workline.retrieval.qdrant import (
    COLLECTION_DOCUMENTS,
    QdrantManager,
    qdrant_manager,
)


class WorklineToolSuite:
    """Toolbox exposing safe domain methods to ADK agents."""

    def __init__(
        self,
        project_repo: Optional[ProjectRepository] = None,
        graph_repo: Optional[GraphRepository] = None,
        collab_repo: Optional[CollaborationRepository] = None,
        qdrant: Optional[QdrantManager] = None,
        procurement: Optional[ProcurementEngine] = None,
    ):
        self.project_repo = project_repo or ProjectRepository()
        self.graph_repo = graph_repo or GraphRepository()
        self.collab_repo = collab_repo or CollaborationRepository()
        self.qdrant = qdrant or QdrantManager()
        self.procurement = procurement or procurement_engine

    async def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Fetch project details from SurrealDB."""
        proj = await self.project_repo.get_project(project_id)
        return proj.model_dump() if proj else None

    async def update_project_state(self, project_id: str, updates: Dict[str, Any]) -> bool:
        """Update lifecycle stage or metadata in SurrealDB."""
        updated = await self.project_repo.update_project(project_id, updates)
        return updated is not None

    async def save_graph_node(self, node_id: str, node_type: str, label: str, data: Dict[str, Any]) -> bool:
        """Add or update an entity node in the engineering knowledge graph."""
        node = GraphNode(id=node_id, type=node_type, label=label, data=data)
        return await self.graph_repo.save_node(node)

    async def save_graph_edge(
        self, edge_id: str, source_id: str, target_id: str, relationship: str, data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Create a directed relationship in SurrealDB (e.g. CONTAINS, CONNECTS_TO, POWERED_BY, BLOCKS, REQUIRES)."""
        edge = GraphEdge(id=edge_id, source_id=source_id, target_id=target_id, relationship=relationship, data=data or {})
        return await self.graph_repo.save_edge(edge)

    async def query_project_graph(self, project_id: str) -> Dict[str, Any]:
        """Fetch full project graph from SurrealDB."""
        payload = await self.graph_repo.get_project_graph(project_id)
        return payload.model_dump()

    def search_knowledge_base(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Perform semantic vector retrieval across research documents."""
        return self.qdrant.search(collection=COLLECTION_DOCUMENTS, query=query, limit=limit)

    def index_research_document(self, doc_id: str, text: str, metadata: Dict[str, Any]) -> bool:
        """Index a document chunk or technical note into Qdrant."""
        return self.qdrant.index_document(collection=COLLECTION_DOCUMENTS, doc_id=doc_id, text=text, payload=metadata)

    async def save_bom(self, project_id: str, bom_items: List[Dict[str, Any]]) -> bool:
        """Persist BOM items to project record in SurrealDB."""
        return await self.update_project_state(project_id, {"bom": bom_items})

    # ==================== PROCUREMENT TOOLS ====================

    async def search_components(self, query: str) -> List[Dict[str, Any]]:
        """Search candidate hardware components across supported vendor catalogs."""
        candidates = await self.procurement.search_engine.search_vendors(query)
        return [c.model_dump() for c in candidates]

    def get_component(self, component_id: str) -> Optional[Dict[str, Any]]:
        """Fetch cached canonical component candidate specifications."""
        cand = self.procurement.get_component(component_id)
        return cand.model_dump() if cand else None

    async def validate_component(
        self,
        candidate_dict: Dict[str, Any],
        requirement_dict: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute deterministic technical validation on candidate specifications against requirements."""
        cand = ComponentCandidate.model_validate(candidate_dict)
        req = ComponentRequirement.model_validate(requirement_dict)
        report = self.procurement.validator.validate(cand, req)
        return report.model_dump()

    def estimate_shipping_cost(self, vendor: str, subtotal_inr: float) -> Dict[str, Any]:
        """Calculate landed shipping estimate for a vendor and subtotal."""
        est = self.procurement.optimizer.shipping_calc.estimate_shipping(vendor, subtotal_inr)
        return est.model_dump()

    async def generate_engineering_bom(
        self,
        project_id: str,
        requirements: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Run complete procurement optimization pipeline and compile authoritative BOM."""
        req_models = [ComponentRequirement.model_validate(r) for r in requirements]
        bom, plan = await self.procurement.generate_project_bom(project_id, req_models)
        return {
            "bom": bom.model_dump(),
            "procurement_plan": plan.model_dump(),
        }

    # ==================== ITEM ORDERING & PAYMENT TOOLS ====================

    async def create_order_plan(self, project_id: str, bom_id: str) -> Dict[str, Any]:
        """Prepare an itemized OrderPlan blueprint from an approved BOM."""
        from backend.workline.orders.service import order_service
        plan = await order_service.create_order_plan(project_id, bom_id)
        return plan.model_dump()

    async def create_orders(self, plan_id: str, user_role: str = "ENGINEER") -> List[Dict[str, Any]]:
        """Split an OrderPlan into vendor-specific draft orders in READY_FOR_APPROVAL status."""
        from backend.workline.orders.service import order_service
        plan = order_service._plans.get(plan_id)
        if not plan:
            raise ValueError(f"Plan '{plan_id}' not found.")
        orders = await order_service.create_orders_from_plan(plan, user_role=user_role)
        return [o.model_dump() for o in orders]

    async def revalidate_order_prices(self, order_id: str) -> Dict[str, Any]:
        """Revalidate live vendor prices and stock availability before payment."""
        from backend.workline.orders.service import order_service
        _, report = await order_service.revalidate_order(order_id)
        return report.model_dump()

    async def get_order_preview(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Fetch order details and financial breakdown."""
        from backend.workline.orders.service import order_service
        order = await order_service.get_order(order_id)
        return order.model_dump() if order else None

    async def request_order_approval(
        self, order_id: str, user_role: str = "OWNER", approved_by: str = "Lead Systems Engineer"
    ) -> Dict[str, Any]:
        """Human approval checkpoint transitioning order to APPROVED and PAYMENT_REQUIRED."""
        from backend.workline.orders.service import order_service
        ok, order, err = await order_service.approve_order(
            order_id=order_id, user_role=user_role, approved_by=approved_by, is_agent=False
        )
        return {"success": ok, "order": order.model_dump() if order else None, "error": err}

    async def create_payment_request(self, order_id: str) -> Dict[str, Any]:
        """Construct an x402 payment challenge for an approved order."""
        from backend.workline.orders.service import order_service
        ok, req, err = await order_service.create_payment_request(order_id)
        return {"success": ok, "payment_request": req.model_dump() if req else None, "error": err}

    async def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """Inspect payment session status."""
        from backend.workline.orders.service import order_service
        session = order_service.session_manager.get_session(payment_id)
        return session.model_dump() if session else {"status": "NOT_FOUND"}

    async def verify_and_submit_order(
        self, order_id: str, payment_id: str, signed_proof: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Verify cryptographic payment proof and execute vendor order / manual checkout kit."""
        from backend.workline.orders.service import order_service
        ok, order, receipt, err = await order_service.verify_payment_and_execute(order_id, payment_id, signed_proof)
        return {
            "success": ok,
            "order": order.model_dump() if order else None,
            "receipt": receipt.model_dump() if receipt else None,
            "error": err,
        }

    async def get_order_status(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Fetch live order status."""
        from backend.workline.orders.service import order_service
        order = await order_service.get_order(order_id)
        return order.model_dump() if order else None

    async def get_receipt(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Fetch verified purchase receipt or invoice."""
        from backend.workline.orders.service import order_service
        receipt = order_service.receipt_service.get_receipt(order_id)
        return receipt.model_dump() if receipt else None

    async def cancel_order(self, order_id: str, reason: str = "User cancelled") -> Dict[str, Any]:
        """Cancel an active draft or unfulfilled order."""
        from backend.workline.orders.service import order_service
        ok, order, err = await order_service.cancel_order(order_id, reason=reason)
        return {"success": ok, "order": order.model_dump() if order else None, "error": err}

    # ==================== PCB ENGINEERING & PINN PHYSICS TOOLS ====================

    async def create_pcb_project(
        self,
        project_id: str,
        bom_id: Optional[str] = None,
        board_width: float = 80.0,
        board_height: float = 60.0,
    ) -> Dict[str, Any]:
        """Construct authoritative PCBProject from project BOM with footprints, stackup, and netlist."""
        from backend.workline.pcb.services import pcb_service
        proj = await pcb_service.create_pcb_project(project_id, bom_id, board_width, board_height)
        return proj.model_dump()

    async def get_pcb_project(self, pcb_id: str) -> Optional[Dict[str, Any]]:
        """Fetch complete PCB project state."""
        from backend.workline.pcb.services import pcb_service
        proj = await pcb_service.get_pcb_project(pcb_id)
        return proj.model_dump() if proj else None

    async def get_pcb_components(self, pcb_id: str) -> List[Dict[str, Any]]:
        """Fetch PCB component instances and spatial coordinates."""
        from backend.workline.pcb.services import pcb_service
        proj = await pcb_service.get_pcb_project(pcb_id)
        return [c.model_dump() for c in proj.components.values()] if proj else []

    async def get_pcb_nets(self, pcb_id: str) -> List[Dict[str, Any]]:
        """Fetch PCB electrical nets and netlist connectivity."""
        from backend.workline.pcb.services import pcb_service
        proj = await pcb_service.get_pcb_project(pcb_id)
        return [n.model_dump() for n in proj.nets.values()] if proj else []

    async def get_footprint(self, footprint_id: str) -> Optional[Dict[str, Any]]:
        """Fetch normalized footprint specification and land pattern pads."""
        from backend.workline.pcb.engine.builder import PCBBuilder
        fps = PCBBuilder.get_standard_footprints()
        fp = fps.get(footprint_id)
        return fp.model_dump() if fp else None

    async def assign_footprint(self, pcb_id: str, component_id: str, footprint_id: str) -> Dict[str, Any]:
        """Assign or update component package footprint."""
        from backend.workline.pcb.services import pcb_service
        proj = await pcb_service.get_pcb_project(pcb_id)
        if not proj or component_id not in proj.components:
            return {"success": False, "error": "Component not found"}
        proj.components[component_id].footprint_id = footprint_id
        await pcb_service.update_pcb_project(proj)
        return {"success": True, "component": proj.components[component_id].model_dump()}

    async def get_pcb_constraints(self, pcb_id: str) -> Optional[Dict[str, Any]]:
        """Fetch traceable design rules and numerical constraint limits."""
        from backend.workline.pcb.services import pcb_service
        proj = await pcb_service.get_pcb_project(pcb_id)
        return proj.constraints.model_dump() if proj else None

    async def create_pcb_constraint(
        self, pcb_id: str, name: str, value: float, unit: str, source: str = "USER"
    ) -> Dict[str, Any]:
        """Add or update an explicit design constraint with engineering provenance."""
        from backend.workline.pcb.models.constraints import ConstraintSource, PCBConstraintItem
        from backend.workline.pcb.services import pcb_service
        proj = await pcb_service.get_pcb_project(pcb_id)
        if not proj:
            return {"success": False, "error": "PCB project not found"}
        item = PCBConstraintItem(name=name, value=value, unit=unit, source=ConstraintSource(source))
        setattr(proj.constraints, name, item)
        await pcb_service.update_pcb_project(proj)
        return {"success": True, "constraint": item.model_dump()}

    async def validate_pcb(self, pcb_id: str) -> Dict[str, Any]:
        """Execute full 12-check PCB structural, electrical, and thermal validation."""
        from backend.workline.pcb.services import pcb_validation_service
        report = await pcb_validation_service.validate_pcb_project(pcb_id)
        return report.model_dump()

    async def generate_physics_features(self, pcb_id: str) -> List[Dict[str, Any]]:
        """Extract dense deterministic physics feature vector across PCB domain."""
        from backend.workline.pcb.services import physics_service
        features = await physics_service.extract_features(pcb_id)
        return [f.model_dump() for f in features]

    async def generate_thermal_dataset(self, pcb_id: str) -> Dict[str, Any]:
        """Produce ground-truth training dataset from reference thermal solver with train/val/test splits."""
        from backend.workline.pcb.services import physics_service
        dataset = await physics_service.generate_thermal_dataset(pcb_id)
        return dataset.model_dump()

    async def train_thermal_pinn(self, pcb_id: str, epochs: int = 50, learning_rate: float = 0.008) -> Dict[str, Any]:
        """Train PCB Thermal PINN model on generated physics dataset."""
        from backend.workline.pcb.services import pcb_optimization_service
        result = await pcb_optimization_service.train_pinn(pcb_id, epochs=epochs, learning_rate=learning_rate)
        return result.model_dump()

    async def run_thermal_pinn(self, pcb_id: str) -> Dict[str, Any]:
        """Evaluate fast PINN predicted 2D thermal distribution and component hotspots."""
        from backend.workline.pcb.services import pcb_optimization_service
        res = await pcb_optimization_service.run_pinn_inference(pcb_id)
        return res.model_dump()

    async def optimize_thermal_placement(self, pcb_id: str, max_iterations: int = 50) -> Dict[str, Any]:
        """Run thermal placement optimization loop minimizing peak hotspot temperatures."""
        from backend.workline.pcb.services import pcb_optimization_service
        proj, res = await pcb_optimization_service.optimize_placement(pcb_id, max_iterations=max_iterations)
        return {"project": proj.model_dump(), "optimization_result": res.model_dump()}

    async def get_pinn_metrics(self, pcb_id: str) -> Optional[Dict[str, Any]]:
        """Fetch quantitative PINN validation metrics (MAE, RMSE, Max Absolute Error)."""
        from backend.workline.pcb.services import pcb_optimization_service
        res = pcb_optimization_service.get_latest_metrics(pcb_id)
        return res.model_dump() if res else None
