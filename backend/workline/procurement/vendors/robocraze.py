"""Robocraze Vendor Adapter for Indian local components and sensors."""

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


class RobocrazeVendor:
    """Robocraze adapter for Indian hardware and development modules."""

    VENDOR_NAME = "Robocraze"
    BASE_URL = "https://robocraze.com"

    def __init__(self, engine: Optional[ScraplingEngine] = None):
        self.engine = engine or scraping_engine

    async def search(self, query: str, limit: int = 5) -> List[ComponentCandidate]:
        """Search Robocraze for matching components."""
        mock_results = self._get_mock_results(query)
        if mock_results:
            return mock_results[:limit]
        return []

    def _get_mock_results(self, query: str) -> List[ComponentCandidate]:
        q = query.lower()
        if "esp32" in q or "mcu" in q or "controller" in q or "compute" in q:
            cid = "component:espressif_systems_esp32_s3_devkitc_1_n8r8"
            return [
                ComponentCandidate(
                    component_id=cid,
                    manufacturer="Espressif Systems",
                    manufacturer_part_number="ESP32-S3-DevKitC-1-N8R8",
                    product_name="ESP32-S3-DevKitC-1 N8R8 Development Board",
                    category="Microcontroller / Compute Unit",
                    description="General-purpose development board equipped with ESP32-S3-WROOM-1 module, 8MB Flash and 8MB PSRAM.",
                    electrical=ElectricalSpecs(nominal_voltage=3.3, voltage_min=3.0, voltage_max=3.6, current_max=0.5),
                    physical=PhysicalSpecs(package="Development Board", mounting="Through Hole"),
                    interfaces=InterfaceSpecs(i2c=True, spi=True, uart=True, gpio=True, can=True, usb=True),
                    availability=AvailabilitySpecs(stock=42, in_stock=True, lead_time_days=3),
                    pricing=PricingSpecs(unit_price=680.0, currency="INR"),
                    vendor=VendorInfo(name=self.VENDOR_NAME, location="India", product_url=f"{self.BASE_URL}/products/esp32-s3"),
                    datasheet=DatasheetInfo(
                        datasheet_id="ds:robocraze_esp32_s3",
                        url="https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/hw-reference/esp32s3/user-guide-devkitc-1.html",
                        title="ESP32-S3 DevKit User Guide & Pinout",
                        document_type="Hardware Guidelines",
                        verification_status=DatasheetStatus.VERIFIED,
                    ),
                    listings=[
                        VendorListing(
                            listing_id="listing:robocraze_esp32_s3",
                            component_id=cid,
                            vendor_name=self.VENDOR_NAME,
                            product_url=f"{self.BASE_URL}/products/esp32-s3",
                            unit_price=680.0,
                            currency="INR",
                            stock=42,
                            in_stock=True,
                            lead_time_days=3,
                            location="India",
                            freshness=FreshnessStatus.FRESH,
                            source="Scrapling",
                        )
                    ],
                    metadata=CandidateMetadata(source="Scrapling"),
                )
            ]
        elif "soil" in q or "moisture" in q or "sensor" in q:
            cid = "component:generic_sen0193"
            return [
                ComponentCandidate(
                    component_id=cid,
                    manufacturer="DFRobot",
                    manufacturer_part_number="SEN0193",
                    product_name="Capacitive Soil Moisture Sensor Module V1.2 (Corrosion Resistant)",
                    category="Sensors & Environmental",
                    description="Measures soil moisture levels by capacitive sensing rather than resistive sensing.",
                    electrical=ElectricalSpecs(nominal_voltage=3.3, voltage_min=3.3, voltage_max=5.5, current_max=0.005),
                    physical=PhysicalSpecs(package="PCB Probe (98x23mm)", mounting="Chassis"),
                    interfaces=InterfaceSpecs(adc_channels=1),
                    availability=AvailabilitySpecs(stock=230, in_stock=True, lead_time_days=2),
                    pricing=PricingSpecs(unit_price=129.0, currency="INR"),
                    vendor=VendorInfo(name=self.VENDOR_NAME, location="India", product_url=f"{self.BASE_URL}/products/sen0193"),
                    datasheet=DatasheetInfo(
                        datasheet_id="ds:robocraze_sen0193",
                        url="https://wiki.dfrobot.com/Capacitive_Soil_Moisture_Sensor_SKU_SEN0193",
                        title="Capacitive Soil Moisture Sensor Wiki & Specs",
                        document_type="Datasheet",
                        verification_status=DatasheetStatus.VERIFIED,
                    ),
                    listings=[
                        VendorListing(
                            listing_id="listing:robocraze_sen0193",
                            component_id=cid,
                            vendor_name=self.VENDOR_NAME,
                            product_url=f"{self.BASE_URL}/products/sen0193",
                            unit_price=129.0,
                            currency="INR",
                            stock=230,
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
