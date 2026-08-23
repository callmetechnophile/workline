"use client";

import React, { useState } from "react";
import { GitPullRequest, Sliders, CheckCircle2, XCircle, AlertTriangle, ShieldCheck } from "lucide-react";

export interface DecisionWorkspaceProps {
  decisionId?: string;
  requirementTitle?: string;
  recommendedCandidate?: string;
  candidates?: Array<{ name: string; eligibility: string; score: number; risk: string }>;
  stability?: "ROBUST" | "MODERATELY_STABLE" | "SENSITIVE" | "UNSTABLE";
  status?: string;
  onApprove?: () => void;
  onReject?: () => void;
}

export const DecisionWorkspace: React.FC<DecisionWorkspaceProps> = ({
  decisionId,
  requirementTitle,
  recommendedCandidate,
  candidates = [],
  stability = "ROBUST",
  status = "RECOMMENDED",
  onApprove,
  onReject,
}) => {
  if (!decisionId || candidates.length === 0) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-8 text-center">
        <GitPullRequest className="w-8 h-8 text-slate-600 mx-auto mb-2" />
        <p className="text-xs text-slate-400">No decision pending.</p>
        <p className="text-[10px] text-slate-500 mt-1">Create or select a project to view decision workspace.</p>
      </div>
    );
  }

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-5 text-zinc-100">
      <div className="flex items-center justify-between pb-3 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <GitPullRequest className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-zinc-100">Engineering Design Decision</h3>
          <span className="text-xs font-mono text-zinc-500">[{decisionId}]</span>
        </div>
        <span
          className={`px-2.5 py-0.5 rounded text-xs font-mono font-bold border ${
            status === "APPROVED"
              ? "bg-emerald-950/60 text-emerald-300 border-emerald-800"
              : status === "RECOMMENDED"
              ? "bg-indigo-950/60 text-indigo-300 border-indigo-800"
              : "bg-amber-950/60 text-amber-300 border-amber-800"
          }`}
        >
          {status}
        </span>
      </div>

      <div className="flex flex-col gap-1">
        <span className="text-xs text-zinc-400">Target Requirement:</span>
        <p className="text-sm font-semibold text-zinc-200">{requirementTitle}</p>
      </div>

      <div className="flex flex-col gap-2">
        <span className="text-xs font-bold text-zinc-400">Candidate Evaluation & Scoring</span>
        <div className="overflow-x-auto border border-zinc-800 rounded-lg">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-zinc-950/80 text-zinc-400 border-b border-zinc-800">
              <tr>
                <th className="p-2.5">Candidate</th>
                <th className="p-2.5">Eligibility</th>
                <th className="p-2.5">Score</th>
                <th className="p-2.5">Risk</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800 bg-zinc-900">
              {candidates.map((c) => (
                <tr key={c.name} className={c.name === recommendedCandidate ? "bg-indigo-950/20" : ""}>
                  <td className="p-2.5 font-bold text-zinc-200">{c.name}</td>
                  <td className="p-2.5">
                    <span
                      className={`px-1.5 py-0.5 rounded text-[10px] ${
                        c.eligibility === "PASS" ? "text-emerald-400 bg-emerald-950/40" : "text-amber-400 bg-amber-950/40"
                      }`}
                    >
                      {c.eligibility}
                    </span>
                  </td>
                  <td className="p-2.5 font-bold text-indigo-300">{c.score > 0 ? c.score : "--"}</td>
                  <td className="p-2.5">
                    <span className={c.risk === "LOW" ? "text-emerald-400" : c.risk === "MED" ? "text-amber-400" : "text-rose-400"}>
                      {c.risk}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="p-4 bg-zinc-950/70 border border-zinc-800 rounded-lg flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold text-indigo-300">RECOMMENDED SELECTION:</span>
          <span className="text-[10px] font-mono text-emerald-400 border border-emerald-800 px-2 py-0.5 rounded bg-emerald-950/40">
            Stability: {stability}
          </span>
        </div>
        <p className="text-sm font-bold text-zinc-100">{recommendedCandidate}</p>
        <p className="text-xs text-zinc-400">
          Selected based on highest deterministic multi-criteria score, passing all mandatory electrical constraints with verified datasheet evidence.
        </p>

        {status !== "APPROVED" && (
          <div className="flex items-center gap-2 pt-3 border-t border-zinc-900">
            <button
              onClick={onApprove}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded text-xs font-semibold transition"
            >
              <CheckCircle2 className="w-3.5 h-3.5" />
              Approve Decision
            </button>
            <button
              onClick={onReject}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-zinc-800 hover:bg-rose-950/60 hover:text-rose-300 text-zinc-300 rounded text-xs font-semibold transition"
            >
              <XCircle className="w-3.5 h-3.5" />
              Reject
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
