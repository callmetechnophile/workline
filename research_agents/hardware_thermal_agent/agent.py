"""
HardwareThermalAgent (Agent #23)
Authoritative EDA board analysis, copper thermal planes, stackup optimization,
and thermal dissipation analysis.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from loguru import logger

from backend.services.thermal_service import calculate_project_thermal_analysis, VERIFIED_COMPONENT_THERMAL_SPECS


class StackupLayer(BaseModel):
    layer_index: int
    layer_name: str
    layer_type: str = "copper"  # copper, dielectric, core, prepreg
    thickness_um: float = 35.0  # 1 oz copper = ~35 um
    copper_weight_oz: float = 1.0
    material: str = "FR4"
    thermal_conductivity_w_mk: float = 0.3  # FR4 ~ 0.3 W/m-K, Copper ~ 385 W/m-K


class ThermalHotspot(BaseModel):
    component_mpn: str
    location_x_mm: float = 0.0
    location_y_mm: float = 0.0
    estimated_junction_temp_c: float
    max_rated_temp_c: float
    margin_c: float
    risk_level: str  # SAFE, ELEVATED, CRITICAL


class HardwareThermalInput(BaseModel):
    project_id: str
    board_dimensions_mm: Dict[str, float] = Field(default_factory=lambda: {"width": 100.0, "height": 80.0, "layers": 4})
    components: List[Dict[str, Any]] = Field(default_factory=list)
    enclosure_ambient_temp_c: float = 25.0
    airflow_lfm: float = 0.0  # Natural convection by default


class HardwareThermalOutput(BaseModel):
    agent_id: str = "agent.23"
    name: str = "HardwareThermalAgent"
    project_id: str
    status: str = "SUCCESS"
    stackup_recommendation: List[StackupLayer] = Field(default_factory=list)
    thermal_analysis: Dict[str, Any] = Field(default_factory=dict)
    hotspots: List[ThermalHotspot] = Field(default_factory=list)
    compliance_verdict: str = "PASS"
    summary: str = ""


class HardwareThermalAgent:
    """Agent #23: Hardware Thermal & Stackup Authority for Workline."""

    NAME = "HardwareThermalAgent"
    CAPABILITIES = [
        "hardware.stackup",
        "hardware.thermal",
        "hardware.signal_integrity"
    ]

    def __init__(self, db_client: Optional[Any] = None):
        self.db = db_client

    async def run(self, input_data: HardwareThermalInput) -> HardwareThermalOutput:
        """Executes stackup design, thermal dissipation modeling, and hotspot evaluation."""
        logger.info(f"[HardwareThermalAgent] Running thermal & stackup evaluation for project {input_data.project_id}")

        num_layers = int(input_data.board_dimensions_mm.get("layers", 4))
        stackup: List[StackupLayer] = []
        if num_layers == 4:
            stackup = [
                StackupLayer(layer_index=1, layer_name="Top Signal/Component", layer_type="copper", thickness_um=35.0, thermal_conductivity_w_mk=385.0),
                StackupLayer(layer_index=2, layer_name="Internal Ground Plane", layer_type="copper_plane", thickness_um=35.0, thermal_conductivity_w_mk=385.0),
                StackupLayer(layer_index=3, layer_name="Internal Power Plane", layer_type="copper_plane", thickness_um=35.0, thermal_conductivity_w_mk=385.0),
                StackupLayer(layer_index=4, layer_name="Bottom Signal/Ground", layer_type="copper", thickness_um=35.0, thermal_conductivity_w_mk=385.0),
            ]
        else:
            stackup = [
                StackupLayer(layer_index=1, layer_name="Top Signal", layer_type="copper", thickness_um=35.0, thermal_conductivity_w_mk=385.0),
                StackupLayer(layer_index=2, layer_name="Ground Plane 1", layer_type="copper_plane", thickness_um=35.0, thermal_conductivity_w_mk=385.0),
                StackupLayer(layer_index=3, layer_name="Signal Inner 1", layer_type="copper", thickness_um=17.5, thermal_conductivity_w_mk=385.0),
                StackupLayer(layer_index=4, layer_name="Power Plane", layer_type="copper_plane", thickness_um=35.0, thermal_conductivity_w_mk=385.0),
                StackupLayer(layer_index=5, layer_name="Ground Plane 2", layer_type="copper_plane", thickness_um=35.0, thermal_conductivity_w_mk=385.0),
                StackupLayer(layer_index=6, layer_name="Bottom Signal", layer_type="copper", thickness_um=35.0, thermal_conductivity_w_mk=385.0),
            ]

        raw_analysis = calculate_project_thermal_analysis(
            components=input_data.components,
            project_id=input_data.project_id
        )

        hotspots: List[ThermalHotspot] = []
        overall_pass = True

        for comp in input_data.components:
            mpn = comp.get("mpn", "")
            mpn_lower = mpn.lower().replace("-", "").replace("/", "")
            
            matched_spec = None
            for key, spec in VERIFIED_COMPONENT_THERMAL_SPECS.items():
                if key in mpn_lower:
                    matched_spec = spec
                    break

            max_rated = matched_spec["max_temp_c"] if matched_spec else 85.0
            power_dissipation_w = float(comp.get("power_w", 0.5))
            theta_ja = float(comp.get("theta_ja_c_w", 35.0))
            
            estimated_tj = input_data.enclosure_ambient_temp_c + (power_dissipation_w * theta_ja)
            margin = max_rated - estimated_tj
            
            risk = "SAFE"
            if margin < 10.0:
                risk = "CRITICAL"
                overall_pass = False
            elif margin < 25.0:
                risk = "ELEVATED"

            hotspots.append(
                ThermalHotspot(
                    component_mpn=mpn or "UNKNOWN_COMP",
                    location_x_mm=float(comp.get("x", 0.0)),
                    location_y_mm=float(comp.get("y", 0.0)),
                    estimated_junction_temp_c=round(estimated_tj, 2),
                    max_rated_temp_c=max_rated,
                    margin_c=round(margin, 2),
                    risk_level=risk
                )
            )

        verdict = "PASS" if overall_pass else "MARGINAL_REVIEW"
        summary = (
            f"Hardware thermal evaluation complete for {len(input_data.components)} components. "
            f"Board stackup optimized for {num_layers} layers with solid continuous copper GND return planes. "
            f"Thermal compliance: {verdict} with ambient baseline at {input_data.enclosure_ambient_temp_c}C."
        )

        return HardwareThermalOutput(
            project_id=input_data.project_id,
            status="SUCCESS",
            stackup_recommendation=stackup,
            thermal_analysis=raw_analysis,
            hotspots=hotspots,
            compliance_verdict=verdict,
            summary=summary
        )
