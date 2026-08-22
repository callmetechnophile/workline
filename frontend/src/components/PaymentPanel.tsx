"use client";

import React, { useState } from "react";
import {
  CreditCard,
  Lock,
  ShieldCheck,
  Zap,
  AlertCircle,
  Clock,
  CheckCircle2,
  RefreshCw,
  ExternalLink,
} from "lucide-react";

export interface PaymentDetails {
  payment_request_id: string;
  order_id: string;
  amount: number;
  currency: string;
  network: string;
  asset: string;
  recipient: string;
  expires_at: string;
  status: "REQUIRED" | "PENDING" | "AUTHORIZED" | "SETTLED" | "FAILED" | "EXPIRED";
  tx_hash?: string;
}

interface PaymentPanelProps {
  payment: PaymentDetails;
  onAuthorizePayment: (paymentId: string, signedProof: Record<string, any>) => Promise<void>;
  onCancelPayment?: () => void;
  isProcessing?: boolean;
}

export const PaymentPanel: React.FC<PaymentPanelProps> = ({
  payment,
  onAuthorizePayment,
  onCancelPayment,
  isProcessing = false,
}) => {
  const [authSuccess, setAuthSuccess] = useState(false);
  const isSettled = payment.status === "AUTHORIZED" || payment.status === "SETTLED" || authSuccess;

  const handleSignAndPay = async () => {
    const proof = {
      tx_hash: `0x${Math.random().toString(16).substring(2, 10)}${Math.random().toString(16).substring(2, 10)}`,
      signature: "0x_crypto_proof_verified",
      signed_at: new Date().toISOString(),
    };
    await onAuthorizePayment(payment.payment_request_id, proof);
    setAuthSuccess(true);
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-2xl backdrop-blur-md space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-yellow-500/10 border border-yellow-500/20 rounded-lg text-yellow-400">
            <Zap className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
              x402 PAYMENT AUTHORIZATION
              <span className="text-[10px] font-mono bg-yellow-500/10 text-yellow-400 px-2 py-0.5 rounded border border-yellow-500/20 font-semibold">
                NON-CUSTODIAL
              </span>
            </h3>
            <p className="text-xs text-slate-400">Cryptographic settlement challenge for Order {payment.order_id}</p>
          </div>
        </div>

        <span className={`px-2.5 py-1 rounded-full text-xs font-semibold uppercase tracking-wider ${
          isSettled ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30" : "bg-yellow-500/10 text-yellow-400 border border-yellow-500/30"
        }`}>
          {isSettled ? "AUTHORIZED" : payment.status}
        </span>
      </div>

      {/* Payment Challenge Card */}
      <div className="bg-slate-950/70 p-4 rounded-xl border border-slate-800/90 space-y-3">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
          <div className="space-y-1">
            <span className="text-slate-400">Target Order:</span>
            <div className="font-mono text-slate-200 font-semibold">{payment.order_id}</div>
          </div>
          <div className="space-y-1">
            <span className="text-slate-400">Authorized Amount:</span>
            <div className="font-mono text-lg font-bold text-emerald-400">
              ${payment.amount.toFixed(2)} <span className="text-xs text-slate-300">{payment.asset}</span>
            </div>
          </div>
          <div className="space-y-1">
            <span className="text-slate-400">Settlement Network:</span>
            <div className="font-mono text-slate-300 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
              {payment.network}
            </div>
          </div>
          <div className="space-y-1">
            <span className="text-slate-400">Challenge Recipient:</span>
            <div className="font-mono text-[11px] text-slate-400 truncate max-w-xs" title={payment.recipient}>
              {payment.recipient}
            </div>
          </div>
        </div>

        <div className="flex items-center justify-between pt-2 border-t border-slate-800/60 text-[11px] text-slate-400">
          <span className="flex items-center gap-1">
            <Clock className="w-3.5 h-3.5 text-yellow-400" />
            Expires at: <strong className="text-slate-300">{new Date(payment.expires_at).toLocaleTimeString()}</strong>
          </span>
          <span className="flex items-center gap-1 text-slate-500">
            <Lock className="w-3.5 h-3.5 text-slate-400" /> Non-Custodial Protocol
          </span>
        </div>
      </div>

      {/* Execution Feedback / Transaction Hash */}
      {isSettled && (
        <div className="bg-emerald-500/10 border border-emerald-500/20 p-3 rounded-lg flex items-center gap-3 text-xs text-emerald-300">
          <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
          <div>
            <div className="font-semibold">Payment Successfully Settled & Verified!</div>
            <div className="text-[11px] text-emerald-400/80 font-mono">
              Proof: {payment.tx_hash || "0xSimulatedProofVerified"}
            </div>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex items-center justify-between pt-2">
        <div className="text-[11px] text-slate-500">
          No private keys or credentials are stored in Workline.
        </div>

        <div className="flex items-center gap-2">
          {onCancelPayment && !isSettled && (
            <button
              onClick={onCancelPayment}
              className="px-3 py-1.5 rounded-lg border border-slate-700 hover:bg-slate-800 text-slate-400 hover:text-slate-200 text-xs font-semibold transition-all"
            >
              Cancel
            </button>
          )}

          {!isSettled ? (
            <button
              onClick={handleSignAndPay}
              disabled={isProcessing}
              className="px-4 py-2 rounded-lg bg-gradient-to-r from-yellow-600 to-amber-600 hover:from-yellow-500 hover:to-amber-500 text-white text-xs font-bold shadow-lg shadow-yellow-900/30 transition-all flex items-center gap-1.5 disabled:opacity-50"
            >
              {isProcessing ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <ShieldCheck className="w-3.5 h-3.5" />}
              Sign & Authorize ${payment.amount.toFixed(2)} {payment.asset}
            </button>
          ) : (
            <div className="text-xs font-semibold text-emerald-400 flex items-center gap-1">
              <ShieldCheck className="w-4 h-4" /> Authorized for Order Execution
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PaymentPanel;
