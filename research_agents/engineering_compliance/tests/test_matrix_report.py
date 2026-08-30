"""
Unit tests for MatrixGenerator and ComplianceReportGenerator (Sections 60 & 61).
"""

from research_agents.engineering_compliance.schemas import (
    ComplianceResult,
    ComplianceWaiver,
    ProjectComplianceSummary,
)
from research_agents.engineering_compliance.services.matrix_generator import MatrixGenerator
from research_agents.engineering_compliance.services.report_generator import ComplianceReportGenerator


def test_matrix_and_25_section_report():
    matrix_gen = MatrixGenerator()
    report_gen = ComplianceReportGenerator()

    results = [
        ComplianceResult(
            compliance_id="C1",
            project_id="p1",
            artifact_id="component:500-0771-01",
            artifact_type="component",
            domain="ELECTRICAL",
            status="PASS",
            severity="HIGH",
            rule_id="RULE-ELEC-01",
            requirement_id="REQ-SAR-001",
            evidence_ids=["EVID-ELEC-01"],
            description="Voltage rating compliant.",
        )
    ]

    matrix = matrix_gen.build_matrix(results)
    assert len(matrix) == 1
    assert matrix[0].requirement_id == "REQ-SAR-001"
    assert matrix[0].result == "PASS"

    summary = ProjectComplianceSummary(
        project_id="p1",
        status="PASS",
        gate="ALLOW",
        total_checks=1,
        passed=1,
    )

    report_md = report_gen.generate_report(summary, results, matrix, [])
    assert "# Engineering Compliance Report" in report_md
    assert "## 25. Final Gate" in report_md
    assert "ALLOW" in report_md
