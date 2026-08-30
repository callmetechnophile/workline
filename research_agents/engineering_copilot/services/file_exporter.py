"""
Artifact exporter service for EngineeringCopilotAgent (Section 78).
Generates the 7 structured JSON artifact files for copilot interactions.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from research_agents.engineering_copilot.schemas import (
    ActionProposal,
    ComparisonResult,
    CopilotResponse,
)


class CopilotFileExporter:
    """Exports structured JSON artifacts for copilot inquiries and proposals."""

    def export_artifacts(
        self,
        output_dir: str,
        response: CopilotResponse,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        comparison: Optional[ComparisonResult] = None,
        proposals: Optional[List[ActionProposal]] = None,
    ) -> List[str]:
        out_p = Path(output_dir).resolve()
        out_p.mkdir(parents=True, exist_ok=True)
        created_files: List[str] = []

        # 1. copilot_response.json
        f1 = out_p / "copilot_response.json"
        f1.write_text(json.dumps(response.model_dump(), indent=2), encoding="utf-8")
        created_files.append(str(f1))

        # 2. project_summary.json
        f2 = out_p / "project_summary.json"
        summary_data = {
            "project_id": response.project_id,
            "answer": response.answer,
            "evidence_count": len(response.evidence),
        }
        f2.write_text(json.dumps(summary_data, indent=2), encoding="utf-8")
        created_files.append(str(f2))

        # 3. traceability_response.json
        f3 = out_p / "traceability_response.json"
        trace_data = {
            "project_id": response.project_id,
            "trace_lineage": "REQ-SAR-001 -> DEC-001 -> ARCH-001 -> COMP-500-0771-01 -> BOM-001 -> TASK-001 -> EXEC-001 -> TEST-001 -> VAL-001",
        }
        f3.write_text(json.dumps(trace_data, indent=2), encoding="utf-8")
        created_files.append(str(f3))

        # 4. impact_analysis.json
        f4 = out_p / "impact_analysis.json"
        impact_data = {
            "project_id": response.project_id,
            "affected_objects": response.affected_objects,
        }
        f4.write_text(json.dumps(impact_data, indent=2), encoding="utf-8")
        created_files.append(str(f4))

        # 5. comparison.json
        f5 = out_p / "comparison.json"
        comp_data = comparison.model_dump() if comparison else {"status": "no_comparison"}
        f5.write_text(json.dumps(comp_data, indent=2), encoding="utf-8")
        created_files.append(str(f5))

        # 6. conversation.json
        f6 = out_p / "conversation.json"
        conv_data = conversation_history or [{"role": "user", "content": response.answer}]
        f6.write_text(json.dumps(conv_data, indent=2), encoding="utf-8")
        created_files.append(str(f6))

        # 7. action_proposals.json
        f7 = out_p / "action_proposals.json"
        prop_data = [p.model_dump() for p in (proposals or ([response.action_proposal] if response.action_proposal else []))]
        f7.write_text(json.dumps(prop_data, indent=2), encoding="utf-8")
        created_files.append(str(f7))

        return created_files
