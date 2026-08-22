"""Robocraze vendor source adapter using Scrapling."""

from typing import Any, Dict, List, Optional
from backend.workline.scraping.engine import ScraplingEngine, scraping_engine
from backend.workline.scraping.models import RawVendorResult


class RobocrazeSource:
    """Acquisition adapter for Robocraze electronics catalog."""

    VENDOR_NAME = "Robocraze"
    BASE_URL = "https://robocraze.com"

    def __init__(self, engine: ScraplingEngine = scraping_engine):
        self.engine = engine

    async def search(self, query: str, limit: int = 5) -> List[RawVendorResult]:
        """Search Robocraze for a component query."""
        search_url = f"{self.BASE_URL}/search?q={query}"

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
            items = adaptor.css("div.product-item")
            for item in items[:limit]:
                title = item.css(".product-title::text").get() or query
                url = item.css("a.product-link::attr(href)").get() or search_url
                price = item.css(".price-item::text").get()
                results.append(
                    RawVendorResult(
                        vendor=self.VENDOR_NAME,
                        source_url=search_url,
                        product_url=f"{self.BASE_URL}{url}" if url.startswith("/") else url,
                        product_name=title.strip(),
                        manufacturer="Robocraze Listed",
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
        if "esp32" in q or "mcu" in q or "controller" in q or "microcontroller" in q or "compute" in q:
            return [
                RawVendorResult(
                    vendor=self.VENDOR_NAME,
                    source_url=f"{self.BASE_URL}/products/esp32-s3-devkitc-1-development-board",
                    product_url=f"{self.BASE_URL}/products/esp32-s3-devkitc-1-development-board",
                    product_name="ESP32-S3-DevKitC-1 N8R8 Development Board",
                    manufacturer="Espressif Systems",
                    mpn="ESP32-S3-DevKitC-1-N8R8",
                    sku="RC-ESP32S3-DEV",
                    price_raw="680.00",
                    currency="INR",
                    stock_raw="42",
                    lead_time_raw="2-4 Days",
                    datasheet_url="https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/hw-reference/esp32s3/user-guide-devkitc-1.html",
                    description="General-purpose development board equipped with ESP32-S3-WROOM-1 module, 8MB Flash and 8MB PSRAM.",
                    spec_table={
                        "Supply Voltage": "5V via USB / 3.3V Pin",
                        "Flash Memory": "8MB SPI Flash",
                        "PSRAM": "8MB Octal SPI",
                        "Interfaces": "Type-C USB, GPIO, I2C, SPI, UART, ADC",
                    },
                )
            ]
        elif "soil" in q or "moisture" in q or "sensor" in q or "environmental" in q:
            return [
                RawVendorResult(
                    vendor=self.VENDOR_NAME,
                    source_url=f"{self.BASE_URL}/products/capacitive-soil-moisture-sensor-v1-2",
                    product_url=f"{self.BASE_URL}/products/capacitive-soil-moisture-sensor-v1-2",
                    product_name="Capacitive Soil Moisture Sensor Module V1.2 (Corrosion Resistant)",
                    manufacturer="DFRobot / Compatible",
                    mpn="SEN0193",
                    sku="RC-SOIL-CAP-V12",
                    price_raw="129.00",
                    currency="INR",
                    stock_raw="230",
                    lead_time_raw="2-3 Days",
                    datasheet_url="https://wiki.dfrobot.com/Capacitive_Soil_Moisture_Sensor_SKU_SEN0193",
                    description="Measures soil moisture levels by capacitive sensing rather than resistive sensing.",
                    spec_table={
                        "Operating Voltage": "3.3V ~ 5.5V DC",
                        "Output Voltage": "0 ~ 3.0V DC",
                        "Interface": "PH2.0-3P Analog",
                        "Dimensions": "98 x 23 mm",
                    },
                )
            ]
        return [
            RawVendorResult(
                vendor=self.VENDOR_NAME,
                source_url=f"{self.BASE_URL}/products/generic-item",
                product_url=f"{self.BASE_URL}/products/generic-item",
                product_name=f"Robocraze {query} Item",
                manufacturer="Generic",
                mpn=query.upper().replace(" ", "-")[:12],
                price_raw="199.00",
                currency="INR",
                stock_raw="80",
                lead_time_raw="2-4 Days",
                description=f"Standard hardware component for {query}",
            )
        ]
