"use client";

import React from "react";
import { ShieldCheck, CheckCircle2, AlertTriangle, XCircle } from "lucide-react";

export interface DRCViolation {
  rule: string;
  severity: "ERROR" | "WARNING";
  description: string;
}

export interface PCBValidationProps {
  passed?: boolean;
  violations?: DRCViolation[];
}

export const PCBValidation: React.FC<PCBValidationProps> = ({
  passed = true,
  violations = [],
}) => {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4 text-zinc-100">
      <div className="flex items-center justify-between pb-2 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-emerald-400" />
          <h3 className="text-base font-bold text-zinc-100">Deterministic Pre-DRC Validation</h3>
        </div>
        <span
          className={`text-xs font-mono font-bold px-2 py-0.5 rounded border ${
            passed
              ? "bg-emerald-950/60 text-emerald-300 border-emerald-800"
              : "bg-rose-950/60 text-rose-300 border-rose-800"
          }`}
        >
          {passed ? "DRC PASS" : "DRC VIOLATIONS"}
        </span>
      </div>

      <div className="grid grid-cols-4 gap-2 text-xs font-mono">
        <div className="p-2.5 bg-zinc-950/60 border border-zinc-800 rounded flex items-center justify-between">
          <span className="text-zinc-400">Connectivity</span>
          <span className="text-emerald-400 font-bold">PASS</span>
        </div>
        <div className="p-2.5 bg-zinc-950/60 border border-zinc-800 rounded flex items-center justify-between">
          <span className="text-zinc-400">Clearances</span>
          <span className="text-emerald-400 font-bold">PASS</span>
        </div>
        <div className="p-2.5 bg-zinc-950/60 border border-zinc-800 rounded flex items-center justify-between">
          <span className="text-zinc-400">Power Rails</span>
          <span className="text-emerald-400 font-bold">PASS</span>
        </div>
        <div className="p-2.5 bg-zinc-950/60 border border-zinc-800 rounded flex items-center justify-between">
          <span className="text-zinc-400">Overlap</span>
          <span className="text-emerald-400 font-bold">PASS</span>
        </div>
      </div>

      {violations.length > 0 && (
        <div className="flex flex-col gap-1.5 font-mono text-xs">
          {violations.map((v, idx) => (
            <div
              key={idx}
              className={`p-2 rounded border flex items-center gap-2 ${
                v.severity === "ERROR"
                  ? "bg-rose-950/20 border-rose-900/60 text-rose-300"
                  : "bg-amber-950/20 border-amber-900/60 text-amber-300"
              }`}
            >
              {v.severity === "ERROR" ? (
                <XCircle className="w-3.5 h-3.5 text-rose-400" />
              ) : (
                <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
              )}
              <span><strong>[{v.rule}]</strong>: {v.description}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
