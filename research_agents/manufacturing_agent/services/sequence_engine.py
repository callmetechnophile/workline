"""
Manufacturing and Assembly Process Sequence Engine (Section 7).
"""

from typing import Any, Dict, List
from research_agents.manufacturing_agent.schemas import ProcessSequence, SequenceStep


class SequenceEngine:
    """Builds process flows and verifies operation sequence dependencies."""

    def build_sequence(
        self,
        component_id: str,
        process_family: str,
    ) -> ProcessSequence:
        pf = process_family.upper()
        steps: List[SequenceStep] = []

        if "CNC" in pf:
            steps = [
                SequenceStep(step_number=1, operation_name="Raw Material Stock Prep / Sawing", process_type="SAWING", duration_status="UNKNOWN"),
                SequenceStep(step_number=2, operation_name="CNC Milling Op 10 (Datum Creation)", process_type="CNC_MILLING", preceding_steps=[1], duration_status="UNKNOWN"),
                SequenceStep(step_number=3, operation_name="CNC Milling Op 20 (Cavity & Holes)", process_type="CNC_MILLING", preceding_steps=[2], duration_status="UNKNOWN"),
                SequenceStep(step_number=4, operation_name="Deburring & Cleaning", process_type="MANUAL_CLEANING", preceding_steps=[3], duration_status="UNKNOWN"),
                SequenceStep(step_number=5, operation_name="In-Process CMM Inspection Gate", process_type="INSPECTION", preceding_steps=[4], is_inspection_gate=True, duration_status="UNKNOWN"),
                SequenceStep(step_number=6, operation_name="Surface Anodizing / Coating", process_type="SURFACE_TREATMENT", preceding_steps=[5], duration_status="UNKNOWN"),
                SequenceStep(step_number=7, operation_name="Final Quality Acceptance", process_type="FINAL_INSPECTION", preceding_steps=[6], is_inspection_gate=True, duration_status="UNKNOWN"),
            ]
        elif "SHEET_METAL" in pf:
            steps = [
                SequenceStep(step_number=1, operation_name="CNC Laser Cutting / Punching", process_type="LASER_CUTTING", duration_status="UNKNOWN"),
                SequenceStep(step_number=2, operation_name="Deburring / Edge Radiusing", process_type="DEBURRING", preceding_steps=[1], duration_status="UNKNOWN"),
                SequenceStep(step_number=3, operation_name="Press Brake Bending", process_type="BENDING", preceding_steps=[2], duration_status="UNKNOWN"),
                SequenceStep(step_number=4, operation_name="PEM Fastener Insertion", process_type="HARDWARE_INSERTION", preceding_steps=[3], duration_status="UNKNOWN"),
                SequenceStep(step_number=5, operation_name="Powder Coating", process_type="SURFACE_FINISH", preceding_steps=[4], duration_status="UNKNOWN"),
                SequenceStep(step_number=6, operation_name="Final Dimensional Inspection", process_type="INSPECTION", preceding_steps=[5], is_inspection_gate=True, duration_status="UNKNOWN"),
            ]
        else:
            steps = [
                SequenceStep(step_number=1, operation_name="Primary Manufacturing Operation", process_type=process_family, duration_status="UNKNOWN"),
                SequenceStep(step_number=2, operation_name="Inspection Gate", process_type="INSPECTION", preceding_steps=[1], is_inspection_gate=True, duration_status="UNKNOWN"),
            ]

        return ProcessSequence(
            sequence_id=f"SEQ-{component_id}",
            component_id=component_id,
            steps=steps,
        )
