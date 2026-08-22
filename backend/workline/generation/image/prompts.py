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
            base_prompt = (
                f"Precision PCB layout and thermal distribution diagram for '{project_id}'. "
                f"Board Dimensions: {board_width}mm x {board_height}mm, 4-Layer FR-4 Stackup. "
                "Key Components: Microcontroller (MCU LQFP-64), Switching Step-Down Regulator (SOIC-8), Power MOSFETs, Decoupling Capacitors, and Thermal Vias. "
                "Features: Ground copper pours, high-current power traces, PINN-predicted thermal heat distribution overlay with localized junction temperature gradients. "
                "Style: Modern CAD electronic design view, copper trace routing, silkscreen reference designators, and thermal heatmap colormap."
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
