"use client";

import React from "react";
import { Columns, Check, X } from "lucide-react";

export interface CandidateComparisonProps {
  candidates?: Array<{
    name: string;
    techFit: number;
    cost: string;
    availability: string;
    risk: string;
  }>;
}

export const CandidateComparison: React.FC<CandidateComparisonProps> = ({
  candidates,
}) => {
  if (!candidates || candidates.length === 0) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-8 text-center">
        <Columns className="w-8 h-8 text-slate-600 mx-auto mb-2" />
        <p className="text-xs text-slate-400">No candidates to compare.</p>
        <p className="text-[10px] text-slate-500 mt-1">Create or select a project to view candidate comparison.</p>
      </div>
    );
  }
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4 text-zinc-100">
      <div className="flex items-center gap-2 pb-2 border-b border-zinc-800">
        <Columns className="w-5 h-5 text-indigo-400" />
        <h3 className="text-base font-bold text-zinc-100">Candidate Comparison Matrix</h3>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {candidates.map((c) => (
          <div key={c.name} className="p-4 bg-zinc-950/60 border border-zinc-800 rounded-lg flex flex-col gap-3">
            <h4 className="text-sm font-bold text-indigo-300">{c.name}</h4>
            <div className="flex flex-col gap-1.5 text-xs font-mono">
              <div className="flex justify-between py-1 border-b border-zinc-900">
                <span className="text-zinc-400">Technical Fit:</span>
                <span className="text-zinc-100 font-bold">{c.techFit}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-zinc-900">
                <span className="text-zinc-400">Unit Cost:</span>
                <span className="text-emerald-400 font-bold">{c.cost}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-zinc-900">
                <span className="text-zinc-400">Availability:</span>
                <span className="text-zinc-100 font-bold">{c.availability}</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-zinc-400">Supply Risk:</span>
                <span className={c.risk === "LOW" ? "text-emerald-400" : "text-amber-400"}>{c.risk}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
