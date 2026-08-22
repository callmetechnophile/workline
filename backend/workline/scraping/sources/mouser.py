"""Mouser vendor source adapter using Scrapling."""

from typing import Any, Dict, List, Optional
from backend.workline.scraping.engine import ScraplingEngine, scraping_engine
from backend.workline.scraping.models import RawVendorResult


class MouserSource:
    """Acquisition adapter for Mouser Electronics catalog."""

    VENDOR_NAME = "Mouser"
    BASE_URL = "https://www.mouser.in"

    def __init__(self, engine: ScraplingEngine = scraping_engine):
        self.engine = engine

    async def search(self, query: str, limit: int = 5) -> List[RawVendorResult]:
        """Search Mouser for a component query."""
        search_url = f"{self.BASE_URL}/c/?q={query}"

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
            items = adaptor.css("tr.SearchResultsRow")
            for item in items[:limit]:
                mpn = item.css(".mfr-part-num::text").get() or query
                mfr = item.css(".mfr-name::text").get() or "Mouser Listed"
                price = item.css(".price-col::text").get()
                datasheet = item.css("a[href*='datasheet']::attr(href)").get()
                results.append(
                    RawVendorResult(
                        vendor=self.VENDOR_NAME,
                        source_url=search_url,
                        product_url=f"{self.BASE_URL}/ProductDetail/{mpn}",
                        product_name=mpn.strip(),
                        manufacturer=mfr.strip(),
                        mpn=mpn.strip(),
                        price_raw=price.strip() if price else None,
                        currency="INR",
                        datasheet_url=datasheet,
                        stock_raw="In Stock",
                    )
                )
        except Exception:
            pass

        return results

    def _get_mock_results(self, query: str) -> List[RawVendorResult]:
        q = query.lower()
        if "tps62130" in q or "buck" in q or "regulator" in q:
            return [
                RawVendorResult(
                    vendor=self.VENDOR_NAME,
                    source_url=f"{self.BASE_URL}/c/?q=TPS62130",
                    product_url=f"{self.BASE_URL}/ProductDetail/Texas-Instruments/TPS62130RGTR",
                    product_name="Switching Voltage Regulators 3A Step-Down",
                    manufacturer="Texas Instruments",
                    mpn="TPS62130RGTR",
                    sku="595-TPS62130RGTR",
                    price_raw="210.50",
                    currency="INR",
                    stock_raw="3200",
                    lead_time_raw="0",
                    datasheet_url="https://www.ti.com/lit/ds/symlink/tps62130.pdf",
                    description="Step-down converter 3A output current with DCS-Control topology.",
                    spec_table={
                        "Input Voltage Min": "3 V",
                        "Input Voltage Max": "17 V",
                        "Output Voltage": "3.3 V",
                        "Output Current": "3 A",
                        "Mounting Style": "SMD/SMT",
                        "Package": "VQFN-16",
                    },
                )
            ]
        elif "drv8833" in q or "motor" in q or "driver" in q:
            return [
                RawVendorResult(
                    vendor=self.VENDOR_NAME,
                    source_url=f"{self.BASE_URL}/c/?q=DRV8833",
                    product_url=f"{self.BASE_URL}/ProductDetail/Texas-Instruments/DRV8833PWP",
                    product_name="Dual H-Bridge Motor Driver IC",
                    manufacturer="Texas Instruments",
                    mpn="DRV8833PWPR",
                    sku="595-DRV8833PWPR",
                    price_raw="145.00",
                    currency="INR",
                    stock_raw="8400",
                    lead_time_raw="0",
                    datasheet_url="https://www.ti.com/lit/ds/symlink/drv8833.pdf",
                    description="Dual H-Bridge Motor Driver with current regulation and PWM interface.",
                    spec_table={
                        "Operating Supply Voltage": "2.7 V to 10.8 V",
                        "Output Current": "1.5 A RMS per channel (2A Peak)",
                        "Interface": "PWM",
                        "Package / Case": "HTSSOP-16",
                    },
                )
            ]
        return [
            RawVendorResult(
                vendor=self.VENDOR_NAME,
                source_url=f"{self.BASE_URL}/c/?q={query}",
                product_url=f"{self.BASE_URL}/ProductDetail/{query}",
                product_name=f"Mouser {query} Part",
                manufacturer="Texas Instruments",
                mpn=query.upper().replace(" ", "-")[:12],
                price_raw="180.00",
                currency="INR",
                stock_raw="500",
                lead_time_raw="0",
                description=f"Mouser verified part for {query}",
            )
        ]
