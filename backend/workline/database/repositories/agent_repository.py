"""SurrealDB repository for Agent Operations, Registry, Tasks, and Executions."""

import asyncio
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Dict, List, Optional
import uuid

from loguru import logger

from backend.workline.database.surrealdb import SurrealDBManager, surreal_db
from backend.workline.interoperability.capabilities import (
    AgentCapability,
    AgentStatus,
    CapabilityType,
    RiskLevel,
)
from backend.workline.interoperability.registry import ExternalAgent, AgentTrustRecord
from backend.workline.interoperability.tasks import AgentTask, TaskStatus


# Canonical Workline Architecture Cluster Definitions (R1-R5)
CANONICAL_AGENTS: List[Dict[str, Any]] = [
    # R1: Core Orchestrator & Governance
    {
        "agent_id": "RootOrchestratorAgent",
        "name": "Root Orchestrator Agent",
        "description": "ADK Root Multi-Agent Orchestrator & Lifecycle Governor managing state transitions and human checkpoints.",
        "provider": "Workline Core Engine",
        "protocol": "ADK_INTERNAL",
        "cluster_tier": "R1_CORE",
        "endpoint": "workline://r1/orchestrator",
        "version": "2.4.0",
        "status": "AVAILABLE",
        "trust_score": 1.0,
        "capabilities": [
            {
                "capability_id": "workflow_orchestration",
                "name": "Workflow Orchestration",
                "description": "Orchestrates multi-agent pipeline execution across stages.",
                "capability_type": "ORCHESTRATION",
                "risk_level": "LOW",
                "estimated_cost": 0.01,
            },
            {
                "capability_id": "lifecycle_coordination",
                "name": "Lifecycle Coordination",
                "description": "Enforces state machine transitions, invariants, and approvals.",
                "capability_type": "ORCHESTRATION",
                "risk_level": "LOW",
                "estimated_cost": 0.01,
            },
        ],
    },
    {
        "agent_id": "ProjectLifecycleOrchestrator",
        "name": "Project Lifecycle Orchestrator",
        "description": "Autonomous Project Lifecycle Orchestrator managing project phases from concept to production release.",
        "provider": "Workline Core Engine",
        "protocol": "ADK_INTERNAL",
        "cluster_tier": "R1_CORE",
        "endpoint": "workline://r1/lifecycle-orchestrator",
        "version": "2.1.0",
        "status": "AVAILABLE",
        "trust_score": 1.0,
        "capabilities": [
            {
                "capability_id": "project_lifecycle",
                "name": "Project Lifecycle Management",
                "description": "Validates state transitions and gates promotion between project milestones.",
                "capability_type": "ORCHESTRATION",
                "risk_level": "LOW",
                "estimated_cost": 0.01,
            },
        ],
    },
    # R2: Research & Literature Harvester
    {
        "agent_id": "DeepResearchAgent",
        "name": "Deep Research Agent",
        "description": "Amazon Bedrock Cross-Source Reasoning & Evidence Synthesis engine for hardware engineering tradeoffs.",
        "provider": "Workline Research Labs",
        "protocol": "AWS_BEDROCK",
        "cluster_tier": "R2_AI",
        "endpoint": "bedrock://us-east-1/claude-3-5-sonnet",
        "version": "3.0.0",
        "status": "AVAILABLE",
        "trust_score": 0.99,
        "capabilities": [
            {
                "capability_id": "deep_reasoning",
                "name": "Deep Engineering Reasoning",
                "description": "Synthesizes multi-source research into verifiable hardware decisions.",
                "capability_type": "RESEARCH",
                "risk_level": "LOW",
                "estimated_cost": 0.04,
            },
            {
                "capability_id": "tradeoff_analysis",
                "name": "Engineering Tradeoff Analysis",
                "description": "Evaluates architectural tradeoffs (efficiency, cost, thermal, safety).",
                "capability_type": "ANALYSIS",
                "risk_level": "LOW",
                "estimated_cost": 0.03,
            },
        ],
    },
    {
        "agent_id": "ResearchPaperAgent",
        "name": "Research Paper Harvester",
        "description": "Academic literature harvester querying ArXiv, Europe PMC, OpenAlex, and IEEE Xplore.",
        "provider": "Workline Research Labs",
        "protocol": "ADK_INTERNAL",
        "cluster_tier": "R2_AI",
        "endpoint": "workline://r2/paper-agent",
        "version": "2.0.0",
        "status": "AVAILABLE",
        "trust_score": 0.98,
        "capabilities": [
            {
                "capability_id": "paper_harvesting",
                "name": "Paper Harvesting",
                "description": "Harvests scientific publications, patents, and academic citations.",
                "capability_type": "RESEARCH",
                "risk_level": "LOW",
                "estimated_cost": 0.01,
            },
        ],
    },
    {
        "agent_id": "DocumentProcessingAgent",
        "name": "Document Processing Agent",
        "description": "High-throughput semiconductor datasheet and PDF technical documentation parser.",
        "provider": "Workline Research Labs",
        "protocol": "ADK_INTERNAL",
        "cluster_tier": "R2_AI",
        "endpoint": "workline://r2/doc-processing",
        "version": "2.2.0",
        "status": "AVAILABLE",
        "trust_score": 0.99,
        "capabilities": [
            {
                "capability_id": "document_parsing",
                "name": "Datasheet Parsing",
                "description": "Extracts pinouts, electrical ratings, and application circuits from PDF datasheets.",
                "capability_type": "DOCUMENT_ANALYSIS",
                "risk_level": "LOW",
                "estimated_cost": 0.02,
            },
        ],
    },
    # R3: Knowledge Graph & Semantic State
    {
        "agent_id": "EngineeringKnowledgeGraphAgent",
        "name": "Engineering Knowledge Graph Agent",
        "description": "SurrealDB Relational Knowledge Graph and state machine for semantic project telemetry.",
        "provider": "Workline Knowledge Engine",
        "protocol": "SURREAL_GRAPH",
        "cluster_tier": "R3_KNOWLEDGE",
        "endpoint": "surreal://cloud/workline-knowledge",
        "version": "2.5.0",
        "status": "AVAILABLE",
        "trust_score": 1.0,
        "capabilities": [
            {
                "capability_id": "graph_query",
                "name": "Knowledge Graph Query",
                "description": "Traverses dependency and causality edges across requirements, components, and decisions.",
                "capability_type": "KNOWLEDGE_GRAPH",
                "risk_level": "LOW",
                "estimated_cost": 0.01,
            },
            {
                "capability_id": "node_lineage",
                "name": "Lineage Tracing",
                "description": "Traces provenance and verification history from user idea to physical component.",
                "capability_type": "KNOWLEDGE_GRAPH",
                "risk_level": "LOW",
                "estimated_cost": 0.01,
            },
        ],
    },
    {
        "agent_id": "EngineeringCopilotAgent",
        "name": "Engineering Copilot Agent",
        "description": "Evidence-Grounded Conversational Engineering Copilot answering questions from verified graph state.",
        "provider": "Workline Knowledge Engine",
        "protocol": "ADK_INTERNAL",
        "cluster_tier": "R3_KNOWLEDGE",
        "endpoint": "workline://r3/copilot",
        "version": "2.0.0",
        "status": "AVAILABLE",
        "trust_score": 0.99,
        "capabilities": [
            {
                "capability_id": "engineering_copilot",
                "name": "Interactive Engineering Q&A",
                "description": "Explains design decisions and system architecture with graph evidence citations.",
                "capability_type": "COPILOT",
                "risk_level": "LOW",
                "estimated_cost": 0.02,
            },
        ],
    },
    # R4: Engineering & Multi-Physics Verification
    {
        "agent_id": "EngineeringArchitectureAgent",
        "name": "Engineering Architecture Agent",
        "description": "Subsystem architecture and electrical power distribution network (PDN) modeling engine.",
        "provider": "Workline Engineering Labs",
        "protocol": "ADK_INTERNAL",
        "cluster_tier": "R4_ENGINEERING",
        "endpoint": "workline://r4/architecture",
        "version": "2.1.0",
        "status": "AVAILABLE",
        "trust_score": 0.99,
        "capabilities": [
            {
                "capability_id": "subsystem_modeling",
                "name": "Subsystem Architecture Modeling",
                "description": "Generates block diagrams, power flow maps, and interconnect matrices.",
                "capability_type": "ARCHITECTURE",
                "risk_level": "LOW",
                "estimated_cost": 0.03,
            },
        ],
    },
    {
        "agent_id": "HardwareThermalAgent",
        "name": "Hardware Thermal Solver",
        "description": "Finite element analysis (FEA) and neural surrogate physics engine for power stage hotspot detection.",
        "provider": "Workline Engineering Labs",
        "protocol": "ADK_INTERNAL",
        "cluster_tier": "R4_ENGINEERING",
        "endpoint": "workline://r4/thermal",
        "version": "2.2.0",
        "status": "AVAILABLE",
        "trust_score": 0.98,
        "capabilities": [
            {
                "capability_id": "thermal_dissipation_check",
                "name": "Thermal Dissipation Check",
                "description": "Calculates junction temperatures and heatsink requirements under continuous load.",
                "capability_type": "THERMAL_ANALYSIS",
                "risk_level": "MEDIUM",
                "estimated_cost": 0.05,
            },
            {
                "capability_id": "fem_hotspot_analysis",
                "name": "PCB Hotspot FEA",
                "description": "Simulates 2D/3D temperature contour on copper planes and MOSFET switches.",
                "capability_type": "THERMAL_ANALYSIS",
                "risk_level": "HIGH",
                "estimated_cost": 0.10,
            },
        ],
    },
    {
        "agent_id": "EngineeringValidationAgent",
        "name": "Engineering Validation Agent",
        "description": "Electrical Design Rule Check (DRC), voltage matching, and BMS cell balancing validator.",
        "provider": "Workline Engineering Labs",
        "protocol": "ADK_INTERNAL",
        "cluster_tier": "R4_ENGINEERING",
        "endpoint": "workline://r4/validation",
        "version": "2.3.0",
        "status": "AVAILABLE",
        "trust_score": 1.0,
        "capabilities": [
            {
                "capability_id": "bms_validation",
                "name": "BMS 4S Safety & Voltage Validation",
                "description": "Verifies 4S Li-ion cell protection thresholds, OVP, UVP, OCD, and balancing topology.",
                "capability_type": "VALIDATION",
                "risk_level": "LOW",
                "estimated_cost": 0.02,
            },
            {
                "capability_id": "electrical_drc",
                "name": "Electrical DRC Verification",
                "description": "Verifies voltage rails, logic levels, and decoupling requirements across ICs.",
                "capability_type": "VALIDATION",
                "risk_level": "LOW",
                "estimated_cost": 0.02,
            },
        ],
    },
    {
        "agent_id": "ComponentPlanningAgent",
        "name": "Component Planning Agent",
        "description": "Component selection and MPN matching against verified semiconductor libraries.",
        "provider": "Workline Engineering Labs",
        "protocol": "ADK_INTERNAL",
        "cluster_tier": "R4_ENGINEERING",
        "endpoint": "workline://r4/component-planner",
        "version": "2.4.0",
        "status": "AVAILABLE",
        "trust_score": 0.99,
        "capabilities": [
            {
                "capability_id": "component_selection",
                "name": "Optimal Component Selection",
                "description": "Selects active and passive components matching electrical specifications.",
                "capability_type": "COMPONENT_PLANNING",
                "risk_level": "LOW",
                "estimated_cost": 0.02,
            },
        ],
    },
    # R5: Procurement, Sourcing & x402
    {
        "agent_id": "BOMOptimizationAgent",
        "name": "BOM Optimization Agent",
        "description": "Multi-distributor BOM cost optimizer, lead time minimizer, and supplier diversity engine.",
        "provider": "Workline Supply Chain Labs",
        "protocol": "ADK_INTERNAL",
        "cluster_tier": "R5_PROCUREMENT",
        "endpoint": "workline://r5/bom-optimizer",
        "version": "2.2.0",
        "status": "AVAILABLE",
        "trust_score": 0.99,
        "capabilities": [
            {
                "capability_id": "bom_optimization",
                "name": "Multi-Source BOM Optimization",
                "description": "Minimizes landed BOM cost across DigiKey, Mouser, and verified distributors.",
                "capability_type": "OPTIMIZATION",
                "risk_level": "LOW",
                "estimated_cost": 0.03,
            },
        ],
    },
    {
        "agent_id": "NexarMCPClient",
        "name": "Nexar / Octopart MCP Client",
        "description": "Real-time semiconductor inventory, pricing, lead time, and lifecycle status via Nexar MCP.",
        "provider": "Workline Sourcing Gateway",
        "protocol": "MCP_STREAM",
        "cluster_tier": "R5_PROCUREMENT",
        "endpoint": "mcp://nexar/octopart-v4",
        "version": "1.8.0",
        "status": "AVAILABLE",
        "trust_score": 1.0,
        "capabilities": [
            {
                "capability_id": "nexar_pricing_query",
                "name": "Live Distributor Pricing & Stock",
                "description": "Queries real-time distributor stock and volume pricing tiers via Nexar GraphQL.",
                "capability_type": "PROCUREMENT",
                "risk_level": "LOW",
                "estimated_cost": 0.01,
            },
        ],
    },
    # External Interoperability Network Agents
    {
        "agent_id": "ThermalSolver",
        "name": "ThermalSolver",
        "description": "High-precision finite element and PINN thermal solver for electronic PCBs and power stages.",
        "provider": "Workline Physics Lab",
        "protocol": "BINDU_A2A",
        "cluster_tier": "EXTERNAL_INTEROP",
        "endpoint": "bindu://local/thermal-solver",
        "version": "2.1.0",
        "status": "AVAILABLE",
        "trust_score": 1.0,
        "capabilities": [
            {
                "capability_id": "thermal_simulation",
                "name": "Thermal Simulation",
                "description": "Simulates steady-state temperature distribution and thermal dissipation on PCB boards.",
                "capability_type": "THERMAL_ANALYSIS",
                "risk_level": "MEDIUM",
                "estimated_cost": 0.05,
            },
            {
                "capability_id": "thermal_optimization",
                "name": "Thermal Placement Optimization",
                "description": "Optimizes component placement to eliminate localized hotspots.",
                "capability_type": "OPTIMIZATION",
                "risk_level": "HIGH",
                "estimated_cost": 0.15,
            },
        ],
    },
    {
        "agent_id": "CodeReviewAgent",
        "name": "CodeReviewAgent",
        "description": "Static analysis, security vulnerability scanning, and MISRA/Embedded C linting.",
        "provider": "Bindu Agent Network",
        "protocol": "BINDU_A2A",
        "cluster_tier": "EXTERNAL_INTEROP",
        "endpoint": "bindu://network/code-review",
        "version": "1.4.0",
        "status": "AVAILABLE",
        "trust_score": 0.98,
        "capabilities": [
            {
                "capability_id": "code_review",
                "name": "Firmware & Driver Code Review",
                "description": "Performs automated security audit and MISRA-C compliance inspection on source files.",
                "capability_type": "CODE_REVIEW",
                "risk_level": "LOW",
                "estimated_cost": 0.01,
            },
        ],
    },
    {
        "agent_id": "ResearchAgent",
        "name": "ResearchAgent",
        "description": "Deep technical research and semiconductor datasheet comparison via Corsair tools.",
        "provider": "Corsair Integrations",
        "protocol": "CORSAIR",
        "cluster_tier": "EXTERNAL_INTEROP",
        "endpoint": "corsair://tools/datasheet-research",
        "version": "3.0.0",
        "status": "AVAILABLE",
        "trust_score": 0.97,
        "capabilities": [
            {
                "capability_id": "research",
                "name": "Semiconductor Deep Research",
                "description": "Synthesizes academic papers, whitepapers, and component errata.",
                "capability_type": "RESEARCH",
                "risk_level": "LOW",
                "estimated_cost": 0.02,
            },
            {
                "capability_id": "document_analysis",
                "name": "Technical Document Analysis",
                "description": "Parses PDF datasheets, pinout tables, and timing diagrams.",
                "capability_type": "DOCUMENT_ANALYSIS",
                "risk_level": "LOW",
                "estimated_cost": 0.02,
            },
        ],
    },
]


