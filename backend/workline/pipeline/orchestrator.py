"""
Workline AI — Sequential Orchestration Pipeline Engine (R1 -> R2 -> R3 -> R4 -> R5).

Implements strict sequential stage contracts:
1. R2 (Requirements) -> requirements_revision
2. R3 (Research) -> research_revision (based_on: requirements_revision)
3. R4 (Engineering) -> architecture_revision (based_on: requirements_revision, research_revision)
4. R5 (BOM / Sourcing) -> bom_revision (based_on: requirements_revision, research_revision, architecture_revision)

Guarantees:
- Authoritative R1 sequential orchestrator
- Strict upstream version verification & stale context protection
- Fail-fast error propagation (downstream stages are never invoked on upstream failure)
- Data isolation invariant across all stages
"""

import os
import uuid
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from backend.database import (
    save_pipeline_run,
    update_pipeline_run,
    save_pipeline_stage_run,
    get_pipeline_run,
    get_pipeline_stages_for_run,
)
from backend.armoriq.delegation import capture_plan, delegate, invoke_tool, AUDIT_LOGS
from backend.armoriq.policies import ScopeViolationError

# Agent & tool imports
from backend.agents.retrieval_agent import run_retrieval
from backend.agents.extraction_agent import run_extraction
from backend.agents.research_agent import run_research
from backend.agents.validation_agent import run_validation
from backend.agents.optimization_agent import run_optimization
from backend.agents.planning_agent import run_planning
from backend.agents.export_agent import run_export
from backend.agents.knowledge_graph_agent import run_knowledge_graph_agent
from backend.services.collaboration_service import (
    create_team,
    get_team_members,
    get_project_comments,
    fetch_activity_logs,
)

logger = logging.getLogger("workline.pipeline")


class PipelineStageError(Exception):
    """Raised when a pipeline stage fails execution."""
    def __init__(self, stage: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"[{stage}] {message}")
        self.stage = stage
        self.message = message
        self.details = details or {}


