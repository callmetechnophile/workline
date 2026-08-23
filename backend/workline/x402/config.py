"""
Algorand x402 Centralized Configuration for Workline AI.
Manages network parameters, asset IDs, treasury addresses, and facilitator URLs.
"""

import os
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field



class X402Config(BaseModel):
    """Centralized configuration for Workline x402 service monetization on Algorand."""

    # Network: 'algorand-testnet' or 'algorand-mainnet'
    network: str = Field(
        default_factory=lambda: (
            "algorand-testnet"
            if os.getenv("X402_NETWORK", os.getenv("WORKLINE_X402_NETWORK", "testnet")).lower() in ("testnet", "algorand-testnet")
            else "algorand-mainnet"
        )
    )

    # Asset: Always USDC on Algorand
    asset: str = Field(
        default_factory=lambda: os.getenv("X402_ASSET", os.getenv("WORKLINE_X402_ASSET", "USDC"))
    )

    # Asset ID: Testnet USDC = 10458941, Mainnet USDC = 31566704
    asset_id: int = Field(
        default_factory=lambda: int(
            os.getenv(
                "X402_ASSET_ID",
                os.getenv(
                    "WORKLINE_X402_ASSET_ID",
                    "10458941" if "testnet" in os.getenv("X402_NETWORK", os.getenv("WORKLINE_X402_NETWORK", "testnet")).lower() else "31566704",
                ),
            )
        )
    )

    # Workline Treasury Pay-To Algorand Wallet Address (58-character public address)
    pay_to: str = Field(
        default_factory=lambda: os.getenv(
            "X402_PAY_TO",
            os.getenv(
                "WORKLINE_X402_PAY_TO",
                os.getenv(
                    "WORKLINE_X402_PAYMENT_ADDRESS",
                    "WORKLINE24EUSDCALGORANDTREASURYRECIPIENT402TESTNETADDRXXXX",
                ),
            ),
        )
    )

    # Test Service Price in USDC
    test_price_usdc: float = Field(
        default_factory=lambda: float(
            os.getenv("X402_PRICE_USDC", os.getenv("WORKLINE_X402_PRICE_USDC", "0.01"))
        )
    )

    # GoPlausible x402 Facilitator API URL
    facilitator_url: str = Field(
        default_factory=lambda: os.getenv(
            "X402_FACILITATOR_URL",
            os.getenv(
                "WORKLINE_X402_FACILITATOR_URL",
                "https://facilitator.goplausible.xyz",
            ),
        )
    )

    # Algorand Node & Indexer URLs
    algod_url: str = Field(
        default_factory=lambda: os.getenv(
            "ALGORAND_NODE_URL",
            os.getenv("ALGOD_URL", "https://testnet-api.algonode.cloud"),
        )
    )
    indexer_url: str = Field(
        default_factory=lambda: os.getenv(
            "ALGORAND_INDEXER_URL",
            os.getenv("INDEXER_URL", "https://testnet-idx.algonode.cloud"),
        )
    )

    # Challenge Time-To-Live in minutes
    challenge_ttl_minutes: int = Field(
        default_factory=lambda: int(os.getenv("X402_TTL_MINUTES", os.getenv("WORKLINE_X402_TTL_MINUTES", "30")))
    )

    # Feature flag to enable/disable x402 enforcement
    enabled: bool = Field(
        default_factory=lambda: os.getenv("X402_ENABLED", os.getenv("WORKLINE_X402_ENABLED", "true")).lower()
        in ("true", "1", "yes")
    )

    # Mode: 'testnet', 'production', 'local'
    mode: str = Field(
        default_factory=lambda: os.getenv("X402_MODE", os.getenv("WORKLINE_X402_MODE", "testnet"))
    )

    def validate_environment(self) -> Dict[str, Any]:
        """Validates critical x402 parameters on startup."""
        missing = []
        if not self.facilitator_url:
            missing.append("X402_FACILITATOR_URL")
        if not self.pay_to:
            missing.append("X402_PAY_TO")
        if not self.network:
            missing.append("X402_NETWORK")
        return {
            "valid": len(missing) == 0,
            "missing_variables": missing,
            "network": self.network,
            "asset_id": self.asset_id,
            "asset": self.asset,
            "pay_to": self.pay_to,
            "facilitator_url": self.facilitator_url,
            "test_price_usdc": self.test_price_usdc,
        }


# Singleton configuration instance
x402_config = X402Config()
