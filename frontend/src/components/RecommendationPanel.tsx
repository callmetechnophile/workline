"use client";

import React from "react";
import { Award, CheckCircle, AlertCircle, HelpCircle } from "lucide-react";

export interface RecommendationPanelProps {
  candidateName?: string;
  score?: number;
  reasons?: string[];
  tradeoffs?: string[];
  unknowns?: string[];
}

export const RecommendationPanel: React.FC<RecommendationPanelProps> = ({
  candidateName = "TPS62130",
  score = 0.91,
  reasons = [
    "Passes all mandatory electrical constraints (3.3V, >= 2A)",
    "Verified continuous output current of 3A from manufacturer datasheet",
    "Active lifecycle with multiple authorized distributors",
  ],
  tradeoffs = [
    "Unit cost ($0.20) is higher than LM2596-5 ($0.10)",
  ],
  unknowns = [
    "Thermal derating margin under continuous 50°C ambient load",
  ],
}) => {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4 text-zinc-100">
      <div className="flex items-center justify-between pb-2 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <Award className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-zinc-100">Recommendation Rationale</h3>
        </div>
        <span className="text-xs font-mono font-bold text-emerald-400 bg-emerald-950/40 border border-emerald-800 px-2 py-0.5 rounded">
          Score: {score}
        </span>
      </div>

      <div className="flex flex-col gap-3 text-xs">
        <div className="flex flex-col gap-1.5">
          <span className="font-bold text-emerald-300 flex items-center gap-1.5">
            <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
            Key Advantages:
          </span>
          <ul className="list-disc pl-5 text-zinc-300 flex flex-col gap-1">
            {reasons.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        </div>

        <div className="flex flex-col gap-1.5 pt-2 border-t border-zinc-800/80">
          <span className="font-bold text-amber-300 flex items-center gap-1.5">
            <AlertCircle className="w-3.5 h-3.5 text-amber-400" />
            Trade-Offs & Compromises:
          </span>
          <ul className="list-disc pl-5 text-zinc-300 flex flex-col gap-1">
            {tradeoffs.map((t, i) => (
              <li key={i}>{t}</li>
            ))}
          </ul>
        </div>

        {unknowns.length > 0 && (
          <div className="flex flex-col gap-1.5 pt-2 border-t border-zinc-800/80">
            <span className="font-bold text-zinc-400 flex items-center gap-1.5">
              <HelpCircle className="w-3.5 h-3.5 text-zinc-400" />
              Remaining Uncertainties:
            </span>
            <ul className="list-disc pl-5 text-zinc-400 flex flex-col gap-1">
              {unknowns.map((u, i) => (
                <li key={i}>{u}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};
