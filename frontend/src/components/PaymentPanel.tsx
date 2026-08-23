"use client";

import React, { useState, useEffect } from "react";
import {
  Wallet,
  Lock,
  ShieldCheck,
  Zap,
  AlertCircle,
  Clock,
  CheckCircle2,
  RefreshCw,
  ExternalLink,
  FileText,
  Download,
  AlertTriangle,
  ArrowRight,
} from "lucide-react";
import { peraWallet, WalletConnectionState, PeraSignedPaymentProof } from "../lib/peraWallet";

export interface PaymentDetails {
  quote_id: string;
  payment_request_id: string;
  order_id?: string;
  bom_id?: string;
  project_id?: string;
  amount_usd: number;
  amount_usdc: number;
  currency: string;
  network: string;
  asset: string;
  asset_id: number;
  recipient: string;
  expires_at: string;
  status: "REQUIRED" | "PENDING" | "VERIFYING" | "SETTLED" | "FAILED" | "EXPIRED";
  tx_hash?: string;
}

interface PaymentPanelProps {
  payment: PaymentDetails;
  onAuthorizePayment: (quoteId: string, proof: PeraSignedPaymentProof) => Promise<void>;
  onGenerateReport?: (quoteId: string) => Promise<{
    artifact_id: string;
    filename: string;
    download_url: string;
    inr_available: boolean;
    approx_inr_total?: number;
    exchange_rate?: number;
  }>;
  onCancelPayment?: () => void;
  isProcessing?: boolean;
}

