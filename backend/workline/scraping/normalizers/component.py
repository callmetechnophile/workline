"""Component normalizer generating canonical ComponentCandidate models."""

import re
from typing import Dict, List, Optional
from backend.workline.scraping.extractors.component import ComponentExtractor
from backend.workline.scraping.extractors.datasheet import DatasheetExtractor
from backend.workline.scraping.models import (
    ComponentCandidate,
    RawVendorResult,
    VendorListing,
)
from backend.workline.scraping.normalizers.vendor import VendorNormalizer


def normalize_mpn(mpn: str) -> str:
    """Normalize MPN string by stripping trailing whitespace, package reel suffixes if generic."""
    if not mpn:
        return ""
    clean = mpn.strip().upper()
    return clean


def generate_component_id(manufacturer: str, mpn: str) -> str:
    """Generates canonical component ID from Manufacturer + MPN."""
    m_clean = re.sub(r'[^a-zA-Z0-9]', '_', (manufacturer or "generic").lower()).strip('_')
    mpn_clean = re.sub(r'[^a-zA-Z0-9]', '_', (mpn or "unknown").lower()).strip('_')
    return f"component:{m_clean}_{mpn_clean}"


class ComponentNormalizer:
    """Consolidates and normalizes multiple raw vendor results into canonical ComponentCandidate."""

    def __init__(self):
        self.comp_extractor = ComponentExtractor()
        self.ds_extractor = DatasheetExtractor()
        self.vendor_normalizer = VendorNormalizer()

    def normalize(self, raw_results: List[RawVendorResult]) -> List[ComponentCandidate]:
        """Group raw vendor results by canonical (Manufacturer, MPN) and synthesize ComponentCandidate."""
        grouped: Dict[str, List[RawVendorResult]] = {}

        for raw in raw_results:
            mfr = raw.manufacturer or "Generic"
            mpn = normalize_mpn(raw.mpn or raw.product_name)
            comp_id = generate_component_id(mfr, mpn)

            if comp_id not in grouped:
                grouped[comp_id] = []
            grouped[comp_id].append(raw)

        candidates: List[ComponentCandidate] = []
        for comp_id, group in grouped.items():
            primary = group[0]
            mfr = primary.manufacturer or "Generic"
            mpn = normalize_mpn(primary.mpn or primary.product_name)

            # Combine spec tables
            all_specs: Dict[str, str] = {}
            for g in group:
                all_specs.update(g.spec_table)

            desc = primary.description or primary.product_name
            electrical = self.comp_extractor.extract_electrical(all_specs, desc)
            physical = self.comp_extractor.extract_physical(all_specs, desc)
            interfaces = self.comp_extractor.extract_interfaces(all_specs, desc)
            environment = self.comp_extractor.extract_environment(all_specs, desc)

            # Build vendor listings
            listings: List[VendorListing] = []
            for g in group:
                listing = self.vendor_normalizer.normalize_listing(g)
                listings.append(listing)

            # Datasheet
            datasheet = None
            for g in group:
                if g.datasheet_url:
                    datasheet = self.ds_extractor.extract_datasheet(
                        url=g.datasheet_url, manufacturer=mfr, mpn=mpn
                    )
                    if datasheet:
                        break

            # Categorize
            category = "General Hardware"
            name_lower = primary.product_name.lower() + " " + (primary.description or "").lower()
            if "regulator" in name_lower or "buck" in name_lower or "boost" in name_lower or "ldo" in name_lower:
                category = "Power Management / Voltage Regulator"
            elif "mcu" in name_lower or "microcontroller" in name_lower or "esp32" in name_lower or "cortex" in name_lower:
                category = "Microcontroller / Compute Unit"
            elif "motor" in name_lower or "driver" in name_lower or "h-bridge" in name_lower:
                category = "Actuator Driver / Motor Control"
            elif "sensor" in name_lower or "temperature" in name_lower or "pressure" in name_lower or "moisture" in name_lower:
                category = "Sensors & Environmental"
            elif "battery" in name_lower or "charger" in name_lower or "bms" in name_lower:
                category = "Power Storage / Battery Management"

            candidate = ComponentCandidate(
                component_id=comp_id,
                manufacturer=mfr,
                manufacturer_part_number=mpn,
                product_name=primary.product_name,
                category=category,
                description=desc,
                electrical=electrical,
                physical=physical,
                interfaces=interfaces,
                environment=environment,
                listings=listings,
                datasheet=datasheet,
            )
            candidates.append(candidate)

        return candidates
