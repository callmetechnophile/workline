"""
Template Engine — returns canonical section templates for each DocumentType.
Templates define required sections; LLM fills prose, deterministic code fills metadata.
"""

from typing import Dict, List
from research_agents.documentation_agent.schemas import DocumentType


TEMPLATES: Dict[str, List[str]] = {
    DocumentType.SYSTEM_REQUIREMENTS_SPEC.value: [
        "Scope", "Applicable_Documents", "System_Overview",
        "Functional_Requirements", "Performance_Requirements",
        "Interface_Requirements", "Verification_Requirements",
    ],
    DocumentType.INTERFACE_CONTROL_DOCUMENT.value: [
        "Scope", "Interface_Identification", "Interface_Description",
        "Data_Formats", "Timing_Constraints", "Error_Handling",
    ],
    DocumentType.DESIGN_DESCRIPTION.value: [
        "Scope", "System_Context", "Architecture_Overview",
        "Component_Descriptions", "Data_Flow", "Design_Rationale",
    ],
    DocumentType.ARCHITECTURE_DOCUMENT.value: [
        "Scope", "Architectural_Drivers", "Architecture_Views",
        "Component_Interfaces", "Deployment_View", "Quality_Attributes",
    ],
    DocumentType.TRADE_STUDY_REPORT.value: [
        "Objective", "Criteria_and_Weights", "Alternatives",
        "Analysis_and_Scoring", "Recommendation", "Assumptions",
    ],
    DocumentType.ENGINEERING_CHANGE_NOTICE.value: [
        "Change_ID", "Affected_Documents", "Reason_for_Change",
        "Description_of_Change", "Impact_Assessment", "Approval",
    ],
    DocumentType.TEST_PLAN.value: [
        "Scope", "Test_Items", "Test_Approach",
        "Entry_Exit_Criteria", "Schedule", "Risk_and_Contingency",
    ],
    DocumentType.TEST_REPORT.value: [
        "Summary", "Test_Environment", "Test_Results",
        "Defects_Found", "Pass_Fail_Criteria", "Conclusion",
    ],
    DocumentType.VERIFICATION_CROSS_REF_MATRIX.value: [
        "Scope", "Traceability_Matrix", "Verification_Method_Legend",
        "Compliance_Status", "Open_Items",
    ],
    DocumentType.FMEA_REPORT.value: [
        "Scope", "Methodology", "FMEA_Table",
        "Risk_Priority_Numbers", "Recommended_Actions", "Summary",
    ],
    DocumentType.THREAT_MODEL_DOCUMENT.value: [
        "Scope", "System_Description", "Threat_Actors",
        "Attack_Surfaces", "STRIDE_Analysis", "Mitigations", "Residual_Risks",
    ],
    DocumentType.OPERATIONS_MANUAL.value: [
        "Scope", "Safety_Warnings", "System_Overview",
        "Normal_Operations", "Abnormal_Operations", "Emergency_Procedures",
    ],
    DocumentType.DEPLOYMENT_GUIDE.value: [
        "Scope", "Prerequisites", "Installation_Steps",
        "Configuration", "Verification", "Rollback_Procedure",
    ],
}

_DEFAULT_SECTIONS = ["Scope", "Background", "Details", "Summary"]


class TemplateEngine:
    """Returns the required section list for a given document type."""

    def get_sections(self, document_type_value: str) -> List[str]:
        return TEMPLATES.get(document_type_value, _DEFAULT_SECTIONS)

    def all_templates(self) -> Dict[str, List[str]]:
        return dict(TEMPLATES)
