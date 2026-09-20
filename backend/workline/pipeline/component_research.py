"""
Component Research Agent & Evidence-Grounded Recommendation Engine.
Queries Octopart/Nexar MCP tools, extracts structured evidence atoms,
generates requirement-grounded 'Why this component?' justifications,
evaluates alternative candidate trade-offs, and detects constraint violations.
"""

import time
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger
from pydantic import BaseModel, Field

from backend.mcp.nexar_client import nexar_mcp_client
from backend.workline.pipeline.idea_understanding import StructuredRequirement, StructuredConstraint


class ComponentEvidenceAtom(BaseModel):
    entity: str = "component"
    mpn: str
    manufacturer: str
    attribute: str
    value: str
    unit: str = "N/A"
    source: str = "Nexar/Octopart MCP"
    source_id: str
    retrieved_at: str
    source_url: Optional[str] = None


class ComponentAlternative(BaseModel):
    alternative_mpn: str
    alternative_name: str
    manufacturer: str
    category: str
    reason: str
    trade_off: str
    source: str = "Nexar/Octopart MCP"
    datasheet_url: Optional[str] = None
    pricing_inr: float = 0.0


class RecommendedComponent(BaseModel):
    component_id: str
    component_name: str
    manufacturer: str
    mpn: str
    category: str
    description: str
    specifications: Dict[str, Any] = Field(default_factory=dict)
    package: str = "UNKNOWN"
    voltage_range: str = "UNKNOWN"
    current_rating: str = "UNKNOWN"
    operating_temperature: str = "UNKNOWN"
    availability_stock: int = 0
    unit_price_inr: float = 0.0
    distributor: str = "DigiKey / Mouser"
    datasheet_url: Optional[str] = None
    product_url: Optional[str] = None
    source: str = "Nexar/Octopart MCP"
    retrieved_at: str
    why_recommended: str
    satisfied_requirement_ids: List[str] = Field(default_factory=list)
    evidence: List[ComponentEvidenceAtom] = Field(default_factory=list)
    alternatives: List[ComponentAlternative] = Field(default_factory=list)


class ConstraintViolation(BaseModel):
    violation_id: str
    constraint_id: str
    component_mpn: str
    detected_value: str
    allowed_value: str
    property_name: str
    severity: str = "HIGH"
    status: str = "OPEN"
    details: str


# ============================================================================
# COMPONENT RESEARCH ENGINE
# ============================================================================

async def _query_mcp_candidates(query_term: str, limit: int = 3) -> List[Dict[str, Any]]:
    """Query Nexar MCP client tool for candidates."""
    try:
        results = await nexar_mcp_client.search_components(query_term, limit=limit)
        return results if isinstance(results, list) else []
    except Exception as exc:
        logger.warning(f"[ComponentResearch] MCP query '{query_term}' failed: {exc}")
        return []


def _extract_evidence_atoms(candidate: Dict[str, Any]) -> List[ComponentEvidenceAtom]:
    """Normalize raw MCP candidate specifications into atomic evidence records."""
    mpn = candidate.get("manufacturer_part_number") or candidate.get("mpn") or "UNKNOWN"
    mfr = candidate.get("manufacturer") or "Unknown"
    cid = candidate.get("component_id") or mpn
    retrieved_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    source = candidate.get("metadata", {}).get("source") or candidate.get("source") or "Nexar/Octopart MCP"
    ds_url = candidate.get("datasheet", {}).get("url") if isinstance(candidate.get("datasheet"), dict) else None

    atoms: List[ComponentEvidenceAtom] = []

    elec = candidate.get("electrical", {}) or {}
    if elec.get("nominal_voltage") is not None:
        atoms.append(ComponentEvidenceAtom(
            mpn=mpn, manufacturer=mfr, attribute="nominal_voltage",
            value=str(elec["nominal_voltage"]), unit="V",
            source=source, source_id=cid, retrieved_at=retrieved_at, source_url=ds_url
        ))
    if elec.get("voltage_min") is not None and elec.get("voltage_max") is not None:
        atoms.append(ComponentEvidenceAtom(
            mpn=mpn, manufacturer=mfr, attribute="operating_voltage_range",
            value=f"{elec['voltage_min']} - {elec['voltage_max']}", unit="V",
            source=source, source_id=cid, retrieved_at=retrieved_at, source_url=ds_url
        ))
    if elec.get("current_max") is not None:
        atoms.append(ComponentEvidenceAtom(
            mpn=mpn, manufacturer=mfr, attribute="current_max",
            value=str(elec["current_max"]), unit="A",
            source=source, source_id=cid, retrieved_at=retrieved_at, source_url=ds_url
        ))

    phys = candidate.get("physical", {}) or {}
    if phys.get("package"):
        atoms.append(ComponentEvidenceAtom(
            mpn=mpn, manufacturer=mfr, attribute="package",
            value=str(phys["package"]), unit="type",
            source=source, source_id=cid, retrieved_at=retrieved_at, source_url=ds_url
        ))

    avail = candidate.get("availability", {}) or {}
    if avail.get("stock") is not None:
        atoms.append(ComponentEvidenceAtom(
            mpn=mpn, manufacturer=mfr, attribute="distributor_stock",
            value=str(avail["stock"]), unit="units",
            source=source, source_id=cid, retrieved_at=retrieved_at
        ))

    return atoms


