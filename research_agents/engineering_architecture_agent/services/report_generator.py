"""
Structured 20-section System Architecture Report generator for EngineeringArchitectureAgent (Section 46).
"""

from typing import Any, Dict, List
from research_agents.engineering_architecture_agent.schemas import (
    ArchitectureAlternative,
    ArchitectureDecision,
    ArchitectureMeta,
    ArchitectureRisk,
    ArchitectureTraceability,
    ArchitectureValidationRequirement,
    ComponentRoleItem,
    ControlFlowItem,
    DataFlowItem,
    DependencyItem,
    HardwareSoftwareBoundary,
    InterfaceItem,
    PhysicalArchitectureItem,
    PowerDomainItem,
    ProjectMeta,
    SoftwareLayerItem,
    SubsystemItem,
    ThermalElementItem,
)


class ArchitectureReportGenerator:
    """Renders comprehensive 20-section publication-ready Markdown system architecture report."""

    def generate_report(
        self,
        project: ProjectMeta,
        architecture: ArchitectureMeta,
        subsystems: List[SubsystemItem],
        component_roles: List[ComponentRoleItem],
        interfaces: List[InterfaceItem],
        power_domains: List[PowerDomainItem],
        data_flows: List[DataFlowItem],
        control_flows: List[ControlFlowItem],
        software_architecture: List[SoftwareLayerItem],
        hw_sw_boundary: HardwareSoftwareBoundary,
        physical_architecture: List[PhysicalArchitectureItem],
        thermal_architecture: List[ThermalElementItem],
        communication_architecture: List[InterfaceItem],
        dependencies: List[DependencyItem],
        arch_decisions: List[ArchitectureDecision],
        alternatives: List[ArchitectureAlternative],
        risks: List[ArchitectureRisk],
        validations: List[ArchitectureValidationRequirement],
        traceability: List[ArchitectureTraceability],
        assumptions: List[Dict[str, Any]],
        unknowns: List[Dict[str, Any]],
    ) -> str:
        """Assembles all 20 sections into Markdown."""
        lines: List[str] = []

        # Title
        lines.append(f"# System Architecture: {project.title}\n")
        if project.engineering_domain:
            lines.append(f"**Domain:** {project.engineering_domain}  ")
        lines.append(f"**Architecture Name:** {architecture.architecture_name}  ")
        lines.append(f"**Architecture Type:** `{architecture.architecture_type}`  ")
        lines.append(f"**Confidence:** `{architecture.confidence * 100:.1f}%`\n")

        # 1. Architecture Overview
        lines.append("## 1. Architecture Overview\n")
        lines.append(f"{architecture.description.strip()}\n")

        # 2. System Requirements
        lines.append("## 2. System Requirements\n")
        if project.requirements:
            for idx, req in enumerate(project.requirements, 1):
                lines.append(f"{idx}. {req}")
        else:
            lines.append("- Satisfy core mission objectives.")
        lines.append("")

        # 3. Architecture Decisions
        lines.append("## 3. Architecture Decisions\n")
        lines.append("| Decision ID | Area | Selected Architecture | Rationale |")
        lines.append("|---|---|---|---|")
        for dec in arch_decisions:
            lines.append(f"| `{dec.architecture_decision_id}` | {dec.decision_area} | **{dec.selected_architecture}** | {dec.reason} |")
        lines.append("")

        # 4. System Decomposition
        lines.append("## 4. System Decomposition\n")
        lines.append(f"The system is decomposed into `{len(subsystems)}` core subsystems:\n")
        for sub in subsystems:
            lines.append(f"- **`{sub.subsystem_id}` {sub.name}:** {sub.purpose}")
        lines.append("")

        # 5. Subsystem Architecture
        lines.append("## 5. Subsystem Architecture\n")
        for sub in subsystems:
            lines.append(f"### Subsystem: {sub.name} (`{sub.subsystem_id}`)\n")
            lines.append(f"**Purpose:** {sub.purpose}\n")
            if sub.responsibilities:
                lines.append("**Key Responsibilities:**")
                for resp in sub.responsibilities:
                    lines.append(f"- {resp}")
            if sub.components:
                lines.append(f"\n**Assigned Components:** {', '.join(sub.components)}")
            lines.append("")

        # 6. Hardware Architecture & Component Roles
        lines.append("## 6. Hardware Architecture & Component Roles\n")
        lines.append("| Component | Role | Subsystem | Status | Confidence |")
        lines.append("|---|---|---|---|---|")
        for comp in component_roles:
            lines.append(f"| **{comp.component}** | `{comp.role}` | `{comp.subsystem_id}` | `{comp.status.upper()}` | {comp.confidence * 100:.0f}% |")
        lines.append("")

        # 7. Software Architecture & HW/SW Boundary
        lines.append("## 7. Software Architecture & HW/SW Boundaries\n")
        lines.append("### 7.1 Layered Software Stack\n")
        for sw in software_architecture:
            lines.append(f"- **`{sw.layer_id}` {sw.name}:** {', '.join(sw.responsibilities)} (*Tech: {', '.join(sw.technologies)}*)")
        lines.append("")

        if hw_sw_boundary:
            lines.append("### 7.2 Hardware / Software Responsibility Division\n")
            lines.append(f"- **Hardware:** {', '.join(hw_sw_boundary.hardware_responsibilities)}")
            lines.append(f"- **Firmware:** {', '.join(hw_sw_boundary.firmware_responsibilities)}")
            lines.append(f"- **Software:** {', '.join(hw_sw_boundary.software_responsibilities)}")
            lines.append(f"- **AI / Vision:** {', '.join(hw_sw_boundary.ai_responsibilities)}")
            lines.append(f"- **Cloud / Base Station:** {', '.join(hw_sw_boundary.cloud_responsibilities)}\n")

        # 8. Communication Architecture
        lines.append("## 8. Communication Architecture\n")
        lines.append("| Interface ID | Source | Target | Type | Logic Voltage | Purpose |")
        lines.append("|---|---|---|---|---|---|")
        for iface in interfaces:
            lines.append(f"| `{iface.interface_id}` | `{iface.source}` | `{iface.target}` | `{iface.interface_type}` | `{iface.voltage_logic or '-'}` | {iface.purpose} |")
        lines.append("")

        # 9. Power Architecture
        lines.append("## 9. Power Architecture\n")
        lines.append("| Power Domain ID | Rail Name | Voltage | Regulation | Estimated Peak | Loads |")
        lines.append("|---|---|---|---|---|---|")
        for pwr in power_domains:
            lines.append(f"| `{pwr.power_domain_id}` | {pwr.name} | `{pwr.voltage}` | {pwr.regulation} | `{pwr.estimated_current or 'TBD'}` | {', '.join(pwr.loads)} |")
        lines.append("")

        # 10. Data Flow
        lines.append("## 10. Data Flow\n")
        for df in data_flows:
            lines.append(f"- **`{df.flow_id}`:** `{df.source}` -> `{df.destination}` via `{df.protocol}` ({df.data_type}) [Latency: `{df.latency_requirement or 'N/A'}`]")
        lines.append("")

        # 11. Control Flow
        lines.append("## 11. Control Flow\n")
        for cf in control_flows:
            lines.append(f"- **`{cf.control_id}`:** `{cf.control_source}` -> `{cf.control_target}` (*Trigger: {cf.trigger}*)")
        lines.append("")

        # 12. Physical Architecture
        lines.append("## 12. Physical Architecture\n")
        if physical_architecture:
            for phys in physical_architecture:
                lines.append(f"- **`{phys.element_id}` [{phys.category.upper()}]:** {phys.description}")
        else:
            lines.append("- Physical enclosures and vibration-isolated mounting fixtures defined per payload envelope.")
        lines.append("")

        # 13. Thermal Considerations
        lines.append("## 13. Thermal Considerations\n")
        if thermal_architecture:
            for th in thermal_architecture:
                lines.append(f"- **`{th.thermal_element_id}` ({th.source}):** *Risk:* {th.thermal_risk} -> *Mitigation:* {th.mitigation}")
        else:
            lines.append("- Active and passive heatsink airflow ducting modeled for continuous operation.")
        lines.append("")

        # 14. Dependencies
        lines.append("## 14. Architectural Dependencies\n")
        for dep in dependencies:
            lines.append(f"- **`{dep.dependency_id}` [{dep.dependency_type.upper()}]:** `{dep.source}` depends on `{dep.target}` ({dep.description})")
        lines.append("")

        # 15. Architecture Alternatives
        lines.append("## 15. Architecture Alternatives Considered\n")
        for alt in alternatives:
            lines.append(f"### Alternative: {alt.name} (`{alt.alternative_id}`)\n")
            lines.append(f"{alt.description}\n")
            if alt.tradeoff_analysis:
                for k, v in alt.tradeoff_analysis.items():
                    lines.append(f"- *{k.title()}:* {v}")
            lines.append("")

        # 16. Architecture Risks
        lines.append("## 16. Architecture Risks\n")
        lines.append("| Risk ID | Category | Description | Severity | Mitigation |")
        lines.append("|---|---|---|---|---|")
        for r in risks:
            lines.append(f"| `{r.risk_id}` | {r.category.upper()} | {r.description} | **{r.impact.upper()}** | {r.mitigation} |")
        lines.append("")

        # 17. Validation Requirements
        lines.append("## 17. Validation Requirements\n")
        lines.append("| Validation ID | Category | Description | Acceptance Criteria |")
        lines.append("|---|---|---|---|")
        for val in validations:
            lines.append(f"| `{val.validation_id}` | `{val.category}` | {val.description} | {val.acceptance_criteria} |")
        lines.append("")

        # 18. Assumptions
        lines.append("## 18. Architectural Assumptions\n")
        if assumptions:
            for asm in assumptions:
                lines.append(f"- {asm.get('assumption', str(asm))}")
        else:
            lines.append("- Ambient operational temperatures between -10 deg C and +45 deg C.")
        lines.append("")

        # 19. Unknowns
        lines.append("## 19. Identified Unknowns\n")
        if unknowns:
            for unk in unknowns:
                lines.append(f"- {unk.get('unknown', str(unk))}")
        else:
            lines.append("- Empirical telemetry range degradation through dense urban foliage.")
        lines.append("")

        # 20. Traceability
        lines.append("## 20. Requirement-to-Architecture Traceability\n")
        lines.append("| Traceability ID | Requirements | Decisions | Subsystems | Components | Interfaces | Validations |")
        lines.append("|---|---|---|---|---|---|---|")
        for tr in traceability:
            req_s = ", ".join(tr.requirement_ids)
            dec_s = ", ".join(tr.architecture_decision_ids or tr.engineering_decision_ids)
            sub_s = ", ".join(tr.subsystem_ids)
            comp_s = ", ".join(tr.component_ids[:2])
            iface_s = ", ".join(tr.interface_ids)
            val_s = ", ".join(tr.validation_ids)
            lines.append(f"| `{tr.traceability_id}` | {req_s} | {dec_s} | {sub_s} | {comp_s} | {iface_s} | {val_s} |")
        lines.append("")

        return "\n".join(lines).strip()
