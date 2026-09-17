"""
Agent capability registry for WorkflowGuide AI (Section 14).
Registers Agents #1–#13 with capabilities, required authorization, and execution levels.
"""

from typing import Dict, List, Optional
from research_agents.project_lifecycle_orchestrator.schemas import AgentDescriptor


class AgentRegistry:
    """Central registry of all specialized engineering agents in the pipeline."""

    def __init__(self):
        self._agents: Dict[str, AgentDescriptor] = {}
        self._register_default_agents()

    def _register_default_agents(self):
        agents = [
            AgentDescriptor(
                agent_id="Agent #1",
                agent_name="ResearchPaperAgent",
                capabilities=["research.papers", "research.arxiv", "research.freephdlabor"],
                execution_level="read_only",
                status="available",
            ),
            AgentDescriptor(
                agent_id="Agent #2",
                agent_name="WebResearchAgent",
                capabilities=["research.web", "research.tavily", "research.anakin"],
                execution_level="read_only",
                status="available",
            ),
            AgentDescriptor(
                agent_id="Agent #3",
                agent_name="DocumentProcessingAgent",
                capabilities=["document.parse", "document.extract_facts", "document.extract_entities"],
                execution_level="read_only",
                status="available",
            ),
            AgentDescriptor(
                agent_id="Agent #4",
                agent_name="DeepResearchAgent",
                capabilities=["research.synthesize", "research.cross_reason"],
                execution_level="read_only",
                status="available",
            ),
            AgentDescriptor(
                agent_id="Agent #5",
                agent_name="EngineeringSynthesisAgent",
                capabilities=["synthesis.requirements", "synthesis.decisions", "synthesis.tradeoffs"],
                execution_level="read_only",
                status="available",
            ),
            AgentDescriptor(
                agent_id="Agent #6",
                agent_name="EngineeringArchitectureAgent",
                capabilities=["architecture.design", "architecture.subsystems", "architecture.interfaces"],
                execution_level="read_only",
                status="available",
            ),
            AgentDescriptor(
                agent_id="Agent #7",
                agent_name="ComponentPlanningAgent",
                capabilities=["bom.plan", "bom.select_components"],
                execution_level="read_only",
                status="available",
            ),
            AgentDescriptor(
                agent_id="Agent #8",
                agent_name="BOMOptimizationAgent",
                capabilities=["bom.optimize", "procurement.landed_cost", "logistics.transit"],
                execution_level="read_only",
                status="available",
            ),
            AgentDescriptor(
                agent_id="Agent #9",
                agent_name="EngineeringValidationAgent",
                capabilities=["validation.design_rules", "validation.electrical", "validation.power"],
                execution_level="read_only",
                status="available",
            ),
            AgentDescriptor(
                agent_id="Agent #10",
                agent_name="ProjectExecutionAgent",
                capabilities=["planning.work_packages", "planning.tasks", "planning.dependencies"],
                execution_level="planning",
                status="available",
            ),
            AgentDescriptor(
                agent_id="Agent #11",
                agent_name="EngineeringExecutionAgent",
                capabilities=["execution.scoped", "execution.filesystem", "execution.tools"],
                required_authorization=["filesystem.write", "shell", "test_runner"],
                execution_level="isolated_execution",
                status="available",
            ),
            AgentDescriptor(
                agent_id="Agent #12",
                agent_name="VerificationQAAgent",
                capabilities=["qa.verify", "qa.pytest", "qa.security_scan", "qa.conformance"],
                required_authorization=["test_runner", "pytest", "security_scan"],
                execution_level="read_only",
                status="available",
            ),
            AgentDescriptor(
                agent_id="Agent #13",
                agent_name="EngineeringKnowledgeGraphAgent",
                capabilities=["graph.query", "graph.trace", "graph.impact", "graph.state", "graph.ingest"],
                required_authorization=["graph.read", "graph.insert", "graph.update"],
                execution_level="read_only",
                status="available",
            ),
            AgentDescriptor(
                agent_id="Agent #14",
                agent_name="ProjectLifecycleOrchestrator",
                capabilities=["lifecycle.orchestrate", "lifecycle.gates", "lifecycle.events"],
                execution_level="privileged_execution",
                status="available",
            ),
            AgentDescriptor(
                agent_id="Agent #15",
                agent_name="EngineeringCopilotAgent",
                capabilities=["copilot.chat", "copilot.query", "copilot.explain"],
                execution_level="read_only",
                status="available",
            ),
            AgentDescriptor(
                agent_id="Agent #16",
                agent_name="EngineeringChangeControlAgent",
                capabilities=["change.request", "change.impact", "change.approve", "change.revalidate"],
                execution_level="privileged_execution",
                status="available",
            ),
            AgentDescriptor(
                agent_id="Agent #17",
                agent_name="EngineeringComplianceAgent",
                capabilities=["compliance.evaluate", "compliance.rules", "compliance.standards", "compliance.gates"],
                execution_level="read_only",
                status="available",
            ),
            AgentDescriptor(
                agent_id="Agent #18",
                agent_name="EngineeringVerificationAgent",
                capabilities=["verification.plan", "verification.execute", "verification.evidence", "verification.vnv"],
                execution_level="read_only",
                status="available",
            ),
            AgentDescriptor(
                agent_id="Agent #19",
                agent_name="EngineeringSimulationAgent",
                capabilities=["simulation.thermal", "simulation.power", "simulation.digital_twin", "simulation.stress"],
                execution_level="read_only",
                status="available",
            ),
            AgentDescriptor(
                agent_id="Agent #20",
                agent_name="EngineeringOptimizationAgent",
                capabilities=["optimization.pareto", "optimization.trade_space", "optimization.candidates"],
                execution_level="read_only",
                status="available",
            ),
            AgentDescriptor(
                agent_id="Agent #21",
                agent_name="EngineeringRiskAgent",
                capabilities=[
                    "risk_analysis",
                    "fmea",
                    "failure_analysis",
                    "risk_prioritization",
                    "risk_mitigation",
                    "fault_propagation",
                    "risk_traceability",
                    "risk_reassessment",
                ],
                execution_level="read_only",
                status="available",
            ),
            AgentDescriptor(
                agent_id="Agent #22",
                agent_name="SecurityThreatModelingAgent",
                capabilities=[
                    "threat_modeling",
                    "attack_surface_analysis",
                    "security_risk_analysis",
                    "security_control_analysis",
                    "security_reassessment",
                    "security_test_generation",
                ],
                execution_level="read_only",
                status="available",
            ),
            AgentDescriptor(
                agent_id="Agent #24",
                agent_name="ManufacturingDFMAgent",
                capabilities=[
                    "dfm_analysis",
                    "dfa_analysis",
                    "manufacturing_process_analysis",
                    "assembly_process_analysis",
                    "tolerance_manufacturability_analysis",
                    "material_process_analysis",
                    "tooling_analysis",
                    "fixture_analysis",
                    "manufacturing_risk_analysis",
                    "manufacturing_variation_analysis",
                    "inspection_analysis",
                    "process_sequence_analysis",
                    "manufacturability_assessment",
                    "assembly_assessment",
                    "design_for_automation_analysis",
                    "manufacturing_recommendation",
                    "manufacturing_traceability",
                ],
                execution_level="read_only",
                status="available",
            ),
            AgentDescriptor(
                agent_id="Agent #25",
                agent_name="CostSupplyChainAgent",
                capabilities=[
                    "cost_estimation",
                    "bom_cost_analysis",
                    "cost_driver_analysis",
                    "supplier_analysis",
                    "sourcing_analysis",
                    "lead_time_analysis",
                    "moq_analysis",
                    "supply_risk_analysis",
                    "make_vs_buy_analysis",
                    "volume_cost_curve",
                    "cost_impact_analysis",
                    "cost_dashboard",
                    "cost_report",
                ],
                execution_level="read_only",
                status="available",
            ),
            AgentDescriptor(
                agent_id="Agent #26",
                agent_name="DeploymentOpsAgent",
                capabilities=[
                    "deployment_analysis",
                    "deployment_planning",
                    "deployment_readiness",
                    "installation_analysis",
                    "commissioning_planning",
                    "configuration_management",
                    "environment_validation",
                    "dependency_analysis",
                    "operational_readiness",
                    "observability_planning",
                    "health_analysis",
                    "alert_analysis",
                    "incident_analysis",
                    "troubleshooting",
                    "recovery_planning",
                    "rollback_planning",
                    "backup_restore_planning",
                    "maintenance_planning",
                    "serviceability_analysis",
                    "spare_parts_planning",
                    "operational_lifecycle",
                    "decommission_planning",
                    "operational_traceability",
                ],
                execution_level="read_only",
                status="available",
            ),
            AgentDescriptor(
                agent_id="agent.27",
                agent_name="TechDocAgent",
                capabilities=[
                    "create_document", "get_document", "list_documents",
                    "review_document", "approve_document", "publish_document",
                    "check_traceability", "detect_conflicts", "compare_documents",
                    "export_document", "quality_check",
                    "document_lifecycle_management", "revision_control",
                    "authority_validation", "conflict_detection",
                    "traceability_link_management", "quality_scoring",
                    "controlled_publication", "armoriq_authorization_check",
                    "document_comparison", "template_management",
                    "zero_fabrication_enforcement", "self_approval_block",
                    "engineering_document_generation",
                ],
                execution_level="isolated_execution",
                status="available",
            ),
        ]
        for ag in agents:
            self._agents[ag.agent_name] = ag
            self._agents[ag.agent_id] = ag

    def get_agent(self, identifier: str) -> Optional[AgentDescriptor]:
        return self._agents.get(identifier)

    def list_agents(self) -> List[AgentDescriptor]:
        unique = {a.agent_name: a for a in self._agents.values()}
        return list(unique.values())

    def is_agent_ready(self, agent_name: str, required_auth: Optional[List[str]] = None) -> bool:
        ag = self.get_agent(agent_name)
        if not ag or ag.status != "available":
            return False
        return True
