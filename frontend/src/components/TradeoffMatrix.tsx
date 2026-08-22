"use client";

import React from "react";
import { ArrowLeftRight, Plus, Minus } from "lucide-react";

export interface TradeoffMatrixProps {
  candidateA?: string;
  candidateB?: string;
  tradeoffs?: Array<{
    criterion: string;
    advCandidate: string;
    scoreDelta: number;
  }>;
}

export const TradeoffMatrix: React.FC<TradeoffMatrixProps> = ({
  candidateA = "TPS62130",
  candidateB = "LM2596-5",
  tradeoffs = [
    { criterion: "Technical Fit", advCandidate: "TPS62130", scoreDelta: 0.1 },
    { criterion: "Unit Cost", advCandidate: "LM2596-5", scoreDelta: 0.1 },
    { criterion: "Package Compactness", advCandidate: "TPS62130", scoreDelta: 0.2 },
  ],
}) => {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4 text-zinc-100">
      <div className="flex items-center gap-2 pb-2 border-b border-zinc-800">
        <ArrowLeftRight className="w-5 h-5 text-indigo-400" />
        <h3 className="text-base font-bold text-zinc-100">
          Pairwise Trade-Offs: {candidateA} vs {candidateB}
        </h3>
      </div>

      <div className="flex flex-col gap-2">
        {tradeoffs.map((t, idx) => (
          <div key={idx} className="p-3 bg-zinc-950/60 border border-zinc-800 rounded-lg flex items-center justify-between text-xs">
            <span className="text-zinc-300 font-semibold">{t.criterion}</span>
            <span className="flex items-center gap-1.5 font-mono text-emerald-400 font-bold">
              <Plus className="w-3.5 h-3.5" />
              {t.advCandidate} (+{t.scoreDelta})
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
