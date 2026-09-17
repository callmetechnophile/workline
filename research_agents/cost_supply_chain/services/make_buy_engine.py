"""
Make-versus-Buy breakeven modeling and decision analysis engine.
"""

from typing import Optional
from research_agents.cost_supply_chain.schemas import (
    MakeBuyRecommendation,
    MakeVsBuyAnalysis,
)


class MakeBuyEngine:
    """Calculates volume breakeven crossover and recommends sourcing strategy."""

    def evaluate(
        self,
        analysis_id: str,
        part_id: str,
        part_name: str,
        make_unit_cost: float,
        make_tooling_nre: float,
        buy_unit_cost: float,
        buy_tooling_nre: float = 0.0,
        target_volume: int = 1000,
    ) -> MakeVsBuyAnalysis:
        delta_nre = make_tooling_nre - buy_tooling_nre
        delta_unit = buy_unit_cost - make_unit_cost

        breakeven: Optional[float] = None
        recommendation: MakeBuyRecommendation = MakeBuyRecommendation.DATA_REQUIRED
        rationale: str = ""

        if delta_unit > 0:
            if delta_nre > 0:
                breakeven = round(delta_nre / delta_unit, 1)
                if target_volume >= breakeven:
                    recommendation = MakeBuyRecommendation.MAKE
                    rationale = (
                        f"Target volume ({target_volume}) exceeds breakeven threshold ({breakeven} units). "
                        f"Internal manufacturing saves ${(delta_unit):.2f} per unit after amortizing "
                        f"${delta_nre:.2f} tooling NRE."
                    )
                else:
                    recommendation = MakeBuyRecommendation.BUY
                    rationale = (
                        f"Target volume ({target_volume}) is below breakeven threshold ({breakeven} units). "
                        f"Commercial off-the-shelf or external purchasing avoids ${make_tooling_nre:.2f} capital tooling risk."
                    )
            else:
                breakeven = 0.0
                recommendation = MakeBuyRecommendation.MAKE
                rationale = "Internal fabrication strictly dominates: lower unit cost and lower tooling NRE."
        else:
            if delta_nre <= 0:
                breakeven = 0.0
                recommendation = MakeBuyRecommendation.BUY
                rationale = "Commercial procurement strictly dominates: lower unit cost and lower tooling NRE."
            else:
                recommendation = MakeBuyRecommendation.BUY
                rationale = "External supplier offers lower recurring unit cost."

        return MakeVsBuyAnalysis(
            analysis_id=analysis_id,
            part_id=part_id,
            part_name=part_name,
            make_unit_cost=round(make_unit_cost, 2),
            make_tooling_nre=round(make_tooling_nre, 2),
            buy_unit_cost=round(buy_unit_cost, 2),
            buy_tooling_nre=round(buy_tooling_nre, 2),
            breakeven_volume=breakeven,
            target_volume=target_volume,
            recommendation=recommendation,
            rationale=rationale,
        )
