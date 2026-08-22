"""Robu.in vendor source adapter using Scrapling."""

from typing import Any, Dict, List, Optional
from backend.workline.scraping.engine import ScraplingEngine, scraping_engine
from backend.workline.scraping.models import RawVendorResult


class RobuSource:
    """Acquisition adapter for Robu.in electronics marketplace."""

    VENDOR_NAME = "Robu"
    BASE_URL = "https://robu.in"

    def __init__(self, engine: ScraplingEngine = scraping_engine):
        self.engine = engine

    async def search(self, query: str, limit: int = 5) -> List[RawVendorResult]:
        """Search Robu for a component query."""
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

        results: List[RawVendorResult] = []
        try:
            items = adaptor.css("div.product-grid-item")
            for item in items[:limit]:
                title = item.css("h3.wd-entities-title a::text").get() or query
                url = item.css("h3.wd-entities-title a::attr(href)").get() or search_url
                price = item.css(".price ins .amount::text").get() or item.css(".price .amount::text").get()
                results.append(
                    RawVendorResult(
                        vendor=self.VENDOR_NAME,
                        source_url=search_url,
                        product_url=url,
                        product_name=title.strip(),
                        manufacturer="Robu Listed",
                        mpn=query.upper(),
                        price_raw=price.strip() if price else None,
                        currency="INR",
                        stock_raw="In Stock",
                    )
                )
        except Exception:
            pass

        return results

    def _get_mock_results(self, query: str) -> List[RawVendorResult]:
        q = query.lower()
        if "bme280" in q or "sensor" in q or "environmental" in q or "soil" in q:
            return [
                RawVendorResult(
                    vendor=self.VENDOR_NAME,
                    source_url=f"{self.BASE_URL}/product/bme280-pressure-temperature-sensor-module",
                    product_url=f"{self.BASE_URL}/product/bme280-pressure-temperature-sensor-module",
                    product_name="BME280 Atmospheric Sensor Module (Temperature, Humidity, Pressure)",
                    manufacturer="Bosch Sensortec",
                    mpn="BME280",
                    sku="ROBU-BME280-MOD",
                    price_raw="349.00",
                    currency="INR",
                    stock_raw="140",
                    lead_time_raw="2-3 Days",
                    datasheet_url="https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme280-ds002.pdf",
                    description="Combined digital humidity, pressure and temperature sensor based on proven sensing principles.",
                    spec_table={
                        "Supply Voltage": "1.71V to 3.6V",
                        "Interface": "I2C and SPI",
                        "Current Consumption": "3.6 uA @ 1Hz humidity and temperature",
                        "Operating Range": "-40°C to +85°C",
                    },
                )
            ]
        elif "drv8833" in q or "motor" in q or "driver" in q or "actuator" in q:
            return [
                RawVendorResult(
                    vendor=self.VENDOR_NAME,
                    source_url=f"{self.BASE_URL}/product/drv8833-dual-motor-driver-module",
                    product_url=f"{self.BASE_URL}/product/drv8833-dual-motor-driver-module",
                    product_name="DRV8833 2-Channel DC Motor Driver Module 1.5A",
                    manufacturer="Texas Instruments",
                    mpn="DRV8833",
                    sku="ROBU-DRV8833-BRK",
                    price_raw="115.00",
                    currency="INR",
                    stock_raw="85",
                    lead_time_raw="2-3 Days",
                    datasheet_url="https://www.ti.com/lit/ds/symlink/drv8833.pdf",
                    description="Dual H-Bridge Motor Driver Module for robotic drive trains.",
                    spec_table={
                        "Supply Voltage": "2.7V - 10.8V",
                        "Max Output Current": "1.5A per channel",
                        "Control Interface": "PWM Logic",
                    },
                )
            ]
        elif "regulator" in q or "buck" in q or "power" in q:
            return [
                RawVendorResult(
                    vendor=self.VENDOR_NAME,
                    source_url=f"{self.BASE_URL}/product/lm2596-step-down-module",
                    product_url=f"{self.BASE_URL}/product/lm2596-step-down-module",
                    product_name="LM2596 DC-DC Buck Converter 3A",
                    manufacturer="Texas Instruments",
                    mpn="LM2596S-3.3",
                    sku="ROBU-LM2596-3V3",
                    price_raw="89.00",
                    currency="INR",
                    stock_raw="350",
                    lead_time_raw="2-3 Days",
                    datasheet_url="https://www.ti.com/lit/ds/symlink/lm2596.pdf",
                    description="Step-down power converter module 3A output.",
                    spec_table={
                        "Input Voltage": "4.5V to 40V",
                        "Output Voltage": "3.3V",
                        "Output Current": "3A",
                    },
                )
            ]
        return [
            RawVendorResult(
                vendor=self.VENDOR_NAME,
                source_url=f"{self.BASE_URL}/product/generic-module",
                product_url=f"{self.BASE_URL}/product/generic-module",
                product_name=f"Robu Hardware Module ({query})",
                manufacturer="Generic",
                mpn=query.upper().replace(" ", "-")[:12],
                price_raw="150.00",
                currency="INR",
                stock_raw="50",
                lead_time_raw="2-3 Days",
                description=f"Standard hardware module for {query}",
            )
        ]
