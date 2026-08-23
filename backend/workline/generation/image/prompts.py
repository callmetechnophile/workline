"""Image Prompt Builder — constructs detailed, technically grounded prompts from real Workline project state."""

from typing import Any, Dict, List, Optional
from backend.workline.generation.models import ImagePurpose


class ImagePromptBuilder:
    """Constructs technical visualization prompts grounded in actual Workline architecture and project state."""

    @classmethod
    def build_prompt(
        cls,
        project_id: str,
        purpose: ImagePurpose,
        user_instructions: Optional[str] = None,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Construct a structured, factual technical visualization prompt."""
        if purpose == ImagePurpose.ARCHITECTURE:
            base_prompt = (
                f"High-resolution technical engineering architecture diagram for project '{project_id}'. "
                "System Layers and Components: "
                "1. User Layer: Workline CLI (wline command) and Next.js 16 React Web Client with TypeScript 7. "
                "2. Multi-Agent Orchestration Layer: Google ADK hierarchical agent engine with Root Orchestrator, Planning Tree, Research Tree, and Hardware Builder Tree. "
                "3. Interoperability & Integration Gateway: Bindu A2A federated protocol adapter, Corsair external tools suite, and Result Schema Validator. "
                "4. Engineering Physics & Hardware Engine: PCB Layout Unit, PINN thermal solver, DRC validation, and BOM generator. "
                "5. Primary Data & Vector Stores: SurrealDB multi-relational graph store (CONTAINS, SATISFIES, CONNECTS_TO) and Qdrant semantic vector index. "
                "6. Commerce & Deployment Layer: x402 payment authorization, Procurement optimizer, Git/GitHub version control, and Podman containerization. "
                "Style: Professional dark-theme technical blueprint, clear directional flow arrows, labeled subsystem boundaries, crisp vector typography."
            )
        elif purpose == ImagePurpose.PCB:
            board_width = extra_context.get("board_width", 100.0) if extra_context else 100.0
            board_height = extra_context.get("board_height", 80.0) if extra_context else 80.0
            board_layers = extra_context.get("board_layers", 4) if extra_context else 4
            p_name = extra_context.get("project_name", project_id) if extra_context else project_id
            components = extra_context.get("components", []) if extra_context else []
            placement_data = extra_context.get("placement", []) if extra_context else []
            power_domains = extra_context.get("power_domains", "12V, 5V, 3.3V, GND") if extra_context else "12V, 5V, 3.3V, GND"
            comm_interfaces = extra_context.get("comm_interfaces", "USB 3.2 Gen 2, I2C, SPI, UART") if extra_context else "USB 3.2 Gen 2, I2C, SPI, UART"
            constraints = extra_context.get("constraints", "4-layer FR-4, 0.15mm trace/space, thermal relief vias near power regulators") if extra_context else "4-layer FR-4, 0.15mm trace/space, thermal relief vias near power regulators"
            
            comp_list_str = ", ".join([str(c.get("name") or c.get("component") or c.get("mpn", "IC")) for c in components[:12]]) if components else "MCU Microcontroller, Step-Down DC/DC Regulator, Power Delivery Controller, ESD Protection Array"
            
            if placement_data:
                placement_str = "; ".join([f"{p.get('designator', f'U{i+1}')} ({p.get('part_number', 'IC')}, {p.get('package', 'SMD')}) at ({p.get('x_mm', 20)}mm, {p.get('y_mm', 20)}mm)" for i, p in enumerate(placement_data[:10])])
            else:
                placement_str = "U1 MCU Core Controller centered at (50mm, 40mm); U2 Step-Down Regulator at (25mm, 25mm); J1 Type-C Receptacle at left edge (10mm, 40mm); J2 Expansion Bus at right edge (90mm, 40mm); Decoupling passives adjacent to IC power pins."

            base_prompt = (
                "Generate a flat 2D top-down PCB placement visualization.\n\n"
                f"Project: {p_name}\n"
                f"Board dimensions: {board_width}mm x {board_height}mm\n"
                f"Board type: {board_layers}-layer FR-4 PCB\n"
                f"Required components: {comp_list_str}\n"
                f"Component placement: {placement_str}\n"
                f"Power domains: {power_domains}\n"
                f"Communication interfaces: {comm_interfaces}\n"
                f"Critical constraints: {constraints} with PINN thermal gradient considerations\n\n"
                "Generate ONLY a 2D engineering PCB layout.\n"
                "Place every component according to the supplied placement data.\n"

                "Do not invent components. Do not omit required components. Do not randomly reposition components.\n\n"
                "Show:\n"
                "- PCB outline with corner mounting holes\n"
                "- 2D component footprints (QFN, SOIC, SOT-223, 0805, SMD connectors)\n"
                "- Component reference designators (U1, U2, C1, J1)\n"
                "- Major copper routing traces and ground plane stitching vias\n"
                "- Connectors positioned at board edges\n"
                "- Major power and signal sections with thermal relief zones\n\n"
                "Use an orthographic top-down view.\n"
                "NO 3D. NO perspective. NO isometric view. NO physical board thickness. NO shadows. "
                "NO floating components. NO photorealistic product render. NO external environment or tools.\n"
                "The final image must look like a professional 2D PCB placement/layout visualization."
            )

        elif purpose == ImagePurpose.WORKFLOW:
            base_prompt = (
                f"Engineering lifecycle workflow diagram for '{project_id}'. "
                "Flow Stages: Requirements Definition -> Multi-Agent Research -> Human Decision Checkpoint -> "
                "Hardware BOM Synthesis -> PCB DRC & PINN Thermal Optimization -> x402 Procurement -> Formal Release & Git Tagging. "
                "Style: Modern dark-mode flowchart with status pill indicators and validation gate diamonds."
            )
        else:
            base_prompt = f"Technical engineering figure for project '{project_id}' ({purpose.value})."

        if user_instructions:
            base_prompt += f" Additional Focus: {user_instructions}"

        return base_prompt
