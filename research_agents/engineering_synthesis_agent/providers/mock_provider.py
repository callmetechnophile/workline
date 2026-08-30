"""
Deterministic mock reasoning provider for EngineeringSynthesisAgent offline testing and CLI demo mode.
"""

from typing import Optional, Type, TypeVar
from pydantic import BaseModel
from research_agents.engineering_synthesis_agent.providers.base import ReasoningProvider

T = TypeVar("T", bound=BaseModel)


class MockEngineeringSynthesisProvider(ReasoningProvider):
    """Deterministic offline reasoning provider simulating Bedrock synthesis decisions."""

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        return "Engineering decision synthesis completed."

    async def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_prompt: Optional[str] = None,
    ) -> T:
        data = {
            "requirement_analysis": [
                {
                    "requirement_id": "REQ-001",
                    "requirement": "Thermal human detection on edge hardware",
                    "coverage": "strong",
                    "evidence_count": 3,
                    "supporting_evidence_ids": ["ev_p_001", "ev_w_001"],
                    "technical_findings": ["FIND-001", "FIND-002"],
                    "decision_available": True,
                    "confidence": 0.95,
                },
                {
                    "requirement_id": "REQ-002",
                    "requirement": "Real-time edge inference latency under 100ms",
                    "coverage": "strong",
                    "evidence_count": 2,
                    "supporting_evidence_ids": ["ev_p_001", "ev_w_001"],
                    "technical_findings": ["FIND-001"],
                    "decision_available": True,
                    "confidence": 0.92,
                },
            ],
            "technical_findings": [
                {
                    "finding_id": "FIND-001",
                    "category": "compute",
                    "finding": "NVIDIA Jetson Orin Nano achieves 45 FPS using YOLOv8n TensorRT INT8 model.",
                    "evidence_ids": ["ev_p_001", "ev_w_001"],
                    "impact_on_project": "Satisfies the 30 FPS / 100 ms latency requirement with 50% margin.",
                    "confidence": 0.96,
                },
                {
                    "finding_id": "FIND-002",
                    "category": "thermal",
                    "finding": "FLIR Lepton 3.5 provides radiometric LWIR sensing with 8.7 Hz raw export refresh.",
                    "evidence_ids": ["ev_f_001"],
                    "impact_on_project": "Requires pipeline frame interpolation to present 30+ FPS search video.",
                    "confidence": 0.98,
                },
            ],
            "tradeoffs": [
                {
                    "tradeoff_id": "TRADE-001",
                    "decision_area": "Edge Compute Platform",
                    "options": [
                        {
                            "option": "NVIDIA Jetson Orin Nano",
                            "advantages": ["40 TOPS AI compute", "Native TensorRT support", "45 FPS detection"],
                            "disadvantages": ["Higher power draw (15 W peak)", "Requires active cooling"],
                            "evidence_ids": ["ev_w_001"],
                        },
                        {
                            "option": "Raspberry Pi 5",
                            "advantages": ["Lower base cost", "Simple ecosystem"],
                            "disadvantages": ["No dedicated NPU/GPU acceleration", "< 10 FPS thermal inference"],
                            "evidence_ids": ["ev_p_001"],
                        },
                    ],
                    "recommended_option": "NVIDIA Jetson Orin Nano",
                    "reasoning": "Real-time 30+ FPS neural detection cannot be achieved on Raspberry Pi 5 without external accelerator.",
                    "confidence": 0.94,
                }
            ],
            "decisions": [
                {
                    "decision_id": "DEC-001",
                    "decision_area": "Primary Edge AI Compute",
                    "selected_option": "NVIDIA Jetson Orin Nano 8GB",
                    "alternatives": ["Raspberry Pi 5 + Hailo-8", "ESP32-S3"],
                    "decision_reason": "Delivers 40 TOPS AI compute for real-time YOLOv8n-pose thermal human detection at 15 W.",
                    "tradeoffs": ["TRADE-001"],
                    "evidence_ids": ["ev_p_001", "ev_w_001"],
                    "requirement_ids": ["REQ-001", "REQ-002"],
                    "confidence": 0.95,
                    "validation_required": True,
                }
            ],
            "recommendations": [
                {
                    "recommendation_id": "REC-001",
                    "category": "hardware",
                    "recommendation": "Integrate Jetson Orin Nano carrier board with dedicated 5V/5A switching regulator.",
                    "reason": "Prevents voltage sag and brownout resets during peak GPU bursts at 15 W.",
                    "supporting_evidence_ids": ["ev_w_001"],
                    "supporting_requirement_ids": ["REQ-001"],
                    "assumptions": ["Payload battery can supply 25 W continuous."],
                    "confidence": 0.94,
                    "validation_required": True,
                }
            ],
            "assumptions": [
                {
                    "assumption_id": "ASM-001",
                    "assumption": "UAV airframe prop wash provides supplemental forced-air convection across compute heatsink.",
                    "impact": "Reduces dedicated fan weight and electrical consumption.",
                    "confidence": 0.80,
                    "validation_required": True,
                }
            ],
            "unknowns": [
                {
                    "unknown_id": "UNK-001",
                    "unknown": "Exact thermal human detection range through heavy canopy foliage.",
                    "why_it_matters": "Determines optimal search flight altitude (e.g. 15m vs 30m).",
                    "required_information": "Empirical field trial data in temperate deciduous forest.",
                    "blocking": False,
                }
            ],
            "risks": [
                {
                    "risk_id": "RISK-001",
                    "category": "thermal",
                    "description": "Jetson Orin Nano thermal throttling during prolonged summer hover flights.",
                    "likelihood": "medium",
                    "impact": "high",
                    "severity": "high",
                    "mitigation": "Design aluminum ducting channeling propeller downdraft over heatsink fins.",
                    "evidence_ids": ["ev_w_001"],
                    "validation_required": True,
                }
            ],
            "validation_requirements": [
                {
                    "validation_id": "VAL-001",
                    "category": "bench_test",
                    "description": "Measure Jetson Orin Nano power draw and FPS over 30 minutes of continuous YOLOv8 inference.",
                    "acceptance_criteria": "Sustained FPS >= 30, Power <= 17 W, Core temperature < 80 deg C.",
                    "decision_ids": ["DEC-001"],
                }
            ],
            "experiments": [
                {
                    "experiment_id": "EXP-001",
                    "question": "Does prop wash provide sufficient cooling without an active fan?",
                    "setup": ["Mount Jetson Orin Nano under drone propeller test rig with simulated 15W GPU load."],
                    "variables": ["Propeller RPM (0, 3000, 6000)", "Ambient temperature (25C, 40C)"],
                    "metrics": ["SoC junction temperature", "Heatsink delta-T"],
                    "acceptance_criteria": ["Junction temp remains < 75C at 40C ambient with 4000+ RPM."],
                }
            ],
            "traceability": [
                {
                    "decision_id": "DEC-001",
                    "requirement_ids": ["REQ-001", "REQ-002"],
                    "evidence_ids": ["ev_p_001", "ev_w_001"],
                    "finding_ids": ["FIND-001"],
                    "tradeoff_id": "TRADE-001",
                    "decision": "NVIDIA Jetson Orin Nano 8GB",
                    "reasoning": "Meets 30+ FPS latency requirement with verified 45 FPS benchmark on INT8 TensorRT.",
                    "validation_ids": ["VAL-001"],
                }
            ],
            "overall_confidence": 0.92,
        }

        return schema.model_validate(data)
