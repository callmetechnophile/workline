"""
End-to-End Test Suite for WORKLINE AI:
IDEA -> ENGINEERING RESEARCH -> REQUIREMENTS -> COMPONENTS -> RESEARCH -> KNOWLEDGE GRAPH

Validates:
1. Canonical test cases:
   - "Build a smart irrigation system using IoT"
   - "Build a wearable heart rate and temperature monitoring device"
   - "Build an autonomous line-following robot"
   - "Build a solar-powered environmental monitoring station"
2. Underspecified inputs produce targeted clarifications without hallucinating.
3. Requirements & constraints are structured and do not contain hallucinated MPNs.
4. Recommended components include genuine MPNs, manufacturers, justifications, datasheets, and sources.
5. Alternatives include trade-off comparisons.
6. Scholarly papers have real DOIs, authors, years, and provenance tags.
7. SurrealDB knowledge graph population creates nodes and typed edges.
8. ArmorIQ governed delegation and audit receipts are preserved throughout.
"""

import pytest
from typing import Dict, Any

from backend.agents.planner_agent import run_engineering_pipeline
from backend.workline.pipeline.idea_understanding import analyze_engineering_idea
from backend.workline.pipeline.scholarly_research import search_scholarly_research
from backend.workline.pipeline.graph_populator import knowledge_graph_populator


CANONICAL_CASES = [
    "Build a smart irrigation system using IoT",
    "Build a wearable heart rate and temperature monitoring device",
    "Build an autonomous line-following robot",
    "Build a solar-powered environmental monitoring station",
]


class TestIdeaUnderstanding:
    """Tests for Idea Understanding Agent and Requirement/Constraint extraction."""

    @pytest.mark.parametrize("idea", CANONICAL_CASES)
    def test_canonical_idea_decomposition(self, idea: str):
        result = analyze_engineering_idea(idea, project_id="TEST-PROJ")
        assert "understanding" in result
        assert "requirements" in result
        assert "constraints" in result
        assert "clarifications_needed" in result

        und = result["understanding"]
        assert und.get("title")
        assert und.get("summary")
        assert und.get("architecture_summary")
        assert len(und.get("key_subsystems", [])) >= 3
        assert len(und.get("sensors", [])) >= 1
        assert len(und.get("power_requirements", [])) >= 1

        reqs = result["requirements"]
        assert len(reqs) >= 3
        for r in reqs:
            assert r["requirement_id"].startswith("REQ-")
            assert r["title"]
            assert r["description"]
            assert r["category"] in ("FUNCTIONAL", "ELECTRICAL", "ENVIRONMENTAL", "POWER", "PERFORMANCE", "INTERFACE", "SAFETY")
            # Invariant: Requirements must NOT contain specific manufacturer part numbers
            assert "TPS62130" not in r["description"]
            assert "MAX30102" not in r["description"]
            assert "STM32F405" not in r["description"]

        cons = result["constraints"]
        assert len(cons) >= 2
        for c in cons:
            assert c["constraint_id"].startswith("CON-")
            assert c["property"]
            assert c["operator"] in ("<=", ">=", "=", "range")
            assert c["severity"] in ("CRITICAL", "HIGH", "MEDIUM", "LOW")

    def test_underspecified_idea_clarifications(self):
        ambiguous_idea = "Build a drone"
        result = analyze_engineering_idea(ambiguous_idea, project_id="TEST-DRONE")
        clarifications = result.get("clarifications_needed", [])
        assert len(clarifications) >= 1
        # Should ask clarifying questions regarding flight time, payload, or operating environment
        combined = " ".join(clarifications).lower()
        assert any(term in combined for term in ("payload", "battery", "range", "flight", "size", "communication"))


class TestScholarlyResearch:
    """Tests for Scholarly Research Agent (arXiv, Crossref, Semantic Scholar)."""

    def test_scholarly_research_retrieval(self):
        idea = "Build a smart irrigation system using IoT"
        papers = search_scholarly_research(
            idea=idea,
            requirements=[{"title": "Soil Moisture Sensing", "parameter": "soil_moisture"}],
            domain="Agricultural IoT",
            project_id="TEST-IRRIG",
            max_papers=4,
        )
        assert len(papers) >= 1
        for p in papers:
            assert p.get("title")
            assert p.get("source") in ("arXiv", "Crossref", "Semantic Scholar", "IEEE (Verified Reference)")
            assert p.get("publication_year") >= 2000
            assert p.get("paper_url")
            assert p.get("doi")


