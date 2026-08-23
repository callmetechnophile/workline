"use client";

import React, { useState } from "react";
import { Cpu, Layers, Activity, ShieldCheck, Play, Download, Settings } from "lucide-react";

export interface PCBWorkspaceProps {
  pcbId?: string;
  projectName?: string;
  dimensions?: { width: number; height: number };
  layers?: number;
  componentCount?: number;
  netCount?: number;
  status?: string;
  onRunDRC?: () => void;
  onRunPINN?: () => void;
  onExportEDA?: (format: string) => void;
}

export const PCBWorkspace: React.FC<PCBWorkspaceProps> = ({
  pcbId,
  projectName,
  dimensions,
  layers,
  componentCount,
  netCount,
  status = "VALIDATION",
  onRunDRC,
  onRunPINN,
  onExportEDA,
}) => {
  if (!pcbId && !projectName && !dimensions) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-8 text-center">
        <Cpu className="w-8 h-8 text-slate-600 mx-auto mb-2" />
        <p className="text-xs text-slate-400">No PCB workspace active.</p>
        <p className="text-[10px] text-slate-500 mt-1">Create or select a project to view PCB workspace.</p>
      </div>
    );
  }

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-5 text-zinc-100">
      <div className="flex items-center justify-between pb-3 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <Cpu className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-zinc-100">PCB Engineering Workspace</h3>
          {(pcbId || projectName) && (
            <span className="text-xs font-mono text-zinc-500">
              [{[pcbId, projectName].filter(Boolean).join(" - ")}]
            </span>
          )}
        </div>
        <span className="px-2.5 py-0.5 rounded text-xs font-mono font-bold bg-indigo-950/60 text-indigo-300 border border-indigo-800">
          {status}
        </span>
      </div>

      <div className="grid grid-cols-4 gap-3">
        <div className="p-3 bg-zinc-950/60 border border-zinc-800 rounded-lg flex flex-col gap-1">
          <span className="text-xs text-zinc-400">Board Dimensions</span>
          <span className="text-base font-mono font-bold text-zinc-100">
            {dimensions ? `${dimensions.width} × ${dimensions.height} mm` : "—"}
          </span>
        </div>
        <div className="p-3 bg-zinc-950/60 border border-zinc-800 rounded-lg flex flex-col gap-1">
          <span className="text-xs text-zinc-400">Layer Stack</span>
          <span className="text-base font-mono font-bold text-indigo-300">
            {layers !== undefined ? `${layers} Layers` : "—"}
          </span>
        </div>
        <div className="p-3 bg-zinc-950/60 border border-zinc-800 rounded-lg flex flex-col gap-1">
          <span className="text-xs text-zinc-400">Components Placed</span>
          <span className="text-base font-mono font-bold text-emerald-400">
            {componentCount !== undefined ? `${componentCount} Parts` : "—"}
          </span>
        </div>
        <div className="p-3 bg-zinc-950/60 border border-zinc-800 rounded-lg flex flex-col gap-1">
          <span className="text-xs text-zinc-400">Configured Nets</span>
          <span className="text-base font-mono font-bold text-amber-300">
            {netCount !== undefined ? `${netCount} Nets` : "—"}
          </span>
        </div>
      </div>

      <div className="flex items-center justify-between pt-2 border-t border-zinc-800/80">
        <div className="flex items-center gap-2">
          <button
            onClick={onRunDRC}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-zinc-800 hover:bg-zinc-700 text-zinc-200 rounded text-xs font-semibold transition"
          >
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            Run Pre-DRC
          </button>
          <button
            onClick={onRunPINN}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-zinc-800 hover:bg-zinc-700 text-zinc-200 rounded text-xs font-semibold transition"
          >
            <Activity className="w-3.5 h-3.5 text-indigo-400" />
            PINN Physics Solver
          </button>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => onExportEDA && onExportEDA("kicad")}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-xs font-bold transition"
          >
            <Download className="w-3.5 h-3.5" />
            Export KiCad (.kicad_pcb)
          </button>
        </div>
      </div>
    </div>
  );
};
