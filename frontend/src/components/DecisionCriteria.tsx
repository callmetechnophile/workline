"use client";

import React from "react";
import { Sliders, Percent } from "lucide-react";

export interface CriterionItem {
  id: string;
  name: string;
  weight: number;
  direction: "MAXIMIZE" | "MINIMIZE" | "TARGET";
  mandatory: boolean;
}

export interface DecisionCriteriaProps {
  criteria?: CriterionItem[];
  onWeightChange?: (id: string, weight: number) => void;
}

export const DecisionCriteria: React.FC<DecisionCriteriaProps> = ({
  criteria = [
    { id: "tech", name: "Technical Fit", weight: 0.4, direction: "MAXIMIZE", mandatory: true },
    { id: "cost", name: "Unit Cost", weight: 0.2, direction: "MINIMIZE", mandatory: false },
    { id: "avail", name: "Supplier Availability", weight: 0.2, direction: "MAXIMIZE", mandatory: false },
    { id: "risk", name: "Supply Chain Risk", weight: 0.2, direction: "MINIMIZE", mandatory: false },
  ],
  onWeightChange,
}) => {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4 text-zinc-100">
      <div className="flex items-center justify-between pb-2 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <Sliders className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-zinc-100">Decision Criteria & Weights</h3>
        </div>
        <span className="text-xs font-mono text-zinc-400">Total Weight: 100%</span>
      </div>

      <div className="flex flex-col gap-3">
        {criteria.map((c) => (
          <div key={c.id} className="p-3 bg-zinc-950/50 border border-zinc-800/80 rounded-lg flex flex-col gap-1.5">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-zinc-200">
                {c.name} {c.mandatory && <span className="text-rose-400 text-[10px]">*Mandatory</span>}
              </span>
              <span className="font-mono text-indigo-300 font-bold">{Math.round(c.weight * 100)}%</span>
            </div>
            <div className="w-full bg-zinc-800 h-1.5 rounded-full overflow-hidden">
              <div className="bg-indigo-500 h-full rounded-full" style={{ width: `${c.weight * 100}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
