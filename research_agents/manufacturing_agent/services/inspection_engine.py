"""
Quality Control and Inspection Planning Engine (Section 11).
"""

from typing import Any, Dict, List
from research_agents.manufacturing_agent.schemas import InspectionItem


class InspectionEngine:
    """Builds inspection requirements for dimensional, electrical, weld, and functional verification."""

    def generate_inspection_plan(
        self,
        components: List[Dict[str, Any]],
    ) -> List[InspectionItem]:
        plan: List[InspectionItem] = []
        for c in components:
            cid = c.get("component_id", "COMP-001")
            proc = str(c.get("intended_process", "CNC_MACHINING")).upper()

            # Critical dimensions
            plan.append(
                InspectionItem(
                    inspection_id=f"INSP-DIM-{cid}",
                    component_id=cid,
                    feature_or_characteristic="Critical mounting hole diameter and true position",
                    inspection_type="DIMENSIONAL",
                    measurement_method="Coordinate Measuring Machine (CMM)",
                    accessibility="EASY",
                    acceptance_criteria="+/- 0.025 mm true position to Datum A/B",
                    required_evidence="CMM Quality Inspection Certificate",
                    verification_status="PROPOSED",
                )
            )

            # Surface finish
            plan.append(
                InspectionItem(
                    inspection_id=f"INSP-SURF-{cid}",
                    component_id=cid,
                    feature_or_characteristic="O-ring seal surface roughness",
                    inspection_type="SURFACE_ROUGHNESS",
                    measurement_method="Contact Profilometer",
                    accessibility="EASY",
                    acceptance_criteria="Ra <= 0.8 micrometers (32 microinches)",
                    required_evidence="Surface Profilometer Scan Report",
                    verification_status="PROPOSED",
                )
            )

            # Weld NDT if welded
            if "WELD" in proc:
                plan.append(
                    InspectionItem(
                        inspection_id=f"INSP-WELD-{cid}",
                        component_id=cid,
                        feature_or_characteristic="Full penetration structural weld seam",
                        inspection_type="WELD_NDT",
                        measurement_method="Ultrasonic / Dye Penetrant Testing",
                        accessibility="EASY",
                        acceptance_criteria="Zero crack indications per AWS D1.1",
                        required_evidence="Certified NDT Inspection Sheet",
                        verification_status="PROPOSED",
                    )
                )

        return plan
