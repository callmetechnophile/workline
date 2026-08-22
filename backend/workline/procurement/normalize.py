"""Component, manufacturer, and pricing normalization engine for Workline Procurement."""

import re
from typing import Any, Dict, List, Optional, Tuple

from backend.workline.procurement.models import (
    AvailabilitySpecs,
    CandidateMetadata,
    ComponentCandidate,
    DatasheetInfo,
    DatasheetStatus,
    ElectricalSpecs,
    EnvironmentSpecs,
    FreshnessStatus,
    InterfaceSpecs,
    PhysicalSpecs,
    PricingSpecs,
    VendorInfo,
    VendorListing,
)

# Standard Exchange Rates to INR (Indian Rupee)
EXCHANGE_RATES_TO_INR: Dict[str, float] = {
    "INR": 1.0,
    "USD": 86.50,
    "EUR": 94.20,
    "GBP": 110.40,
    "JPY": 0.58,
    "CNY": 12.05,
    "SGD": 64.80,
    "HKD": 11.08,
}

# Manufacturer Normalization Mapping
MANUFACTURER_SYNONYMS: Dict[str, str] = {
    "ti": "Texas Instruments",
    "texas instruments": "Texas Instruments",
    "texas instruments inc": "Texas Instruments",
    "texas instruments inc.": "Texas Instruments",
    "espressif": "Espressif Systems",
    "espressif systems": "Espressif Systems",
    "espressif systems (shanghai) co., ltd.": "Espressif Systems",
    "st": "STMicroelectronics",
    "stmicroelectronics": "STMicroelectronics",
    "stm": "STMicroelectronics",
    "bosch": "Bosch Sensortec",
    "bosch sensortec": "Bosch Sensortec",
    "microchip": "Microchip Technology",
    "microchip technology": "Microchip Technology",
    "analog devices": "Analog Devices",
    "adi": "Analog Devices",
    "linear technology": "Analog Devices",
    "maxim integrated": "Analog Devices",
    "nxp": "NXP Semiconductors",
    "nxp semiconductors": "NXP Semiconductors",
    "nordic": "Nordic Semiconductor",
    "nordic semiconductor": "Nordic Semiconductor",
    "infineon": "Infineon Technologies",
    "infineon technologies": "Infineon Technologies",
    "rohm": "ROHM Semiconductor",
    "vishay": "Vishay Intertechnology",
    "diodes inc": "Diodes Incorporated",
    "diodes incorporated": "Diodes Incorporated",
    "murata": "Murata Manufacturing",
    "on semi": "onsemi",
    "on semiconductor": "onsemi",
    "onsemi": "onsemi",
}


def normalize_manufacturer(manufacturer: Optional[str]) -> str:
    """Normalize vendor manufacturer strings into canonical industry names."""
    if not manufacturer or not str(manufacturer).strip():
        return "Generic"
    clean = str(manufacturer).strip()
    key = clean.lower()
    return MANUFACTURER_SYNONYMS.get(key, clean)


def normalize_mpn(mpn: Optional[str]) -> str:
    """
    Normalize MPN whitespace and casing without destroying package suffixes or dashes.
    Does NOT over-normalize.
    """
    if not mpn or not str(mpn).strip():
        return "UNKNOWN_MPN"
    clean = str(mpn).strip()
    clean = re.sub(r'[\r\n\t]+', '', clean)
    clean = re.sub(r'\s+', ' ', clean)
    return clean


def generate_component_id(manufacturer: str, mpn: str) -> str:
    """
    Generate authoritative canonical component ID: component:<mfr>_<mpn>
    """
    mfr_clean = re.sub(r'[^a-zA-Z0-9]', '_', normalize_manufacturer(manufacturer).lower()).strip('_')
    mpn_clean = re.sub(r'[^a-zA-Z0-9]', '_', normalize_mpn(mpn).lower()).strip('_')
    return f"component:{mfr_clean}_{mpn_clean}"


class PricingNormalizer:
    """Normalizes multi-currency pricing into INR with tiered quantity breaks."""

    @staticmethod
    def convert_to_inr(price: Optional[float], currency: Optional[str] = "INR") -> Optional[float]:
        """Convert foreign currency amounts into INR."""
        if price is None:
            return None
        curr = (currency or "INR").upper().strip()
        rate = EXCHANGE_RATES_TO_INR.get(curr, 1.0)
        return round(float(price) * rate, 2)

    @staticmethod
    def parse_raw_price(raw_str: Optional[str]) -> Tuple[Optional[float], str]:
        """Extract float price and currency symbol from unformatted string."""
        if not raw_str:
            return None, "INR"
        s = str(raw_str).strip()
        curr = "INR"
        if "$" in s or "USD" in s:
            curr = "USD"
        elif "€" in s or "EUR" in s:
            curr = "EUR"
        elif "£" in s or "GBP" in s:
            curr = "GBP"
        elif "¥" in s or "JPY" in s:
            curr = "JPY"

        match = re.search(r'([0-9]+(?:[.,][0-9]+)?)', s.replace(",", ""))
        if match:
            try:
                val = float(match.group(1))
                return val, curr
            except ValueError:
                pass
        return None, curr


