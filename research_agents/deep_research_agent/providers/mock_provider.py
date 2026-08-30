"""
Deterministic mock reasoning provider for offline testing and CLI development mode.
"""

from typing import Optional, Type, TypeVar
from pydantic import BaseModel

from research_agents.deep_research_agent.providers.base import ReasoningProvider
from research_agents.deep_research_agent.schemas import (
    ComponentTradeStudy,
    ContradictionReport,
    CrossSourceComparison,
    EngineeringImplication,
    EngineeringRecommendation,
    SynthesizedClaim,
)

T = TypeVar("T", bound=BaseModel)


class MockReasoningProvider(ReasoningProvider):
    """Deterministic offline reasoning provider simulating Amazon Bedrock output."""

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        return (
            "# Autonomous Thermal Drone System Synthesis\n\n"
            "## Architecture Overview\n"
            "The proposed system uses an edge computing architecture pairing the NVIDIA Jetson Orin Nano "
            "with a FLIR Lepton 3.5 thermal camera over SPI and I2C interfaces."
        )

    async def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_prompt: Optional[str] = None,
    ) -> T:
        # Dynamically instantiate requested schema with realistic mock fields
        dummy_data = {
            "executive_summary": (
                "An edge computing architecture combining the NVIDIA Jetson Orin Nano with a FLIR Lepton 3.5 "
                "radiometric thermal camera enables real-time 45 FPS human detection at 15 W power envelope."
            ),
            "architecture_analysis": (
                "The system partitions workloads into real-time sensing via ESP32-S3 and neural inference "
                "via TensorRT on Jetson Orin Nano over high-speed UART and ROS 2 Humble micro-ROS."
            ),
            "component_trade_studies": [
                {
                    "component_type": "Edge Compute Module",
                    "candidates_evaluated": ["NVIDIA Jetson Orin Nano", "Raspberry Pi 5", "ESP32-S3"],
                    "tradeoff_matrix": {
                        "NVIDIA Jetson Orin Nano": {"AI_TOPS": 40, "Power_W": 15, "Thermal_FPS": 45},
                        "Raspberry Pi 5": {"AI_TOPS": 0, "Power_W": 12, "Thermal_FPS": 8},
                        "ESP32-S3": {"AI_TOPS": 0.05, "Power_W": 0.5, "Thermal_FPS": 1},
                    },
                    "recommended_option": "NVIDIA Jetson Orin Nano",
                    "recommendation_reason": "Delivers necessary 40 TOPS for real-time YOLOv8 thermal inference at acceptable 15 W payload power.",
                }
            ],
            "extracted_claims": [
                {
                    "claim": "NVIDIA Jetson Orin Nano delivers up to 40 TOPS AI compute at 15 W.",
                    "claim_type": "explicit_source_claim",
                    "source_evidence_ids": ["ev_nvidia_01"],
                    "confidence": 0.98,
                },
                {
                    "claim": "The architecture satisfies real-time search requirements under 100 ms latency.",
                    "claim_type": "model_inference",
                    "source_evidence_ids": ["ev_nvidia_01", "ev_paper_02"],
                    "confidence": 0.90,
                    "rationale": "45 FPS execution yields ~22 ms frame time, well below 100 ms threshold.",
                },
                {
                    "claim": "Select NVIDIA Jetson Orin Nano with 8 GB RAM for high-resolution TensorRT models.",
                    "claim_type": "engineering_recommendation",
                    "source_evidence_ids": ["ev_nvidia_01"],
                    "confidence": 0.95,
                },
            ],
            "cross_source_comparisons": [
                {
                    "topic": "Thermal Camera Interface",
                    "sources_agree": True,
                    "summary": "Both datasheet and open-source packages confirm SPI for video and I2C for CCI commands.",
                    "evidence_ids": ["ev_flir_01", "ev_gh_01"],
                }
            ],
            "contradictions": [
                {
                    "topic": "FLIR Lepton Radiometric Refresh Rate",
                    "source_a_claim": "Datasheet specifies 8.7 Hz export-compliant refresh rate.",
                    "source_a_evidence_id": "ev_flir_01",
                    "source_b_claim": "Research paper claims 30 Hz thermal tracking rate using interpolation.",
                    "source_b_evidence_id": "ev_paper_02",
                    "resolution": "Camera hardware operates at 8.7 Hz raw; paper achieved 30 Hz via optical flow frame interpolation.",
                }
            ],
            "engineering_implications": [
                {
                    "category": "power",
                    "finding": "Combined compute and camera load reaches 18 W peak.",
                    "impact_on_project": "Requires dedicated 5V/5A buck converter and 4S LiPo battery sizing.",
                },
                {
                    "category": "thermal",
                    "finding": "Jetson Orin Nano requires active heatsink fan at 15 W continuous load.",
                    "impact_on_project": "Must incorporate forced-air ducting from drone prop wash.",
                },
            ],
            "recommendations": [
                {
                    "recommendation": "Deploy YOLOv8n-pose with INT8 TensorRT quantization on Jetson Orin Nano.",
                    "category": "software",
                    "priority": "high",
                    "justification": "Provides best trade-off between thermal accuracy and power consumption.",
                    "backed_by_claims": ["NVIDIA Jetson Orin Nano delivers up to 40 TOPS AI compute at 15 W."],
                }
            ],
            "research_gaps": [
                "Empirical validation of thermal detection range through heavy smoke / foliage.",
                "Long-term vibration reliability of micro-coaxial SPI wiring in UAV airframe.",
            ],
        }

        return schema.model_validate(dummy_data)
