"use client";

import React from "react";
import {
  FileText,
  ShieldCheck,
  Download,
  Building,
  CheckCircle2,
  ExternalLink,
} from "lucide-react";

export interface ReceiptData {
  receipt_id: string;
  order_id: string;
  vendor: string;
  external_order_id?: string;
  subtotal: number;
  shipping: number;
  tax: number;
  fees: number;
  total: number;
  currency: string;
  receipt_url?: string;
  invoice_url?: string;
  issued_at: string;
  verification_status: "VERIFIED" | "UNVERIFIED" | "RETRIEVED" | "FAILED";
}

interface ReceiptPanelProps {
  receipt: ReceiptData;
}

export const ReceiptPanel: React.FC<ReceiptPanelProps> = ({ receipt }) => {
  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-2xl backdrop-blur-md space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-emerald-500/10 border border-emerald-500/20 rounded-lg text-emerald-400">
            <FileText className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-bold text-slate-100">PURCHASE RECEIPT</h3>
              <span className="font-mono text-xs px-2 py-0.5 rounded bg-slate-800 text-emerald-400 font-semibold">
                {receipt.receipt_id}
              </span>
            </div>
            <p className="text-xs text-slate-400">Official Invoice for Order {receipt.order_id}</p>
          </div>
        </div>

        <span className="inline-flex items-center gap-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-2.5 py-1 rounded-full text-xs font-semibold">
          <ShieldCheck className="w-3.5 h-3.5" /> {receipt.verification_status}
        </span>
      </div>

      {/* Invoice Details */}
      <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800 space-y-3">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
          <div>
            <span className="text-slate-400">Vendor:</span>
            <div className="font-bold text-slate-200">{receipt.vendor}</div>
          </div>
          <div>
            <span className="text-slate-400">External Order ID:</span>
            <div className="font-mono text-cyan-400 font-semibold">{receipt.external_order_id || "N/A"}</div>
          </div>
          <div>
            <span className="text-slate-400">Issued At:</span>
            <div className="text-slate-300">{new Date(receipt.issued_at).toLocaleDateString()}</div>
          </div>
          <div>
            <span className="text-slate-400">Total Settled:</span>
            <div className="font-mono text-base font-bold text-emerald-400">
              {receipt.currency} {receipt.total.toFixed(2)}
            </div>
          </div>
        </div>

        <div className="pt-3 border-t border-slate-800/80 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs">
          <div className="text-slate-400">
            Subtotal: <span className="text-slate-200">{receipt.currency} {receipt.subtotal.toFixed(2)}</span> • Shipping: <span className="text-slate-200">{receipt.currency} {receipt.shipping.toFixed(2)}</span>
          </div>

          <div className="flex items-center gap-2">
            {receipt.invoice_url && (
              <a
                href={receipt.invoice_url}
                target="_blank"
                rel="noopener noreferrer"
                className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium inline-flex items-center gap-1.5 transition-all"
              >
                <Download className="w-3.5 h-3.5" /> Download Invoice PDF
              </a>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReceiptPanel;
