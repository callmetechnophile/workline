"""
Configuration settings, exchange rates, risk thresholds, and constants for Agent #25.
Cost & Supply Chain Agent (CostSupplyChainAgent / agent.25).
"""

import os
from typing import Dict
from pydantic import BaseModel, Field


# Zero-Fabrication Sentinel Constants
PRICE_UNKNOWN: str = "PRICE_UNKNOWN"
LEAD_TIME_UNKNOWN: str = "LEAD_TIME_UNKNOWN"
MOQ_UNKNOWN: str = "MOQ_UNKNOWN"
FX_UNKNOWN: str = "FX_UNKNOWN"
DATA_REQUIRED: str = "DATA_REQUIRED"


class CurrencyConfig(BaseModel):
    """Supported currencies and baseline exchange rates relative to 1.0 USD."""

    base_currency: str = "USD"
    # Exchange rate: 1 unit of foreign currency = X USD
    exchange_rates_to_usd: Dict[str, float] = Field(
        default_factory=lambda: {
            "USD": 1.0,
            "EUR": 1.08,
            "GBP": 1.28,
            "JPY": 0.0067,
            "INR": 0.012,
            "CAD": 0.74,
            "AUD": 0.65,
            "CNY": 0.14,
            "CHF": 1.13,
            "KRW": 0.00075,
            "TWD": 0.031,
            "SGD": 0.75,
            "MXN": 0.058,
        }
    )


class RiskThresholds(BaseModel):
    """Supply chain risk thresholds and trigger rules."""

    lead_time_warning_weeks: float = 16.0
    lead_time_critical_weeks: float = 26.0
    high_moq_ratio_threshold: float = 2.0  # MOQ / Target Batch Volume
    single_source_cost_threshold: float = 1000.0  # Part value where single-sourcing is high risk
    currency_fluctuation_buffer_pct: float = 5.0
    obsolescence_horizon_years: float = 3.0


class CostSupplyChainConfig(BaseModel):
    """Master configuration for Agent #25."""

    agent_id: str = "Agent #25"
    agent_name: str = "CostSupplyChainAgent"
    version: str = "1.0.0"
    default_currency: str = "USD"
    currencies: CurrencyConfig = Field(default_factory=CurrencyConfig)
    risk_thresholds: RiskThresholds = Field(default_factory=RiskThresholds)
    default_target_volume: int = 1000
    model_id: str = os.getenv(
        "BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0"
    )
    aws_region: str = os.getenv("AWS_DEFAULT_REGION", "us-east-1")


config = CostSupplyChainConfig()
