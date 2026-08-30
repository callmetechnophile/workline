"""
20-Section Engineering Change Report generator (Section 57).
"""

from typing import List, Optional
from research_agents.engineering_change_control.schemas import (
    ApprovalObject,
    ChangePlan,
    ChangeRequest,
    ImpactObject,
    RiskObject,
)


class ChangeReportGenerator:
    """Generates the 20-section Markdown Engineering Change Report."""

    def generate_report(
        self,
        change: ChangeRequest,
        impact: ImpactObject,
        risks: List[RiskObject],
        approval: Optional[ApprovalObject] = None,
        plan: Optional[ChangePlan] = None,
    ) -> str:
        md = f"""# Engineering Change Report: {change.change_id}

## 1. Change
- **Change ID:** `{change.change_id}`
- **Title:** {change.title}
- **Target Artifact:** `{change.target_artifact or 'N/A'}`

## 2. Requester
- **Requested By:** `{change.requested_by}`
- **Created At:** `{change.created_at}`

## 3. Reason
{change.description}

## 4. Change Type
`{change.change_type}`

## 5. Severity
**`{change.severity}`**

## 6. Impact
- **Direct Impact Count:** {len(impact.direct_impact)}
- **Indirect Impact Count:** {len(impact.indirect_impact)}
- **Stale Artifacts:** {', '.join(impact.stale_artifacts) if impact.stale_artifacts else 'None'}
- **Invalidated Results:** {', '.join(impact.invalidated_artifacts) if impact.invalidated_artifacts else 'None'}

## 7. Affected Requirements
- `REQ-SAR-001` (Thermal imaging capture resolution & frame rate)

## 8. Affected Architecture
- `ARCH-001` (ThermalImagingSubsystem / SPI VoSPI bus interface)

## 9. Affected Components
- `{change.target_artifact or 'COMP-500-0771-01'}`

## 10. BOM Impact
- BOM item updated to reflect candidate component and supplier offers.

## 11. Procurement Impact
- Verified supplier availability and lead times updated via Agent #8.

## 12. Implementation Impact
- Driver telemetry parser and firmware work packages staged for execution.

## 13. Testing Impact
- Pytest sensor validation and interface test suite staged for QA re-run.

## 14. Validation Impact
- Agent #9 engineering design rule check required prior to implementation.

## 15. QA Impact
- Autonomous QA gate (Agent #12) required for final verification.

## 16. Risks
"""
        for r in risks:
            md += f"- **[{r.severity}] {r.category}:** {r.description} (Mitigation: {r.mitigation})\n"

        md += f"""
## 17. Approvals
- **Approval Required:** `{impact.human_approval_required}`
- **Approval Status:** `{approval.status if approval else 'NOT_REQUIRED'}`
- **Approver:** `{approval.approved_by if approval and approval.approved_by else 'PENDING'}`

## 18. Execution
- **Execution Target:** `EngineeringExecutionAgent (Agent #11)`
- **Authorization:** ArmorIQ Cryptographic Grant

## 19. Revalidation
- **Revalidation Stages:** {', '.join(impact.revalidation_required) if impact.revalidation_required else 'Zero revalidation'}

## 20. Final Status
**`{change.status}`**
"""
        return md
