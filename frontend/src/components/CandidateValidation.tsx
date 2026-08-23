"use client";

import React from "react";
import { Cpu, CheckCircle2, XCircle, ArrowRight } from "lucide-react";

export interface CandidateItem {
  candidateId: string;
  name: string;
  manufacturer: string;
  overallStatus: "PASS" | "FAIL" | "UNKNOWN" | "CONFLICT";
  specsMatchCount: number;
  totalConstraints: number;
}

interface CandidateValidationProps {
  requirementId?: string;
  candidates?: CandidateItem[];
  onSelectCandidate?: (candidateId: string) => void;
}

export const CandidateValidation: React.FC<CandidateValidationProps> = ({
  requirementId,
  candidates,
  onSelectCandidate,
}) => {
  if (!candidates || candidates.length === 0) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-8 text-center">
        <Cpu className="w-8 h-8 text-slate-600 mx-auto mb-2" />
        <p className="text-xs text-slate-400">No validation data available.</p>
        <p className="text-[10px] text-slate-500 mt-1">Create or select a project to view validation data.</p>
      </div>
    );
  }
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4 text-zinc-100">
      <div className="flex items-center justify-between pb-2 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <Cpu className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-zinc-100">Candidate Evaluation Set</h3>
        </div>
        <span className="text-xs font-mono text-zinc-400">{candidates.length} Components Evaluated</span>
      </div>

      <div className="flex flex-col gap-2.5">
        {candidates.map((c) => (
          <div
            key={c.candidateId}
            onClick={() => onSelectCandidate && onSelectCandidate(c.candidateId)}
            className="p-3.5 bg-zinc-950/60 border border-zinc-800 rounded-lg flex items-center justify-between hover:border-zinc-700 transition cursor-pointer"
          >
            <div className="flex flex-col gap-1">
              <div className="flex items-center gap-2">
                <span className="text-sm font-bold text-zinc-100">{c.name}</span>
                <span className="text-xs text-zinc-500 font-mono">({c.manufacturer})</span>
              </div>
              <span className="text-[11px] font-mono text-zinc-400">
                Matched {c.specsMatchCount}/{c.totalConstraints} constraints
              </span>
            </div>

            <span
              className={`px-2.5 py-1 rounded text-xs font-mono font-bold border ${
                c.overallStatus === "PASS"
                  ? "bg-emerald-950/60 text-emerald-300 border-emerald-800"
                  : "bg-rose-950/60 text-rose-300 border-rose-800"
              }`}
            >
              {c.overallStatus}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
