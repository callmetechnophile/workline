"""BOM and Procurement Intelligence Service."""

import threading
import time
from typing import Dict, List, Optional, Tuple
from backend.workline.procurement.models import (
    BillOfMaterials,
    BomItem,
    BomStatus,
    PartVariant,
    ProcurementPackage,
    ProcurementPackageItem,
    ProcurementStatus,
    QuantityBreak,
    SupplierBreakdown,
    SupplierOffer,
)
from backend.workline.procurement.part_resolver import PartResolver
from backend.workline.procurement.pricing import PriceCalculator


class ProcurementIntelligenceService:
    """Service managing Bill of Materials, supplier aggregation, and procurement packages."""

    def __init__(self):
        self._lock = threading.RLock()
        self._boms: Dict[str, BillOfMaterials] = {}
        self._bom_history: Dict[str, List[BillOfMaterials]] = {}
        self._supplier_catalog: Dict[str, List[SupplierOffer]] = {}
        self._init_mock_catalog()

    def _init_mock_catalog(self):
        """Seed supplier catalog for deterministic unit testing."""
        self._supplier_catalog["TPS62130"] = [
            SupplierOffer(
                supplier_id="digikey",
                supplier_item_id="296-30232-1-ND",
                manufacturer="Texas Instruments",
                part_number="TPS62130",
                ordering_code="TPS62130RGTR",
                description="IC REG BUCK 3.3V 3A 16QFN",
                package="VQFN-16",
                unit_price=180.0,
                currency="INR",
                quantity_breaks=[
                    QuantityBreak(quantity=1, unit_price=180.0),
                    QuantityBreak(quantity=10, unit_price=160.0),
                    QuantityBreak(quantity=100, unit_price=140.0),
                ],
                stock=500,
                lead_time_days=3,
                moq=1,
                source="digikey",
                confidence="HIGH",
            ),
            SupplierOffer(
                supplier_id="mouser",
                supplier_item_id="595-TPS62130RGTR",
                manufacturer="Texas Instruments",
                part_number="TPS62130",
                ordering_code="TPS62130RGTR",
                description="Switching Voltage Regulators 3-17V 3A Step-Down",
                package="VQFN-16",
                unit_price=175.0,
                currency="INR",
                quantity_breaks=[
                    QuantityBreak(quantity=1, unit_price=175.0),
                    QuantityBreak(quantity=10, unit_price=155.0),
                ],
                stock=120,
                lead_time_days=5,
                moq=1,
                source="mouser",
                confidence="HIGH",
            ),
        ]
        self._supplier_catalog["LM2596"] = [
            SupplierOffer(
                supplier_id="robu",
                supplier_item_id="ROBU-LM2596-5",
                manufacturer="Texas Instruments",
                part_number="LM2596",
                ordering_code="LM2596S-5.0/NOPB",
                description="Simple Switcher 3A Step-Down Regulator",
                package="TO-263-5",
                unit_price=65.0,
                currency="INR",
                quantity_breaks=[
                    QuantityBreak(quantity=1, unit_price=65.0),
                    QuantityBreak(quantity=5, unit_price=58.0),
                ],
                stock=350,
                lead_time_days=2,
                moq=1,
                source="robu",
                confidence="HIGH",
            )
        ]

    def create_bom(
        self,
        bom_id: str,
        project_id: str,
        team_id: str = "default_team",
        source_decisions: Optional[List[str]] = None,
    ) -> BillOfMaterials:
        with self._lock:
            bom = BillOfMaterials(
                bom_id=bom_id,
                project_id=project_id,
                team_id=team_id,
                version=1,
                status=BomStatus.DRAFT,
                source_decisions=source_decisions or [],
                items=[],
                currency="INR",
                estimated_total=0.0,
            )
            self._boms[bom_id] = bom
            self._bom_history[bom_id] = [bom]
            return bom

    def get_bom(self, bom_id: str) -> Optional[BillOfMaterials]:
        with self._lock:
            return self._boms.get(bom_id)

    def list_boms(self, project_id: Optional[str] = None) -> List[BillOfMaterials]:
        with self._lock:
            if project_id:
                return [b for b in self._boms.values() if b.project_id == project_id]
            return list(self._boms.values())

    def add_bom_item(
        self,
        bom_id: str,
        reference_designator: str,
        part_number: str,
        quantity: int = 1,
        description: str = "",
        manufacturer: str = "",
        component_entity_id: str = "",
    ) -> BomItem:
        with self._lock:
            bom = self._boms.get(bom_id)
            if not bom:
                raise ValueError(f"BOM '{bom_id}' not found.")

            # Resolve ordering code and package
            resolved, exact_match, variants, is_ambiguous = PartResolver.resolve(part_number)
            ordering_code = exact_match.ordering_code if exact_match else (variants[0].ordering_code if variants else part_number)
            pkg = exact_match.package if exact_match else (variants[0].package if variants else "Standard")
            mfg = manufacturer or (exact_match.manufacturer if exact_match else "Generic")

            # Look up supplier offers
            offers = self.get_offers(part_number)
            selected_offer = offers[0] if offers else None

            status = ProcurementStatus.RESOLVED if resolved else (ProcurementStatus.AMBIGUOUS if is_ambiguous else ProcurementStatus.UNRESOLVED)
            stock = selected_offer.stock if selected_offer else 0
            unit_price = PriceCalculator.get_unit_price(selected_offer, quantity) if selected_offer else 0.0

            item = BomItem(
                bom_item_id=f"BOMI-{int(time.time()*1000)}",
                bom_id=bom_id,
                reference_designator=reference_designator,
                description=description or f"Part {part_number}",
                component_entity_id=component_entity_id or f"comp_{part_number.lower()}",
                part_number=part_number,
                manufacturer=mfg,
                ordering_code=ordering_code,
                package=pkg,
                quantity=quantity,
                required_quantity=quantity,
                selected_supplier=selected_offer.supplier_id if selected_offer else None,
                supplier_item_id=selected_offer.supplier_item_id if selected_offer else None,
                unit_price=unit_price,
                stock=stock,
                lead_time_days=selected_offer.lead_time_days if selected_offer else None,
                moq=selected_offer.moq if selected_offer else 1,
                status=status,
                confidence="HIGH" if resolved and selected_offer else "MEDIUM",
            )

            bom.items.append(item)
            self._recalculate_totals(bom)
            return item

    def get_offers(self, part_number: str) -> List[SupplierOffer]:
        with self._lock:
            return self._supplier_catalog.get(part_number.upper(), [])

    def validate_bom(self, bom_id: str) -> Tuple[BomStatus, List[str]]:
        with self._lock:
            bom = self._boms.get(bom_id)
            if not bom:
                raise ValueError(f"BOM '{bom_id}' not found.")

            issues: List[str] = []
            for item in bom.items:
                if not item.ordering_code:
                    issues.append(f"{item.reference_designator}: Ordering code unresolved")
                if not item.selected_supplier:
                    issues.append(f"{item.reference_designator}: Missing supplier offer")
                elif item.stock < item.quantity:
                    issues.append(f"{item.reference_designator}: Insufficient supplier stock ({item.stock} < {item.quantity})")
                if item.quantity < item.moq:
                    issues.append(f"{item.reference_designator}: Quantity below supplier MOQ ({item.quantity} < {item.moq})")

            if issues:
                bom.status = BomStatus.BLOCKED
            else:
                bom.status = BomStatus.READY_FOR_PROCUREMENT

            bom.updated_at = time.time()
            return bom.status, issues

    def generate_procurement_package(self, bom_id: str) -> ProcurementPackage:
        with self._lock:
            bom = self._boms.get(bom_id)
            if not bom:
                raise ValueError(f"BOM '{bom_id}' not found.")

            status, issues = self.validate_bom(bom_id)
            if status != BomStatus.READY_FOR_PROCUREMENT:
                raise ValueError(f"BOM '{bom_id}' is BLOCKED or INCOMPLETE: {', '.join(issues)}")

            pkg_items: List[ProcurementPackageItem] = []
            supplier_counts: Dict[str, Dict[str, Any]] = {}

            for item in bom.items:
                line_total = round((item.unit_price or 0.0) * item.quantity, 2)
                p_item = ProcurementPackageItem(
                    manufacturer=item.manufacturer,
                    part_number=item.part_number,
                    ordering_code=item.ordering_code,
                    supplier=item.selected_supplier or "unknown",
                    supplier_item_id=item.supplier_item_id or "",
                    quantity=item.quantity,
                    unit_price=item.unit_price or 0.0,
                    currency=item.currency,
                    estimated_total=line_total,
                    stock=item.stock,
                    lead_time_days=item.lead_time_days,
                    moq=item.moq,
                    validation_status="VALID",
                )
                pkg_items.append(p_item)

                sup = item.selected_supplier or "unknown"
                if sup not in supplier_counts:
                    supplier_counts[sup] = {"count": 0, "total": 0.0}
                supplier_counts[sup]["count"] += 1
                supplier_counts[sup]["total"] += line_total

            breakdowns = [
                SupplierBreakdown(supplier_id=k, item_count=v["count"], subtotal=round(v["total"], 2))
                for k, v in supplier_counts.items()
            ]

            pkg = ProcurementPackage(
                package_id=f"PKG-{int(time.time()*1000)}",
                project_id=bom.project_id,
                team_id=bom.team_id,
                bom_id=bom.bom_id,
                bom_version=bom.version,
                items=pkg_items,
                subtotal=bom.estimated_total,
                currency=bom.currency,
                supplier_breakdown=breakdowns,
                validation_status="READY",
            )
            return pkg

    def _recalculate_totals(self, bom: BillOfMaterials):
        total = sum((item.unit_price or 0.0) * item.quantity for item in bom.items)
        bom.estimated_total = round(total, 2)
        bom.updated_at = time.time()


# Global singleton
procurement_service = ProcurementIntelligenceService()
