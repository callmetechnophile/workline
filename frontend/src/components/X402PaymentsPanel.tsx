'use client';

import React, { useState, useEffect } from 'react';
import {
  CreditCard,
  CheckCircle2,
  Clock,
  AlertCircle,
  ExternalLink,
  RefreshCw,
  Layers,
  ArrowRight,
  ShieldCheck,
} from 'lucide-react';

interface PaymentRecordItem {
  id: string;
  payment_request_id: string;
  service_id: string;
  user_id?: string;
  project_id?: string;
  amount: number;
  asset: string;
  network: string;
  transaction_id?: string;
  status: string;
  created_at: string;
  settled_at?: string;
}

interface X402PaymentsPanelProps {
  apiBase?: string;
}

export default function X402PaymentsPanel({ apiBase }: X402PaymentsPanelProps) {
  const base = apiBase || 'https://workline-core-gateway.onrender.com';
  const [payments, setPayments] = useState<PaymentRecordItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchPayments = async () => {
    setIsLoading(true);
    try {
      const res = await fetch(`${base}/api/x402/payments`);
      if (res.ok) {
        const data = await res.json();
        setPayments(data.payments || []);
      } else {
        setPayments([]);
      }
    } catch (err) {
      console.error('Failed to load x402 payments:', err);
      setPayments([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPayments();
  }, [base]);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'EXECUTED':
      case 'SETTLED':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-emerald-950/80 text-emerald-400 border border-emerald-800/40">
            <CheckCircle2 className="w-3 h-3" />
            <span>{status}</span>
          </span>
        );
      case 'VERIFYING':
      case 'PENDING':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-blue-950/80 text-blue-400 border border-blue-800/40">
            <Clock className="w-3 h-3 animate-spin" />
            <span>{status}</span>
          </span>
        );
      case 'PAYMENT_REQUIRED':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-amber-950/80 text-amber-300 border border-amber-800/40">
            <Clock className="w-3 h-3" />
            <span>PAYMENT REQUIRED</span>
          </span>
        );
      case 'FAILED':
      case 'EXPIRED':
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-red-950/80 text-red-400 border border-red-800/40">
            <AlertCircle className="w-3 h-3" />
            <span>{status}</span>
          </span>
        );
    }
  };

  return (
    <div className="space-y-6 max-w-6xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2.5">
            <CreditCard className="w-5 h-5 text-indigo-400" />
            <h1 className="text-lg font-bold text-slate-100 uppercase font-mono tracking-wide">
              x402 Payment Ledger
            </h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Audit history of non-custodial <strong className="text-indigo-300">Algorand USDC</strong> micro-payments settled via GoPlausible.
          </p>
        </div>

        <div className="flex items-center gap-2 self-start sm:self-auto">
          <a
            href="/wallet"
            className="px-3.5 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-mono font-bold flex items-center gap-1.5 cursor-pointer transition-all shadow"
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Open Wallet & Pay</span>
          </a>
          <button
            onClick={fetchPayments}
            disabled={isLoading}
            className="px-3.5 py-2 rounded-lg bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300 hover:text-white text-xs font-mono flex items-center gap-1.5 cursor-pointer transition-all"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Ledger Table / Empty State */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
        <div className="px-5 py-4 border-b border-slate-800 bg-slate-950/60 flex items-center justify-between">
          <span className="text-xs font-bold text-slate-200 uppercase font-mono">
            Settlement Audit Trail ({payments.length})
          </span>
          <span className="text-[10px] text-slate-500 font-mono">
            Immutable Blockchain Provenance
          </span>
        </div>

        {isLoading ? (
          <div className="p-16 text-center text-xs text-slate-500 font-mono">
            Querying x402 ledger...
          </div>
        ) : payments.length === 0 ? (
          <div className="p-16 text-center space-y-3">
            <div className="w-10 h-10 rounded-full bg-slate-800 text-slate-500 flex items-center justify-center mx-auto">
              <CreditCard className="w-5 h-5" />
            </div>
            <div className="space-y-1">
              <h3 className="text-sm font-bold text-slate-300">No x402 payments yet</h3>
              <p className="text-xs text-slate-500 max-w-sm mx-auto">
                Payments generated when autonomous AI agents or external clients invoke Workline payable APIs will appear here.
              </p>
            </div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-slate-950 text-slate-400 border-b border-slate-800 text-[11px]">
                <tr>
                  <th className="p-3.5 font-semibold">Service</th>
                  <th className="p-3.5 font-semibold">Project</th>
                  <th className="p-3.5 font-semibold">Amount</th>
                  <th className="p-3.5 font-semibold">Network</th>
                  <th className="p-3.5 font-semibold">Status</th>
                  <th className="p-3.5 font-semibold">Tx / Proof</th>
                  <th className="p-3.5 font-semibold">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {payments.map((p) => (
                  <tr key={p.id} className="hover:bg-slate-850/40 transition-colors">
                    <td className="p-3.5 font-bold text-indigo-300">
                      {p.service_id}
                    </td>
                    <td className="p-3.5 text-slate-400">
                      {p.project_id || '—'}
                    </td>
                    <td className="p-3.5 font-bold text-emerald-400">
                      ${p.amount.toFixed(2)} {p.asset}
                    </td>
                    <td className="p-3.5 text-slate-400 text-[11px]">
                      {p.network}
                    </td>
                    <td className="p-3.5">
                      {getStatusBadge(p.status)}
                    </td>
                    <td className="p-3.5 text-[11px] text-slate-400 truncate max-w-xs">
                      {p.transaction_id ? (
                        <span className="font-mono text-slate-300 select-all" title={p.transaction_id}>
                          {p.transaction_id.slice(0, 16)}...
                        </span>
                      ) : (
                        <span className="text-slate-600">—</span>
                      )}
                    </td>
                    <td className="p-3.5 text-slate-500 text-[11px]">
                      {new Date(p.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
