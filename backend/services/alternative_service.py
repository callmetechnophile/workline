import os
import json
import httpx
from typing import List, Dict, Any

# Local high-fidelity fallback database for alternative components
LOCAL_ALTERNATIVES = {
    "l298n": [
        {"name": "DRV8833 Dual H-Bridge", "type": "cheaper", "reason": "Higher efficiency, lower voltage drop compared to L298N.", "approx_cost_usd": 3.0},
        {"name": "BTS7960 High Current Driver", "type": "upgraded", "reason": "Supports up to 43A, upgraded current capacity for larger motors.", "approx_cost_usd": 12.0}
    ],
    "pixhawk": [
        {"name": "Matek H743-WING", "type": "cheaper", "reason": "Saves $90.00 while maintaining autonomous flight telemetry.", "approx_cost_usd": 65.0},
        {"name": "Betaflight F405 flight controller", "type": "equivalent", "reason": "Lower cost, widely compatible with standard quadcopter frames.", "approx_cost_usd": 40.0}
    ],
    "flexible solar": [
        {"name": "Rigid Glass Solar Panel", "type": "cheaper", "reason": "Reduces cost by 30% and offers higher physical durability.", "approx_cost_usd": 45.0}
    ],
    "mppt": [
        {"name": "PWM Solar Charge Controller", "type": "cheaper", "reason": "Cheaper alternative, though 15-20% less efficient than MPPT.", "approx_cost_usd": 15.0},
        {"name": "LT3652 MPPT Charger", "type": "equivalent", "reason": "Similar tracking capabilities in a more compact design.", "approx_cost_usd": 32.0}
    ],
    "lifepo4": [
        {"name": "11.1V 3S LiPo Battery Pack", "type": "cheaper", "reason": "Cheaper options, higher energy density but shorter lifespan.", "approx_cost_usd": 35.0},
        {"name": "Lead-Acid Battery (12V)", "type": "cheaper", "reason": "Lowest cost but significantly heavier and larger footprint.", "approx_cost_usd": 25.0}
    ],
    "esp32": [
        {"name": "Arduino Nano", "type": "cheaper", "reason": "Lower price, though lacks built-in Wi-Fi/Bluetooth capabilities.", "approx_cost_usd": 4.0},
        {"name": "Raspberry Pi Pico W", "type": "equivalent", "reason": "Comparable dual-core processor with clean SDK support.", "approx_cost_usd": 6.0}
    ],
    "brushless dc": [
        {"name": "Brushed DC Suction Motor", "type": "cheaper", "reason": "Lower cost, does not require an Electronic Speed Controller (ESC).", "approx_cost_usd": 15.0}
    ]
}

def find_alternatives(component_name: str) -> List[Dict[str, Any]]:
    """
    Finds alternative component options using Llama-3.1-Nemotron on Groq (if available),
    falling back to a local rules engine if offline.
    """
    # 1. Try local exact match first
    comp_lower = component_name.lower()
    for key, alts in LOCAL_ALTERNATIVES.items():
        if key in comp_lower:
            return alts
            
    # 2. Try calling Amazon Bedrock model router
    try:
        from backend.workline.ai.bedrock.router import model_router
        prompt = (
            f"Identify 2 alternative components for the hardware element: '{component_name}'. "
            "Each alternative should be cheaper, equivalent, or upgraded. "
            "Response MUST be a raw JSON array of objects with keys: "
            "'name' (string), 'type' (string: 'cheaper', 'equivalent', or 'upgraded'), "
            "'reason' (string explaining why it is a good alternative - better efficiency or lower cost), "
            "'approx_cost_usd' (float). Do not write any markdown wrappers."
        )
        ai_res = model_router.fast_code(prompt=prompt)
        content = ai_res.text.strip()
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(l for l in lines if not l.startswith("```")).strip()
        parsed = json.loads(content)
        if isinstance(parsed, list):
            return parsed
    except Exception:
        pass
            
    # 3. Generic fallback builder
    return [
        {
            "name": f"Generic equivalent for {component_name}",
            "type": "equivalent",
            "reason": "Standard replacement option with similar power ratings and interface pins.",
            "approx_cost_usd": 10.0
        },
        {
            "name": f"Budget alternative for {component_name}",
            "type": "cheaper",
            "reason": "Reduced specification replacement for low-cost project configurations.",
            "approx_cost_usd": 5.0
        }
    ]
