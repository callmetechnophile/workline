"use client";

import React from "react";
import { Flame } from "lucide-react";

export interface ThermalMapProps {
  maxTempC?: number;
  minTempC?: number;
}

export const ThermalMap: React.FC<ThermalMapProps> = ({
  maxTempC,
  minTempC,
}) => {
  if (maxTempC === undefined && minTempC === undefined) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-8 text-center">
        <Flame className="w-8 h-8 text-slate-600 mx-auto mb-2" />
        <p className="text-xs text-slate-400">No thermal data available.</p>
        <p className="text-[10px] text-slate-500 mt-1">Create or select a project to view thermal data.</p>
      </div>
    );
  }

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4 text-zinc-100">
      <div className="flex items-center justify-between pb-2 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <Flame className="w-5 h-5 text-rose-400" />
          <h3 className="text-base font-bold text-zinc-100">Thermal Distribution Heatmap</h3>
        </div>
        <div className="flex items-center gap-2 text-xs font-mono">
          <span className="text-indigo-400">{minTempC !== undefined ? `${minTempC}°C` : ""}</span>
          <div className="w-24 h-2 rounded bg-gradient-to-r from-blue-600 via-yellow-500 to-red-600" />
          <span className="text-rose-400 font-bold">{maxTempC !== undefined ? `${maxTempC}°C` : ""}</span>
        </div>
      </div>

      <div className="relative w-full h-48 bg-zinc-950 border border-zinc-800 rounded-lg flex items-center justify-center overflow-hidden">
        {/* Heatmap gradient overlay */}
        <div className="w-4/5 h-4/5 rounded bg-gradient-to-tr from-blue-900/40 via-amber-700/30 to-red-600/50 flex items-center justify-center relative border border-zinc-700/60">
          <div className="w-12 h-12 rounded-full bg-red-500/60 blur-md absolute top-10 left-16 animate-pulse" />
          <span className="text-xs font-mono text-zinc-300 font-bold bg-zinc-950/80 px-2 py-1 rounded border border-zinc-800">
            {maxTempC !== undefined ? `Peak Temp: ${maxTempC}°C` : "Thermal Hotspot"}
          </span>
        </div>
      </div>
    </div>
  );
};
