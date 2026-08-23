"use client";

import React from "react";
import { Sliders, ShieldAlert, Check } from "lucide-react";

export interface ConstraintPanelProps {
  minTraceWidthMm?: number;
  minClearanceMm?: number;
  maxBoardTempC?: number;
  targetDiffImpedanceOhm?: number;
}

export const ConstraintPanel: React.FC<ConstraintPanelProps> = ({
  minTraceWidthMm,
  minClearanceMm,
  maxBoardTempC,
  targetDiffImpedanceOhm,
}) => {
  if (
    minTraceWidthMm === undefined &&
    minClearanceMm === undefined &&
    maxBoardTempC === undefined &&
    targetDiffImpedanceOhm === undefined
  ) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-8 text-center">
        <Sliders className="w-8 h-8 text-slate-600 mx-auto mb-2" />
        <p className="text-xs text-slate-400">No design constraints configured.</p>
        <p className="text-[10px] text-slate-500 mt-1">Create or select a project to view design constraints.</p>
      </div>
    );
  }

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4 text-zinc-100">
      <div className="flex items-center gap-2 pb-2 border-b border-zinc-800">
        <Sliders className="w-5 h-5 text-indigo-400" />
        <h3 className="text-base font-bold text-zinc-100">Design Constraints & Rules</h3>
      </div>

      <div className="grid grid-cols-2 gap-3 font-mono text-xs">
        <div className="p-3 bg-zinc-950/60 border border-zinc-800 rounded-lg flex flex-col gap-1">
          <span className="text-zinc-500">Min Trace Width</span>
          <span className="font-bold text-zinc-200">{minTraceWidthMm !== undefined ? `${minTraceWidthMm} mm` : "—"}</span>
        </div>
        <div className="p-3 bg-zinc-950/60 border border-zinc-800 rounded-lg flex flex-col gap-1">
          <span className="text-zinc-500">Min Clearance</span>
          <span className="font-bold text-zinc-200">{minClearanceMm !== undefined ? `${minClearanceMm} mm` : "—"}</span>
        </div>
        <div className="p-3 bg-zinc-950/60 border border-zinc-800 rounded-lg flex flex-col gap-1">
          <span className="text-zinc-500">Max Component Temp</span>
          <span className="font-bold text-rose-400">{maxBoardTempC !== undefined ? `${maxBoardTempC} °C` : "—"}</span>
        </div>
        <div className="p-3 bg-zinc-950/60 border border-zinc-800 rounded-lg flex flex-col gap-1">
          <span className="text-zinc-500">Diff Impedance (USB)</span>
          <span className="font-bold text-indigo-300">{targetDiffImpedanceOhm !== undefined ? `${targetDiffImpedanceOhm} Ω ± 10%` : "—"}</span>
        </div>
      </div>
    </div>
  );
};
