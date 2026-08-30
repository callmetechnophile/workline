"""
Unit tests for ProcurementFileExporter service (Section 47).
"""

from pathlib import Path
import tempfile
from research_agents.bom_optimization_agent.schemas import (
    BOMOptimizationAgentOutput,
    CostSummary,
    OptimizedBOMItem,
    ProcurementStrategy,
    SupplierOrder,
)
from research_agents.bom_optimization_agent.services.file_exporter import ProcurementFileExporter


def test_file_export_creates_7_artifacts():
    exporter = ProcurementFileExporter()
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = BOMOptimizationAgentOutput(
            project_id="proj_test_01",
            bom_id="BOM-001",
            optimization_id="OPT-001",
            selected_strategy=ProcurementStrategy(name="Lowest Cost"),
            strategies=[ProcurementStrategy(name="Lowest Cost")],
            optimized_items=[
                OptimizedBOMItem(
                    bom_item_id="BOM-001",
                    selected_supplier="Robu",
                    selected_part_number="Jetson",
                    manufacturer="NVIDIA",
                    category="SBC",
                    subsystem_id="SUB-001",
                    required_quantity=1,
                    purchased_quantity=1,
                    selection_reason="Best price",
                )
            ],
            orders=[
                SupplierOrder(order_id="ORD-001", supplier_id="SUPP-1", supplier_name="Robu")
            ],
            cost_summary=CostSummary(total_known_landed_cost=45000.0),
            structured_report_markdown="# Procurement Optimization Report",
        )

        files = exporter.export_artifacts(output, tmp_dir, overwrite=True)
        assert len(files) == 7

        dir_p = Path(tmp_dir)
        assert (dir_p / "procurement_optimization.json").exists()
        assert (dir_p / "procurement_report.md").exists()
        assert (dir_p / "optimized_bom.json").exists()
        assert (dir_p / "supplier_comparison.json").exists()
        assert (dir_p / "shipping_analysis.json").exists()
        assert (dir_p / "procurement_strategies.json").exists()
        assert (dir_p / "procurement_traceability.json").exists()


def test_file_export_prevents_overwrite_without_flag():
    exporter = ProcurementFileExporter()
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = BOMOptimizationAgentOutput(
            project_id="proj_test_01",
            bom_id="BOM-001",
            structured_report_markdown="Original Content",
        )

        exporter.export_artifacts(output, tmp_dir, overwrite=True)
        report_file = Path(tmp_dir) / "procurement_report.md"
        assert report_file.read_text(encoding="utf-8") == "Original Content"

        output.structured_report_markdown = "Modified Content"
        exporter.export_artifacts(output, tmp_dir, overwrite=False)
        assert report_file.read_text(encoding="utf-8") == "Original Content"
