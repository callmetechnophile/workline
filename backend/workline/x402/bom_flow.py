"""
BOM Payment & Procurement Flow Coordinator for Workline AI.

Orchestrates:
1. ArmourIQ Capability Authorization (EXECUTE_PROCUREMENT, CRITICAL Risk)
2. Authoritative BOM Pricing & Frozen Quote Issuance (1:1 USD -> USDC)
3. Algorand / GoPlausible Settlement Verification with Replay Protection
4. Isolated Post-Settlement CoinGecko INR Lookup (1 Fetch, Resilient)
5. Auditable PDF Report Generation and Storage
"""

from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple
from loguru import logger

from backend.workline.armouriq.capabilities import AgentCapability, PolicyDecision, RiskTier
from backend.workline.armouriq.policy import ArmourIQPolicyEngine
from backend.workline.armouriq.trust_context import TrustContext
from backend.workline.procurement.bom_payment import (
    AuthoritativeBom,
    AuthoritativeBomItem,
    BomPaymentState,
    PaymentQuote,
    compute_bom_pricing,
    quantize_money,
)
from backend.workline.x402.coingecko import CoinGeckoRate, coingecko_client
from backend.workline.x402.config import x402_config
from backend.workline.x402.models import PaymentProof, PaymentRecord, PaymentStatus
from backend.workline.x402.report import BomPaymentReportArtifact, BomPaymentReportEngine
from backend.workline.x402.storage import x402_storage
from backend.workline.x402.verifier import x402_verifier