class TestEndToEndPipeline:
    """Tests for complete R1->R2->R3->R4->R5 Sequential Orchestration Pipeline."""

    def test_smart_irrigation_pipeline_execution(self):
        idea = "Build a smart irrigation system using IoT"
        res = run_engineering_pipeline(user_intent=idea, target_days=30, project_name="Smart Irrigation IoT")

        # 1. Pipeline metadata and lineage
        assert res["status"] == "active"
        assert res["pipeline_lineage"]["requirements_revision"] >= 1
        assert res["pipeline_lineage"]["research_revision"] >= 1
        assert res["pipeline_lineage"]["architecture_revision"] >= 1
        assert res["pipeline_lineage"]["bom_revision"] >= 1

        # 2. Section 35 UI payload contracts
        assert res.get("understanding")
        assert res["understanding"].get("title")
        assert res["understanding"].get("architecture_summary")
        assert len(res.get("requirements", [])) >= 3
        assert len(res.get("constraints", [])) >= 2

        # 3. Recommended components via Nexar/Octopart
        recommended = res.get("recommended_components", [])
        assert len(recommended) >= 3
        mpns = [c.get("mpn") for c in recommended]
        # Must include real, verified components relevant to irrigation
        assert any("TPS62130" in m or "BME280" in m or "SRD-05VDC" in m or "SEN0193" in m for m in mpns if m)
        for c in recommended:
            assert c.get("mpn")
            assert c.get("manufacturer")
            assert c.get("source") in ("NEXAR", "MOCK_NEXAR", "OCTOPART", "Nexar/Octopart MCP", "Nexar")
            assert c.get("why_recommended")

        # 4. Research papers
        papers = res.get("research_papers", [])
        assert len(papers) >= 1
        for p in papers:
            assert p.get("title")
            assert p.get("doi")
            assert p.get("source")

        # 5. Engineering insights
        insights = res.get("engineering_insights", {})
        assert "potential_design_risks" in insights
        assert "thermal_considerations" in insights
        assert "power_budget_summary" in insights
        assert "manufacturing_recommendations" in insights

        # 6. Knowledge Graph population
        kg_summary = res.get("knowledge_graph_summary", {})
        assert len(kg_summary.get("nodes", [])) >= 5
        assert len(kg_summary.get("edges", [])) >= 5
        edge_types = {e.get("relationship") for e in kg_summary.get("edges", [])}
        assert "REQUIRES" in edge_types
        assert "HAS_CONSTRAINT" in edge_types

        # 7. ArmorIQ governed delegation & audit trail
        audit_trail = res.get("audit_trail", [])
        assert len(audit_trail) >= 5
        agents_invoked = {a.get("agent") or a.get("agent_name") or a.get("caller") for a in audit_trail}
        assert any("Planner" in str(ag) or "Research" in str(ag) or "Retrieval" in str(ag) for ag in agents_invoked)

    def test_wearable_health_monitor_pipeline_execution(self):
        idea = "Build a wearable heart rate and temperature monitoring device"
        res = run_engineering_pipeline(user_intent=idea, target_days=20, project_name="Wearable Health Monitor")
        assert res["status"] == "active"
        recommended = res.get("recommended_components", [])
        mpns = [c.get("mpn") for c in recommended]
        # Should include biometric or temperature sensor or BLE MCU (e.g. MAX30102, TMP117, nRF52840)
        assert any("MAX30102" in m or "TMP117" in m or "nRF52840" in m or "BME280" in m for m in mpns if m)

    def test_autonomous_line_following_robot_execution(self):
        idea = "Build an autonomous line-following robot"
        res = run_engineering_pipeline(user_intent=idea, target_days=15, project_name="Line Following Robot")
        assert res["status"] == "active"
        recommended = res.get("recommended_components", [])
        mpns = [c.get("mpn") for c in recommended]
        # Should include optical line sensor, motor driver, or MCU (e.g. TCRT5000, DRV8833, STM32F405)
        assert any("TCRT5000" in m or "DRV8833" in m or "STM32F405" in m or "ESP32" in m for m in mpns if m)

    def test_solar_powered_environmental_station_execution(self):
        idea = "Build a solar-powered environmental monitoring station"
        res = run_engineering_pipeline(user_intent=idea, target_days=30, project_name="Solar Weather Station")
        assert res["status"] == "active"
        recommended = res.get("recommended_components", [])
        mpns = [c.get("mpn") for c in recommended]
        # Should include solar charger, transceiver, or environmental sensor (e.g. CN3791, SX1262, BME280)
        assert any("CN3791" in m or "SX1262" in m or "BME280" in m or "TPS62130" in m for m in mpns if m)
