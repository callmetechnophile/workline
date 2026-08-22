"use client";

import React from "react";
import { Activity, AlertTriangle, CheckCircle } from "lucide-react";

export interface SensitivityPanelProps {
  currentWinner?: string;
  stability?: "ROBUST" | "MODERATELY_STABLE" | "SENSITIVE" | "UNSTABLE";
  perturbations?: Array<{
    criterion: string;
    weightChange: string;
    winner: string;
    isShift: boolean;
  }>;
}

export const SensitivityPanel: React.FC<SensitivityPanelProps> = ({
  currentWinner = "TPS62130",
  stability = "SENSITIVE",
  perturbations = [
    { criterion: "Unit Cost", weightChange: "0.20 → 0.30", winner: "TPS62130", isShift: false },
    { criterion: "Unit Cost", weightChange: "0.20 → 0.40", winner: "LM2596-5", isShift: true },
    { criterion: "Supply Risk", weightChange: "0.20 → 0.35", winner: "TPS62130", isShift: false },
  ],
}) => {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4 text-zinc-100">
      <div className="flex items-center justify-between pb-2 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <Activity className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-zinc-100">Sensitivity & Stability Analysis</h3>
        </div>
        <span
          className={`text-xs font-mono font-bold px-2 py-0.5 rounded border ${
            stability === "ROBUST"
              ? "bg-emerald-950/60 text-emerald-300 border-emerald-800"
              : stability === "SENSITIVE"
              ? "bg-amber-950/60 text-amber-300 border-amber-800"
              : "bg-rose-950/60 text-rose-300 border-rose-800"
          }`}
        >
          {stability}
        </span>
      </div>

      <p className="text-xs text-zinc-400">
        Tests whether rank ordering shifts when individual criterion weights are perturbed.
      </p>

      <div className="flex flex-col gap-2 font-mono text-xs">
        {perturbations.map((p, idx) => (
          <div
            key={idx}
            className={`p-3 rounded-lg border flex items-center justify-between ${
              p.isShift
                ? "bg-amber-950/20 border-amber-800/80 text-amber-300"
                : "bg-zinc-950/60 border-zinc-800 text-zinc-300"
            }`}
          >
            <div className="flex items-center gap-2">
              {p.isShift ? <AlertTriangle className="w-3.5 h-3.5 text-amber-400" /> : <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />}
              <span>{p.criterion} ({p.weightChange})</span>
            </div>
            <span className="font-bold">Winner: {p.winner}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
