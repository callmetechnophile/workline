"use client";

import React, { useState } from "react";
import { Layers, ShoppingBag, CheckCircle2, AlertTriangle, RefreshCw, FileDown } from "lucide-react";

export interface BOMWorkspaceProps {
  bomId?: string;
  projectId?: string;
  version?: number;
  status?: string;
  totalCost?: number;
  itemCount?: number;
  onRefresh?: () => void;
  onValidate?: () => void;
  onGeneratePackage?: () => void;
}

export const BOMWorkspace: React.FC<BOMWorkspaceProps> = ({
  bomId = "BOM-001",
  projectId = "rover_v2",
  version = 1,
  status = "READY_FOR_PROCUREMENT",
  totalCost = 180.0,
  itemCount = 1,
  onRefresh,
  onValidate,
  onGeneratePackage,
}) => {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-5 text-zinc-100">
      <div className="flex items-center justify-between pb-3 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <Layers className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-zinc-100">Bill of Materials & Procurement</h3>
          <span className="text-xs font-mono text-zinc-500">[{bomId} v{version}]</span>
        </div>
        <div className="flex items-center gap-2">
          <span
            className={`px-2.5 py-0.5 rounded text-xs font-mono font-bold border ${
              status === "READY_FOR_PROCUREMENT"
                ? "bg-emerald-950/60 text-emerald-300 border-emerald-800"
                : status === "BLOCKED"
                ? "bg-rose-950/60 text-rose-300 border-rose-800"
                : "bg-amber-950/60 text-amber-300 border-amber-800"
            }`}
          >
            {status}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <div className="p-3 bg-zinc-950/60 border border-zinc-800 rounded-lg flex flex-col gap-1">
          <span className="text-xs text-zinc-400">Total Line Items</span>
          <span className="text-base font-mono font-bold text-zinc-100">{itemCount} Parts</span>
        </div>
        <div className="p-3 bg-zinc-950/60 border border-zinc-800 rounded-lg flex flex-col gap-1">
          <span className="text-xs text-zinc-400">Estimated Subtotal</span>
          <span className="text-base font-mono font-bold text-emerald-400">₹{totalCost.toFixed(2)}</span>
        </div>
        <div className="p-3 bg-zinc-950/60 border border-zinc-800 rounded-lg flex flex-col gap-1">
          <span className="text-xs text-zinc-400">Target Project</span>
          <span className="text-base font-mono font-bold text-indigo-300">{projectId}</span>
        </div>
      </div>

      <div className="flex items-center justify-between pt-2 border-t border-zinc-800/80">
        <div className="flex items-center gap-2">
          <button
            onClick={onRefresh}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-zinc-800 hover:bg-zinc-700 text-zinc-200 rounded text-xs font-semibold transition"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Refresh Prices
          </button>
          <button
            onClick={onValidate}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-zinc-800 hover:bg-zinc-700 text-zinc-200 rounded text-xs font-semibold transition"
          >
            <CheckCircle2 className="w-3.5 h-3.5" />
            Validate BOM
          </button>
        </div>

        <button
          onClick={onGeneratePackage}
          className="flex items-center gap-1.5 px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-xs font-bold transition shadow-sm"
        >
          <ShoppingBag className="w-4 h-4" />
          Prepare Procurement Package
        </button>
      </div>
    </div>
  );
};
