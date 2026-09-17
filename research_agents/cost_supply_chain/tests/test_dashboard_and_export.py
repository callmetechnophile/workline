"""Tests for dashboard compilation and file exports."""
from research_agents.cost_supply_chain.schemas import PartCost
from research_agents.cost_supply_chain.services.bom_cost_engine import BOMCostEngine
from research_agents.cost_supply_chain.services.dashboard_service import DashboardService
from research_agents.cost_supply_chain.services.file_exporter import FileExporter
from research_agents.cost_supply_chain.services.report_generator import ReportGenerator


def test_dashboard_and_export():
    bom_engine = BOMCostEngine()
    parts = [PartCost(part_id="P1", part_name="Motor", unit_cost=30.0)]
    rollup = bom_engine.rollup_bom_cost("BOM-DASH", "PROJ-DASH", parts)

    dash_service = DashboardService()
    dash = dash_service.compile_dashboard("PROJ-DASH", rollup, [])
    assert dash.total_bom_cost == 30.0
    assert dash.total_risks_count == 0

    reporter = ReportGenerator()
    report = reporter.generate_full_report(rollup, dash, [])
    assert "Engineering Cost & Supply Chain Analysis Report" in report

    exporter = FileExporter()
    json_out = exporter.to_json(rollup)
    assert "BOM-DASH" in json_out

    csv_out = exporter.to_csv_bom(rollup)
    assert "Part ID,Part Name" in csv_out
    assert "P1,Motor" in csv_out