class AgentRepository:
    """SurrealDB and durable in-memory repository for Workline Agent Operations."""

    def __init__(self, db: SurrealDBManager = surreal_db):
        self.db = db
        self._memory_agents: Dict[str, Dict[str, Any]] = {}
        self._memory_tasks: Dict[str, Dict[str, Any]] = {}
        self._memory_executions: Dict[str, Dict[str, Any]] = {}
        self._memory_audits: List[Dict[str, Any]] = []
        self._memory_project_agents: Dict[str, List[str]] = {}
        self._synced = True

        # Load canonical agents into memory
        for ag in CANONICAL_AGENTS:
            ag_copy = dict(ag)
            caps = []
            for c in ag_copy.get("capabilities", []):
                c_copy = dict(c)
                c_copy.setdefault("agent_id", ag_copy["agent_id"])
                c_copy.setdefault("availability", True)
                c_copy.setdefault("version", ag_copy.get("version", "1.0.0"))
                caps.append(c_copy)
            ag_copy["capabilities"] = caps
            self._memory_agents[ag_copy["agent_id"]] = ag_copy

    async def sync_to_surrealdb(self) -> None:
        """Sync canonical agents and project bindings to SurrealDB concurrently."""
        if self._synced:
            return
        if not await self.db.is_connected():
            try:
                await self.db.connect()
            except Exception as e:
                logger.warning(f"SurrealDB connect during sync skipped: {e}")
                return

        async def _upsert_ag(ag):
            try:
                aid = ag["agent_id"]
                await self.db.upsert(f"agent:{aid}", ag)
            except Exception as e:
                logger.debug(f"Agent upsert to SurrealDB fallback: {e}")

        await asyncio.gather(*[_upsert_ag(ag) for ag in self._memory_agents.values()])
        self._synced = True

    async def list_agents(
        self,
        project_id: Optional[str] = None,
        status: Optional[str] = None,
        cluster: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List all agents, optionally filtered by project, status, or cluster tier."""
        if not self._synced:
            # Sync in background so HTTP response is instant
            asyncio.create_task(self.sync_to_surrealdb())

        agents = list(self._memory_agents.values())

        if status:
            agents = [a for a in agents if a.get("status") == status]
        if cluster:
            agents = [a for a in agents if a.get("cluster_tier") == cluster]

        return agents

    async def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Fetch an agent by ID."""
        if agent_id in self._memory_agents:
            return self._memory_agents[agent_id]

        if await self.db.is_connected():
            try:
                res = await self.db.select(f"agent:{agent_id}")
                if res and isinstance(res, list) and len(res) > 0:
                    item = dict(res[0])
                    self._memory_agents[agent_id] = item
                    return item
            except Exception:
                pass
        return None

    async def register_agent(self, manifest: Dict[str, Any], project_id: Optional[str] = None) -> Dict[str, Any]:
        """Register an agent manifest into SurrealDB and active registry."""
        aid = manifest.get("agent_id") or f"agent_{uuid.uuid4().hex[:8]}"
        manifest["agent_id"] = aid
        manifest.setdefault("version", "1.0.0")
        manifest.setdefault("status", "AVAILABLE")
        manifest.setdefault("capabilities", [])
        manifest.setdefault("trust_score", 1.0)
        manifest.setdefault("cluster_tier", "EXTERNAL_INTEROP")
        manifest["updated_at"] = datetime.now(timezone.utc).isoformat()
        manifest["created_at"] = manifest.get("created_at") or datetime.now(timezone.utc).isoformat()

        # Update in-memory
        self._memory_agents[aid] = manifest

        # Persist to SurrealDB
        if await self.db.is_connected():
            try:
                await self.db.upsert(f"agent:{aid}", manifest)
                reg_record = {
                    "registration_id": f"reg_{uuid.uuid4().hex[:10]}",
                    "agent_id": aid,
                    "name": manifest.get("name"),
                    "protocol": manifest.get("protocol"),
                    "project_id": project_id,
                    "registered_at": manifest["created_at"],
                }
                await self.db.create("agent_registration", reg_record)

                if project_id:
                    await self.bind_agent_to_project(project_id, aid)
            except Exception as e:
                logger.warning(f"SurrealDB register_agent fallback: {e}")

        return manifest

    async def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent."""
        if agent_id in self._memory_agents:
            del self._memory_agents[agent_id]

        if await self.db.is_connected():
            try:
                await self.db.delete(f"agent:{agent_id}")
                return True
            except Exception as e:
                logger.warning(f"SurrealDB unregister_agent fallback: {e}")
        return True

    async def bind_agent_to_project(self, project_id: str, agent_id: str) -> None:
        """Bind an agent to a project in SurrealDB."""
        p_list = self._memory_project_agents.setdefault(project_id, [])
        if agent_id not in p_list:
            p_list.append(agent_id)

        if await self.db.is_connected():
            try:
                record = {
                    "project_id": project_id,
                    "agent_id": agent_id,
                    "bound_at": datetime.now(timezone.utc).isoformat(),
                }
                await self.db.upsert(f"project_agent:{project_id}_{agent_id}", record)
            except Exception as e:
                logger.debug(f"SurrealDB bind_agent_to_project fallback: {e}")

    # ========================================================================
    # Task Operations
    # ========================================================================

    async def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create and persist a task."""
        tid = task_data.get("task_id") or f"task_{uuid.uuid4().hex[:10]}"
        task_data["task_id"] = tid
        task_data.setdefault("created_at", datetime.now(timezone.utc).isoformat())

        self._memory_tasks[tid] = task_data

        if await self.db.is_connected():
            try:
                await self.db.upsert(f"task:{tid}", task_data)
            except Exception as e:
                logger.debug(f"SurrealDB create_task fallback: {e}")

        return task_data

    async def update_task(self, task_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing task."""
        if task_id in self._memory_tasks:
            self._memory_tasks[task_id].update(updates)
            task_data = self._memory_tasks[task_id]

            if await self.db.is_connected():
                try:
                    await self.db.upsert(f"task:{task_id}", task_data)
                except Exception as e:
                    logger.debug(f"SurrealDB update_task fallback: {e}")

            return task_data
        return None

    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Fetch task by ID."""
        if task_id in self._memory_tasks:
            return self._memory_tasks[task_id]

        if await self.db.is_connected():
            try:
                res = await self.db.select(f"task:{task_id}")
                if res and isinstance(res, list) and len(res) > 0:
                    item = dict(res[0])
                    self._memory_tasks[task_id] = item
                    return item
            except Exception:
                pass
        return None

    async def list_tasks(
        self,
        project_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List tasks, optionally filtered by project and status."""
        if await self.db.is_connected():
            try:
                surreal_tasks = await self.db.select("task")
                if isinstance(surreal_tasks, list):
                    for t in surreal_tasks:
                        item = dict(t)
                        tid = item.get("task_id")
                        if tid:
                            self._memory_tasks[tid] = item
            except Exception as e:
                logger.debug(f"SurrealDB select task fallback: {e}")

        tasks = list(self._memory_tasks.values())

        if project_id:
            # Match either exact project_id or sanitized slug
            p_slug = project_id.lower().replace(" ", "_")
            tasks = [
                t for t in tasks
                if t.get("project_id") == project_id
                or t.get("project_id") == p_slug
                or (t.get("project_id") and p_slug in t.get("project_id", "").lower())
            ]

        if status:
            tasks = [t for t in tasks if t.get("status") == status]

        # Sort newest first
        tasks.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return tasks

    # ========================================================================
    # Execution & ArmorIQ Audit Operations
    # ========================================================================

    async def create_execution(self, exec_data: Dict[str, Any]) -> Dict[str, Any]:
        """Record an agent execution timeline step."""
        eid = exec_data.get("execution_id") or f"exec_{uuid.uuid4().hex[:10]}"
        exec_data["execution_id"] = eid
        exec_data.setdefault("created_at", datetime.now(timezone.utc).isoformat())

        self._memory_executions[eid] = exec_data

        if await self.db.is_connected():
            try:
                await self.db.upsert(f"execution:{eid}", exec_data)
            except Exception as e:
                logger.debug(f"SurrealDB create_execution fallback: {e}")

        return exec_data

    async def list_executions(self, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List executions for timeline display."""
        if await self.db.is_connected():
            try:
                surreal_execs = await self.db.select("execution")
                if isinstance(surreal_execs, list):
                    for ex in surreal_execs:
                        item = dict(ex)
                        eid = item.get("execution_id")
                        if eid:
                            self._memory_executions[eid] = item
            except Exception as e:
                logger.debug(f"SurrealDB select execution fallback: {e}")

        execs = list(self._memory_executions.values())

        if project_id:
            p_slug = project_id.lower().replace(" ", "_")
            execs = [
                e for e in execs
                if e.get("project_id") == project_id
                or e.get("project_id") == p_slug
                or (e.get("project_id") and p_slug in e.get("project_id", "").lower())
            ]

        execs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return execs

    async def record_armoriq_audit(self, audit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Record an immutable ArmorIQ cryptographic audit event."""
        audit_id = audit_data.get("audit_id") or f"audit_{uuid.uuid4().hex[:12]}"
        audit_data["audit_id"] = audit_id
        audit_data.setdefault("timestamp", datetime.now(timezone.utc).isoformat())

        self._memory_audits.append(audit_data)

        if await self.db.is_connected():
            try:
                await self.db.upsert(f"armoriq_audit:{audit_id}", audit_data)
            except Exception as e:
                logger.debug(f"SurrealDB record_armoriq_audit fallback: {e}")

        return audit_data


# Singleton repository instance
agent_repository = AgentRepository()