export const PaymentPanel: React.FC<PaymentPanelProps> = ({
  payment,
  onAuthorizePayment,
  onGenerateReport,
  onCancelPayment,
  isProcessing = false,
}) => {
  const [walletState, setWalletState] = useState<WalletConnectionState>(peraWallet.getState());
  const [walletAddress, setWalletAddress] = useState<string | null>(peraWallet.getAddress());
  const [submitting, setSubmitting] = useState(false);
  const [settledTxHash, setSettledTxHash] = useState<string | null>(payment.tx_hash || null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Report state
  const [reportLoading, setReportLoading] = useState(false);
  const [reportResult, setReportResult] = useState<{
    artifact_id: string;
    filename: string;
    download_url: string;
    inr_available: boolean;
    approx_inr_total?: number;
    exchange_rate?: number;
  } | null>(null);

  useEffect(() => {
    const unsub = peraWallet.subscribe((state, address) => {
      setWalletState(state);
      setWalletAddress(address);
    });
    return () => unsub();
  }, []);

  const isSettled = payment.status === "SETTLED" || !!settledTxHash;
  const isTestnet = payment.network?.toLowerCase().includes("testnet");
  const explorerBase = isTestnet
    ? "https://lora.algokit.io/testnet/transaction"
    : "https://lora.algokit.io/mainnet/transaction";

  const handleConnectWallet = async () => {
    setErrorMessage(null);
    try {
      await peraWallet.connect();
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to connect Pera Wallet.");
    }
  };

  const handleDisconnectWallet = async () => {
    await peraWallet.disconnect();
  };

  const handleSignAndPay = async () => {
    setErrorMessage(null);
    setSubmitting(true);

    try {
      // 1. Client-Side Amount & Recipient Pre-Validation
      if (Math.abs(payment.amount_usd - payment.amount_usdc) > 0.001) {
        throw new Error(
          `Financial Parity Mismatch: BOM Total ($${payment.amount_usd}) does not equal USDC charge (${payment.amount_usdc} USDC).`
        );
      }

      // 2. Prompt Pera Wallet for user signature
      const signedProof = await peraWallet.signPaymentTransaction({
        quote_id: payment.quote_id,
        payment_request_id: payment.payment_request_id,
        amount_usdc: payment.amount_usdc,
        asset_id: payment.asset_id || 31566704,
        network: payment.network,
        pay_to: payment.recipient,
      });

      // 3. Submit proof to backend R1/R5 for GoPlausible verification
      await onAuthorizePayment(payment.quote_id || payment.payment_request_id, signedProof);
      setSettledTxHash(signedProof.tx_hash);
    } catch (err: any) {
      setErrorMessage(err.message || "Payment settlement failed.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleGenerateReport = async () => {
    if (!onGenerateReport) return;
    setReportLoading(true);
    setErrorMessage(null);
    try {
      const res = await onGenerateReport(payment.quote_id || payment.payment_request_id);
      setReportResult(res);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to generate procurement report.");
    } finally {
      setReportLoading(false);
    }
  };

  return (
    <div className="bg-slate-900/95 border border-slate-800 rounded-xl p-5 shadow-2xl backdrop-blur-md space-y-5 font-mono">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-yellow-500/10 border border-yellow-500/20 rounded-lg text-yellow-400">
            <Zap className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold tracking-wider text-slate-100 uppercase">
              Algorand x402 Procurement Settlement
            </h3>
            <p className="text-[11px] text-slate-400">
              Authoritative BOM Sourcing • Exact USDC Settlement
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {isSettled ? (
            <span className="flex items-center gap-1 text-[11px] font-bold text-emerald-400 bg-emerald-950/60 border border-emerald-800/60 px-2.5 py-1 rounded">
              <CheckCircle2 className="w-3.5 h-3.5" /> SETTLED
            </span>
          ) : (
            <span className="flex items-center gap-1 text-[11px] font-bold text-amber-400 bg-amber-950/60 border border-amber-800/60 px-2.5 py-1 rounded">
              <Clock className="w-3.5 h-3.5" /> PAYMENT REQUIRED
            </span>
          )}
        </div>
      </div>

      {/* Quote & Financial Summary */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="bg-slate-950/80 p-3 rounded-lg border border-slate-800/80 space-y-1">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider block">BOM Total</span>
          <span className="text-sm font-bold text-slate-100">
            ${payment.amount_usd.toFixed(2)} USD
          </span>
        </div>
        <div className="bg-slate-950/80 p-3 rounded-lg border border-slate-800/80 space-y-1">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider block">x402 Charge</span>
          <span className="text-sm font-bold text-cyan-400">
            {payment.amount_usdc.toFixed(2)} USDC
          </span>
        </div>
        <div className="bg-slate-950/80 p-3 rounded-lg border border-slate-800/80 space-y-1">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Network / Asset</span>
          <span className="text-xs font-bold text-slate-300 truncate block">
            {payment.network}
          </span>
        </div>
        <div className="bg-slate-950/80 p-3 rounded-lg border border-slate-800/80 space-y-1">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Quote ID</span>
          <span className="text-xs font-bold text-slate-400 truncate block">
            {payment.quote_id || payment.payment_request_id}
          </span>
        </div>
      </div>

      {/* Recipient & Security Details */}
      <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/60 space-y-1.5 text-xs">
        <div className="flex justify-between text-slate-400 text-[11px]">
          <span>Pay-To Algorand Address:</span>
          <span className="text-slate-300 font-bold select-all">{payment.recipient}</span>
        </div>
        <div className="flex justify-between text-slate-400 text-[11px]">
          <span>USDC Asset ID:</span>
          <span className="text-slate-300 font-bold">{payment.asset_id || 31566704}</span>
        </div>
      </div>

      {/* Pera Wallet Status */}
      <div className="p-3.5 bg-slate-950/90 border border-slate-800 rounded-lg flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <Wallet className="w-4 h-4 text-cyan-400" />
          <div>
            <div className="text-xs font-bold text-slate-200">
              Pera Wallet:{" "}
              <span
                className={
                  walletState === "CONNECTED"
                    ? "text-emerald-400"
                    : walletState === "CONNECTING"
                    ? "text-amber-400"
                    : "text-slate-500"
                }
              >
                {walletState}
              </span>
            </div>
            {walletAddress && (
              <div className="text-[10px] text-slate-500 truncate max-w-xs">{walletAddress}</div>
            )}
          </div>
        </div>

        {walletState === "CONNECTED" ? (
          <button
            onClick={handleDisconnectWallet}
            className="text-[11px] px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded transition"
          >
            Disconnect
          </button>
        ) : (
          <button
            onClick={handleConnectWallet}
            className="text-xs px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white font-bold rounded transition flex items-center gap-1.5"
          >
            <Wallet className="w-3.5 h-3.5" /> Connect Pera Wallet
          </button>
        )}
      </div>

      {/* Error Banner */}
      {errorMessage && (
        <div className="p-3 bg-rose-950/60 border border-rose-800/60 rounded-lg text-rose-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Actions */}
      {!isSettled ? (
        <div className="space-y-3">
          <button
            onClick={handleSignAndPay}
            disabled={walletState !== "CONNECTED" || submitting || isProcessing}
            className={`w-full py-3 px-4 font-bold text-xs rounded-lg transition flex items-center justify-center gap-2 ${
              walletState === "CONNECTED" && !submitting && !isProcessing
                ? "bg-gradient-to-r from-cyan-600 to-emerald-600 hover:from-cyan-500 hover:to-emerald-500 text-white shadow-lg cursor-pointer"
                : "bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700"
            }`}
          >
            {submitting || isProcessing ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" /> Verifying Settlement with GoPlausible...
              </>
            ) : walletState !== "CONNECTED" ? (
              <>
                <Wallet className="w-4 h-4" /> Connect Pera Wallet to Sign Payment
              </>
            ) : (
              <>
                <ShieldCheck className="w-4 h-4" /> Sign & Pay {payment.amount_usdc.toFixed(2)} USDC via Pera
              </>
            )}
          </button>
        </div>
      ) : (
        <div className="space-y-3 pt-2">
          <div className="p-3 bg-emerald-950/40 border border-emerald-800/60 rounded-lg space-y-1.5 text-xs">
            <div className="flex items-center justify-between text-emerald-400 font-bold">
              <span>Settlement Confirmed</span>
              <CheckCircle2 className="w-4 h-4" />
            </div>
            {settledTxHash && (
              <div className="flex items-center justify-between text-[11px] text-slate-300">
                <span>Transaction ID:</span>
                <a
                  href={`${explorerBase}/${settledTxHash}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-cyan-400 hover:underline flex items-center gap-1 font-bold"
                >
                  {settledTxHash.substring(0, 16)}... <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            )}
          </div>

          {/* PDF Procurement Report Generation */}
          <button
            onClick={handleGenerateReport}
            disabled={reportLoading}
            className="w-full py-2.5 px-4 bg-slate-800 hover:bg-slate-700 text-slate-100 font-bold text-xs rounded-lg transition flex items-center justify-center gap-2 border border-slate-700"
          >
            {reportLoading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" /> Generating Auditable Report...
              </>
            ) : (
              <>
                <FileText className="w-4 h-4 text-cyan-400" /> Generate Procurement Report (PDF + INR)
              </>
            )}
          </button>

          {reportResult && (
            <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg text-xs space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-slate-300 font-bold">{reportResult.filename}</span>
                <a
                  href={reportResult.download_url}
                  download={reportResult.filename}
                  className="px-2.5 py-1 bg-cyan-600 hover:bg-cyan-500 text-white rounded text-[11px] font-bold flex items-center gap-1"
                >
                  <Download className="w-3 h-3" /> Download PDF
                </a>
              </div>
              {reportResult.inr_available && reportResult.approx_inr_total ? (
                <div className="text-[11px] text-slate-400">
                  Approx. INR Equivalent:{" "}
                  <span className="text-emerald-400 font-bold">
                    ₹{reportResult.approx_inr_total.toLocaleString("en-IN", { maximumFractionDigits: 2 })}
                  </span>{" "}
                  (Rate: ₹{reportResult.exchange_rate?.toFixed(2)}/USD)
                </div>
              ) : (
                <div className="text-[11px] text-slate-500">
                  INR exchange rate snapshot unavailable (informational only).
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default PaymentPanel;