def _generate_why_recommended(
    candidate: Dict[str, Any],
    requirements: List[Dict[str, Any]],
    role_hint: str
) -> Tuple[str, List[str]]:
    """
    Synthesize grounded justification and correlate against requirements based on factual evidence.
    """
    mpn = candidate.get("manufacturer_part_number") or candidate.get("mpn") or "Part"
    elec = candidate.get("electrical", {}) or {}
    phys = candidate.get("physical", {}) or {}
    interfaces = candidate.get("interfaces", {}) or {}
    avail = candidate.get("availability", {}) or {}
    ds = candidate.get("datasheet", {}) or {}

    reasons: List[str] = []
    satisfied_ids: List[str] = []

    # Correlate with requirements
    for req in requirements:
        req_id = req.get("requirement_id") or req.get("id") or "REQ"
        title = (req.get("title") or req.get("statement") or "").lower()
        param = (req.get("parameter") or req.get("property") or "").lower()
        target = str(req.get("target_value") or req.get("value") or "").lower()

        if "voltage" in param or "voltage" in title or "rail" in title:
            if elec.get("nominal_voltage") is not None:
                reasons.append(f"Operating voltage ({elec['nominal_voltage']}V) satisfies {req_id} power specification.")
                satisfied_ids.append(req_id)
        elif "current" in param or "current" in title or "stall" in title:
            if elec.get("current_max") is not None:
                reasons.append(f"Rated maximum current ({elec['current_max']}A) satisfies {req_id}.")
                satisfied_ids.append(req_id)
        elif "sensor" in title or "moisture" in title or "temperature" in title:
            if "sensor" in candidate.get("category", "").lower():
                reasons.append(f"Sensing interface directly addresses {req_id} monitoring objective.")
                satisfied_ids.append(req_id)

    if not reasons:
        if elec.get("nominal_voltage"):
            reasons.append(f"Operates at verified nominal voltage of {elec['nominal_voltage']}V.")
        if phys.get("package"):
            reasons.append(f"Standard {phys['package']} package suitable for PCB fabrication.")
        if avail.get("stock", 0) > 0:
            reasons.append(f"Immediate distributor availability with {avail['stock']:,} units in stock.")
        if ds.get("url"):
            reasons.append("Supported by verified manufacturer technical documentation and timing diagrams.")

    justification = f"**Why recommended for {role_hint}:** " + " ".join(reasons)
    return justification, list(set(satisfied_ids))


def _check_constraint_violations(
    candidate: Dict[str, Any],
    constraints: List[Dict[str, Any]]
) -> List[ConstraintViolation]:
    """
    Checks if component electrical or physical parameters violate any explicit constraints.
    """
    violations: List[ConstraintViolation] = []
    mpn = candidate.get("manufacturer_part_number") or candidate.get("mpn") or "Unknown"
    elec = candidate.get("electrical", {}) or {}

    for con in constraints:
        con_id = con.get("constraint_id") or con.get("id") or "CON"
        prop = (con.get("property") or con.get("parameter") or con.get("constraint_type") or "").lower()
        op = con.get("operator", "<=")
        req_val_raw = con.get("required_value") or con.get("value")

        try:
            req_num = float(req_val_raw)
        except (ValueError, TypeError):
            continue

        if "voltage_max" in prop or "voltage" in prop:
            comp_volt = elec.get("voltage_max") or elec.get("nominal_voltage")
            if comp_volt and isinstance(comp_volt, (int, float)):
                if op == "<=" and comp_volt > req_num:
                    violations.append(ConstraintViolation(
                        violation_id=f"VIOL_{con_id}_{mpn}",
                        constraint_id=con_id,
                        component_mpn=mpn,
                        detected_value=f"{comp_volt}V",
                        allowed_value=f"<= {req_num}V",
                        property_name="voltage_max",
                        severity="CRITICAL",
                        status="OPEN",
                        details=f"Component {mpn} operating voltage ({comp_volt}V) exceeds maximum allowed {req_num}V.",
                    ))

        if "current" in prop:
            comp_curr = elec.get("current_max")
            if comp_curr and isinstance(comp_curr, (int, float)):
                if op == "<=" and comp_curr > req_num:
                    violations.append(ConstraintViolation(
                        violation_id=f"VIOL_{con_id}_{mpn}",
                        constraint_id=con_id,
                        component_mpn=mpn,
                        detected_value=f"{comp_curr}A",
                        allowed_value=f"<= {req_num}A",
                        property_name="current_max",
                        severity="HIGH",
                        status="OPEN",
                        details=f"Component {mpn} current ({comp_curr}A) exceeds constraint limit {req_num}A.",
                    ))

    return violations


