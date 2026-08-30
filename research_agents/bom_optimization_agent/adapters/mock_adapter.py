"""
Deterministic mock supplier adapter simulating Indian and global electronic component distributors.
"""

from typing import List
from research_agents.bom_optimization_agent.adapters.base import SupplierAdapter
from research_agents.bom_optimization_agent.schemas import Location, SupplierOffer


class MockDistributorAdapter(SupplierAdapter):
    """Multi-supplier mock adapter providing realistic distributor offers with MOQ and price breaks."""

    def __init__(
        self,
        supp_id: str,
        name: str,
        city: str,
        state: str,
        country: str = "India",
        postal_code: str = "560001",
    ):
        self._id = supp_id
        self._name = name
        self._location = Location(city=city, state=state, country=country, postal_code=postal_code)

    @property
    def supplier_id(self) -> str:
        return self._id

    @property
    def supplier_name(self) -> str:
        return self._name

    def get_supplier_location(self) -> Location:
        return self._location

    async def get_offers_for_bom_item(
        self,
        bom_item_id: str,
        part_number: str,
        category: str,
        quantity: int,
    ) -> List[SupplierOffer]:
        offers: List[SupplierOffer] = []
        timestamp = "2026-08-30T12:00:00Z"

        # Deterministic pricing catalog based on component part number & supplier
        part_lower = part_number.lower()

        if "900-13766" in part_lower or "orin" in part_lower:
            if self._id == "SUPP-ROBU":
                offers.append(
                    SupplierOffer(
                        supplier_id=self._id,
                        supplier_name=self._name,
                        location=self._location,
                        bom_item_id=bom_item_id,
                        part_number="900-13766-0000-000",
                        manufacturer="NVIDIA",
                        unit_price=45000.0,
                        available_quantity=15,
                        minimum_order_quantity=1,
                        lead_time_days=2,
                        stock_status="in_stock",
                        source_url="https://robu.in/product/nvidia-jetson-orin-nano-developer-kit/",
                        data_timestamp=timestamp,
                        confidence=0.98,
                    )
                )
            elif self._id == "SUPP-MOUSER":
                offers.append(
                    SupplierOffer(
                        supplier_id=self._id,
                        supplier_name=self._name,
                        location=self._location,
                        bom_item_id=bom_item_id,
                        part_number="900-13766-0000-000",
                        manufacturer="NVIDIA",
                        unit_price=44200.0,
                        available_quantity=50,
                        minimum_order_quantity=1,
                        lead_time_days=4,
                        stock_status="in_stock",
                        source_url="https://www.mouser.in/ProductDetail/NVIDIA/900-13766-0000-000",
                        data_timestamp=timestamp,
                        confidence=0.98,
                    )
                )

        elif "500-0771" in part_lower or "lepton" in part_lower:
            if self._id == "SUPP-ROBU":
                offers.append(
                    SupplierOffer(
                        supplier_id=self._id,
                        supplier_name=self._name,
                        location=self._location,
                        bom_item_id=bom_item_id,
                        part_number="500-0771-01",
                        manufacturer="Teledyne FLIR",
                        unit_price=24500.0,
                        available_quantity=8,
                        minimum_order_quantity=1,
                        lead_time_days=2,
                        stock_status="in_stock",
                        source_url="https://robu.in/product/flir-lepton-3-5-thermal-camera-core/",
                        data_timestamp=timestamp,
                        confidence=0.98,
                    )
                )
            elif self._id == "SUPP-DIGIKEY":
                offers.append(
                    SupplierOffer(
                        supplier_id=self._id,
                        supplier_name=self._name,
                        location=self._location,
                        bom_item_id=bom_item_id,
                        part_number="500-0771-01",
                        manufacturer="Teledyne FLIR",
                        unit_price=23800.0,
                        available_quantity=25,
                        minimum_order_quantity=1,
                        lead_time_days=5,
                        stock_status="in_stock",
                        source_url="https://www.digikey.in/en/products/detail/flir-lepton/500-0771-01",
                        data_timestamp=timestamp,
                        confidence=0.98,
                    )
                )

        elif "esp32-s3" in part_lower:
            if self._id == "SUPP-ROBU":
                offers.append(
                    SupplierOffer(
                        supplier_id=self._id,
                        supplier_name=self._name,
                        location=self._location,
                        bom_item_id=bom_item_id,
                        part_number="ESP32-S3-WROOM-1-N8R8",
                        manufacturer="Espressif Systems",
                        unit_price=420.0,
                        available_quantity=120,
                        minimum_order_quantity=1,
                        price_breaks={1: 420.0, 10: 390.0, 50: 360.0},
                        lead_time_days=2,
                        stock_status="in_stock",
                        source_url="https://robu.in/product/esp32-s3-wroom-1-n8r8/",
                        data_timestamp=timestamp,
                        confidence=0.98,
                    )
                )
            elif self._id == "SUPP-PROBOTS":
                offers.append(
                    SupplierOffer(
                        supplier_id=self._id,
                        supplier_name=self._name,
                        location=self._location,
                        bom_item_id=bom_item_id,
                        part_number="ESP32-S3-WROOM-1-N8R8",
                        manufacturer="Espressif Systems",
                        unit_price=405.0,
                        available_quantity=45,
                        minimum_order_quantity=1,
                        price_breaks={1: 405.0, 10: 385.0},
                        lead_time_days=1,
                        stock_status="in_stock",
                        source_url="https://probots.co.in/esp32-s3-wroom-1-n8r8.html",
                        data_timestamp=timestamp,
                        confidence=0.96,
                    )
                )

        elif "tps565208" in part_lower:
            if self._id == "SUPP-MOUSER":
                offers.append(
                    SupplierOffer(
                        supplier_id=self._id,
                        supplier_name=self._name,
                        location=self._location,
                        bom_item_id=bom_item_id,
                        part_number="TPS565208DDCR",
                        manufacturer="Texas Instruments",
                        unit_price=85.0,
                        available_quantity=500,
                        minimum_order_quantity=5,  # MOQ = 5
                        lead_time_days=4,
                        stock_status="in_stock",
                        source_url="https://www.mouser.in/ProductDetail/Texas-Instruments/TPS565208DDCR",
                        data_timestamp=timestamp,
                        confidence=0.98,
                    )
                )
            elif self._id == "SUPP-ROBU":
                offers.append(
                    SupplierOffer(
                        supplier_id=self._id,
                        supplier_name=self._name,
                        location=self._location,
                        bom_item_id=bom_item_id,
                        part_number="TPS565208DDCR",
                        manufacturer="Texas Instruments",
                        unit_price=95.0,
                        available_quantity=60,
                        minimum_order_quantity=1,
                        lead_time_days=2,
                        stock_status="in_stock",
                        source_url="https://robu.in/product/tps565208-buck-regulator-ic/",
                        data_timestamp=timestamp,
                        confidence=0.95,
                    )
                )

        elif "ecas0d107" in part_lower or "capacitor" in category.lower():
            if self._id == "SUPP-MOUSER":
                offers.append(
                    SupplierOffer(
                        supplier_id=self._id,
                        supplier_name=self._name,
                        location=self._location,
                        bom_item_id=bom_item_id,
                        part_number="ECAS0D107M010K00",
                        manufacturer="Murata",
                        unit_price=45.0,
                        available_quantity=200,
                        minimum_order_quantity=10,  # MOQ = 10
                        lead_time_days=4,
                        stock_status="in_stock",
                        source_url="https://www.mouser.in/ProductDetail/Murata-Electronics/ECAS0D107M010K00",
                        data_timestamp=timestamp,
                        confidence=0.98,
                    )
                )

        elif "0297030" in part_lower or "fuse" in category.lower():
            if self._id == "SUPP-ROBU":
                offers.append(
                    SupplierOffer(
                        supplier_id=self._id,
                        supplier_name=self._name,
                        location=self._location,
                        bom_item_id=bom_item_id,
                        part_number="0297030.WXNV",
                        manufacturer="Littelfuse",
                        unit_price=25.0,
                        available_quantity=300,
                        minimum_order_quantity=1,
                        lead_time_days=2,
                        stock_status="in_stock",
                        source_url="https://robu.in/product/littelfuse-30a-blade-fuse/",
                        data_timestamp=timestamp,
                        confidence=0.98,
                    )
                )

        return offers
