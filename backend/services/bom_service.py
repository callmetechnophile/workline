import os
import csv
import json
import uuid
from typing import List, Dict, Any

EXPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exports")
os.makedirs(EXPORT_DIR, exist_ok=True)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
VENDOR_MATRIX_FILE = os.path.join(DATA_DIR, "bom_vendor_matrix.json")

def load_vendor_matrix() -> List[Dict[str, Any]]:
    if os.path.exists(VENDOR_MATRIX_FILE):
        with open(VENDOR_MATRIX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def search_component_sources(component_name: str, cost_usd: float = 10.0) -> List[Dict[str, Any]]:
    """
    Simulates searching multiple platforms to match the exact product
    and returns their raw prices, locations, and stock information.
    """
    vendors = load_vendor_matrix()
    base_inr = int(cost_usd * 83) if cost_usd > 0 else 500
    
    sources = []
    # Seed variations based on component name to keep it deterministic
    seed = sum(ord(c) for c in component_name)
    
    for idx, v in enumerate(vendors):
        # Vary price slightly per vendor
        var_pct = ((seed + idx) % 30 - 15) / 100.0  # -15% to +15%
        price = int(base_inr * (1.0 + var_pct))
        if price < 10:
            price = 10
            
        stock_status = "In Stock" if (seed + idx + v["distance_km"]) % 7 != 0 else "Low Stock"
        
        # Product URL
        platform_clean = v["platform"].lower().split(" ")[0].replace(".", "")
        url = f"https://www.{platform_clean}.in/search?q={component_name.replace(' ', '+')}"
        if "digikey" in platform_clean:
            url = f"https://www.digikey.in/en/products?keywords={component_name.replace(' ', '+')}"
        elif "element14" in platform_clean:
            url = f"https://in.element14.com/search?q={component_name.replace(' ', '+')}"
            
        sources.append({
            "component": component_name,
            "vendor": v["platform"],
            "location": v["location"],
            "distance_km": v["distance_km"],
            "base_price": price,
            "stock": stock_status,
            "url": url
        })
        
    return sources

def calculate_transport_cost(vendor: str, component_cost: int, mode: str = "normal") -> int:
    """
    Calculates transport cost based on vendor thresholds and delivery modes (express/normal).
    """
    v = vendor.lower()
    
    if "mouser" in v:
        if component_cost >= 3300:
            return 0
        return 200 # flat rate if under threshold
        
    elif "element14" in v:
        if mode == "express":
            return 200 # average of 150-250
        return 90 # average of 80-100
        
    elif "robu" in v:
        if mode == "express":
            return 99
        if component_cost >= 999:
            return 0
        return 49
        
    elif "probots" in v:
        if mode == "express":
            return 150
        return 80
        
    elif "tomson" in v:
        if mode == "express":
            return 200 # 150-250
        return 100 # 80-120
        
    elif "digikey" in v:
        if component_cost >= 4400:
            return 0
        return 1200 # international express
        
    elif "millennium" in v:
        if mode == "express":
            return 500 # custom quote
        return 300
        
    elif "campus" in v:
        if mode == "express":
            return 225 # 200-250
        return 115 # 100-130
        
    elif "pantronics" in v:
        if mode == "express":
            return 175 # 150-200
        return 90 # 80-100
        
    elif "electronic spices" in v:
        if mode == "express":
            return 300 # 250-350
        return 135 # 120-150
        
    return 150 # fallback

def calculate_landed_cost(component: Dict[str, Any], mode: str = "normal") -> Dict[str, Any]:
    """
    Landed Cost = Base Price + Transport Cost
    """
    base_price = component.get("base_price", 0)
    vendor = component.get("vendor", "")
    transport_cost = calculate_transport_cost(vendor, base_price, mode)
    
    return {
        "component": component.get("component", ""),
        "vendor": vendor,
        "location": component.get("location", ""),
        "base_price": base_price,
        "transport_cost": transport_cost,
        "distance_km": component.get("distance_km", 0),
        "landed_cost": base_price + transport_cost,
        "stock": component.get("stock", "In Stock"),
        "url": component.get("url", "")
    }

def find_alternative_components(component_name: str) -> List[Dict[str, Any]]:
    """
    Fetches raw cheaper/equivalent alternatives and ranks them by landed cost.
    """
    from backend.services.alternative_service import find_alternatives
    alts = find_alternatives(component_name)
    alt_ranked = []
    
    for alt in alts:
        alt_cost = alt.get("approx_cost_usd", 5.0)
        ranked = rank_bom_components(alt["name"], alt_cost)
        if ranked:
            best = ranked[0]
            alt_ranked.append({
                "alternative": alt["name"],
                "vendor": best["vendor"],
                "base_cost": best["base_price"],
                "shipping_cost": best["transport_cost"],
                "final_cost": best["landed_cost"],
                "reason": alt.get("reason", "Better efficiency / lower cost")
            })
            
    # Rank by landed cost ascending
    alt_ranked.sort(key=lambda x: x["final_cost"])
    return alt_ranked

def rank_bom_components(component_name: str, cost_usd: float = 10.0, mode: str = "normal") -> List[Dict[str, Any]]:
    """
    Scoring Formula:
    score = (base_price * 0.5) + (transport_cost * 0.25) + (distance_factor * 0.15) + (stock_factor * 0.10)
    Lower score = better.
    """
    sources = search_component_sources(component_name, cost_usd)
    ranked = []
    
    for s in sources:
        landed = calculate_landed_cost(s, mode)
        
        base = landed["base_price"]
        trans = landed["transport_cost"]
        dist = landed["distance_km"]
        
        stock_val = landed["stock"]
        if stock_val == "In Stock":
            stock_factor = 0
        elif stock_val == "Low Stock":
            stock_factor = 200
        else:
            stock_factor = 5000
            
        score = (base * 0.5) + (trans * 0.25) + (dist * 0.15) + (stock_factor * 0.10)
        landed["score"] = score
        ranked.append(landed)
        
    ranked.sort(key=lambda x: x["score"])
    return ranked

def generate_optimized_bom(components: List[Dict[str, Any]], mode: str = "normal") -> Dict[str, Any]:
    """
    Generates the core optimized BOM, mapping each item to its optimal scored vendor,
    and returning category subtotals and grand totals in INR.
    """
    optimized_items = []
    
    electronics_total = 0
    mechanical_total = 0
    shipping_total = 0
    
    for comp in components:
        name = comp.get("name", "")
        cost_usd = float(comp.get("cost", 0.0))
        
        ranked = rank_bom_components(name, cost_usd, mode)
        best = ranked[0]
        
        # Categorize
        cat = comp.get("category", "").lower()
        nm = name.lower()
        if any(k in cat for k in ["power", "energy", "solar", "battery", "esc", "charger", "supply", "voltage"]) or any(k in nm for k in ["battery", "solar", "power supply", "charger", "esc"]):
            category_group = "Power"
        elif any(k in cat for k in ["electronics", "navigation", "sensor", "controller", "board", "flight", "gps", "receiver", "mcu", "cpu", "processor", "led", "display", "screen", "wire", "module", "communication", "actuator", "indicator"]) or any(k in nm for k in ["esp32", "arduino", "pico", "sensor", "led", "wire", "gps", "display", "screen", "transceiver", "mcu", "controller"]):
            category_group = "Electronics"
        else:
            category_group = "Mechanical"
            
        base_cost = best["base_price"]
        shipping_cost = best["transport_cost"]
        final_cost = best["landed_cost"]
        
        if category_group == "Mechanical":
            mechanical_total += base_cost
        else:
            electronics_total += base_cost
            
        shipping_total += shipping_cost
        
        # Get alternatives
        alts = find_alternative_components(name)
        
        # ETA based on distance
        dist = best["distance_km"]
        if dist == 0:
            eta = "2 Days"
        elif dist <= 1000:
            eta = "3-4 Days"
        else:
            eta = "7-10 Days"
            
        import re
        mpn_match = re.search(r'\b([A-Z0-9]{3,}[A-Z0-9\-\/]{2,})\b', name)
        extracted_mpn = mpn_match.group(1) if mpn_match else name.split()[0]

        optimized_items.append({
            "name": name,
            "cost": float(final_cost) / 83.0,
            "notes": f"Landed at {best['vendor']} (Distance: {dist} km, ETA: {eta})",
            "component": name,
            "category": comp.get("category", ""),
            "selected_vendor": best["vendor"],
            "supplier": best["vendor"],
            "vendor_location": best["location"],
            "base_cost": base_cost,
            "unit_price": base_cost,
            "unitPrice": base_cost,
            "shipping_cost": shipping_cost,
            "distance": f"{dist} km",
            "final_cost": final_cost,
            "stock": best["stock"],
            "eta": eta,
            "alternatives": alts,
            "url": best["url"],
            "ref": f"U{len(optimized_items) + 1}",
            "reference_designator": f"U{len(optimized_items) + 1}",
            "part_number": extracted_mpn,
            "ordering_code": extracted_mpn,
            "mpn": extracted_mpn,
            "qty": 1,
            "status": "PASS",
        })
        
    grand_total = electronics_total + mechanical_total + shipping_total
    
    return {
        "bom_items": optimized_items,
        "totals": {
            "electronics_total": electronics_total,
            "mechanical_total": mechanical_total,
            "shipping_total": shipping_total,
            "grand_total": grand_total
        }
    }

def export_bom(components: List[Dict[str, Any]], cost_summary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Exports the upgraded optimized BOM including vendor locations, shipping,
    distance, landed costs, and alternatives.
    """
    file_id = str(uuid.uuid4())[:8]
    
    bom_items = components
    totals = cost_summary.get("totals", cost_summary) if isinstance(cost_summary, dict) else {}
    
    # --- Generate CSV ---
    csv_filename = f"{file_id}_bom.csv"
    csv_filepath = os.path.join(EXPORT_DIR, csv_filename)
    with open(csv_filepath, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Component", "Vendor", "Vendor Location", "Distance", "Base Cost", "Shipping Cost", "Final Cost", "Stock", "Alternatives"])
        for item in bom_items:
            alt_names = ", ".join([a["alternative"] for a in item.get("alternatives", [])]) or "None"
            writer.writerow([
                item["component"], item["selected_vendor"], item["vendor_location"],
                item["distance"], f"INR {item['base_cost']}", f"INR {item['shipping_cost']}",
                f"INR {item['final_cost']}", item["stock"], alt_names
            ])
        writer.writerow([])
        writer.writerow(["Electronics Total", f"INR {totals.get('electronics_total', 0)}"])
        writer.writerow(["Mechanical Total", f"INR {totals.get('mechanical_total', 0)}"])
        writer.writerow(["Shipping Total", f"INR {totals.get('shipping_total', 0)}"])
        writer.writerow(["Grand Total", f"INR {totals.get('grand_total', 0)}"])

    # --- Generate JSON ---
    json_filename = f"{file_id}_bom.json"
    json_filepath = os.path.join(EXPORT_DIR, json_filename)
    json_payload = {
        "bom_items": bom_items,
        "totals": totals
    }
    with open(json_filepath, mode='w', encoding='utf-8') as f:
        json.dump(json_payload, f, indent=2)

    # --- Generate Markdown ---
    md_filename = f"{file_id}_bom.md"
    md_filepath = os.path.join(EXPORT_DIR, md_filename)
    with open(md_filepath, mode='w', encoding='utf-8') as f:
        f.write(f"# Optimized Bill of Materials (BOM)\n\n")
        f.write(f"| Component | Vendor | Location | Distance | Base Cost | Shipping | Final Cost | Stock | Alternatives |\n")
        f.write(f"| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for item in bom_items:
            alt_names = ", ".join([a["alternative"] for a in item.get("alternatives", [])]) or "None"
            f.write(f"| {item['component']} | {item['selected_vendor']} | {item['vendor_location']} | {item['distance']} | INR {item['base_cost']} | INR {item['shipping_cost']} | **INR {item['final_cost']}** | {item['stock']} | {alt_names} |\n")
            
        f.write(f"\n## Logistics & Cost Summary\n\n")
        f.write(f"* **Electronics/Power Base Subtotal**: INR {totals.get('electronics_total', 0)}\n")
        f.write(f"* **Mechanical Base Subtotal**: INR {totals.get('mechanical_total', 0)}\n")
        f.write(f"* **Total Shipping/Transport Cost**: INR {totals.get('shipping_total', 0)}\n")
        f.write(f"\n**Grand Landed Total: INR {totals.get('grand_total', 0)}**\n")

    return {
        "csv": f"/api/exports/{csv_filename}",
        "json": f"/api/exports/{json_filename}",
        "markdown": f"/api/exports/{md_filename}"
    }
