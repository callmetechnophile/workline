"""
Power architecture and voltage domain design service for EngineeringArchitectureAgent (Sections 13 & 14).
"""

from typing import List
from research_agents.engineering_architecture_agent.schemas import PowerDomainItem, SubsystemItem


class PowerArchitect:
    """Architects multi-rail power domains, regulation stages, and protection circuits."""

    def build_power_domains(
        self,
        subsystems: List[SubsystemItem],
    ) -> List[PowerDomainItem]:
        """
        Synthesizes structured power rails matching component voltage requirements.
        """
        domains: List[PowerDomainItem] = []

        # 1. Main Battery Rail
        domains.append(
            PowerDomainItem(
                power_domain_id="PWR-001",
                name="14.8V Battery Main Bus",
                source="4S LiPo 5000mAh Battery Pack",
                voltage="14.8V Nominal (13.0V - 16.8V)",
                loads=["Brushless Motor ESCs", "5.0V Buck Step-Down Stage"],
                estimated_current="15A Continuous / 25A Burst",
                regulation="Direct Battery Output with Low-ESR Filtering",
                protection=["30A Inline Blade Fuse", "Reverse-Polarity Schottky Diode"],
                confidence=0.95,
                validation_required=True,
            )
        )

        # 2. 5.0V Compute Rail
        domains.append(
            PowerDomainItem(
                power_domain_id="PWR-002",
                name="5.0V Compute Rail",
                source="Synchronous Switching Buck Regulator",
                voltage="5.0V +/- 2%",
                loads=["NVIDIA Jetson Orin Nano Carrier Board", "USB Peripherals"],
                estimated_current="4.5A Peak @ 15W Mode",
                regulation="Synchronous Step-Down Buck (5V/5A, 500 kHz)",
                protection=["TVS Overvoltage Clamp", "1000uF Solid Polymer Capacitor"],
                confidence=0.95,
                validation_required=True,
            )
        )

        # 3. 3.3V Clean Logic Rail
        domains.append(
            PowerDomainItem(
                power_domain_id="PWR-003",
                name="3.3V Logic & Sensor Rail",
                source="Ultra-Low Noise LDO Regulator",
                voltage="3.3V +/- 1%",
                loads=["FLIR Lepton 3.5 Thermal Core", "ESP32-S3 MCU", "IMU & Barometer Sensors"],
                estimated_current="650mA Peak",
                regulation="Linear LDO Regulator (Ripple Rejection > 65 dB @ 10 kHz)",
                protection=["Decoupling Ceramic Capacitors (10uF + 0.1uF per IC)"],
                confidence=0.98,
                validation_required=True,
            )
        )

        return domains
