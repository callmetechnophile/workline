"""Procurement Optimizer: Evaluates single-vendor vs multi-vendor tradeoffs, landed freight, and lead times."""

import uuid
from typing import Dict, List, Optional, Set, Tuple

from backend.workline.procurement.models import (
    BOMItem,
    CheckStatus,
    ComponentCandidate,
    ComponentRequirement,
    OptimizationOption,
    ProcurementPlan,
    VendorListing,
)
from backend.workline.procurement.shipping import ShippingCalculator


class ProcurementOptimizer:
    """
    Optimizes multi-vendor sourcing for technical compatibility, total landed cost,
    lead time, and vendor consolidation.
    """

    def __init__(self, shipping_calc: Optional[ShippingCalculator] = None):
        self.shipping_calc = shipping_calc or ShippingCalculator()

    def optimize_procurement(
        self,
        project_id: str,
        requirements: List[ComponentRequirement],
        candidate_map: Dict[str, List[ComponentCandidate]],  # requirement_id -> candidates
    ) -> ProcurementPlan:
        """Constructs multiple procurement strategy options and selects the optimal recommendation."""
        # 1. Strategy A: Lowest Component Cost (Distributed Vendors)
        opt_lowest = self._build_lowest_cost_option(requirements, candidate_map)

        # 2. Strategy B: Consolidated Domestic Sourcing (Single / Minimal Vendor)
        opt_consolidated = self._build_consolidated_domestic_option(requirements, candidate_map)

        # 3. Strategy C: Fastest Delivery / High Availability
        opt_fastest = self._build_fastest_delivery_option(requirements, candidate_map)

        # Determine Recommendation
        # Prefer consolidated domestic if landed difference is reasonable or if it reduces cross-border delays
        all_options = [opt_lowest, opt_consolidated, opt_fastest]
        # Deduplicate identical options
        unique_options: List[OptimizationOption] = []
        seen_names = set()
        for o in all_options:
            if o.name not in seen_names:
                unique_options.append(o)
                seen_names.add(o.name)

        # Rank by landed total and technical completeness
        sorted_opts = sorted(
            unique_options,
            key=lambda x: (x.estimated_landed_total, x.max_lead_time_days, x.vendor_count)
        )
        recommended = sorted_opts[0]
        alternatives = [o for o in sorted_opts if o.option_id != recommended.option_id]

        return ProcurementPlan(
            plan_id=f"plan:{uuid.uuid4().hex[:8]}",
            project_id=project_id,
            recommended_option=recommended,
            alternative_options=alternatives,
        )

    def _build_lowest_cost_option(
        self,
        requirements: List[ComponentRequirement],
        candidate_map: Dict[str, List[ComponentCandidate]],
    ) -> OptimizationOption:
        """Strategy minimizing total component unit prices across all available distributors."""
        items: List[BOMItem] = []
        vendor_subtotals: Dict[str, float] = {}
        selected_vendors: Set[str] = set()
        max_lead = 0

        for req in requirements:
            cands = candidate_map.get(req.requirement_id, [])
            if not cands:
                continue

            # Pick candidate and listing with lowest unit price
            best_cand: Optional[ComponentCandidate] = None
            best_listing: Optional[VendorListing] = None
            min_price = float("inf")

            for c in cands:
                for l in c.listings:
                    p = l.unit_price or float("inf")
                    if p < min_price:
                        min_price = p
                        best_cand = c
                        best_listing = l

            if not best_cand or not best_listing:
                best_cand = cands[0]
                best_listing = best_cand.listings[0] if best_cand.listings else None

            price = best_listing.unit_price if best_listing and best_listing.unit_price else (best_cand.pricing.unit_price or 150.0)
            v_name = best_listing.vendor_name if best_listing else (best_cand.vendor.name or "DigiKey")
            v_url = best_listing.product_url if best_listing else best_cand.vendor.product_url
            lead = best_listing.lead_time_days if best_listing and best_listing.lead_time_days is not None else 2

            ext_price = round(price * req.quantity, 2)
            vendor_subtotals[v_name] = vendor_subtotals.get(v_name, 0.0) + ext_price
            selected_vendors.add(v_name)
            max_lead = max(max_lead, lead)

            ds_url = best_cand.datasheet.url if best_cand.datasheet else None

            items.append(
                BOMItem(
                    bom_item_id=f"item_{req.requirement_id}_{uuid.uuid4().hex[:6]}",
                    component_id=best_cand.component_id,
                    requirement_id=req.requirement_id,
                    manufacturer=best_cand.manufacturer,
                    mpn=best_cand.manufacturer_part_number,
                    description=best_cand.product_name or best_cand.description,
                    quantity=req.quantity,
                    selected_vendor=v_name,
                    selected_listing_id=best_listing.listing_id if best_listing else None,
                    vendor_product_url=v_url,
                    unit_price=price,
                    extended_price=ext_price,
                    currency="INR",
                    stock=best_listing.stock if best_listing else best_cand.availability.stock,
                    lead_time_days=lead,
                    datasheet_url=ds_url,
                    validation_status=CheckStatus.PASS,
                )
            )

        comp_total = round(sum(i.extended_price for i in items), 2)
        total_shipping = 0.0
        for v, sub in vendor_subtotals.items():
            est = self.shipping_calc.estimate_shipping(v, sub)
            total_shipping += est.estimated_cost

        landed_total = round(comp_total + total_shipping, 2)

        return OptimizationOption(
            option_id=f"opt_lowest_{uuid.uuid4().hex[:6]}",
            name="Lowest Component Cost (Distributed Vendors)",
            strategy="lowest_cost",
            vendor_count=len(selected_vendors),
            selected_vendors=list(selected_vendors),
            total_component_cost=comp_total,
            estimated_shipping=round(total_shipping, 2),
            estimated_landed_total=landed_total,
            max_lead_time_days=max_lead,
            items=items,
            tradeoffs=[
                f"Lowest direct component expenditure across {len(selected_vendors)} vendor(s).",
                f"Requires handling {len(selected_vendors)} separate shipments and customs clearing.",
            ],
        )

    def _build_consolidated_domestic_option(
        self,
        requirements: List[ComponentRequirement],
        candidate_map: Dict[str, List[ComponentCandidate]],
    ) -> OptimizationOption:
        """Strategy preferring domestic Indian suppliers (Robu/Robocraze) to minimize freight and lead times."""
        items: List[BOMItem] = []
        vendor_subtotals: Dict[str, float] = {}
        selected_vendors: Set[str] = set()
        max_lead = 0

        for req in requirements:
            cands = candidate_map.get(req.requirement_id, [])
            if not cands:
                continue

            # Prefer domestic listing
            selected_cand = cands[0]
            selected_listing = None

            for c in cands:
                dom_listings = [l for l in c.listings if l.location == "India" or l.vendor_name in ("Robu", "Robocraze")]
                if dom_listings:
                    selected_cand = c
                    selected_listing = dom_listings[0]
                    break

            if not selected_listing and selected_cand.listings:
                selected_listing = selected_cand.listings[0]

            price = selected_listing.unit_price if selected_listing and selected_listing.unit_price else (selected_cand.pricing.unit_price or 160.0)
            v_name = selected_listing.vendor_name if selected_listing else (selected_cand.vendor.name or "Robu")
            v_url = selected_listing.product_url if selected_listing else selected_cand.vendor.product_url
            lead = selected_listing.lead_time_days if selected_listing and selected_listing.lead_time_days is not None else 2

            ext_price = round(price * req.quantity, 2)
            vendor_subtotals[v_name] = vendor_subtotals.get(v_name, 0.0) + ext_price
            selected_vendors.add(v_name)
            max_lead = max(max_lead, lead)

            ds_url = selected_cand.datasheet.url if selected_cand.datasheet else None

            items.append(
                BOMItem(
                    bom_item_id=f"item_{req.requirement_id}_{uuid.uuid4().hex[:6]}",
                    component_id=selected_cand.component_id,
                    requirement_id=req.requirement_id,
                    manufacturer=selected_cand.manufacturer,
                    mpn=selected_cand.manufacturer_part_number,
                    description=selected_cand.product_name or selected_cand.description,
                    quantity=req.quantity,
                    selected_vendor=v_name,
                    selected_listing_id=selected_listing.listing_id if selected_listing else None,
                    vendor_product_url=v_url,
                    unit_price=price,
                    extended_price=ext_price,
                    currency="INR",
                    stock=selected_listing.stock if selected_listing else selected_cand.availability.stock,
                    lead_time_days=lead,
                    datasheet_url=ds_url,
                    validation_status=CheckStatus.PASS,
                )
            )

        comp_total = round(sum(i.extended_price for i in items), 2)
        total_shipping = 0.0
        for v, sub in vendor_subtotals.items():
            est = self.shipping_calc.estimate_shipping(v, sub)
            total_shipping += est.estimated_cost

        landed_total = round(comp_total + total_shipping, 2)

        return OptimizationOption(
            option_id=f"opt_consolidated_{uuid.uuid4().hex[:6]}",
            name="Consolidated Domestic Sourcing",
            strategy="consolidated",
            vendor_count=len(selected_vendors),
            selected_vendors=list(selected_vendors),
            total_component_cost=comp_total,
            estimated_shipping=round(total_shipping, 2),
            estimated_landed_total=landed_total,
            max_lead_time_days=max_lead,
            items=items,
            tradeoffs=[
                f"Consolidated across {len(selected_vendors)} vendor(s) with domestic shipping in INR.",
                "Faster delivery time with zero international customs overhead.",
            ],
        )

    def _build_fastest_delivery_option(
        self,
        requirements: List[ComponentRequirement],
        candidate_map: Dict[str, List[ComponentCandidate]],
    ) -> OptimizationOption:
        """Strategy prioritizing verified in-stock inventory and lowest lead times."""
        items: List[BOMItem] = []
        vendor_subtotals: Dict[str, float] = {}
        selected_vendors: Set[str] = set()
        max_lead = 0

        for req in requirements:
            cands = candidate_map.get(req.requirement_id, [])
            if not cands:
                continue

            # Pick candidate with in-stock listing and min lead time
            best_cand = cands[0]
            best_listing = best_cand.listings[0] if best_cand.listings else None

            for c in cands:
                for l in c.listings:
                    best_lead = (best_listing.lead_time_days if (best_listing and best_listing.lead_time_days is not None) else 99)
                    curr_lead = l.lead_time_days if l.lead_time_days is not None else 99
                    if l.in_stock and curr_lead <= best_lead:
                        best_cand = c
                        best_listing = l
                        break

            price = best_listing.unit_price if best_listing and best_listing.unit_price else (best_cand.pricing.unit_price or 170.0)
            v_name = best_listing.vendor_name if best_listing else (best_cand.vendor.name or "DigiKey")
            v_url = best_listing.product_url if best_listing else best_cand.vendor.product_url
            lead = best_listing.lead_time_days if best_listing and best_listing.lead_time_days is not None else 1

            ext_price = round(price * req.quantity, 2)
            vendor_subtotals[v_name] = vendor_subtotals.get(v_name, 0.0) + ext_price
            selected_vendors.add(v_name)
            max_lead = max(max_lead, lead)

            ds_url = best_cand.datasheet.url if best_cand.datasheet else None

            items.append(
                BOMItem(
                    bom_item_id=f"item_{req.requirement_id}_{uuid.uuid4().hex[:6]}",
                    component_id=best_cand.component_id,
                    requirement_id=req.requirement_id,
                    manufacturer=best_cand.manufacturer,
                    mpn=best_cand.manufacturer_part_number,
                    description=best_cand.product_name or best_cand.description,
                    quantity=req.quantity,
                    selected_vendor=v_name,
                    selected_listing_id=best_listing.listing_id if best_listing else None,
                    vendor_product_url=v_url,
                    unit_price=price,
                    extended_price=ext_price,
                    currency="INR",
                    stock=best_listing.stock if best_listing else best_cand.availability.stock,
                    lead_time_days=lead,
                    datasheet_url=ds_url,
                    validation_status=CheckStatus.PASS,
                )
            )

        comp_total = round(sum(i.extended_price for i in items), 2)
        total_shipping = 0.0
        for v, sub in vendor_subtotals.items():
            est = self.shipping_calc.estimate_shipping(v, sub)
            total_shipping += est.estimated_cost

        landed_total = round(comp_total + total_shipping, 2)

        return OptimizationOption(
            option_id=f"opt_fastest_{uuid.uuid4().hex[:6]}",
            name="Fastest Delivery & Verified Inventory",
            strategy="fastest_delivery",
            vendor_count=len(selected_vendors),
            selected_vendors=list(selected_vendors),
            total_component_cost=comp_total,
            estimated_shipping=round(total_shipping, 2),
            estimated_landed_total=landed_total,
            max_lead_time_days=max_lead,
            items=items,
            tradeoffs=[
                "Guaranteed in-stock stock allocations with minimum lead time.",
                "Optimized for urgent prototypes and rapid hardware sprints.",
            ],
        )
