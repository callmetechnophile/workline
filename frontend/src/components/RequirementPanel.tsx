"use client";

import React, { useState } from "react";
import { CheckSquare, Plus, Layers, AlertCircle, Bookmark } from "lucide-react";

export interface ConstraintItem {
  constraintId: string;
  property: string;
  operator: string;
  requiredValue: string;
  dimension: string;
}

export interface RequirementItem {
  requirementId: string;
  projectId: string;
  category: string;
  description: string;
  constraints: ConstraintItem[];
  priority: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  status: string;
}

interface RequirementPanelProps {
  requirements?: RequirementItem[];
  selectedReqId?: string;
  onSelectRequirement?: (reqId: string) => void;
  onCreateRequirement?: (desc: string, category: string) => void;
}

export const RequirementPanel: React.FC<RequirementPanelProps> = ({
  requirements = [],
  selectedReqId,
  onSelectRequirement,
  onCreateRequirement,
}) => {
  const [newDesc, setNewDesc] = useState("");

  if (!requirements || requirements.length === 0) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-8 text-center">
        <CheckSquare className="w-8 h-8 text-slate-600 mx-auto mb-2" />
        <p className="text-xs text-slate-400">No requirements defined.</p>
        <p className="text-[10px] text-slate-500 mt-1">Create or select a project to view requirements.</p>
      </div>
    );
  }

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4 text-zinc-100">
      <div className="flex items-center justify-between pb-2 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <CheckSquare className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-zinc-100">Engineering Requirements</h3>
        </div>
        <span className="text-xs font-mono text-zinc-400">{requirements.length} Active Requirements</span>
      </div>

      <div className="flex flex-col gap-2.5">
        {requirements.map((req) => {
          const isSelected = req.requirementId === selectedReqId;
          return (
            <div
              key={req.requirementId}
              onClick={() => onSelectRequirement && onSelectRequirement(req.requirementId)}
              className={`p-3.5 rounded-lg border transition cursor-pointer flex flex-col gap-2 ${
                isSelected
                  ? "bg-indigo-950/40 border-indigo-500/80 text-zinc-100"
                  : "bg-zinc-950/60 border-zinc-800 hover:border-zinc-700 text-zinc-300"
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold text-zinc-100">{req.requirementId}</span>
                  <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-zinc-800 text-zinc-400 border border-zinc-700">
                    {req.category}
                  </span>
                </div>
                <span
                  className={`px-2 py-0.5 rounded text-[10px] font-mono border ${
                    req.priority === "CRITICAL"
                      ? "bg-rose-950/60 text-rose-300 border-rose-800"
                      : "bg-amber-950/60 text-amber-300 border-amber-800"
                  }`}
                >
                  {req.priority}
                </span>
              </div>

              <p className="text-xs text-zinc-300">{req.description}</p>

              <div className="flex items-center gap-2 flex-wrap pt-1">
                {req.constraints.map((c) => (
                  <span
                    key={c.constraintId}
                    className="px-2 py-0.5 rounded text-[10px] font-mono bg-zinc-900 text-indigo-300 border border-zinc-800"
                  >
                    {c.property} {c.operator} {c.requiredValue}
                  </span>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
