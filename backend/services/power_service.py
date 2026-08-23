import re
from typing import List, Dict, Any, Optional

# Comprehensive semiconductor & passive power reference mapping
POWER_DATABASE = {
    "hub controller": {"voltage": 3.3, "current": 250, "peak_current": 450, "standby": 15.0},
    "usb controller": {"voltage": 3.3, "current": 250, "peak_current": 450, "standby": 15.0},
    "usb5734": {"voltage": 3.3, "current": 280, "peak_current": 500, "standby": 20.0},
    "power delivery": {"voltage": 5.0, "current": 40, "peak_current": 100, "standby": 5.0},
    "tps65987": {"voltage": 5.0, "current": 45, "peak_current": 120, "standby": 4.0},
    "esd": {"voltage": 5.0, "current": 0.001, "peak_current": 0.01, "standby": 0.001},
    "oscillator": {"voltage": 3.3, "current": 15, "peak_current": 25, "standby": 2.0},
    "crystal": {"voltage": 3.3, "current": 2, "peak_current": 5, "standby": 0.1},
    "regulator": {"voltage": 5.0, "current": 5, "peak_current": 15, "standby": 1.0},
    "buck": {"voltage": 5.0, "current": 10, "peak_current": 25, "standby": 1.5},
    "ldo": {"voltage": 3.3, "current": 2, "peak_current": 5, "standby": 0.5},
    "esp32": {"voltage": 3.3, "current": 80, "peak_current": 240, "standby": 0.015},
    "mcu": {"voltage": 3.3, "current": 40, "peak_current": 90, "standby": 1.0},
    "microcontroller": {"voltage": 3.3, "current": 50, "peak_current": 100, "standby": 1.0},
    "pca9685": {"voltage": 5.0, "current": 10, "peak_current": 15, "standby": 0.1},
    "servo": {"voltage": 5.0, "current": 400, "peak_current": 1800, "standby": 10.0},
    "motor": {"voltage": 12.0, "current": 1500, "peak_current": 4500, "standby": 0.0},
    "sensor": {"voltage": 3.3, "current": 8, "peak_current": 20, "standby": 0.5},
    "display": {"voltage": 3.3, "current": 60, "peak_current": 120, "standby": 5.0},
    "oled": {"voltage": 3.3, "current": 45, "peak_current": 80, "standby": 2.0},
    "connector": {"voltage": 5.0, "current": 0, "peak_current": 0, "standby": 0},
    "usb-c": {"voltage": 5.0, "current": 0, "peak_current": 0, "standby": 0},
}


def get_component_power_specs(name: str, category: Optional[str] = None) -> Dict[str, float]:
    """Infers real voltage, current, and standby power for any given electronic component."""
    text = f"{name} {category or ''}".lower()
    
    # Match explicit voltage keywords if in name (e.g. "3.3V LDO", "12V Buck", "5V Rail")
    explicit_v = None
    v_match = re.search(r"(\d+(?:\.\d+)?)\s*v(?:olts?)?", text)
    if v_match:
        try:
            val = float(v_match.group(1))
            if 0.8 <= val <= 48.0:
                explicit_v = val
        except ValueError:
            pass

    for key, specs in POWER_DATABASE.items():
        if key in text:
            res = dict(specs)
            if explicit_v is not None:
                res["voltage"] = explicit_v
            return res
            
    # Default active semiconductor rail specs (3.3V or 5.0V depending on class)
    default_v = explicit_v or (3.3 if "controller" in text or "logic" in text or "sensor" in text else 5.0)
    return {
        "voltage": default_v,
        "current": 35.0,
        "peak_current": 80.0,
        "standby": 1.0,
    }


