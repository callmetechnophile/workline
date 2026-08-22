"use client";

import React from "react";
import { Package, Send, CheckCircle, Store, Zap } from "lucide-react";

export interface ProcurementSummaryProps {
  packageId?: string;
  bomId?: string;
  subtotal?: number;
  currency?: string;
  supplierBreakdown?: Array<{ supplier: string; items: number; subtotal: number }>;
  onHandoffToX402?: () => void;
}

export const ProcurementSummary: React.FC<ProcurementSummaryProps> = ({
  packageId = "PKG-001",
  bomId = "BOM-001 v1",
  subtotal = 180.0,
  currency = "INR",
  supplierBreakdown = [
    { supplier: "DigiKey", items: 1, subtotal: 180.0 },
  ],
  onHandoffToX402,
}) => {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-5 text-zinc-100">
      <div className="flex items-center justify-between pb-3 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <Package className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-zinc-100">Procurement Package Overview</h3>
          <span className="text-xs font-mono text-zinc-500">[{packageId}]</span>
        </div>
        <span className="px-2.5 py-0.5 rounded text-xs font-mono font-bold bg-emerald-950/60 text-emerald-300 border border-emerald-800">
          STATUS: READY
        </span>
      </div>

      <div className="flex flex-col gap-2">
        <span className="text-xs font-bold text-zinc-400">Supplier Sourcing Breakdown</span>
        <div className="flex flex-col gap-2 font-mono text-xs">
          {supplierBreakdown.map((s) => (
            <div key={s.supplier} className="p-3 bg-zinc-950/60 border border-zinc-800 rounded-lg flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Store className="w-3.5 h-3.5 text-indigo-400" />
                <span className="font-bold text-zinc-200">{s.supplier}</span>
                <span className="text-zinc-500">({s.items} line item)</span>
              </div>
              <span className="font-bold text-emerald-400">₹{s.subtotal.toFixed(2)}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="p-4 bg-zinc-950/80 border border-zinc-800 rounded-lg flex items-center justify-between">
        <div>
          <span className="text-xs text-zinc-400 block">Total Landed Estimate:</span>
          <span className="text-xl font-mono font-bold text-emerald-400">₹{subtotal.toFixed(2)} {currency}</span>
        </div>

        <button
          onClick={onHandoffToX402}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded font-bold text-xs transition"
        >
          <Zap className="w-4 h-4 text-amber-300" />
          Handoff to Phase 5 x402 Unit
        </button>
      </div>
    </div>
  );
};
