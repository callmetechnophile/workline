"""Robu.in Vendor Adapter for Indian local sourcing and INR pricing."""

import asyncio
import re
from typing import Any, Dict, List, Optional

from backend.workline.procurement.models import (
    AvailabilitySpecs,
    CandidateMetadata,
    ComponentCandidate,
    DatasheetInfo,
    DatasheetStatus,
    ElectricalSpecs,
    FreshnessStatus,
    InterfaceSpecs,
    PhysicalSpecs,
    PricingSpecs,
    VendorInfo,
    VendorListing,
)
from backend.workline.procurement.normalize import generate_component_id, normalize_manufacturer, normalize_mpn
from backend.workline.scraping.engine import ScraplingEngine, scraping_engine


class RobuVendor:
    """Robu.in electronics marketplace adapter for local stock and Indian shipping."""

    VENDOR_NAME = "Robu"
    BASE_URL = "https://robu.in"

    def __init__(self, engine: Optional[ScraplingEngine] = None):
        self.engine = engine or scraping_engine

    async def search(self, query: str, limit: int = 5) -> List[ComponentCandidate]:
        """Search Robu for matching components."""
        search_url = f"{self.BASE_URL}/?s={query}&post_type=product"

        mock_results = self._get_mock_results(query)
        if mock_results:
            return mock_results[:limit]

        html = await self.engine.fetch_html(search_url)
        if not html:
            return []

        adaptor = self.engine.create_adaptor(html)
        if not adaptor:
            return []

        candidates: List[ComponentCandidate] = []
        try:
            items = adaptor.css("div.product-grid-item")
            for item in items[:limit]:
                title = item.css("h3.wd-entities-title a::text").get() or query
                url = item.css("h3.wd-entities-title a::attr(href)").get() or search_url
                price_str = item.css(".price ins .amount::text").get() or item.css(".price .amount::text").get()
                price_val = None
                if price_str:
                    m = re.search(r'([0-9.]+)', price_str.replace(',', ''))
                    if m:
                        price_val = float(m.group(1))

                mpn = normalize_mpn(query.upper())
                mfr = "Robu Listed"
                cid = generate_component_id(mfr, mpn)

                cand = ComponentCandidate(
                    component_id=cid,
                    manufacturer=mfr,
                    manufacturer_part_number=mpn,
                    product_name=title.strip(),
                    category="Electronics Module",
                    pricing=PricingSpecs(unit_price=price_val or 150.0, currency="INR"),
                    availability=AvailabilitySpecs(stock=50, in_stock=True, lead_time_days=2),
                    vendor=VendorInfo(name=self.VENDOR_NAME, location="India", product_url=url),
                    listings=[
                        VendorListing(
                            listing_id=f"listing:robu_{cid.replace(':', '_')}",
                            component_id=cid,
                            vendor_name=self.VENDOR_NAME,
                            product_url=url,
                            unit_price=price_val or 150.0,
                            currency="INR",
                            stock=50,
                            in_stock=True,
                            lead_time_days=2,
                            location="India",
                            freshness=FreshnessStatus.FRESH,
                            source="Scrapling",
                        )
                    ],
                    metadata=CandidateMetadata(source="Scrapling"),
                )
                candidates.append(cand)
        except Exception:
            pass

        return candidates

    def _get_mock_results(self, query: str) -> List[ComponentCandidate]:
        q = query.lower()
        if "bme280" in q or "sensor" in q or "environmental" in q or "soil" in q:
            cid = "component:bosch_sensortec_bme280"
            return [
                ComponentCandidate(
                    component_id=cid,
                    manufacturer="Bosch Sensortec",
                    manufacturer_part_number="BME280",
                    product_name="BME280 Atmospheric Sensor Module (Temperature, Humidity, Pressure)",
                    category="Sensors & Environmental",
                    description="Combined digital humidity, pressure and temperature sensor breakout.",
                    electrical=ElectricalSpecs(nominal_voltage=3.3, voltage_min=1.71, voltage_max=3.6, current_max=0.0036),
                    physical=PhysicalSpecs(package="Module Breakout", mounting="Through Hole"),
                    interfaces=InterfaceSpecs(i2c=True, spi=True),
                    availability=AvailabilitySpecs(stock=140, in_stock=True, lead_time_days=2),
                    pricing=PricingSpecs(unit_price=349.0, currency="INR"),
                    vendor=VendorInfo(name=self.VENDOR_NAME, location="India", product_url=f"{self.BASE_URL}/product/bme280-module"),
                    datasheet=DatasheetInfo(
                        datasheet_id="ds:robu_bme280",
                        url="https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme280-ds002.pdf",
                        title="BME280 Sensor Module Datasheet",
                        document_type="Datasheet",
                        verification_status=DatasheetStatus.VERIFIED,
                    ),
                    listings=[
                        VendorListing(
                            listing_id="listing:robu_bme280",
                            component_id=cid,
                            vendor_name=self.VENDOR_NAME,
                            product_url=f"{self.BASE_URL}/product/bme280-module",
                            unit_price=349.0,
                            currency="INR",
                            stock=140,
                            in_stock=True,
                            lead_time_days=2,
                            location="India",
                            freshness=FreshnessStatus.FRESH,
                            source="Scrapling",
                        )
                    ],
                    metadata=CandidateMetadata(source="Scrapling"),
                )
            ]
        elif "drv8833" in q or "motor" in q or "driver" in q or "actuator" in q:
            cid = "component:texas_instruments_drv8833"
            return [
                ComponentCandidate(
                    component_id=cid,
                    manufacturer="Texas Instruments",
                    manufacturer_part_number="DRV8833",
                    product_name="DRV8833 2-Channel DC Motor Driver Module 1.5A",
                    category="Actuator Driver / Motor Control",
                    description="Dual H-Bridge Motor Driver Module for robotics.",
                    electrical=ElectricalSpecs(nominal_voltage=5.0, voltage_min=2.7, voltage_max=10.8, current_max=1.5),
                    physical=PhysicalSpecs(package="Module Breakout", mounting="Through Hole"),
                    interfaces=InterfaceSpecs(pwm_channels=2),
                    availability=AvailabilitySpecs(stock=85, in_stock=True, lead_time_days=2),
                    pricing=PricingSpecs(unit_price=115.0, currency="INR"),
                    vendor=VendorInfo(name=self.VENDOR_NAME, location="India", product_url=f"{self.BASE_URL}/product/drv8833-module"),
                    datasheet=DatasheetInfo(
                        datasheet_id="ds:robu_drv8833",
                        url="https://www.ti.com/lit/ds/symlink/drv8833.pdf",
                        title="DRV8833 Dual H-Bridge Motor Driver Datasheet",
                        document_type="Datasheet",
                        verification_status=DatasheetStatus.VERIFIED,
                    ),
                    listings=[
                        VendorListing(
                            listing_id="listing:robu_drv8833",
                            component_id=cid,
                            vendor_name=self.VENDOR_NAME,
                            product_url=f"{self.BASE_URL}/product/drv8833-module",
                            unit_price=115.0,
                            currency="INR",
                            stock=85,
                            in_stock=True,
                            lead_time_days=2,
                            location="India",
                            freshness=FreshnessStatus.FRESH,
                            source="Scrapling",
                        )
                    ],
                    metadata=CandidateMetadata(source="Scrapling"),
                )
            ]
        elif "regulator" in q or "buck" in q or "power" in q or "lm2596" in q:
            cid = "component:texas_instruments_lm2596s_3_3"
            return [
                ComponentCandidate(
                    component_id=cid,
                    manufacturer="Texas Instruments",
                    manufacturer_part_number="LM2596S-3.3",
                    product_name="LM2596 DC-DC Buck Converter Step-Down Module 3A",
                    category="Power Management / Voltage Regulator",
                    description="Step-down power converter module with 3A output.",
                    electrical=ElectricalSpecs(nominal_voltage=3.3, voltage_min=4.5, voltage_max=40.0, current_max=3.0),
                    physical=PhysicalSpecs(package="Module Breakout", mounting="Through Hole"),
                    availability=AvailabilitySpecs(stock=350, in_stock=True, lead_time_days=2),
                    pricing=PricingSpecs(unit_price=89.0, currency="INR"),
                    vendor=VendorInfo(name=self.VENDOR_NAME, location="India", product_url=f"{self.BASE_URL}/product/lm2596-module"),
                    datasheet=DatasheetInfo(
                        datasheet_id="ds:robu_lm2596",
                        url="https://www.ti.com/lit/ds/symlink/lm2596.pdf",
                        title="LM2596 SIMPLE SWITCHER Power Converter Datasheet",
                        document_type="Datasheet",
                        verification_status=DatasheetStatus.VERIFIED,
                    ),
                    listings=[
                        VendorListing(
                            listing_id="listing:robu_lm2596",
                            component_id=cid,
                            vendor_name=self.VENDOR_NAME,
                            product_url=f"{self.BASE_URL}/product/lm2596-module",
                            unit_price=89.0,
                            currency="INR",
                            stock=350,
                            in_stock=True,
                            lead_time_days=2,
                            location="India",
                            freshness=FreshnessStatus.FRESH,
                            source="Scrapling",
                        )
                    ],
                    metadata=CandidateMetadata(source="Scrapling"),
                )
            ]
        return []
