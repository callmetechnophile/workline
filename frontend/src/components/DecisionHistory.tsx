"use client";

import React from "react";
import { History, GitCommit, ArrowRight, ShieldCheck } from "lucide-react";

export interface DecisionHistoryRecord {
  version: number;
  title: string;
  selectedCandidate: string;
  status: string;
  actor: string;
  timestamp: string;
  supersededBy?: string;
}

export interface DecisionHistoryProps {
  decisionId?: string;
  history?: DecisionHistoryRecord[];
}

export const DecisionHistory: React.FC<DecisionHistoryProps> = ({
  decisionId,
  history = [],
}) => {
  if (!history || history.length === 0) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-8 text-center">
        <History className="w-8 h-8 text-slate-600 mx-auto mb-2" />
        <p className="text-xs text-slate-400">No decision history.</p>
        <p className="text-[10px] text-slate-500 mt-1">Create or select a project to view decision history.</p>
      </div>
    );
  }

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4 text-zinc-100">
      <div className="flex items-center gap-2 pb-2 border-b border-zinc-800">
        <History className="w-5 h-5 text-indigo-400" />
        <h3 className="text-base font-bold text-zinc-100">Decision Audit & Supersession History</h3>
      </div>

      <div className="flex flex-col gap-3 font-mono text-xs">
        {history.map((h) => (
          <div key={h.version} className="p-3 bg-zinc-950/60 border border-zinc-800 rounded-lg flex flex-col gap-1.5">
            <div className="flex items-center justify-between">
              <span className="font-bold text-indigo-300">
                v{h.version}: {h.title}
              </span>
              <span
                className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                  h.status === "APPROVED"
                    ? "bg-emerald-950/60 text-emerald-300 border border-emerald-800"
                    : "bg-amber-950/60 text-amber-300 border border-amber-800"
                }`}
              >
                {h.status}
              </span>
            </div>
            <div className="text-zinc-300">
              Selected: <strong className="text-zinc-100">{h.selectedCandidate}</strong>
            </div>
            <div className="text-[11px] text-zinc-500 flex items-center justify-between pt-1 border-t border-zinc-900">
              <span>Sign-off: {h.actor}</span>
              <span>{h.timestamp}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
