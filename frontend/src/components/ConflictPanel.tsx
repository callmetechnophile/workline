"use client";

import React from "react";
import { AlertTriangle, Check, X, FileText } from "lucide-react";

export interface ConflictItem {
  conflictId: string;
  entityId: string;
  property: string;
  valueA: string;
  sourceA: string;
  valueB: string;
  sourceB: string;
  status: string;
}

interface ConflictPanelProps {
  conflicts?: ConflictItem[];
  onResolve?: (conflictId: string, choice: "A" | "B" | "BOTH") => void;
}

export const ConflictPanel: React.FC<ConflictPanelProps> = ({
  conflicts = [],
  onResolve,
}) => {
  if (!conflicts || (Array.isArray(conflicts) && conflicts.length === 0)) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-8 text-center">
        <AlertTriangle className="w-8 h-8 text-slate-600 mx-auto mb-2" />
        <p className="text-xs text-slate-400">No conflicts detected.</p>
        <p className="text-[10px] text-slate-500 mt-1">Create or select a project to view conflicts.</p>
      </div>
    );
  }
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4 text-zinc-100">
      <div className="flex items-center justify-between pb-2 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-amber-400" />
          <h3 className="text-base font-bold text-zinc-100">Specification Conflicts</h3>
        </div>
        <span className="text-xs font-mono text-amber-400">{conflicts.length} Open Conflicts</span>
      </div>

      {conflicts.length === 0 ? (
        <div className="p-4 text-center text-xs text-zinc-500 font-mono">
          No conflicting specifications detected across documents.
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {conflicts.map((c) => (
            <div
              key={c.conflictId}
              className="p-4 bg-amber-950/20 border border-amber-800/60 rounded-lg flex flex-col gap-3"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-amber-300">{c.entityId}</span>
                  <span className="text-xs text-zinc-400">• Property: <strong className="text-zinc-200">{c.property}</strong></span>
                </div>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-amber-950 text-amber-300 border border-amber-800">
                  {c.status}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="p-3 bg-zinc-950 border border-zinc-800 rounded flex flex-col gap-1">
                  <span className="text-[10px] font-mono text-zinc-500">Source A</span>
                  <span className="font-bold text-emerald-400">{c.valueA}</span>
                  <span className="text-[11px] text-zinc-400 truncate">{c.sourceA}</span>
                  {onResolve && (
                    <button
                      onClick={() => onResolve(c.conflictId, "A")}
                      className="mt-2 py-1 px-2 text-[10px] font-semibold bg-zinc-800 hover:bg-zinc-700 text-zinc-200 rounded border border-zinc-700 transition"
                    >
                      Accept Source A
                    </button>
                  )}
                </div>

                <div className="p-3 bg-zinc-950 border border-zinc-800 rounded flex flex-col gap-1">
                  <span className="text-[10px] font-mono text-zinc-500">Source B</span>
                  <span className="font-bold text-rose-400">{c.valueB}</span>
                  <span className="text-[11px] text-zinc-400 truncate">{c.sourceB}</span>
                  {onResolve && (
                    <button
                      onClick={() => onResolve(c.conflictId, "B")}
                      className="mt-2 py-1 px-2 text-[10px] font-semibold bg-zinc-800 hover:bg-zinc-700 text-zinc-200 rounded border border-zinc-700 transition"
                    >
                      Accept Source B
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