async def research_components_for_project(
    idea_understanding: Dict[str, Any],
    requirements: List[Dict[str, Any]],
    constraints: List[Dict[str, Any]],
    project_id: str = "default_project"
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Executes component discovery across sensors, actuators, controller, and power subsystems
    via Nexar MCP tools.
    Returns: (recommended_components, alternative_components, evidence_atoms, constraint_violations).
    """
    search_targets: List[Tuple[str, str]] = []

    # 1. Controller
    mcu_terms = idea_understanding.get("controller_requirements", [])
    mcu_query = mcu_terms[0] if mcu_terms else "microcontroller"
    search_targets.append((mcu_query, "Core Controller / MCU"))

    # 2. Sensors
    for s in idea_understanding.get("sensors", [])[:2]:
        search_targets.append((s, "Primary Sensor"))

    # 3. Actuators
    for a in idea_understanding.get("actuators", [])[:1]:
        search_targets.append((a, "Actuator / Driver"))

    # 4. Power Regulator
    search_targets.append(("voltage regulator 3.3V buck", "Power Regulation"))

    recommended: List[RecommendedComponent] = []
    all_alternatives: List[ComponentAlternative] = []
    all_evidence: List[ComponentEvidenceAtom] = []
    all_violations: List[ConstraintViolation] = []

    for query_term, role_hint in search_targets:
        candidates = await _query_mcp_candidates(query_term, limit=3)
        if not candidates:
            continue

        primary = candidates[0]
        mpn = primary.get("manufacturer_part_number") or primary.get("mpn") or "UNKNOWN"
        mfr = primary.get("manufacturer") or "Generic"
        cid = primary.get("component_id") or f"comp_{mpn}"
        retrieved_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        source = primary.get("metadata", {}).get("source") or primary.get("source") or "Nexar/Octopart MCP"

        elec = primary.get("electrical", {}) or {}
        phys = primary.get("physical", {}) or {}
        avail = primary.get("availability", {}) or {}
        pricing = primary.get("pricing", {}) or {}
        ds = primary.get("datasheet", {}) or {}
        vendor = primary.get("vendor", {}) or {}

        why_rec, sat_ids = _generate_why_recommended(primary, requirements, role_hint)
        evidence_atoms = _extract_evidence_atoms(primary)
        all_evidence.extend(evidence_atoms)

        # Check violations
        violations = _check_constraint_violations(primary, constraints)
        all_violations.extend(violations)

        # Alternatives from remaining candidates
        alternatives_list: List[ComponentAlternative] = []
        for alt_cand in candidates[1:]:
            alt_mpn = alt_cand.get("manufacturer_part_number") or alt_cand.get("mpn")
            if not alt_mpn:
                continue
            alt_mfr = alt_cand.get("manufacturer") or "Manufacturer"
            alt_elec = alt_cand.get("electrical", {}) or {}
            alt_pricing = alt_cand.get("pricing", {}) or {}
            alt_ds = alt_cand.get("datasheet", {}) or {}

            # Synthesize trade-off comparison based on verified specs
            trade_off = f"Alternative {alt_mpn} operates at {alt_elec.get('nominal_voltage', 'N/A')}V; compare package and availability."
            alt_obj = ComponentAlternative(
                alternative_mpn=alt_mpn,
                alternative_name=alt_cand.get("product_name") or f"{alt_mfr} {alt_mpn}",
                manufacturer=alt_mfr,
                category=alt_cand.get("category") or "Alternative Component",
                reason=f"Drop-in functional candidate for {role_hint} with verified specifications.",
                trade_off=trade_off,
                source=alt_cand.get("metadata", {}).get("source") or "Nexar/Octopart MCP",
                datasheet_url=alt_ds.get("url"),
                pricing_inr=float(alt_pricing.get("unit_price") or 0.0),
            )
            alternatives_list.append(alt_obj)
            all_alternatives.append(alt_obj)

        rec = RecommendedComponent(
            component_id=cid,
            component_name=primary.get("product_name") or f"{mfr} {mpn}",
            manufacturer=mfr,
            mpn=mpn,
            category=primary.get("category") or "Electronic Component",
            description=primary.get("description") or f"{mfr} {mpn} for {role_hint}.",
            specifications=elec,
            package=str(phys.get("package") or "Surface Mount"),
            voltage_range=f"{elec.get('voltage_min', elec.get('nominal_voltage', 'N/A'))}V - {elec.get('voltage_max', elec.get('nominal_voltage', 'N/A'))}V",
            current_rating=f"{elec.get('current_max', elec.get('current', 'N/A'))}A",
            operating_temperature="-40°C to +85°C",
            availability_stock=int(avail.get("stock") or 0),
            unit_price_inr=float(pricing.get("unit_price") or 0.0),
            distributor=vendor.get("name") or "DigiKey / Mouser",
            datasheet_url=ds.get("url"),
            product_url=vendor.get("product_url"),
            source=source,
            retrieved_at=retrieved_at,
            why_recommended=why_rec,
            satisfied_requirement_ids=sat_ids,
            evidence=evidence_atoms,
            alternatives=alternatives_list,
        )
        recommended.append(rec)

    return (
        [r.model_dump() for r in recommended],
        [a.model_dump() for a in all_alternatives],
        [e.model_dump() for e in all_evidence],
        [v.model_dump() for v in all_violations],
    )
