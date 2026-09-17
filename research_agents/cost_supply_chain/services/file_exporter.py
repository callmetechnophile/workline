"""
JSON and CSV export utilities for Agent #25 cost artifacts.
"""

import csv
import io
import json
from research_agents.cost_supply_chain.schemas import BOMCostRollup, SupplyRisk


class FileExporter:
    """Exports cost data to standard data exchange formats."""

    def to_json(self, rollup: BOMCostRollup) -> str:
        return json.dumps(rollup.model_dump(), indent=2)

    def to_csv_bom(self, rollup: BOMCostRollup) -> str:
        out = io.StringIO()
        writer = csv.writer(out)
        writer.writerow([
            "Part ID", "Part Name", "Qty", "Unit Cost", "Currency",
            "Extended Cost", "Price Status", "Lead Time (wks)", "MOQ", "Lifecycle Status"
        ])
        for p in rollup.parts_cost_breakdown:
            ext = round((p.unit_cost or 0.0) * p.quantity_per_assembly, 2) if p.unit_cost else "N/A"
            writer.writerow([
                p.part_id,
                p.part_name,
                p.quantity_per_assembly,
                p.unit_cost if p.unit_cost is not None else "PRICE_UNKNOWN",
                p.currency,
                ext,
                p.price_status,
                p.lead_time_weeks if p.lead_time_weeks is not None else "N/A",
                p.moq if p.moq is not None else "N/A",
                p.lifecycle_status.value,
            ])
        return out.getvalue()