def calculate_power_budget(components: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Multi-Rail Voltage Domain Solver:
    - Never sums operating voltages (e.g. 5V + 3.3V != 8.3V).
    - Groups components into separate physical voltage rails.
    - Computes P = V * I per rail.
    - Computes total system power accounting for converter efficiencies (88%).
    - Determines source current, required converters, and safety headroom.
    """
    rails_map: Dict[float, Dict[str, Any]] = {}
    power_items = []
    
    total_active_load_w = 0.0
    total_peak_load_w = 0.0
    total_standby_load_w = 0.0

    for comp in components:
        name = comp.get("component") or comp.get("name", "Component")
        category = comp.get("category", "General")
        specs = get_component_power_specs(name, category)
        
        voltage = float(specs["voltage"])
        nominal_ma = float(specs["current"])
        peak_ma = float(specs["peak_current"])
        standby_ma = float(specs["standby"])
        
        nominal_a = nominal_ma / 1000.0
        peak_a = peak_ma / 1000.0
        
        power_w = round(voltage * nominal_a, 4)
        peak_power_w = round(voltage * peak_a, 4)
        
        total_active_load_w += power_w
        total_peak_load_w += peak_power_w
        total_standby_load_w += round(voltage * (standby_ma / 1000.0), 4)
        
        # Initialize voltage rail domain if not existing
        if voltage not in rails_map:
            rails_map[voltage] = {
                "rail": f"{voltage:.1f}V Domain",
                "voltage": voltage,
                "current_ma": 0.0,
                "current_a": 0.0,
                "peak_current_a": 0.0,
                "power_w": 0.0,
                "components": [],
            }
            
        rails_map[voltage]["current_ma"] += nominal_ma
        rails_map[voltage]["current_a"] = round(rails_map[voltage]["current_ma"] / 1000.0, 3)
        rails_map[voltage]["peak_current_a"] += peak_a
        rails_map[voltage]["power_w"] = round(rails_map[voltage]["power_w"] + power_w, 3)
        rails_map[voltage]["components"].append(name)
        
        power_items.append({
            "component": name,
            "category": category,
            "voltage": voltage,
            "nominal_current_ma": nominal_ma,
            "peak_current_ma": peak_ma,
            "power_w": power_w,
        })

    # Sort voltage domains descending (e.g. 12V -> 5V -> 3.3V -> 1.8V)
    sorted_voltages = sorted(rails_map.keys(), reverse=True)
    voltage_domains = [rails_map[v] for v in sorted_voltages]

    # Input Voltage & Converter Sizing
    # Input voltage must be at least the highest internal rail (or standard 5V/12V input with step-down regulators)
    primary_rail_v = sorted_voltages[0] if sorted_voltages else 5.0
    recommended_input_v = max(5.0, primary_rail_v)
    
    # DC-DC Step-down efficiency ~88%
    converter_efficiency = 0.88
    total_system_power_w = round(total_active_load_w / converter_efficiency, 2) if total_active_load_w > 0 else 0.5
    peak_system_power_w = round(total_peak_load_w / converter_efficiency, 2)
    required_source_current_a = round(total_system_power_w / recommended_input_v, 2)

    # Converter requirements list
    converter_requirements = []
    for v in sorted_voltages:
        if v < recommended_input_v:
            c_type = "LDO Regulator" if v <= 3.3 and rails_map[v]["current_a"] < 0.5 else "Buck Switching Regulator"
            converter_requirements.append({
                "type": c_type,
                "input_voltage": recommended_input_v,
                "output_voltage": v,
                "max_load_current_a": round(rails_map[v]["current_a"] * 1.5, 2),  # 50% design margin
                "efficiency_pct": 92 if "Buck" in c_type else 75,
                "description": f"Steps down {recommended_input_v}V input to clean {v}V for {len(rails_map[v]['components'])} components."
            })

    # Safety margin calculation
    safety_margin_pct = 25.0  # standard 25% thermal/current headroom
    recommended_supply_power_w = round(total_system_power_w * (1.0 + safety_margin_pct / 100.0), 2)

    # Warnings & Validation
    warnings = []
    if len(voltage_domains) > 1:
        rail_labels = ", ".join([f"{v:.1f}V" for v in sorted_voltages])
        # Informational verification of multi-rail architecture
        if any(v == 3.3 for v in sorted_voltages) and any(v >= 5.0 for v in sorted_voltages):
            warnings.append("Multi-rail architecture active: Verify 3.3V logic level translation if high-speed GPIO interconnects 5V domain.")

    status = "PASS"
    if total_system_power_w > 100.0:
        status = "WARNING"
        warnings.append(f"High power load ({total_system_power_w}W): Active forced cooling / heatsinking recommended.")

    return {
        "status": status,
        "power_items": power_items,
        "voltage_domains": voltage_domains,
        "voltage_domains_count": len(voltage_domains),
        "converter_requirements": converter_requirements,
        "summary": {
            "total_power_load_w": round(total_active_load_w, 3),
            "total_system_power_w": total_system_power_w,
            "peak_power_load_w": peak_system_power_w,
            "required_input_v": recommended_input_v,
            "required_source_current_a": required_source_current_a,
            "recommended_supply_power_w": recommended_supply_power_w,
            "safety_margin_pct": safety_margin_pct,
            "converter_efficiency_pct": round(converter_efficiency * 100),
        },
        "warnings": warnings,
    }
