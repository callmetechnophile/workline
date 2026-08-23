import os
import json
import httpx
from typing import Dict, Any, List

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def ask_connection_assistant(message: str, context: Dict[str, Any]) -> str:
    """
    Acts as an engineering connection advisor. Evaluates electrical connections,
    pins, voltage, and protocol compatibilities using Amazon Bedrock.
    """
    msg_lower = message.lower()
    
    # 1. Route through centralized Amazon Bedrock Model Router
    try:
        from backend.workline.ai.bedrock.router import model_router
        bom_summary = ", ".join([c.get("component") or c.get("name", "") for c in context.get("bom", [])])
        wiring_summary = json.dumps(context.get("wiring", []), indent=2)
        power_summary = json.dumps(context.get("power", {}).get("summary", {}), indent=2)

        system_prompt = f"""You are an engineering connection assistant.
Focus ONLY on:
- electrical connections
- protocol issues (I2C, SPI, UART, PWM, CAN, GPIO)
- pin compatibility and thresholds
- datasheet interpretation
- power issues and power budget analysis
- connection debugging

You have access to the active project context:
- BOM: {bom_summary}
- Wiring Connections: {wiring_summary}
- Power Budget Summary: {power_summary}

Rules:
1. Do NOT answer unrelated questions.
2. Keep replies concise, technical, and blueprint-focused.
3. Reference pin maps and voltage domains from the context.
"""
        ai_res = model_router.reasoning(prompt=message, system_instruction=system_prompt)
        if ai_res and ai_res.text:
            return ai_res.text
    except Exception:
        pass
            
    # --- Local Fallback Rules for Offline Sandbox Stability ---
    components = context.get("bom", [])
    comp_names = [c.get("component") or c.get("name", "").lower() for c in components]
    
    if "mpu" in msg_lower or "sensor" in msg_lower or "flex" in msg_lower:
        return (
            "⚠️ [Connection Assistant]: MPU6050 / Flex sensors require analog or I2C serial lines. "
            "Verify that your sensor SDA/SCL lines are mapped to ESP32 GPIO 21 (SDA) and GPIO 22 (SCL). "
            "Flex Sensors should be connected to Analog ADC pins (GPIO 32, 33, 34, 35, 36) with 10k ohm pull-down resistors. "
            "Caution: Flex sensors operate at 3.3V logic. Connecting directly to a 5V supply will overload the input gates."
        )
    elif "pwm" in msg_lower or "servo" in msg_lower or "motor" in msg_lower:
        return (
            "⚙️ [Connection Assistant]: Servos (SG90 / MG996R) draw high transient currents. "
            "In your active configuration, connect them to PCA9685 channels 0 to 5. "
            "Ensure the orange PWM wire goes to the signal pin, red to the center V+ pin, and brown to GND. "
            "Do NOT power servos directly from the ESP32 5V/3.3V logic pins; use the 7.4V battery pack terminal on the PCA9685 board."
        )
    elif "voltage" in msg_lower or "power" in msg_lower or "current" in msg_lower:
        power_w = context.get("power", {}).get("summary", {}).get("total_power_load_w", 0.0)
        runtime = context.get("power", {}).get("summary", {}).get("estimated_runtime_hours", 0.0)
        return (
            f"⚡ [Connection Assistant]: Power Budget Summary: Total system load is {power_w} Watts. "
            f"Estimated battery runtime is {runtime} hours. "
            "Verify that common ground (GND) is connected across all boards (ESP32, PCA9685, battery) to prevent logic glitches. "
            "Ensure voltage level shifters are connected between 3.3V logic (ESP32) and 5.0V logic (PCA9685/Servos) buses."
        )
        
    # Default fallback summarizing the loaded context
    bom_list = ", ".join([c.get("component") or c.get("name", "") for c in components])
    return (
        f"📝 [Connection Assistant]: Project Context: {bom_list or 'No components extracted'}.\n"
        "Regarding your query: Focus on pin wiring safety. Ensure I2C lines have pull-up resistors, "
        "voltage levels match logic thresholds, and motors are isolated from controller logic rails."
    )
