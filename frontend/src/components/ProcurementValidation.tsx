"use client";

import React from "react";
import { CheckCircle2, AlertOctagon, AlertTriangle, ShieldAlert } from "lucide-react";

export interface ProcurementValidationProps {
  status?: "READY" | "BLOCKED" | "INCOMPLETE";
  issues?: string[];
}

export const ProcurementValidation: React.FC<ProcurementValidationProps> = ({
  status = "READY",
  issues = [],
}) => {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4 text-zinc-100">
      <div className="flex items-center justify-between pb-2 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          {status === "READY" ? (
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
          ) : (
            <ShieldAlert className="w-5 h-5 text-rose-400" />
          )}
          <h3 className="text-base font-bold text-zinc-100">Procurement Readiness Check</h3>
        </div>
        <span
          className={`text-xs font-mono font-bold px-2 py-0.5 rounded border ${
            status === "READY"
              ? "bg-emerald-950/60 text-emerald-300 border-emerald-800"
              : "bg-rose-950/60 text-rose-300 border-rose-800"
          }`}
        >
          {status}
        </span>
      </div>

      {issues.length === 0 ? (
        <div className="p-3 bg-emerald-950/20 border border-emerald-800/60 rounded-lg text-xs text-emerald-300 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>All BOM items resolved with confirmed distributor inventory and verified specifications.</span>
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          <span className="text-xs font-bold text-rose-400">Blocking Issues Detected:</span>
          <div className="flex flex-col gap-1.5 font-mono text-xs">
            {issues.map((issue, idx) => (
              <div key={idx} className="p-2.5 bg-rose-950/20 border border-rose-900/60 rounded flex items-center gap-2 text-rose-300">
                <AlertOctagon className="w-3.5 h-3.5 text-rose-400 shrink-0" />
                <span>{issue}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
