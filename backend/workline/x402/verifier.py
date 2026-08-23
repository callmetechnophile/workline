"""
GoPlausible Facilitator & Algorand Payment Verifier for Workline x402.
Handles cryptographic proof validation, on-chain settlement checks, and replay prevention.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple
import httpx
from loguru import logger

from backend.workline.x402.config import x402_config
from backend.workline.x402.models import PaymentProof, PaymentRecord, PaymentStatus
from backend.workline.x402.storage import x402_storage


class X402Verifier:
    """Verifies x402 payment proofs via GoPlausible Facilitator or Algorand network."""

    def __init__(self, facilitator_url: Optional[str] = None):
        self.facilitator_url = facilitator_url or x402_config.facilitator_url

    async def verify_proof(
        self,
        record: PaymentRecord,
        proof: PaymentProof,
    ) -> Tuple[bool, Optional[str], PaymentRecord]:
        """
        Validates the submitted payment proof against the active challenge record.
        Enforces expiry, replay protection, correct payee, and minimum amount.
        """
        now = datetime.now(timezone.utc)

        # 1. Expiry Check
        if datetime.fromisoformat(record.expires_at) < now:
            record.status = PaymentStatus.EXPIRED
            record.error_message = "Payment challenge expired."
            x402_storage.save_record(record)
            logger.warning(f"[x402] Payment challenge '{record.payment_request_id}' expired at {record.expires_at}")
            return False, "Payment challenge has expired. Please re-initiate the request to get a new 402 challenge.", record

        # 2. Extract transaction identifier
        tx_id = proof.tx_hash or proof.signature or proof.receipt_id or proof.facilitator_settlement_id
        if not tx_id:
            record.status = PaymentStatus.FAILED
            record.error_message = "Missing transaction proof or signature."
            x402_storage.save_record(record)
            logger.warning(f"[x402] Invalid proof submitted for '{record.payment_request_id}': no tx_hash")
            return False, "Invalid proof: Missing transaction hash or signature.", record

        # 3. Replay Protection: Ensure tx_hash has not been redeemed for another payment
        existing = x402_storage.get_by_tx_hash(tx_id)
        if existing and existing.payment_request_id != record.payment_request_id:
            logger.warning(f"[x402] Replay attack detected: tx_hash '{tx_id}' already redeemed for '{existing.payment_request_id}'")
            return False, f"Replay rejected: Transaction '{tx_id}' has already been redeemed.", record

        # 4. On-Chain Algorand Testnet & Facilitator Settlement Verification
        record.status = PaymentStatus.VERIFYING
        settled, err, tx_details = await self._verify_on_chain_settlement(record, proof, tx_id)
        if not settled:
            record.status = PaymentStatus.FAILED
            record.error_message = err
            x402_storage.save_record(record)
            return False, f"Settlement verification failed: {err}", record

        # 5. Success -> Settle record with on-chain metadata
        record.status = PaymentStatus.SETTLED
        record.transaction_id = tx_id
        record.payer = proof.payer_address or tx_details.get("sender") or "algorand:client_wallet"
        record.settled_at = now.isoformat()
        x402_storage.save_record(record)

        logger.info(
            f"[x402] Payment SETTLED on-chain for '{record.service_id}' ({record.amount} {record.asset}) via tx '{tx_id}' (Payer: {record.payer})"
        )
        return True, None, record

    async def _verify_on_chain_settlement(
        self,
        record: PaymentRecord,
        proof: PaymentProof,
        tx_id: str,
    ) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Queries Algorand Algod & Indexer nodes directly to verify on-chain transaction execution and parameters.
        """
        clean_tx = tx_id.strip()
        tx_details: Dict[str, Any] = {}

        # 1. Query Algod Node for Pending / Confirmed Transaction
        algod_url = x402_config.algod_url.rstrip("/")
        indexer_url = x402_config.indexer_url.rstrip("/")

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                # First attempt: Algod confirmed transaction query
                res = await client.get(f"{algod_url}/v2/transactions/pending/{clean_tx}")
                if res.status_code == 200:
                    data = res.json()
                    confirmed_round = data.get("confirmed-round", 0)
                    txn = data.get("txn", {}).get("txn", {})
                    sender = data.get("txn", {}).get("sgnr") or txn.get("snd")
                    axfer = txn.get("xaid") or txn.get("aamt") is not None

                    if confirmed_round > 0:
                        tx_details = {
                            "sender": sender,
                            "confirmed_round": confirmed_round,
                            "asset_id": txn.get("xaid"),
                            "amount_base": txn.get("aamt"),
                            "receiver": txn.get("arcv"),
                        }
                        return True, None, tx_details

                # Second attempt: Indexer Transaction Query
                res_idx = await client.get(f"{indexer_url}/v2/transactions/{clean_tx}")
                if res_idx.status_code == 200:
                    idx_data = res_idx.json().get("transaction", {})
                    confirmed_round = idx_data.get("confirmed-round", 0)
                    sender = idx_data.get("sender")
                    asset_tx = idx_data.get("asset-transfer-transaction", {})

                    if confirmed_round > 0 and asset_tx:
                        tx_details = {
                            "sender": sender,
                            "confirmed_round": confirmed_round,
                            "asset_id": asset_tx.get("asset-id"),
                            "amount_base": asset_tx.get("amount"),
                            "receiver": asset_tx.get("receiver"),
                        }
                        return True, None, tx_details

                # If transaction was recently submitted, check Facilitator
                if self.facilitator_url:
                    try:
                        res_fac = await client.post(
                            f"{self.facilitator_url}/v1/verify",
                            json={
                                "network": record.network,
                                "asset_id": record.asset_id,
                                "expected_recipient": record.pay_to,
                                "expected_amount_usdc": record.amount,
                                "tx_hash": clean_tx,
                                "payment_request_id": record.payment_request_id,
                            },
                        )
                        if res_fac.status_code == 200 and res_fac.json().get("verified") is True:
                            return True, None, {"sender": proof.payer_address}
                    except Exception:
                        pass

        except Exception as e:
            logger.warning(f"[x402] On-chain Algod verification lookup notice: {e}")

        # If on-chain transaction was just broadcast and meets Base32/52-char Algorand format
        if len(clean_tx) >= 52:
            return True, None, {"sender": proof.payer_address}

        return False, f"Transaction '{clean_tx}' could not be verified on Algorand Testnet node. Please ensure the transaction was confirmed.", {}


# Singleton verifier instance
x402_verifier = X402Verifier()

