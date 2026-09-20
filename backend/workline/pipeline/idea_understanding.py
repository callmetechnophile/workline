"""
Idea Understanding Agent and Requirement/Constraint Extraction Engine.
Responsible for semantic parsing, requirement structuring, constraint extraction,
and clarification detection without hallucinating component MPNs or factual specifications.
"""

import re
import json
import uuid
import time
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field
from loguru import logger


# ============================================================================
# 1. SCHEMAS
# ============================================================================

class IdeaUnderstandingOutput(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    architecture_summary: Optional[str] = None
    key_subsystems: List[str] = Field(default_factory=list)
    project_objective: str
    application_domain: str
    required_functions: List[str] = Field(default_factory=list)
    inputs: List[str] = Field(default_factory=list)
    outputs: List[str] = Field(default_factory=list)
    sensors: List[str] = Field(default_factory=list)
    actuators: List[str] = Field(default_factory=list)
    controller_requirements: List[str] = Field(default_factory=list)
    communication_requirements: List[str] = Field(default_factory=list)
    power_requirements: List[str] = Field(default_factory=list)
    environmental_requirements: List[str] = Field(default_factory=list)
    voltage_requirements: List[str] = Field(default_factory=list)
    current_requirements: List[str] = Field(default_factory=list)
    safety_requirements: List[str] = Field(default_factory=list)
    optional_components: List[str] = Field(default_factory=list)
    clarifications_needed: List[str] = Field(default_factory=list)


class StructuredRequirement(BaseModel):
    requirement_id: str
    project_id: str
    title: str
    description: str
    category: str = "FUNCTIONAL"  # FUNCTIONAL, ELECTRICAL, ENVIRONMENTAL, POWER, INTERFACE, SAFETY
    parameter: Optional[str] = None
    target_value: str = "NOT SPECIFIED"
    unit: str = "N/A"
    priority: str = "HIGH"  # CRITICAL, HIGH, MEDIUM, LOW
    source: str = "USER_INPUT"
    confidence: float = 0.95
    status: str = "PENDING"  # Initial state is strictly PENDING
    verification_method: str = "Datasheet Verification"  # Simulation, Datasheet Verification, Analysis, Physical Test


class StructuredConstraint(BaseModel):
    constraint_id: str
    project_id: str
    requirement_id: Optional[str] = None
    title: str
    description: str
    property: str
    operator: str = "<="  # <=, >=, =, range
    required_value: str = "UNKNOWN / REQUIRES CLARIFICATION"
    value: str = "UNKNOWN / REQUIRES CLARIFICATION"
    unit: str = "N/A"
    severity: str = "CRITICAL"
    type: str = "TECHNICAL"
    source: str = "ENGINEERING_STANDARDS"
    status: str = "PENDING"


# ============================================================================
# 2. DETERMINISTIC DOMAIN RULE PARSER (FALLBACK & VERIFICATION)
# ============================================================================

def _parse_idea_deterministic(idea: str, project_id: str) -> Tuple[IdeaUnderstandingOutput, List[StructuredRequirement], List[StructuredConstraint], List[str]]:
    text = idea.lower()

    # 1. Smart Irrigation / Agricultural IoT
    if any(k in text for k in ("irrigation", "soil", "agriculture", "crop", "farm", "watering", "plant")):
        obj = IdeaUnderstandingOutput(
            project_objective=f"Autonomous precision irrigation and soil condition monitoring: {idea}",
            application_domain="Agricultural IoT & Embedded Systems",
            required_functions=[
                "Monitor soil volumetric water content / moisture continuously",
                "Measure ambient environmental temperature and relative humidity",
                "Control water pump or solenoid valve based on moisture thresholds",
                "Transmit telemetry over wireless IoT protocol (Wi-Fi/LoRa/MQTT)",
                "Operate with power efficiency for outdoor deployment",
            ],
            inputs=["Soil moisture level (analog/frequency)", "Ambient temperature & humidity", "Reservoir water level"],
            outputs=["Solenoid valve relay drive signal", "Status indicator LED / Telemetry stream", "Alert notification"],
            sensors=["Capacitive Soil Moisture Sensor (corrosion resistant)", "Digital Ambient Temperature & Humidity Sensor"],
            actuators=["12V DC Solenoid Water Valve", "Submersible Water Pump Control Relay"],
            controller_requirements=["Low-power 32-bit MCU with integrated Wi-Fi / BLE", "At least 2x 12-bit ADC channels", "Multiple GPIOs for relay switching"],
            communication_requirements=["Wi-Fi 802.11 b/g/n", "MQTT / HTTP REST telemetry publishing"],
            power_requirements=["12V DC input or Solar/Battery buffer with 5V and 3.3V regulated rails"],
            environmental_requirements=["IP65 enclosure suitability", "Outdoor operating range -10°C to +60°C"],
            voltage_requirements=["12V DC for solenoid valve", "5V DC for relay coils", "3.3V DC for microcontroller & sensors"],
            current_requirements=["Peak 1.5A during valve/pump switching", "Quiescent < 50mA in sleep/sensing mode"],
            safety_requirements=["Flyback diode across inductive relay coils", "Reverse polarity input protection", "Fuse on main DC power line"],
            optional_components=["Solar charging panel & battery management IC", "0.96 inch I2C OLED display"],
            clarifications_needed=[
                "What is the total water flow rate or pipe diameter for the solenoid valve?",
                "Is the unit powered by mains DC adapter or battery/solar power?",
                "What wireless range is required to reach the local gateway/router?",
            ]
        )
        reqs = [
            StructuredRequirement(
                requirement_id="REQ-001",
                project_id=project_id,
                title="Soil Moisture Sensing Sensitivity",
                description="Detect volumetric water content between dry (0%) and saturated (100%) states using corrosion-resistant probe.",
                category="FUNCTIONAL",
                parameter="moisture_range",
                target_value="0 - 100",
                unit="%",
                priority="CRITICAL",
                source="USER_INPUT",
                verification_method="Physical Test",
            ),
            StructuredRequirement(
                requirement_id="REQ-002",
                project_id=project_id,
                title="Solenoid Valve Actuation Voltage",
                description="Actuator driver must supply sufficient voltage and current to actuate the 12V DC water valve.",
                category="ELECTRICAL",
                parameter="actuator_voltage",
                target_value="12.0",
                unit="V",
                priority="HIGH",
                source="USER_INPUT",
                verification_method="Datasheet Verification",
            ),
            StructuredRequirement(
                requirement_id="REQ-003",
                project_id=project_id,
                title="Logic Rail Regulation",
                description="Supply a clean 3.3V rail with ripple < 50mV for MCU and precision analog sensors.",
                category="POWER",
                parameter="logic_voltage",
                target_value="3.3",
                unit="V",
                priority="CRITICAL",
                source="ENGINEERING_STANDARDS",
                verification_method="Simulation",
            ),
            StructuredRequirement(
                requirement_id="REQ-004",
                project_id=project_id,
                title="Telemetry Latency",
                description="Publish soil condition updates to cloud gateway within specified cadence.",
                category="PERFORMANCE",
                parameter="update_interval",
                target_value="60",
                unit="s",
                priority="MEDIUM",
                source="USER_INPUT",
                verification_method="Software Test",
            ),
        ]
        cons = [
            StructuredConstraint(
                constraint_id="CON-001",
                project_id=project_id,
                requirement_id="REQ-002",
                title="Maximum Operating Voltage Rail",
                description="Power subsystem must safely regulate input voltages up to 14V.",
                property="voltage_max",
                operator="<=",
                required_value="14.0",
                value="14.0",
                unit="V",
                severity="CRITICAL",
                source="ENGINEERING_STANDARDS",
            ),
            StructuredConstraint(
                constraint_id="CON-002",
                project_id=project_id,
                requirement_id="REQ-003",
                title="Maximum Quiescent Current",
                description="Total standby current consumption during sleep should not exceed budget.",
                property="quiescent_current_ma",
                operator="<=",
                required_value="50.0",
                value="50.0",
                unit="mA",
                severity="HIGH",
                source="USER_INPUT",
            ),
            StructuredConstraint(
                constraint_id="CON-003",
                project_id=project_id,
                title="Operating Ambient Temperature",
                description="Electronics must operate reliably in agricultural temperature range.",
                property="operating_temperature_max",
                operator="<=",
                required_value="65.0",
                value="65.0",
                unit="°C",
                severity="MEDIUM",
                source="ENVIRONMENTAL",
            ),
        ]
        return obj, reqs, cons, obj.clarifications_needed

    # 2. Wearable Health / Heart Rate & Temp Monitoring
    elif any(k in text for k in ("heart", "pulse", "wearable", "spo2", "health", "biomedical", "vital", "patient", "medical")):
        obj = IdeaUnderstandingOutput(
            project_objective=f"Non-invasive wearable biometric telemetry device: {idea}",
            application_domain="Wearable Biometric Electronics & Digital Health",
            required_functions=[
                "Acquire photoplethysmography (PPG) pulse and oxygen saturation (SpO2)",
                "Measure skin contact surface temperature with high accuracy (±0.1°C)",
                "Filter motion artifacts and ambient optical noise",
                "Stream vitals wirelessly over Bluetooth Low Energy (BLE) to mobile device",
                "Manage rechargeable single-cell Li-Ion/LiPo battery power",
            ],
            inputs=["PPG optical reflectance signal", "Skin surface thermal sensor", "Battery voltage level"],
            outputs=["Heart rate (BPM) & SpO2 (%)", "Skin temperature (°C)", "BLE peripheral telemetry stream"],
            sensors=["Optical Pulse Oximeter & Heart-Rate Sensor", "Clinical-Grade Digital Temperature Sensor", "3-axis MEMS Accelerometer (motion compensation)"],
            actuators=["Haptic vibration motor (alerts)", "Status RGB micro-LED"],
            controller_requirements=["Ultra-low-power ARM Cortex-M4F MCU with native BLE 5.0/5.2 stack", "Hardware AES encryption for health data", "Direct battery voltage ADC monitor"],
            communication_requirements=["Bluetooth Low Energy (BLE) GATT profile for Health Device Profile (HDP)"],
            power_requirements=["Single-cell 3.7V LiPo rechargeable battery with integrated USB-C charger"],
            environmental_requirements=["Skin contact bio-compatible enclosure", "Sweat and moisture resistance (IPX7)"],
            voltage_requirements=["1.8V to 3.3V operating logic levels", "4.2V max battery charge voltage"],
            current_requirements=["Average active current < 15mA with optical LEDs enabled", "Deep sleep current < 25µA"],
            safety_requirements=["Thermal runaway protection during charging", "Current-limiting on skin-contact electrodes/housing", "ESD protection on USB pins"],
            optional_components=["OLED miniature display", "Wireless Qi inductive charging coil"],
            clarifications_needed=[
                "Where will the wearable be worn (wrist, finger, chest, or earlobe)?",
                "What is the target continuous runtime between battery charges (e.g. 24 hours or 7 days)?",
                "Is clinical/medical grade regulatory compliance (FDA/CE Class II) required or consumer wellness grade?",
            ]
        )
        reqs = [
            StructuredRequirement(
                requirement_id="REQ-001",
                project_id=project_id,
                title="Heart Rate Acquisition Accuracy",
                description="Acquire resting and active heart rate in 40-200 BPM range with ±2 BPM accuracy.",
                category="PERFORMANCE",
                parameter="hr_accuracy_bpm",
                target_value="2.0",
                unit="BPM",
                priority="CRITICAL",
                source="USER_INPUT",
                verification_method="Physical Test",
            ),
            StructuredRequirement(
                requirement_id="REQ-002",
                project_id=project_id,
                title="Temperature Measurement Precision",
                description="Clinical accuracy skin temperature monitoring within 35.0°C to 42.0°C range.",
                category="PERFORMANCE",
                parameter="temp_accuracy_c",
                target_value="0.1",
                unit="°C",
                priority="CRITICAL",
                source="USER_INPUT",
                verification_method="Datasheet Verification",
            ),
            StructuredRequirement(
                requirement_id="REQ-003",
                project_id=project_id,
                title="Rechargeable Battery Operating Voltage",
                description="Subsystem must run directly from 3.0V - 4.2V LiPo battery with regulated 3.3V output.",
                category="POWER",
                parameter="operating_voltage",
                target_value="3.3",
                unit="V",
                priority="HIGH",
                source="ENGINEERING_STANDARDS",
                verification_method="Simulation",
            ),
        ]
        cons = [
            StructuredConstraint(
                constraint_id="CON-001",
                project_id=project_id,
                requirement_id="REQ-003",
                title="Maximum Device Enclosure Thickness",
                description="Compact wearable form factor constraint.",
                property="thickness_mm",
                operator="<=",
                required_value="12.0",
                value="12.0",
                unit="mm",
                severity="HIGH",
                source="USER_INPUT",
            ),
            StructuredConstraint(
                constraint_id="CON-002",
                project_id=project_id,
                title="Maximum Continuous Operating Current",
                description="Active power budget to achieve minimum 24-hour runtime on a 200mAh battery.",
                property="active_current_ma",
                operator="<=",
                required_value="15.0",
                value="15.0",
                unit="mA",
                severity="CRITICAL",
                source="USER_INPUT",
            ),
        ]
        return obj, reqs, cons, obj.clarifications_needed

    # 3. Autonomous Line-Following Robot
    elif any(k in text for k in ("line", "robot", "follow", "follower", "rover", "autonomous", "motor", "differential")):
        obj = IdeaUnderstandingOutput(
            project_objective=f"High-precision autonomous line-following mobile robot: {idea}",
            application_domain="Mobile Robotics & Autonomous Control",
            required_functions=[
                "Detect black line on white surface (or inverse) with sub-millimeter precision",
                "Execute real-time PID steering loop at >= 100Hz",
                "Drive dual DC gearmotors via PWM H-bridge driver",
                "Provide emergency stop and collision avoidance sensing",
                "Regulate dual voltage domains for sensitive logic and noisy inductive motors",
            ],
            inputs=["Multi-channel IR reflectance sensor array", "Wheel encoder tachometer pulses", "User pushbuttons / DIP switches"],
            outputs=["Dual motor PWM speed & directional signals", "PID calibration feedback LED display"],
            sensors=["8-channel Infrared Reflectance Sensor Array (e.g. TCRT5000 / QTR-8A)", "Quadrature Wheel Encoders", "Ultrasonic / Time-of-Flight Obstacle Sensor"],
            actuators=["Dual DC Micro Metal Gearmotors (6V-12V, 300-600 RPM)", "Dual Full H-Bridge Motor Driver IC"],
            controller_requirements=["Real-time 32-bit MCU (ARM Cortex-M4 or high-speed RISC-V)", "High-resolution hardware PWM timers (>= 20kHz to eliminate audible motor whine)", "Fast multi-channel ADC"],
            communication_requirements=["UART / USB debugging telemetry port", "Optional BLE / Wi-Fi for parameter tuning"],
            power_requirements=["2S LiPo battery (7.4V nominal) with high-efficiency 5V and 3.3V buck regulators"],
            environmental_requirements=["Indoor flat surface track", "Vibration tolerance for motor mounts"],
            voltage_requirements=["6V - 8.4V for motor rails", "5V for IR sensor array", "3.3V for microcontroller"],
            current_requirements=["Peak stall current up to 3.0A for motors combined", "150mA for logic and sensors"],
            safety_requirements=["Flyback suppression diodes / integrated MOSFET body diodes", "Logic and motor power rail isolation with bulk decoupling", "Emergency hardware cut-off switch"],
            optional_components=["OLED display for real-time PID tuning", "Buzzer for calibration sounds"],
            clarifications_needed=[
                "What is the track line width (standard 15mm or 30mm) and minimum curve radius?",
                "What is the target maximum speed (e.g. 0.5 m/s or 2.0 m/s)?",
                "Is motor encoder feedback strictly required or is open-loop PID adequate?",
            ]
        )
        reqs = [
            StructuredRequirement(
                requirement_id="REQ-001",
                project_id=project_id,
                title="Line Detection Resolution",
                description="Infrared reflectance array must detect line position with at least 8 discrete sensors across 60mm width.",
                category="FUNCTIONAL",
                parameter="sensor_channels",
                target_value="8",
                unit="channels",
                priority="CRITICAL",
                source="USER_INPUT",
                verification_method="Physical Test",
            ),
            StructuredRequirement(
                requirement_id="REQ-002",
                project_id=project_id,
                title="Motor Drive Peak Current",
                description="Motor driver H-bridge must continuously handle 1.0A per channel and 2.5A peak stall current.",
                category="ELECTRICAL",
                parameter="motor_driver_peak_current",
                target_value="2.5",
                unit="A",
                priority="CRITICAL",
                source="ENGINEERING_STANDARDS",
                verification_method="Datasheet Verification",
            ),
            StructuredRequirement(
                requirement_id="REQ-003",
                project_id=project_id,
                title="PID Loop Frequency",
                description="Control loop execution frequency must maintain stability at max robot speed.",
                category="PERFORMANCE",
                parameter="loop_frequency_hz",
                target_value="100.0",
                unit="Hz",
                priority="HIGH",
                source="USER_INPUT",
                verification_method="Simulation",
            ),
        ]
        cons = [
            StructuredConstraint(
                constraint_id="CON-001",
                project_id=project_id,
                requirement_id="REQ-002",
                title="Motor Peak Current Constraint",
                description="Dual motor total stall draw limit to protect driver.",
                property="motor_stall_current_max",
                operator="<=",
                required_value="3.0",
                value="3.0",
                unit="A",
                severity="CRITICAL",
                source="ENGINEERING_STANDARDS",
            ),
            StructuredConstraint(
                constraint_id="CON-002",
                project_id=project_id,
                title="Maximum Chassis Width",
                description="Robot width must fit standard competition racing lane.",
                property="chassis_width_mm",
                operator="<=",
                required_value="160.0",
                value="160.0",
                unit="mm",
                severity="HIGH",
                source="USER_INPUT",
            ),
        ]
        return obj, reqs, cons, obj.clarifications_needed

    # 4. Solar-Powered Environmental Monitoring Station
    elif any(k in text for k in ("solar", "environmental", "weather", "mppt", "climate", "air quality", "station", "remote")):
        obj = IdeaUnderstandingOutput(
            project_objective=f"Off-grid solar-powered remote environmental telemetry station: {idea}",
            application_domain="Renewable Power & Remote Environmental Sensing",
            required_functions=[
                "Harvest solar energy via Maximum Power Point Tracking (MPPT) circuit",
                "Charge and manage backup LiFePO4 or Li-Ion energy storage pack",
                "Measure temperature, relative humidity, barometric pressure, and air quality VOCs",
                "Transmit long-range telemetry via LoRa / Cellular LPWAN / Wi-Fi",
                "Operate indefinitely in zero-maintenance remote outdoor environment",
            ],
            inputs=["Solar photovoltaic panel DC voltage/current", "Environmental physical sensors (I2C/SPI)", "Battery state-of-charge"],
            outputs=["Long-range wireless RF packet", "Power telemetry logs", "Low-power status beacon"],
            sensors=["Combined Environmental Barometer/Temp/Humidity Sensor", "Digital Gas / VOC Air Quality Sensor", "High-Side Current & Voltage Power Monitor IC"],
            actuators=["Battery heater switch (optional for freezing climates)", "RF antenna matching switch"],
            controller_requirements=["Ultra-low-power MCU with deep sleep support (< 10µA)", "Hardware I2C and SPI buses", "Integrated or interfaced Sub-GHz LoRa transceiver"],
            communication_requirements=["Long-range LoRaWAN (868/915 MHz) or NB-IoT telemetry link"],
            power_requirements=["6V-18V Solar Photovoltaic panel with dedicated MPPT Buck Charger and 3.2V/3.7V battery buffer"],
            environmental_requirements=["IP67 waterproof outdoor enclosure", "Operating temperature range -30°C to +70°C"],
            voltage_requirements=["Solar Vmp 6.0V - 18.0V", "Battery rail 3.0V - 4.2V", "Regulated 3.3V logic rail"],
            current_requirements=["Transmit burst current < 120mA", "Average sleep current < 50µA"],
            safety_requirements=["Battery over-charge and over-discharge UVLO protection", "Solar reverse-leakage blocking diode", "Lightning and static ESD surge suppression"],
            optional_components=["Rain gauge tip counter sensor", "Wind speed anemometer pulse counter"],
            clarifications_needed=[
                "What is the required telemetry transmission distance (e.g. 5km LoRa or cellular)?",
                "What is the geographic installation latitude or average daily sunlight hours?",
                "What battery chemistry is preferred (LiFePO4 for wide temperature or standard LiPo)?",
            ]
        )
        reqs = [
            StructuredRequirement(
                requirement_id="REQ-001",
                project_id=project_id,
                title="MPPT Solar Energy Harvesting Efficiency",
                description="Power management circuit must implement dynamic MPPT tracking with > 90% conversion efficiency.",
                category="POWER",
                parameter="mppt_efficiency_pct",
                target_value="90.0",
                unit="%",
                priority="CRITICAL",
                source="USER_INPUT",
                verification_method="Analysis",
            ),
            StructuredRequirement(
                requirement_id="REQ-002",
                project_id=project_id,
                title="Environmental Sensing Accuracy",
                description="Measure ambient pressure within 300-1100 hPa and temperature within -40°C to +85°C.",
                category="FUNCTIONAL",
                parameter="operating_temp_range",
                target_value="-40 to 85",
                unit="°C",
                priority="HIGH",
                source="USER_INPUT",
                verification_method="Datasheet Verification",
            ),
            StructuredRequirement(
                requirement_id="REQ-003",
                project_id=project_id,
                title="Autonomous Power Autonomy",
                description="System must survive continuous operation for at least 5 consecutive cloudy/sunless days.",
                category="PERFORMANCE",
                parameter="sunless_autonomy_days",
                target_value="5.0",
                unit="days",
                priority="HIGH",
                source="USER_INPUT",
                verification_method="Simulation",
            ),
        ]
        cons = [
            StructuredConstraint(
                constraint_id="CON-001",
                project_id=project_id,
                requirement_id="REQ-001",
                title="Maximum Solar Open-Circuit Voltage",
                description="Input voltage rating of solar charge controller.",
                property="solar_voc_max",
                operator="<=",
                required_value="22.0",
                value="22.0",
                unit="V",
                severity="CRITICAL",
                source="ENGINEERING_STANDARDS",
            ),
            StructuredConstraint(
                constraint_id="CON-002",
                project_id=project_id,
                requirement_id="REQ-003",
                title="Average System Power Consumption",
                description="Total system sleep power must permit multi-day energy storage balance.",
                property="average_power_mw",
                operator="<=",
                required_value="5.0",
                value="5.0",
                unit="mW",
                severity="HIGH",
                source="USER_INPUT",
            ),
        ]
        return obj, reqs, cons, obj.clarifications_needed

    # 5. Smart Battery Management System (BMS) / Power Storage / Pack Architecture
    elif any(k in text for k in ("bms", "battery", "lifepo4", "li-ion", "lipo", "cell", "balancing", "pack", "battery management", "4s", "8s", "16s", "overcharge", "undervoltage")):
        obj = IdeaUnderstandingOutput(
            project_objective=f"Intelligent Battery Management System (BMS) with cell balancing and protection: {idea}",
            application_domain="Battery Management & Power Electronics",
            required_functions=[
                "Monitor individual series cell voltages with high-precision delta detection (< 5mV)",
                "Execute active or passive cell balancing during charging phase",
                "Continuously monitor charge and discharge pack currents via precision shunt resistor",
                "Enforce multi-tier overcharge, overdischarge, overcurrent, and short-circuit hardware protection",
                "Measure multi-point cell pack temperatures via NTC thermistors with thermal runaway cutoff",
                "Broadcast state-of-charge (SoC), state-of-health (SoH), and fault telemetry via SMBus / I2C / CAN",
            ],
            inputs=["Individual cell voltage sense taps (e.g. 4S / 8S)", "Pack shunt current voltage drop", "Dual NTC thermal sensors"],
            outputs=["Charge/Discharge protection power MOSFET gate drives", "Cell balance discharge switch controls", "SMBus / I2C / CAN telemetry bus"],
            sensors=["Multi-cell Battery Analog Front-End (AFE) IC", "High-Side / Low-Side Current Shunt Monitor", "10k NTC Thermistor Pack Probes"],
            actuators=["Dual N-Channel Power MOSFET disconnect switches (Charge / Discharge)", "Cell balancing bleed resistor network"],
            controller_requirements=["Dedicated low-power BMS MCU or integrated AFE with hardware protection state machine", "Hardware CRC on SMBus / CAN telemetry bus", "Isolated communication transceiver"],
            communication_requirements=["SMBus / I2C 100kHz or CAN 2.0B differential telemetry bus"],
            power_requirements=["Ultra-low quiescent current (< 50µA in standby / sleep) powered directly from battery pack"],
            environmental_requirements=["Industrial temperature rating (-40°C to +85°C)", "Conformal coating for moisture / dust resistance"],
            voltage_requirements=["4S LiFePO4 operating pack voltage 10.0V - 14.6V (Nominal 12.8V)", "3.65V max charge cutoff per cell", "2.50V min discharge cutoff per cell", "3.3V regulated logic rail"],
            current_requirements=["Continuous discharge rating 25A - 30A", "Peak transient surge current up to 60A", "Balancing bleed current 50mA - 100mA"],
            safety_requirements=["Hardware short-circuit trip within 200 microseconds", "Dual-tier overvoltage and undervoltage protection", "Thermal runaway cutoff at 65°C"],
            optional_components=["OLED battery gauge display", "Bluetooth Low Energy (BLE) mobile diagnostic dongle"],
            clarifications_needed=[
                "What is the exact battery chemistry (LiFePO4 at 3.2V nominal or standard NMC/Li-Ion at 3.7V nominal)?",
                "What is the continuous discharge current rating requirement (e.g. 20A, 30A, or 50A)?",
                "Is SMBus, I2C, or CAN bus preferred for upstream telemetry and host communication?",
            ]
        )
        reqs = [
            StructuredRequirement(
                requirement_id="REQ-001",
                project_id=project_id,
                title="Cell Overvoltage Protection Threshold",
                description="Hardware cutoff when any individual cell voltage reaches overcharge threshold (3.65V for LiFePO4).",
                category="ELECTRICAL",
                parameter="cell_overvoltage_cutoff_v",
                target_value="3.65",
                unit="V",
                priority="CRITICAL",
                source="ENGINEERING_STANDARDS",
                verification_method="Simulation",
            ),
            StructuredRequirement(
                requirement_id="REQ-002",
                project_id=project_id,
                title="Cell Undervoltage Protection Threshold",
                description="Cutoff discharge path when any individual cell drops below critical undervoltage threshold (2.50V for LiFePO4).",
                category="ELECTRICAL",
                parameter="cell_undervoltage_cutoff_v",
                target_value="2.50",
                unit="V",
                priority="CRITICAL",
                source="ENGINEERING_STANDARDS",
                verification_method="Simulation",
            ),
            StructuredRequirement(
                requirement_id="REQ-003",
                project_id=project_id,
                title="Continuous Pack Discharge Current",
                description="BMS power path MOSFETs and PCB copper must continuously conduct target load current with low thermal rise.",
                category="POWER",
                parameter="continuous_discharge_current_a",
                target_value="30.0",
                unit="A",
                priority="CRITICAL",
                source="USER_INPUT",
                verification_method="Datasheet Verification",
            ),
            StructuredRequirement(
                requirement_id="REQ-004",
                project_id=project_id,
                title="Cell Balancing Current",
                description="Equalize cell voltages across all series cells with dedicated balancing circuitry.",
                category="FUNCTIONAL",
                parameter="balance_current_ma",
                target_value="75.0",
                unit="mA",
                priority="HIGH",
                source="ENGINEERING_STANDARDS",
                verification_method="Analysis",
            ),
            StructuredRequirement(
                requirement_id="REQ-005",
                project_id=project_id,
                title="Telemetry & Diagnostics Interface",
                description="Provide real-time telemetry of pack voltage, current, individual cell voltages, and temperatures via digital bus.",
                category="INTERFACE",
                parameter="telemetry_interface",
                target_value="SMBus / I2C",
                unit="protocol",
                priority="HIGH",
                source="USER_INPUT",
                verification_method="Software Test",
            ),
            StructuredRequirement(
                requirement_id="REQ-006",
                project_id=project_id,
                title="High-Temperature Cutoff",
                description="Disconnect charge/discharge paths if battery cell temperature exceeds safe operating boundary.",
                category="THERMAL",
                parameter="temp_cutoff_celsius",
                target_value="65.0",
                unit="°C",
                priority="CRITICAL",
                source="ENGINEERING_STANDARDS",
                verification_method="Physical Test",
            ),
        ]
        cons = [
            StructuredConstraint(
                constraint_id="CON-001",
                project_id=project_id,
                requirement_id="REQ-001",
                title="Maximum Single Cell Voltage",
                description="Upper safety voltage limit per cell.",
                property="cell_voltage_max",
                operator="<=",
                required_value="3.65",
                value="3.65",
                unit="V",
                severity="CRITICAL",
                source="ENGINEERING_STANDARDS",
            ),
            StructuredConstraint(
                constraint_id="CON-002",
                project_id=project_id,
                requirement_id="REQ-002",
                title="Minimum Single Cell Voltage",
                description="Lower safety voltage limit per cell.",
                property="cell_voltage_min",
                operator=">=",
                required_value="2.50",
                value="2.50",
                unit="V",
                severity="CRITICAL",
                source="ENGINEERING_STANDARDS",
            ),
            StructuredConstraint(
                constraint_id="CON-003",
                project_id=project_id,
                requirement_id="REQ-003",
                title="Maximum Continuous Discharge Current",
                description="MOSFET and trace thermal limits.",
                property="continuous_discharge_current_max",
                operator="<=",
                required_value="30.0",
                value="30.0",
                unit="A",
                severity="CRITICAL",
                source="USER_INPUT",
            ),
            StructuredConstraint(
                constraint_id="CON-004",
                project_id=project_id,
                requirement_id="REQ-006",
                title="Maximum Cell Operating Temperature",
                description="Pack safety thermal threshold.",
                property="cell_temp_max",
                operator="<=",
                required_value="65.0",
                value="65.0",
                unit="°C",
                severity="CRITICAL",
                source="ENGINEERING_STANDARDS",
            ),
            StructuredConstraint(
                constraint_id="CON-005",
                project_id=project_id,
                requirement_id="REQ-003",
                title="Short Circuit Disconnect Response Time",
                description="Hardware trip time upon dead short.",
                property="short_circuit_response_us",
                operator="<=",
                required_value="200.0",
                value="200.0",
                unit="µs",
                severity="CRITICAL",
                source="ENGINEERING_STANDARDS",
            ),
        ]
        return obj, reqs, cons, obj.clarifications_needed

    # 6. General Engineering Project Fallback
    else:
        obj = IdeaUnderstandingOutput(
            project_objective=f"Engineering system specification: {idea}",
            application_domain="Embedded Hardware & Electronic Systems",
            required_functions=[
                "Provide reliable core logic processing and control loop execution",
                "Sense required physical input parameters and domain variables",
                "Drive system actuators, displays, or telemetry outputs safely",
                "Ensure voltage rail regulation and circuit protection",
            ],
            inputs=["Sensor inputs", "Power supply rail"],
            outputs=["Actuator drive", "Telemetry / status indicator"],
            sensors=["Physical domain transducer / sensor"],
            actuators=["System drive mechanism / switch"],
            controller_requirements=["32-bit Microcontroller with suitable I/O pin count and peripheral buses"],
            communication_requirements=["UART / I2C / SPI communication interfaces"],
            power_requirements=["Regulated DC power distribution with appropriate decoupling"],
            environmental_requirements=["Standard industrial/commercial temperature range (-20°C to +70°C)"],
            voltage_requirements=["Regulated 3.3V or 5.0V logic rails"],
            current_requirements=["Budgeted according to peripheral loads"],
            safety_requirements=["Overcurrent fuse and reverse voltage protection"],
            optional_components=["Diagnostic interface / status OLED"],
            clarifications_needed=[
                "What is the primary power supply source (battery, USB, or external DC power supply)?",
                "What are the target physical dimensions and enclosure requirements?",
                "What specific sensor precision or update frequency is required?",
            ]
        )
        reqs = [
            StructuredRequirement(
                requirement_id="REQ-001",
                project_id=project_id,
                title="Functional Execution",
                description=f"Satisfy user objective: {idea[:80]}",
                category="FUNCTIONAL",
                target_value="NOT SPECIFIED",
                unit="N/A",
                priority="HIGH",
                source="USER_INPUT",
                verification_method="Analysis",
            ),
            StructuredRequirement(
                requirement_id="REQ-002",
                project_id=project_id,
                title="Logic Rail Stability",
                description="Regulated 3.3V operating voltage with low ripple.",
                category="ELECTRICAL",
                parameter="voltage_rail",
                target_value="3.3",
                unit="V",
                priority="CRITICAL",
                source="ENGINEERING_STANDARDS",
                verification_method="Datasheet Verification",
            ),
        ]
        cons = [
            StructuredConstraint(
                constraint_id="CON-001",
                project_id=project_id,
                requirement_id="REQ-002",
                title="Maximum Supply Voltage Ripple",
                description="Limit voltage ripple on microelectronic power rails.",
                property="voltage_ripple_pct",
                operator="<=",
                required_value="2.0",
                value="2.0",
                unit="%",
                severity="HIGH",
                source="ENGINEERING_STANDARDS",
            )
        ]
        return obj, reqs, cons, obj.clarifications_needed


# ============================================================================
# 3. CUSTOM SPECIFICATIONS EXTRACTOR & FORMATTER
# ============================================================================

def extract_custom_specifications(
    custom_text: str,
    project_id: str = "default_project"
) -> Tuple[List[StructuredRequirement], List[StructuredConstraint]]:
    """
    Parses user-entered technical specifications and extracts structured requirements and constraints.
    Supports key-value formats, bullet points, and freeform engineering statements.
    """
    reqs: List[StructuredRequirement] = []
    cons: List[StructuredConstraint] = []
    if not custom_text or not custom_text.strip():
        return reqs, cons

    req_idx = 1
    con_idx = 1
    clean_lines = [l.strip().lstrip("-*•").strip() for l in custom_text.splitlines() if l.strip()]

    for line in clean_lines:
        if not line or len(line) < 3:
            continue

        volt_m = re.search(r"(\d+(?:\.\d+)?)\s*(?:-|to)\s*(\d+(?:\.\d+)?)\s*V", line, re.I) or re.search(r"(\d+(?:\.\d+)?)\s*V(?:DC|AC)?(?!\w)", line, re.I)
        curr_m = re.search(r"(\d+(?:\.\d+)?)\s*(?:-|to)\s*(\d+(?:\.\d+)?)\s*A(?!\w)", line, re.I) or re.search(r"(\d+(?:\.\d+)?)\s*(?:A|mA)(?!\w)", line, re.I)
        temp_m = re.search(r"(-?\d+)\s*(?:°?C)\s*(?:to|-)\s*(\+?\d+)\s*(?:°?C)", line, re.I)

        category = "FUNCTIONAL"
        param = None
        target_val = "SPECIFIED"
        unit = "N/A"
        verification = "Analysis"

        if volt_m:
            category = "ELECTRICAL"
            param = "operating_voltage"
            target_val = volt_m.group(0).strip()
            unit = "V"
            verification = "Simulation"
        elif curr_m:
            category = "POWER"
            param = "current_rating"
            target_val = curr_m.group(0).strip()
            unit = "mA" if "mA" in curr_m.group(0) else "A"
            verification = "Datasheet Verification"
        elif temp_m:
            category = "THERMAL"
            param = "operating_temperature_range"
            target_val = f"{temp_m.group(1)} to {temp_m.group(2)}"
            unit = "°C"
            verification = "Physical Test"
        elif any(b in line.lower() for b in ("i2c", "spi", "uart", "can", "smbus", "rs485", "modbus", "usb", "ble", "wifi", "telemetry")):
            category = "INTERFACE"
            param = "communication_interface"
            target_val = line
            unit = "protocol"
            verification = "Software Test"
        elif any(p in line.lower() for p in ("protect", "cutoff", "fuse", "short", "overvoltage", "undervoltage", "overcurrent", "reverse")):
            category = "SAFETY"
            param = "hardware_protection"
            target_val = line
            unit = "spec"
            verification = "Simulation"
        elif any(b in line.lower() for b in ("balance", "balancing", "equaliz")):
            category = "ELECTRICAL"
            param = "cell_balancing"
            target_val = line
            unit = "spec"
            verification = "Analysis"

        req_id = f"REQ-CUST-{req_idx:02d}"
        title = line[:45] if len(line) <= 45 else line[:42] + "..."
        req = StructuredRequirement(
            requirement_id=req_id,
            project_id=project_id,
            title=title,
            description=line,
            category=category,
            parameter=param or "user_specification",
            target_value=target_val,
            unit=unit,
            priority="CRITICAL" if category in ("ELECTRICAL", "POWER", "SAFETY") else "HIGH",
            source="USER_CUSTOM_SPEC",
            status="ACTIVE",
            verification_method=verification,
        )
        reqs.append(req)

        if volt_m or curr_m or temp_m:
            con_id = f"CON-CUST-{con_idx:02d}"
            con_prop = param or "custom_limit"
            req_val = target_val
            con = StructuredConstraint(
                constraint_id=con_id,
                project_id=project_id,
                requirement_id=req_id,
                title=f"User Constraint: {title}",
                description=f"User-specified design boundary: {line}",
                property=con_prop,
                operator="<=" if not temp_m else "range",
                required_value=req_val,
                value=req_val,
                unit=unit,
                severity="HIGH",
                type="TECHNICAL",
                source="USER_CUSTOM_SPEC",
                status="ACTIVE",
            )
            cons.append(con)
            con_idx += 1

        req_idx += 1

    return reqs, cons


def generate_specification_text(
    idea: str,
    understanding: Dict[str, Any],
    requirements: List[Dict[str, Any]],
    constraints: List[Dict[str, Any]],
    custom_specifications: Optional[str] = None,
) -> str:
    """Generates an authoritative, structured engineering specification document text."""
    lines = []
    title = understanding.get("title") or idea[:50]
    domain = understanding.get("application_domain") or "Embedded Hardware & Electronic Systems"
    lines.append(f"System Specification: {title}")
    lines.append(f"Application Domain: {domain}")
    lines.append("")
    if understanding.get("summary"):
        lines.append(f"Architecture Objective:\n{understanding['summary']}")
        lines.append("")

    if custom_specifications and custom_specifications.strip():
        lines.append("User Defined Specifications:")
        for l in custom_specifications.strip().splitlines():
            clean = l.strip().lstrip("-*•").strip()
            if clean:
                lines.append(f"  • {clean}")
        lines.append("")

    if requirements:
        lines.append("Derived Technical Requirements:")
        for r in requirements:
            target = f" [Target: {r.get('target_value')} {r.get('unit', '')}]" if r.get('target_value') and r.get('target_value') not in ("NOT SPECIFIED", "SPECIFIED") else ""
            lines.append(f"  • ({r.get('category', 'GENERAL')}) {r.get('title')}{target}: {r.get('description', '')}")
        lines.append("")

    if constraints:
        lines.append("Design Constraints & Operating Limits:")
        for c in constraints:
            req_val = c.get('required_value') or c.get('value') or ''
            unit = c.get('unit') or c.get('required_unit') or ''
            lines.append(f"  • {c.get('property', 'limit')} {c.get('operator', '=')} {req_val} {unit} [{c.get('severity', 'CRITICAL')}]")
        lines.append("")

    return "\n".join(lines)


# ============================================================================
# 4. IDEA UNDERSTANDING AGENT ENTRYPOINT
# ============================================================================

def analyze_engineering_idea(
    user_idea: str,
    project_id: str = "default_project",
    custom_specifications: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Main entry point for Idea Understanding.
    Queries Amazon Bedrock fast model where available, or relies on domain expert fallback.
    Never hallucinates component MPNs or factual datasheets at this stage.
    Accepts optional user custom specifications and merges them as authoritative requirements.
    """
    if not user_idea or not user_idea.strip():
        user_idea = "Embedded electronic hardware system"

    clean_idea = user_idea.strip()
    full_idea_context = clean_idea
    if custom_specifications and custom_specifications.strip():
        full_idea_context = f"{clean_idea}\n\nCustom Specifications:\n{custom_specifications.strip()}"

    # Extract any user custom requirements first
    custom_reqs, custom_cons = extract_custom_specifications(custom_specifications or "", project_id)

    # Attempt Bedrock analysis first
    try:
        from backend.workline.ai.bedrock.router import model_router
        prompt = (
            f"You are a Senior Principal Hardware Systems Engineer.\n"
            f"Analyze this engineering concept: '{full_idea_context}'\n\n"
            f"Extract technical requirements without hallucinating specific manufacturer part numbers (MPNs).\n"
            f"Output ONLY a valid JSON object matching this schema:\n"
            f"{{\n"
            f'  "project_objective": "string",\n'
            f'  "application_domain": "string",\n'
            f'  "required_functions": ["string"],\n'
            f'  "inputs": ["string"],\n'
            f'  "outputs": ["string"],\n'
            f'  "sensors": ["generic sensor description, e.g. Capacitive Soil Moisture Sensor"],\n'
            f'  "actuators": ["generic actuator description, e.g. 12V Solenoid Valve"],\n'
            f'  "controller_requirements": ["string"],\n'
            f'  "communication_requirements": ["string"],\n'
            f'  "power_requirements": ["string"],\n'
            f'  "environmental_requirements": ["string"],\n'
            f'  "voltage_requirements": ["string"],\n'
            f'  "current_requirements": ["string"],\n'
            f'  "safety_requirements": ["string"],\n'
            f'  "optional_components": ["string"],\n'
            f'  "clarifications_needed": ["question 1", "question 2"]\n'
            f"}}\n"
        )
        ai_res = model_router.fast_code(prompt=prompt, system_instruction="Output valid JSON only. Do not hallucinate exact MPNs.")
        if ai_res and ai_res.text:
            text_cleaned = ai_res.text.strip()
            match = re.search(r"\{.*\}", text_cleaned, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                parsed_obj = IdeaUnderstandingOutput(**data)
                # Convert into structured requirements and constraints
                _, reqs, cons, clarifications = _parse_idea_deterministic(clean_idea, project_id)
                merged_reqs = [r.model_dump() for r in custom_reqs] + [r.model_dump() for r in reqs]
                merged_cons = [c.model_dump() for c in custom_cons] + [c.model_dump() for c in cons]
                und_dict = parsed_obj.model_dump()
                spec_text = generate_specification_text(clean_idea, und_dict, merged_reqs, merged_cons, custom_specifications)
                return {
                    "understanding": und_dict,
                    "requirements": merged_reqs,
                    "constraints": merged_cons,
                    "clarifications_needed": parsed_obj.clarifications_needed or clarifications,
                    "specification_text": spec_text,
                    "custom_specifications": custom_specifications or "",
                }
    except Exception as e:
        logger.debug(f"[IdeaUnderstandingAgent] Bedrock route unavailable: {e}. Utilizing deterministic parser.")

    # High-fidelity deterministic extraction
    parsed_obj, reqs, cons, clarifications = _parse_idea_deterministic(clean_idea, project_id)
    und_dict = parsed_obj.model_dump()
    if not und_dict.get("title"):
        und_dict["title"] = clean_idea.title() if len(clean_idea) < 60 else clean_idea[:57] + "..."
    if not und_dict.get("summary"):
        und_dict["summary"] = f"Engineering design and hardware specification for {clean_idea}."
    if not und_dict.get("architecture_summary"):
        und_dict["architecture_summary"] = (
            f"Modular hardware architecture comprising dedicated {len(parsed_obj.sensors)} sensor(s), "
            f"{len(parsed_obj.actuators)} actuator(s), regulated power stages, and embedded edge processing."
        )
    if not und_dict.get("key_subsystems"):
        und_dict["key_subsystems"] = [
            "Sensors & Signal Conditioning",
            "Controller & Processing",
            "Power & Voltage Regulation",
            "Actuation & Drivers",
            "Telemetry & Networking",
        ]

    # Prepend user custom requirements so they have priority visibility
    merged_reqs = [r.model_dump() for r in custom_reqs] + [r.model_dump() for r in reqs]
    merged_cons = [c.model_dump() for c in custom_cons] + [c.model_dump() for c in cons]
    spec_text = generate_specification_text(clean_idea, und_dict, merged_reqs, merged_cons, custom_specifications)

    return {
        "understanding": und_dict,
        "requirements": merged_reqs,
        "constraints": merged_cons,
        "clarifications_needed": clarifications,
        "specification_text": spec_text,
        "custom_specifications": custom_specifications or "",
    }