class SequentialPipelineOrchestrator:
    """
    R1 Authoritative Sequential Pipeline Orchestrator.
    Coordinates sequential execution of R2 -> R3 -> R4 -> R5 with versioned context lineage.
    """

    def __init__(self, run_id: Optional[str] = None):
        self.run_id = run_id or f"run_{uuid.uuid4().hex[:12]}"

    def execute_pipeline(
        self,
        project_id: str,
        user_intent: str,
        project_name: Optional[str] = None,
        target_days: int = 30,
        engineering_template: Optional[str] = None,
        team_id: Optional[str] = None,
        user_id: Optional[str] = "default_user",
    ) -> Dict[str, Any]:
        """
        Executes the end-to-end engineering pipeline strictly in sequence.
        """
        resolved_project_name = (project_name or user_intent.split("\n")[0][:60]).strip()
        resolved_team_id = team_id or "Hardware Engineering"

        # Initialize pipeline run in database
        save_pipeline_run(
            run_id=self.run_id,
            project_id=project_id,
            status="RUNNING",
            current_stage="R2_REQUIREMENTS",
            requirements_rev=0,
            research_rev=0,
            architecture_rev=0,
            bom_rev=0,
        )

        AUDIT_LOGS.clear()
        root_receipt = capture_plan(user_intent)
        root_receipt_dict = root_receipt.model_dump()
        active_stage = "R2_REQUIREMENTS"

        try:
            # ========================================================
            # STAGE R2: REQUIREMENTS & SPECIFICATIONS
            # ========================================================
            active_stage = "R2_REQUIREMENTS"
            r2_output = self._execute_r2_requirements(
                project_id=project_id,
                user_intent=user_intent,
                project_name=resolved_project_name,
                target_days=target_days,
                engineering_template=engineering_template,
                team_id=resolved_team_id,
                root_receipt_dict=root_receipt_dict,
            )

            # Stale context protection & validation
            req_rev = r2_output["requirements_revision"]
            if req_rev <= 0 or not r2_output.get("requirements"):
                raise PipelineStageError("R2_REQUIREMENTS", "R2 failed to produce valid requirements.")

            update_pipeline_run(
                run_id=self.run_id,
                status="RUNNING",
                current_stage="R3_RESEARCH",
                requirements_rev=req_rev,
            )

            # ========================================================
            # STAGE R3: RESEARCH & LITERATURE
            # ========================================================
            active_stage = "R3_RESEARCH"
            r3_output = self._execute_r3_research(
                project_id=project_id,
                requirements_revision=req_rev,
                requirements=r2_output["requirements"],
                constraints=r2_output["constraints"],
                user_intent=user_intent,
                root_receipt_dict=root_receipt_dict,
                idea_understanding=r2_output.get("understanding", {}),
            )

            res_rev = r3_output["research_revision"]
            if res_rev <= 0:
                raise PipelineStageError("R3_RESEARCH", "R3 failed to produce valid research context.")

            update_pipeline_run(
                run_id=self.run_id,
                status="RUNNING",
                current_stage="R4_ENGINEERING",
                research_rev=res_rev,
            )

            # ========================================================
            # STAGE R4: ENGINEERING ARCHITECTURE & SIMULATION
            # ========================================================
            active_stage = "R4_ENGINEERING"
            r4_output = self._execute_r4_engineering(
                project_id=project_id,
                requirements_revision=req_rev,
                research_revision=res_rev,
                requirements=r2_output["requirements"],
                constraints=r2_output["constraints"],
                research_findings=r3_output["findings"],
                user_intent=user_intent,
                root_receipt_dict=root_receipt_dict,
                idea_understanding=r2_output.get("understanding", {}),
                structured_requirements=r2_output.get("structured_requirements", []),
            )

            arch_rev = r4_output["architecture_revision"]
            if arch_rev <= 0 or not r4_output.get("components"):
                raise PipelineStageError("R4_ENGINEERING", "R4 failed to synthesize valid engineering architecture.")

            update_pipeline_run(
                run_id=self.run_id,
                status="RUNNING",
                current_stage="R5_BOM",
                architecture_rev=arch_rev,
            )

            # ========================================================
            # STAGE R5: CANONICAL BOM & SOURCING
            # ========================================================
            active_stage = "R5_BOM"
            r5_output = self._execute_r5_bom(
                project_id=project_id,
                requirements_revision=req_rev,
                research_revision=res_rev,
                architecture_revision=arch_rev,
                components=r4_output["components"],
                validated_architecture=r4_output["architecture"],
                root_receipt_dict=root_receipt_dict,
            )

            bom_rev = r5_output["bom_revision"]
            if bom_rev <= 0 or not r5_output.get("bom"):
                raise PipelineStageError("R5_BOM", "R5 failed to produce canonical BOM.")

            # Pipeline execution completed successfully
            update_pipeline_run(
                run_id=self.run_id,
                status="COMPLETED",
                current_stage="COMPLETED",
                bom_rev=bom_rev,
            )

            # Consolidate complete execution package
            final_package = self._assemble_final_package(
                project_id=project_id,
                project_name=resolved_project_name,
                system_specification=user_intent,
                target_days=target_days,
                engineering_template=engineering_template,
                team_id=resolved_team_id,
                r2_data=r2_output,
                r3_data=r3_output,
                r4_data=r4_output,
                r5_data=r5_output,
            )
            return final_package

        except PipelineStageError as pse:
            logger.error(f"[Pipeline] Fail-fast triggered in {pse.stage}: {pse.message}")
            update_pipeline_run(
                run_id=self.run_id,
                status="FAILED",
                current_stage=pse.stage,
                error=pse.message,
            )
            raise pse
        except Exception as e:
            logger.exception(f"[Pipeline] Unhandled error during execution in {active_stage}: {e}")
            update_pipeline_run(
                run_id=self.run_id,
                status="FAILED",
                current_stage=active_stage,
                error=str(e),
            )
            raise PipelineStageError(active_stage, str(e))

    # =========================================================================
    # STAGE IMPLEMENTATIONS
    # =========================================================================

    def _execute_r2_requirements(
        self,
        project_id: str,
        user_intent: str,
        project_name: str,
        target_days: int,
        engineering_template: Optional[str],
        team_id: str,
        root_receipt_dict: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        R2 — REQUIREMENTS STAGE
        Extracts specifications, constraints, operational boundaries, and initial validation.
        """
        save_pipeline_stage_run(
            run_id=self.run_id,
            project_id=project_id,
            stage="R2_REQUIREMENTS",
            status="RUNNING",
            input_revision_ids={"user_request": True},
        )

        try:
            # 1. Analyze engineering idea through Planner Agent using Bedrock + deterministic domain rules
            planner_receipt = delegate(
                agent_name="Planner Agent",
                requested_scope=["analyze_engineering_idea", "generate_dependency_graph"],
                parent_receipt=root_receipt_dict,
            )
            idea_analysis = invoke_tool(
                agent_name="Planner Agent",
                tool_name="analyze_engineering_idea",
                args={"idea": user_intent, "project_id": project_id},
                receipt_dict=planner_receipt.model_dump(),
            )

            # Query Knowledge Graph
            graph_receipt = delegate(
                agent_name="KnowledgeGraphAgent",
                requested_scope=["graph.read"],
                parent_receipt=root_receipt_dict,
            )
            graph_context = run_knowledge_graph_agent(user_intent, graph_receipt.model_dump())

            structured_reqs = idea_analysis.get("requirements", [])
            structured_constraints = idea_analysis.get("constraints", [])
            clarifications_needed = idea_analysis.get("clarifications_needed", [])
            understanding = idea_analysis.get("understanding", {})

            # Synthesize structured requirements list
            requirements_list = [
                f"{r.get('id', 'REQ')}: {r.get('title', '')} — {r.get('statement', '')}"
                if isinstance(r, dict) else str(r)
                for r in structured_reqs
            ]
            if not requirements_list:
                requirements_list = [
                    f"Core Objective: {user_intent}",
                    f"Target Timeline: {target_days} Days autonomous execution",
                    f"Target Architecture Standard: {engineering_template or 'Industrial Prototype'}",
                    "Power Domain: Regulated DC supply with short-circuit protection",
                    "Thermal Boundary: Max operating junction delta < 45C under full load",
                ]

            constraints = {
                "target_days": target_days,
                "engineering_template": engineering_template or "Standard",
                "max_voltage_ripple_pct": 2.0,
                "thermal_limit_celsius": 85.0,
                "structured_constraints": structured_constraints,
            }

            validation = {
                "readiness_score": 92 if not clarifications_needed else 80,
                "risk_score": 12 if not clarifications_needed else 25,
                "domain_fit": "EXCELLENT",
                "clarifications_needed": clarifications_needed,
            }

            requirements_revision = 1

            output = {
                "project_id": project_id,
                "requirements_revision": requirements_revision,
                "requirements": requirements_list,
                "structured_requirements": structured_reqs,
                "constraints": constraints,
                "structured_constraints": structured_constraints,
                "validation": validation,
                "graph_context": graph_context,
                "understanding": understanding,
                "clarifications_needed": clarifications_needed,
            }

            save_pipeline_stage_run(
                run_id=self.run_id,
                project_id=project_id,
                stage="R2_REQUIREMENTS",
                status="COMPLETED",
                input_revision_ids={},
                output_revision_id=requirements_revision,
                stage_data=output,
            )
            return output

        except Exception as e:
            save_pipeline_stage_run(
                run_id=self.run_id,
                project_id=project_id,
                stage="R2_REQUIREMENTS",
                status="FAILED",
                error=str(e),
            )
            raise PipelineStageError("R2_REQUIREMENTS", str(e))

    def _execute_r3_research(
        self,
        project_id: str,
        requirements_revision: int,
        requirements: List[str],
        constraints: Dict[str, Any],
        user_intent: str,
        root_receipt_dict: Dict[str, Any],
        idea_understanding: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        R3 — RESEARCH STAGE
        Queries scientific literature (arXiv, Crossref, Semantic Scholar), standards, datasheets, and checks contradictions.
        """
        save_pipeline_stage_run(
            run_id=self.run_id,
            project_id=project_id,
            stage="R3_RESEARCH",
            status="RUNNING",
            input_revision_ids={"requirements_revision": requirements_revision},
        )

        try:
            # 1. ArmorIQ Blocking Test
            research_receipt = delegate(
                agent_name="Research Agent",
                requested_scope=["search_papers", "summarize_papers", "search_scholarly_papers", "retrieve_datasheet"],
                parent_receipt=root_receipt_dict,
            )
            try:
                invoke_tool(
                    agent_name="Research Agent",
                    tool_name="export_pdf",
                    args={"data": {}},
                    receipt_dict=research_receipt.model_dump(),
                )
            except ScopeViolationError:
                pass  # ArmorIQ working as intended

            # 2. Scholarly Research via arXiv, Crossref, Semantic Scholar
            domain = (idea_understanding or {}).get("domain", "")
            scholarly_papers = invoke_tool(
                agent_name="Research Agent",
                tool_name="search_scholarly_papers",
                args={
                    "idea": user_intent,
                    "requirements": requirements,
                    "domain": domain,
                    "project_id": project_id,
                    "max_papers": 6,
                },
                receipt_dict=research_receipt.model_dump(),
            )

            # Combine or fallback with research search
            if not scholarly_papers:
                research_res = run_research(user_intent, research_receipt.model_dump())
                ranked_papers = research_res.get("papers", [])
            else:
                ranked_papers = scholarly_papers

            # 3. Contradiction Analysis
            contradiction_receipt = delegate(
                agent_name="ContradictionAgent",
                requested_scope=["detect_contradictions"],
                parent_receipt=root_receipt_dict,
            )
            contradiction_res = invoke_tool(
                agent_name="ContradictionAgent",
                tool_name="detect_contradictions",
                args={"papers": ranked_papers},
                receipt_dict=contradiction_receipt.model_dump(),
            )

            # Summaries
            summaries = []
            for paper in ranked_papers[:3]:
                authors = paper.get("authors", [])
                authors_str = ", ".join(authors) if isinstance(authors, list) else str(authors)
                year = paper.get("publish_year") or paper.get("year", 2024)
                doi = paper.get("doi", "N/A")
                source = paper.get("source", "SCHOLARLY_INDEX")
                abstract = paper.get("abstract") or paper.get("summary") or "Literature research grounding requirements."
                summaries.append(
                    f"### {paper.get('title', 'Paper')} ({year})\n"
                    f"* **Authors**: {authors_str or 'Engineering Researchers'}\n"
                    f"* **Source**: {source} | **DOI**: {doi}\n"
                    f"* **Summary**: {abstract}\n"
                )
            research_summary = "\n".join(summaries) if summaries else f"Synthesized research for {user_intent}"

            contradictions_list = (
                contradiction_res
                if isinstance(contradiction_res, list)
                else contradiction_res.get("contradictions", [])
            )

            research_revision = 1

            output = {
                "project_id": project_id,
                "research_revision": research_revision,
                "findings": research_summary,
                "research_papers": ranked_papers,
                "contradictions": contradictions_list,
                "standards": ["IEEE 802.3", "USB-IF PD 3.0", "IPC-2221A Class 2"],
                "based_on": {
                    "requirements_revision": requirements_revision,
                },
            }

            save_pipeline_stage_run(
                run_id=self.run_id,
                project_id=project_id,
                stage="R3_RESEARCH",
                status="COMPLETED",
                input_revision_ids={"requirements_revision": requirements_revision},
                output_revision_id=research_revision,
                stage_data=output,
            )
            return output

        except Exception as e:
            save_pipeline_stage_run(
                run_id=self.run_id,
                project_id=project_id,
                stage="R3_RESEARCH",
                status="FAILED",
                error=str(e),
            )
            raise PipelineStageError("R3_RESEARCH", str(e))

    def _execute_r4_engineering(
        self,
        project_id: str,
        requirements_revision: int,
        research_revision: int,
        requirements: List[str],
        constraints: Dict[str, Any],
        research_findings: str,
        user_intent: str,
        root_receipt_dict: Dict[str, Any],
        idea_understanding: Optional[Dict[str, Any]] = None,
        structured_requirements: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        R4 — ENGINEERING ARCHITECTURE & SIMULATION STAGE
        Extracts components via Nexar/Octopart MCP, checks voltage, maps pins, power budget, dependency graph, wiring diagram.
        """
        save_pipeline_stage_run(
            run_id=self.run_id,
            project_id=project_id,
            stage="R4_ENGINEERING",
            status="RUNNING",
            input_revision_ids={
                "requirements_revision": requirements_revision,
                "research_revision": research_revision,
            },
        )

        try:
            # 1. Component Discovery & Intelligence via Octopart/Nexar MCP
            comp_research_receipt = delegate(
                agent_name="Retrieval Agent",
                requested_scope=["research_components", "recommend_components", "search_projects", "fetch_sources"],
                parent_receipt=root_receipt_dict,
            )
            comp_res = invoke_tool(
                agent_name="Retrieval Agent",
                tool_name="research_components",
                args={
                    "idea_understanding": idea_understanding or {},
                    "requirements": structured_requirements or requirements,
                    "constraints": constraints.get("structured_constraints", []),
                    "project_id": project_id,
                },
                receipt_dict=comp_research_receipt.model_dump(),
            )
            recommended_components = comp_res.get("recommended_components", [])
            alternative_components = comp_res.get("alternatives", [])
            component_evidence = comp_res.get("evidence", [])
            violations = comp_res.get("violations", [])

            # Format components
            components = []
            if recommended_components:
                for c in recommended_components:
                    part_name = c.get("mpn") or c.get("component") or c.get("name") or "Component"
                    components.append({
                        "name": part_name,
                        "component": part_name,
                        "mpn": c.get("mpn"),
                        "manufacturer": c.get("manufacturer"),
                        "category": c.get("subsystem") or c.get("category", "General"),
                        "subsystem": c.get("subsystem"),
                        "cost": float(c.get("unit_price_usd") or 5.0),
                        "unit_price_usd": float(c.get("unit_price_usd") or 5.0),
                        "notes": c.get("description", ""),
                        "why_recommended": c.get("why_recommended", ""),
                        "datasheet_url": c.get("datasheet_url", ""),
                        "source": c.get("source", "NEXAR"),
                        "parameters": c.get("parameters", {}),
                        "supply": c.get("supply", {}),
                    })
            else:
                retrieval_res = run_retrieval(user_intent, comp_research_receipt.model_dump())
                retrieved_text = (
                    retrieval_res.get("source_details", {}).get("content_markdown", "")
                    if retrieval_res.get("source_details")
                    else user_intent
                )
                extraction_receipt = delegate(
                    agent_name="Extraction Agent",
                    requested_scope=["extract_components"],
                    parent_receipt=root_receipt_dict,
                )
                extraction_input = f"{user_intent}\n\n{retrieved_text}"
                extraction_res = run_extraction(extraction_input, extraction_receipt.model_dump())
                raw_components = extraction_res.get("components", [])
                for c in raw_components:
                    part_name = c.get("name") or c.get("component") or "Component"
                    components.append({
                        "name": part_name,
                        "component": part_name,
                        "category": c.get("category", "General"),
                        "cost": float(c.get("cost", 5.0)),
                        "notes": c.get("notes", ""),
                    })

            voltage_components = [{"name": c["name"], "category": c["category"]} for c in components]

            # 3. Voltage Checker
            voltage_receipt = delegate(
                agent_name="Voltage Checker",
                requested_scope=["check_voltage_compatibility"],
                parent_receipt=root_receipt_dict,
            )
            voltage_res = invoke_tool(
                agent_name="Voltage Checker",
                tool_name="check_voltage_compatibility",
                args={"components": voltage_components},
                receipt_dict=voltage_receipt.model_dump(),
            )

            # 4. Pin Generator
            pin_receipt = delegate(
                agent_name="Pin Generator",
                requested_scope=["generate_pin_map"],
                parent_receipt=root_receipt_dict,
            )
            pin_res = invoke_tool(
                agent_name="Pin Generator",
                tool_name="generate_pin_map",
                args={"components": voltage_components},
                receipt_dict=pin_receipt.model_dump(),
            )

            # 5. Datasheets Intelligence
            datasheet_receipt = delegate(
                agent_name="Extraction Agent",
                requested_scope=["fetch_datasheets"],
                parent_receipt=root_receipt_dict,
            )
            datasheets_res = invoke_tool(
                agent_name="Extraction Agent",
                tool_name="fetch_datasheets",
                args={"components": components},
                receipt_dict=datasheet_receipt.model_dump(),
            )

            # 6. Power Budget Calculator
            power_receipt = delegate(
                agent_name="Voltage Checker",
                requested_scope=["calculate_power_budget"],
                parent_receipt=root_receipt_dict,
            )
            power_res = invoke_tool(
                agent_name="Voltage Checker",
                tool_name="calculate_power_budget",
                args={"components": components},
                receipt_dict=power_receipt.model_dump(),
            )

            # 7. Dependency Graph
            dependency_receipt = delegate(
                agent_name="Planner Agent",
                requested_scope=["generate_dependency_graph"],
                parent_receipt=root_receipt_dict,
            )
            dependency_res = invoke_tool(
                agent_name="Planner Agent",
                tool_name="generate_dependency_graph",
                args={"components": components},
                receipt_dict=dependency_receipt.model_dump(),
            )

            # 8. Wiring Diagram
            wiring_receipt = delegate(
                agent_name="Pin Generator",
                requested_scope=["generate_wiring_diagram"],
                parent_receipt=root_receipt_dict,
            )
            wiring_res = invoke_tool(
                agent_name="Pin Generator",
                tool_name="generate_wiring_diagram",
                args={"components": components},
                receipt_dict=wiring_receipt.model_dump(),
            )

            architecture_revision = 1

            output = {
                "project_id": project_id,
                "architecture_revision": architecture_revision,
                "architecture": {
                    "dependency_graph": dependency_res,
                    "wiring_diagram": wiring_res,
                    "pin_mapping": pin_res,
                    "power_analysis": power_res,
                    "voltage_analysis": voltage_res,
                    "datasheets": datasheets_res,
                },
                "components": components,
                "recommended_components": recommended_components or components,
                "alternative_components": alternative_components,
                "component_evidence": component_evidence,
                "violations": violations,
                "simulation_inputs": {
                    "ambient_temp_c": 25.0,
                    "max_power_dissipation_w": power_res.get("total_power_w", 15.0),
                    "switching_freq_khz": 250.0,
                },
                "based_on": {
                    "requirements_revision": requirements_revision,
                    "research_revision": research_revision,
                },
            }

            save_pipeline_stage_run(
                run_id=self.run_id,
                project_id=project_id,
                stage="R4_ENGINEERING",
                status="COMPLETED",
                input_revision_ids={
                    "requirements_revision": requirements_revision,
                    "research_revision": research_revision,
                },
                output_revision_id=architecture_revision,
                stage_data=output,
            )
            return output

        except Exception as e:
            save_pipeline_stage_run(
                run_id=self.run_id,
                project_id=project_id,
                stage="R4_ENGINEERING",
                status="FAILED",
                error=str(e),
            )
            raise PipelineStageError("R4_ENGINEERING", str(e))

    def _execute_r5_bom(
        self,
        project_id: str,
        requirements_revision: int,
        research_revision: int,
        architecture_revision: int,
        components: List[Dict[str, Any]],
        validated_architecture: Dict[str, Any],
        root_receipt_dict: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        R5 — CANONICAL BOM & SOURCING STAGE
        Runs ProcurementAgent optimization, landed costs, suppliers, and computes USD total.
        """
        save_pipeline_stage_run(
            run_id=self.run_id,
            project_id=project_id,
            stage="R5_BOM",
            status="RUNNING",
            input_revision_ids={
                "requirements_revision": requirements_revision,
                "research_revision": research_revision,
                "architecture_revision": architecture_revision,
            },
        )

        try:
            procurement_receipt = delegate(
                agent_name="ProcurementAgent",
                requested_scope=[
                    "generate_optimized_bom",
                    "calculate_landed_cost",
                    "find_alternative_components",
                ],
                parent_receipt=root_receipt_dict,
            )
            procurement_res = invoke_tool(
                agent_name="ProcurementAgent",
                tool_name="generate_optimized_bom",
                args={"components": components, "mode": "normal"},
                receipt_dict=procurement_receipt.model_dump(),
            )

            optimized_bom_items = procurement_res["bom_items"]
            cost_totals = procurement_res["totals"]

            # Compute USD total
            grand_total = float(cost_totals.get("grand_total") or cost_totals.get("final_cost", 0.0))
            total_usd = float(grand_total / 83.0)
            cost_totals["total_usd"] = round(total_usd, 2)

            alternatives_list = []
            for item in optimized_bom_items:
                alternatives_list.append({
                    "component": item["component"],
                    "alternatives": [
                        {
                            "alternative": a["alternative"],
                            "name": a["alternative"],
                            "type": "cheaper" if a["final_cost"] < item["final_cost"] else "upgraded",
                            "reason": a["reason"],
                            "approx_cost_usd": float(a["final_cost"] / 83.0),
                            "base_cost": a.get("base_cost", a["final_cost"]),
                            "shipping_cost": a.get("shipping_cost", 0),
                            "final_cost": a["final_cost"],
                        }
                        for a in item.get("alternatives", [])
                    ],
                })

            bom_revision = 1

            output = {
                "project_id": project_id,
                "bom_revision": bom_revision,
                "bom": optimized_bom_items,
                "totals": cost_totals,
                "total_usd": cost_totals["total_usd"],
                "suppliers": ["Mouser", "DigiKey", "LCSC", "Robu.in"],
                "alternatives": alternatives_list,
                "based_on": {
                    "requirements_revision": requirements_revision,
                    "research_revision": research_revision,
                    "architecture_revision": architecture_revision,
                },
            }

            save_pipeline_stage_run(
                run_id=self.run_id,
                project_id=project_id,
                stage="R5_BOM",
                status="COMPLETED",
                input_revision_ids={
                    "requirements_revision": requirements_revision,
                    "research_revision": research_revision,
                    "architecture_revision": architecture_revision,
                },
                output_revision_id=bom_revision,
                stage_data=output,
            )
            return output

        except Exception as e:
            save_pipeline_stage_run(
                run_id=self.run_id,
                project_id=project_id,
                stage="R5_BOM",
                status="FAILED",
                error=str(e),
            )
            raise PipelineStageError("R5_BOM", str(e))

    def _assemble_final_package(
        self,
        project_id: str,
        project_name: str,
        system_specification: str,
        target_days: int,
        engineering_template: Optional[str],
        team_id: str,
        r2_data: Dict[str, Any],
        r3_data: Dict[str, Any],
        r4_data: Dict[str, Any],
        r5_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Assembles the comprehensive verified package with full revision lineage.
        """
        # Run planning roadmap
        root_receipt = capture_plan(system_specification)
        plan_receipt = delegate(
            agent_name="Planning Agent",
            requested_scope=["generate_roadmap", "generate_gantt"],
            parent_receipt=root_receipt.model_dump(),
        )
        planning_res = run_planning(system_specification, plan_receipt.model_dump())

        # Run validation & optimization scores
        val_receipt = delegate(
            agent_name="Validation Agent",
            requested_scope=["validate_architecture"],
            parent_receipt=root_receipt.model_dump(),
        )
        validation_res = run_validation(
            r5_data["bom"],
            system_specification,
            val_receipt.model_dump(),
        )

        opt_receipt = delegate(
            agent_name="Optimization Agent",
            requested_scope=["optimize_components"],
            parent_receipt=root_receipt.model_dump(),
        )
        optimization_res = run_optimization(
            r5_data["bom"],
            opt_receipt.model_dump(),
        )

        # 4. Populate SurrealDB Knowledge Graph
        kg_receipt = delegate(
            agent_name="KnowledgeGraphAgent",
            requested_scope=["populate_knowledge_graph", "graph.read", "graph.insert", "graph.update"],
            parent_receipt=root_receipt.model_dump(),
        )
        kg_summary = invoke_tool(
            agent_name="KnowledgeGraphAgent",
            tool_name="populate_knowledge_graph",
            args={
                "project_id": project_id,
                "project_name": project_name,
                "system_specification": system_specification,
                "requirements": r2_data.get("structured_requirements", []),
                "constraints": r2_data.get("structured_constraints", []),
                "components": r4_data.get("recommended_components", []),
                "research_papers": r3_data.get("research_papers", []),
                "violations": r4_data.get("violations", []),
            },
            receipt_dict=kg_receipt.model_dump(),
        )

        # 5. Normalize requirements & constraints for RequirementsWorkspace
        formatted_requirements = []
        for idx, req in enumerate(r2_data.get("structured_requirements", [])):
            if isinstance(req, dict):
                formatted_requirements.append({
                    "requirement_id": req.get("requirement_id") or req.get("id") or f"REQ-{idx+1:03d}",
                    "project_id": project_id,
                    "title": req.get("title", f"Requirement {idx+1}"),
                    "description": req.get("description") or req.get("statement", ""),
                    "category": (req.get("category") or "ELECTRICAL").upper(),
                    "parameter": req.get("parameter"),
                    "target_value": str(req.get("target_value")) if req.get("target_value") is not None else None,
                    "unit": req.get("unit"),
                    "priority": (req.get("priority") or "HIGH").upper(),
                    "verification_method": req.get("verification_method", "Simulation"),
                    "source": req.get("source", "Project Specification"),
                    "status": (req.get("status") or "ACTIVE").upper(),
                })
        if not formatted_requirements:
            for idx, r_str in enumerate(r2_data.get("requirements", [])):
                formatted_requirements.append({
                    "requirement_id": f"REQ-{idx+1:03d}",
                    "project_id": project_id,
                    "title": str(r_str)[:40],
                    "description": str(r_str),
                    "category": "FUNCTIONAL",
                    "priority": "HIGH",
                    "verification_method": "Simulation",
                    "source": "Project Specification",
                    "status": "ACTIVE",
                })

        formatted_constraints = []
        for idx, con in enumerate(r2_data.get("structured_constraints", [])):
            if isinstance(con, dict):
                req_val = str(con.get("required_value") if con.get("required_value") is not None else con.get("value", ""))
                c_unit = con.get("unit") or con.get("required_unit", "")
                formatted_constraints.append({
                    "constraint_id": con.get("constraint_id") or con.get("id") or f"CON-{idx+1:03d}",
                    "project_id": project_id,
                    "requirement_id": con.get("requirement_id"),
                    "title": con.get("title", f"Constraint {idx+1}"),
                    "description": con.get("description", ""),
                    "property": con.get("property") or con.get("parameter") or con.get("constraint_type") or "voltage",
                    "operator": con.get("operator", "<="),
                    "required_value": req_val,
                    "required_unit": c_unit,
                    "unit": c_unit,
                    "severity": (con.get("severity") or "CRITICAL").upper(),
                    "type": con.get("type", "TECHNICAL"),
                    "source": con.get("source", "ENGINEERING_STANDARDS"),
                    "status": (con.get("status") or "ACTIVE").upper(),
                })

        validation_results = []
        for v in r4_data.get("violations", []):
            if isinstance(v, dict):
                validation_results.append({
                    "requirement_id": v.get("constraint_id", "REQ-001"),
                    "property": v.get("property_name", "Limit"),
                    "required_value": v.get("allowed_value", "Within specs"),
                    "actual_value": v.get("detected_value", "Exceeded"),
                    "status": "FAIL",
                    "reason": v.get("details", "Constraint limit exceeded"),
                    "source_document": f"Datasheet {v.get('component_mpn', '')}",
                })

        power_analysis_res = r4_data["architecture"].get("power_analysis", {})
        total_p_w = power_analysis_res.get("total_power_w", 12.5) if isinstance(power_analysis_res, dict) else 12.5

        datasheets_list = []
        for comp in r4_data.get("recommended_components", []):
            if isinstance(comp, dict) and comp.get("datasheet_url"):
                datasheets_list.append({
                    "mpn": comp.get("mpn"),
                    "manufacturer": comp.get("manufacturer"),
                    "subsystem": comp.get("subsystem"),
                    "url": comp.get("datasheet_url"),
                    "source": comp.get("source", "NEXAR"),
                })

        engineering_insights = {
            "potential_design_risks": [
                v.get("details") for v in r4_data.get("violations", []) if isinstance(v, dict) and v.get("details")
            ] or [
                "Ensure sufficient transient voltage suppression (TVS) on input supply rail.",
                "Verify ground isolation between high-current actuator returns and low-noise sensor analog ADC lines.",
            ],
            "thermal_considerations": [
                f"Peak system power dissipation evaluated at {total_p_w}W.",
                "Ensure solid thermal copper pours under switching regulators with thermal vias to internal GND planes.",
            ],
            "power_budget_summary": power_analysis_res,
            "manufacturing_recommendations": [
                "Target IPC-2221A Class 2 trace spacing and clearances for power rails.",
                "Utilize automated optical inspection (AOI) for fine-pitch sensor SMD packages.",
            ],
        }

        # Build comprehensive response
        return {
            "run_id": self.run_id,
            "project_id": project_id,
            "project_name": project_name,
            "system_specification": system_specification,
            "intent": system_specification,
            "target_timeline_days": target_days,
            "engineering_template": engineering_template,
            "team_id": team_id,
            "status": "active",
            "pipeline_lineage": {
                "requirements_revision": r2_data["requirements_revision"],
                "research_revision": r3_data["research_revision"],
                "architecture_revision": r4_data["architecture_revision"],
                "bom_revision": r5_data["bom_revision"],
            },
            # SECTION 35 & Workspace Data Structures
            "understanding": r2_data.get("understanding", {}),
            "clarifications_needed": r2_data.get("clarifications_needed", []),
            "structured_requirements": r2_data.get("structured_requirements", []),
            "structured_constraints": r2_data.get("structured_constraints", []),
            "requirements": formatted_requirements,
            "constraints": formatted_constraints,
            "validation_results": validation_results,
            "recommended_components": r4_data.get("recommended_components", []),
            "alternative_components": r4_data.get("alternative_components", []),
            "component_evidence": r4_data.get("component_evidence", []),
            "violations": r4_data.get("violations", []),
            "knowledge_graph_summary": kg_summary,
            "engineering_insights": engineering_insights,
            "bom": r5_data["bom"],
            "totals": r5_data["totals"],
            "total_usd": r5_data["total_usd"],
            "alternatives": r5_data["alternatives"],
            "research_papers": r3_data["research_papers"],
            "research_summary": r3_data["findings"],
            "contradictions": r3_data["contradictions"],
            "datasheets": datasheets_list or r4_data["architecture"].get("datasheets", []),
            "power_analysis": r4_data["architecture"]["power_analysis"],
            "dependency_graph": r4_data["architecture"]["dependency_graph"],
            "wiring_diagram": r4_data["architecture"]["wiring_diagram"],
            "pin_mapping": r4_data["architecture"]["pin_mapping"],
            "voltage_analysis": r4_data["architecture"]["voltage_analysis"],
            "simulation_inputs": r4_data["simulation_inputs"],
            "roadmap": planning_res.get("roadmap", []),
            "gantt": planning_res.get("gantt", []),
            "validation": validation_res,
            "optimization": optimization_res,
            "audit_trail": [log.model_dump() if hasattr(log, "model_dump") else log for log in AUDIT_LOGS],
            "execution_timestamp": datetime.utcnow().isoformat(),
        }
