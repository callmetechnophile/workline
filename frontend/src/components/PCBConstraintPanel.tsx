"use client";

import React from "react";
import { ShieldCheck, Ruler, Activity, Layers, Tag } from "lucide-react";

export interface ConstraintItemData {
  name: string;
  value: number;
  unit: string;
  source: "USER" | "DATASHEET" | "ENGINEERING_RULE" | "MANUFACTURING_RULE";
  source_reference?: string;
}

interface PCBConstraintPanelProps {
  constraints: ConstraintItemData[];
}

export const PCBConstraintPanel: React.FC<PCBConstraintPanelProps> = ({ constraints }) => {
  const getSourceBadge = (src: string) => {
    switch (src) {
      case "DATASHEET":
        return "bg-cyan-500/10 text-cyan-400 border-cyan-500/30";
      case "MANUFACTURING_RULE":
        return "bg-amber-500/10 text-amber-400 border-amber-500/30";
      case "USER":
        return "bg-purple-500/10 text-purple-400 border-purple-500/30";
      default:
        return "bg-slate-800 text-slate-300 border-slate-700";
    }
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-2xl backdrop-blur-md space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-indigo-500/10 border border-indigo-500/20 rounded-lg text-indigo-400">
            <Ruler className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-100">DESIGN CONSTRAINTS & PROVENANCE</h3>
            <p className="text-xs text-slate-400">Physical clearance limits, trace bounds, and thermal ceilings</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {constraints.map((c, idx) => (
          <div
            key={idx}
            className="bg-slate-950/60 p-3.5 rounded-lg border border-slate-800 flex items-center justify-between text-xs space-y-1"
          >
            <div>
              <div className="font-semibold text-slate-200">{c.name.replace(/_/g, " ")}</div>
              <div className="text-[10px] text-slate-500">{c.source_reference || "Standard Rule"}</div>
            </div>
            <div className="text-right space-y-1">
              <div className="font-mono text-sm font-bold text-emerald-400">
                {c.value} <span className="text-xs text-slate-400">{c.unit}</span>
              </div>
              <span className={`px-2 py-0.5 rounded text-[9px] font-semibold border ${getSourceBadge(c.source)}`}>
                {c.source}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PCBConstraintPanel;
