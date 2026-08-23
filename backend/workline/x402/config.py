"""
Algorand x402 Centralized Configuration for Workline AI.
Manages network parameters, asset IDs, treasury addresses, and facilitator URLs.
"""

import os
from pydantic import BaseModel, Field


class X402Config(BaseModel):
    """Centralized configuration for Workline x402 service monetization."""

    # Network: 'algorand-mainnet' or 'algorand-testnet'
    network: str = Field(
        default_factory=lambda: os.getenv("WORKLINE_X402_NETWORK", "algorand-mainnet")
    )

    # Asset: Always USDC on Algorand
    asset: str = Field(
        default_factory=lambda: os.getenv("WORKLINE_X402_ASSET", "USDC")
    )

    # Asset ID: Mainnet USDC = 31566704, Testnet USDC = 10458941
    asset_id: int = Field(
        default_factory=lambda: int(
            os.getenv(
                "WORKLINE_X402_ASSET_ID",
                "31566704" if os.getenv("WORKLINE_X402_NETWORK", "algorand-mainnet") == "algorand-mainnet" else "10458941",
            )
        )
    )

    # Workline Treasury Pay-To Algorand Wallet Address (58-character public address)
    pay_to: str = Field(
        default_factory=lambda: os.getenv(
            "WORKLINE_X402_PAY_TO",
            os.getenv(
                "WORKLINE_X402_PAYMENT_ADDRESS",
                "WORKLINE24EUSDCALGORANDTREASURYRECIPIENT402XXXXXXXXXXXXXX",
            ),
        )
    )

    # GoPlausible x402 Facilitator API URL
    facilitator_url: str = Field(
        default_factory=lambda: os.getenv(
            "WORKLINE_X402_FACILITATOR_URL",
            "https://facilitator.goplausible.com",
        )
    )

    # Challenge Time-To-Live in minutes
    challenge_ttl_minutes: int = Field(
        default_factory=lambda: int(os.getenv("WORKLINE_X402_TTL_MINUTES", "30"))
    )

    # Feature flag to enable/disable x402 enforcement
    enabled: bool = Field(
        default_factory=lambda: os.getenv("WORKLINE_X402_ENABLED", "true").lower()
        in ("true", "1", "yes")
    )

    # Mode: 'production', 'testnet', 'local'
    mode: str = Field(
        default_factory=lambda: os.getenv("WORKLINE_X402_MODE", "production")
    )


# Singleton configuration instance
x402_config = X402Config()