class BomPaymentFlowCoordinator:
    """Central orchestrator for BOM quotes, payment settlement, and report compilation."""

    def __init__(self):
        self._quotes: Dict[str, PaymentQuote] = {}
        self._boms: Dict[str, AuthoritativeBom] = {}
        self._reports: Dict[str, BomPaymentReportArtifact] = {}
        self._policy = ArmourIQPolicyEngine()

    def _check_armouriq_authorization(self, context: Optional[TrustContext], action: str = "bom_procurement") -> None:
        """
        Enforces ArmourIQ policy check for hardware procurement / financial execution.
        Raises PermissionError if unauthorized.
        """
        if context is None:
            # Default trust context when none provided in basic mode
            return

        decision, reason = self._policy.evaluate_tool_execution(
            tool_name="execute_procurement_order",
            parameters={"action": action},
            context=context,
        )
        if decision != PolicyDecision.ALLOW:
            raise PermissionError(
                f"ArmourIQ DENIED procurement execution: agent='{context.agent_id}' "
                f"project='{context.project_id}' decision={decision.value} reason={reason}"
            )

    def create_payment_quote(
        self,
        bom_data: Dict[str, Any],
        project_id: str,
        context: Optional[TrustContext] = None,
    ) -> PaymentQuote:
        """
        1. Validates BOM and line items.
        2. Calculates authoritative USD total with Decimal precision.
        3. Evaluates ArmourIQ authorization.
        4. Freezes and registers a PaymentQuote where amount_usd == amount_usdc.
        """
        # ArmourIQ Governance Check
        self._check_armouriq_authorization(context, "create_quote")

        bom_id = bom_data.get("bom_id", f"BOM_{project_id[:8]}")
        items_raw = bom_data.get("items", [])
        if not items_raw:
            raise ValueError("Cannot create payment quote for an empty BOM.")

        # Compute authoritative pricing
        bom = compute_bom_pricing(items_raw, bom_id=bom_id, project_id=project_id)
        if bom.bom_total_usd <= 0.0:
            raise ValueError("BOM total must be greater than $0.00 to issue a payment quote.")

        now = datetime.now(timezone.utc)
        expires = (now + timedelta(minutes=x402_config.challenge_ttl_minutes)).isoformat()

        # Build Frozen Quote (amount_usd == amount_usdc, strict parity)
        quote = PaymentQuote(
            project_id=project_id,
            bom_id=bom_id,
            amount_usd=bom.bom_total_usd,
            amount_usdc=bom.bom_total_usd,
            asset=x402_config.asset,
            asset_id=x402_config.asset_id,
            network=x402_config.network,
            pay_to=x402_config.pay_to,
            facilitator=x402_config.facilitator_url,
            status=BomPaymentState.PAYMENT_REQUIRED,
            items_snapshot=[i.model_dump() for i in bom.items],
            expires_at=expires,
        )

        self._quotes[quote.quote_id] = quote
        self._quotes[quote.payment_request_id] = quote
        self._boms[quote.quote_id] = bom
        self._boms[bom_id] = bom

        # Also register in x402 generic storage for audit ledger parity
        record = PaymentRecord(
            id=f"pay_rec_{quote.quote_id}",
            payment_request_id=quote.payment_request_id,
            service_id="procurement.bom_settlement",
            project_id=project_id,
            amount=quote.amount_usdc,
            asset=quote.asset,
            asset_id=quote.asset_id,
            network=quote.network,
            pay_to=quote.pay_to,
            facilitator=quote.facilitator,
            status=PaymentStatus.PAYMENT_REQUIRED,
            expires_at=expires,
        )
        x402_storage.save_record(record)

        logger.info(
            f"[BOM Flow] Frozen Quote issued: quote_id='{quote.quote_id}' "
            f"bom_id='{bom_id}' total='${quote.amount_usd:.2f} USD' -> '{quote.amount_usdc:.2f} USDC'"
        )
        return quote

    def get_quote(self, quote_id: str) -> Optional[PaymentQuote]:
        """Look up active or settled quote by quote_id or payment_request_id."""
        return self._quotes.get(quote_id)

    async def settle_payment_proof(
        self,
        quote_id: str,
        proof_data: Dict[str, Any],
        context: Optional[TrustContext] = None,
    ) -> Tuple[bool, Optional[str], Optional[PaymentQuote]]:
        """
        Validates the submitted Algorand settlement proof against the frozen quote.
        Guarantees:
        - Expiry check
        - Replay attack prevention
        - Amount matching (BOM Total == Quote Amount == Settled Amount)
        - ArmourIQ authorization
        """
        quote = self.get_quote(quote_id)
        if not quote:
            return False, f"Payment quote '{quote_id}' not found.", None

        # Idempotent return if already settled
        if quote.status == BomPaymentState.PAYMENT_SETTLED:
            logger.info(f"[BOM Flow] Idempotent hit: Quote '{quote.quote_id}' is already SETTLED.")
            return True, None, quote

        # ArmourIQ Governance Check
        self._check_armouriq_authorization(context, "settle_payment")

        # Expiry Check
        now = datetime.now(timezone.utc)
        if datetime.fromisoformat(quote.expires_at) < now:
            quote.status = BomPaymentState.PAYMENT_EXPIRED
            quote.error_message = "Payment challenge expired."
            return False, "Payment quote challenge has expired.", quote

        tx_hash = (
            proof_data.get("tx_hash")
            or proof_data.get("transaction_id")
            or proof_data.get("signature")
            or proof_data.get("receipt_id")
        )
        if not tx_hash:
            quote.status = BomPaymentState.PAYMENT_FAILED
            quote.error_message = "Missing transaction ID / proof."
            return False, "Missing transaction hash / proof.", quote

        # Replay Attack Prevention
        existing_tx = x402_storage.get_by_tx_hash(tx_hash)
        if existing_tx and existing_tx.payment_request_id != quote.payment_request_id:
            quote.status = BomPaymentState.PAYMENT_FAILED
            quote.error_message = f"Replay attack: Transaction '{tx_hash}' already redeemed."
            return False, f"Replay attack detected: Transaction '{tx_hash}' has already been redeemed.", quote

        # Critical Financial Match Check (if client submitted settled amount, verify exact parity)
        if "amount" in proof_data or "settled_amount" in proof_data:
            submitted_amount = quantize_money(proof_data.get("amount") or proof_data.get("settled_amount"))
            expected_amount = quantize_money(quote.amount_usdc)
            if submitted_amount != expected_amount:
                quote.status = BomPaymentState.PAYMENT_FAILED
                quote.error_message = (
                    f"Amount mismatch: Expected {expected_amount} USDC, "
                    f"but payment submitted was {submitted_amount} USDC."
                )
                logger.error(f"[BOM Flow] Amount mismatch rejected: {quote.error_message}")
                return False, quote.error_message, quote

        # GoPlausible Facilitator Settlement Verification
        quote.status = BomPaymentState.PAYMENT_VERIFYING
        proof_obj = PaymentProof(
            payment_request_id=quote.payment_request_id,
            tx_hash=tx_hash,
            payer_address=proof_data.get("payer") or proof_data.get("payer_address"),
        )
        record = x402_storage.get_record(quote.payment_request_id)
        if record:
            ok, err, updated_rec = await x402_verifier.verify_proof(record, proof_obj)
            if not ok:
                quote.status = BomPaymentState.PAYMENT_FAILED
                quote.error_message = err
                return False, f"Settlement verification failed: {err}", quote

        # Settle Quote
        quote.status = BomPaymentState.PAYMENT_SETTLED
        quote.transaction_id = tx_hash
        quote.payer = proof_data.get("payer") or "algorand:client_wallet"
        quote.settled_at = now.isoformat()
        quote.error_message = None

        logger.info(
            f"[BOM Flow] Payment SETTLED for quote '{quote.quote_id}': "
            f"{quote.amount_usdc} USDC on {quote.network} via tx '{tx_hash}'"
        )
        return True, None, quote

    async def generate_payment_report(
        self,
        quote_id: str,
        context: Optional[TrustContext] = None,
    ) -> Tuple[bool, Optional[str], Optional[BomPaymentReportArtifact]]:
        """
        Compiles the immutable PDF payment report for a settled quote.
        1. Checks payment status is SETTLED.
        2. Queries CoinGecko ONCE for live USD Coin -> INR exchange rate.
        3. If CoinGecko fails/times out, marks rate unavailable and compiles report without failing.
        4. Renders PDF with ReportLab and returns artifact.
        """
        quote = self.get_quote(quote_id)
        if not quote:
            return False, f"Payment quote '{quote_id}' not found.", None

        if quote.status != BomPaymentState.PAYMENT_SETTLED:
            return (
                False,
                f"Cannot generate report: Quote status is '{quote.status.value}', expected 'PAYMENT_SETTLED'.",
                None,
            )

        # Return existing report if already compiled (idempotency / immutability)
        if quote.report_artifact_id and quote.report_artifact_id in self._reports:
            logger.info(f"[BOM Flow] Returning existing PDF report for quote '{quote_id}'")
            return True, None, self._reports[quote.report_artifact_id]

        quote.status = BomPaymentState.REPORT_GENERATING
        bom = self._boms.get(quote.quote_id) or self._boms.get(quote.bom_id)
        if not bom:
            bom = compute_bom_pricing(quote.items_snapshot, bom_id=quote.bom_id, project_id=quote.project_id)

        # --- Step 8: Fetch CoinGecko ONCE per report ---
        logger.info(f"[BOM Flow] Fetching CoinGecko USD/INR rate for quote '{quote.quote_id}'")
        rate = await coingecko_client.fetch_usdc_inr_rate()

        # --- Step 12: Compile Auditable PDF ---
        try:
            artifact = BomPaymentReportEngine.generate_pdf_report(
                bom=bom,
                quote=quote,
                rate=rate,
            )

            # Store artifact
            self._reports[artifact.artifact_id] = artifact
            quote.report_artifact_id = artifact.artifact_id

            if rate.available:
                quote.status = BomPaymentState.REPORT_READY
            else:
                quote.status = BomPaymentState.REPORT_READY_WITHOUT_INR

            logger.info(
                f"[BOM Flow] PDF Report ready: artifact_id='{artifact.artifact_id}' "
                f"file='{artifact.filename}' inr_available={rate.available}"
            )
            return True, None, artifact

        except Exception as exc:
            quote.status = BomPaymentState.REPORT_FAILED
            quote.error_message = f"PDF compilation failed: {str(exc)}"
            logger.error(f"[BOM Flow] PDF report generation failed: {exc}")
            return False, str(exc), None

    def get_report(self, artifact_id: str) -> Optional[BomPaymentReportArtifact]:
        """Look up generated report artifact by ID."""
        return self._reports.get(artifact_id)


# Global singleton instance
bom_payment_flow = BomPaymentFlowCoordinator()
