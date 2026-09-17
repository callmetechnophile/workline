"""Tests for Make-vs-Buy breakeven engine."""
from research_agents.cost_supply_chain.schemas import MakeBuyRecommendation
from research_agents.cost_supply_chain.services.make_buy_engine import MakeBuyEngine


def test_make_buy_crossover():
    engine = MakeBuyEngine()
    # Make: $20 unit + $10,000 NRE
    # Buy: $30 unit + $0 NRE
    # Delta unit = $10. Breakeven = 10000 / 10 = 1000 units.
    res_at_2000 = engine.evaluate("MB-1", "P1", "Bracket", 20.0, 10000.0, 30.0, 0.0, target_volume=2000)
    assert res_at_2000.breakeven_volume == 1000.0
    assert res_at_2000.recommendation == MakeBuyRecommendation.MAKE

    res_at_500 = engine.evaluate("MB-1", "P1", "Bracket", 20.0, 10000.0, 30.0, 0.0, target_volume=500)
    assert res_at_500.recommendation == MakeBuyRecommendation.BUY


def test_make_buy_domination():
    engine = MakeBuyEngine()
    # Buy is strictly cheaper in unit cost AND has zero tooling
    res = engine.evaluate("MB-2", "P2", "Bolt", 2.0, 500.0, 1.0, 0.0, target_volume=1000)
    assert res.recommendation == MakeBuyRecommendation.BUY