class ComponentNormalizer:
    """
    Consolidates raw component inputs (Nexar, Scrapling, manual) into canonical
    ComponentCandidate nodes deduplicated by (Manufacturer, MPN).
    """

    def __init__(self):
        self.pricing_norm = PricingNormalizer()

    def merge_candidate(
        self, existing: ComponentCandidate, incoming: ComponentCandidate
    ) -> ComponentCandidate:
        """Merge specifications and vendor offers into an existing canonical candidate."""
        # 1. Merge Electrical (fill missing)
        e = existing.electrical
        i_e = incoming.electrical
        e.nominal_voltage = e.nominal_voltage if e.nominal_voltage is not None else i_e.nominal_voltage
        e.voltage_min = e.voltage_min if e.voltage_min is not None else i_e.voltage_min
        e.voltage_max = e.voltage_max if e.voltage_max is not None else i_e.voltage_max
        e.current_max = e.current_max if e.current_max is not None else (i_e.current_max or i_e.current)
        e.current = e.current if e.current is not None else (i_e.current or i_e.current_max)
        e.power = e.power if e.power is not None else i_e.power

        # 2. Merge Physical
        p = existing.physical
        i_p = incoming.physical
        p.package = p.package or i_p.package
        p.dimensions = p.dimensions or i_p.dimensions
        p.mounting = p.mounting or i_p.mounting or i_p.mounting_type
        p.mounting_type = p.mounting_type or i_p.mounting_type or i_p.mounting

        # 3. Merge Interfaces
        inf = existing.interfaces
        i_inf = incoming.interfaces
        inf.i2c = inf.i2c if inf.i2c is not None else i_inf.i2c
        inf.spi = inf.spi if inf.spi is not None else i_inf.spi
        inf.uart = inf.uart if inf.uart is not None else i_inf.uart
        inf.gpio = inf.gpio if inf.gpio is not None else i_inf.gpio
        inf.can = inf.can if inf.can is not None else i_inf.can
        inf.usb = inf.usb if inf.usb is not None else i_inf.usb
        inf.ethernet = inf.ethernet if inf.ethernet is not None else i_inf.ethernet
        inf.pwm_channels = inf.pwm_channels or i_inf.pwm_channels
        inf.adc_channels = inf.adc_channels or i_inf.adc_channels

        # 4. Merge Datasheet
        if not existing.datasheet and incoming.datasheet:
            existing.datasheet = incoming.datasheet

        # 5. Append unique listings
        seen_urls = {l.product_url for l in existing.listings}
        for l in incoming.listings:
            if l.product_url not in seen_urls:
                existing.listings.append(l)
                seen_urls.add(l.product_url)

        # 6. Update best pricing & availability
        self._update_candidate_summary(existing)
        return existing

    def _update_candidate_summary(self, cand: ComponentCandidate) -> None:
        """Derive lowest active price, stock, and lead time from listings."""
        if not cand.listings:
            return

        valid_prices = [l.unit_price for l in cand.listings if l.unit_price and l.unit_price > 0]
        if valid_prices:
            cand.pricing.unit_price = min(valid_prices)
            cand.pricing.currency = "INR"

        total_stock = sum(l.stock for l in cand.listings if l.stock)
        cand.availability.stock = total_stock if total_stock > 0 else (100 if any(l.in_stock for l in cand.listings) else 0)
        cand.availability.in_stock = any(l.in_stock for l in cand.listings)

        lead_times = [l.lead_time_days for l in cand.listings if l.lead_time_days is not None]
        if lead_times:
            cand.availability.lead_time_days = min(lead_times)
            cand.availability.lead_time = min(lead_times)

        # Best vendor info
        sorted_listings = sorted(
            cand.listings,
            key=lambda x: (0 if x.in_stock else 1, x.unit_price or 999999)
        )
        if sorted_listings:
            best = sorted_listings[0]
            cand.vendor = VendorInfo(
                name=best.vendor_name,
                vendor_id=best.vendor_id,
                product_url=best.product_url,
                location=best.location,
            )

    def normalize(self, raw_candidates: List[ComponentCandidate]) -> List[ComponentCandidate]:
        """Deduplicate and consolidate a list of candidates by canonical ID."""
        candidate_map: Dict[str, ComponentCandidate] = {}
        for c in raw_candidates:
            cid = c.component_id or generate_component_id(c.manufacturer, c.manufacturer_part_number)
            c.component_id = cid
            c.manufacturer = normalize_manufacturer(c.manufacturer)
            c.manufacturer_part_number = normalize_mpn(c.manufacturer_part_number)

            if cid in candidate_map:
                candidate_map[cid] = self.merge_candidate(candidate_map[cid], c)
            else:
                self._update_candidate_summary(c)
                candidate_map[cid] = c

        return list(candidate_map.values())
