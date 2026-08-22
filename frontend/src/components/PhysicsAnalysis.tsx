"use client";

import React from "react";
import { Activity, Flame, AlertTriangle, ShieldCheck } from "lucide-react";

export interface PhysicsAnalysisProps {
  modelId?: string;
  modelVersion?: string;
  peakTempC?: number;
  avgTempC?: number;
  hotspots?: Array<{ ref: string; tempC: number }>;
  isOod?: boolean;
}

export const PhysicsAnalysis: React.FC<PhysicsAnalysisProps> = ({
  modelId = "PCB-THERMAL-v1",
  modelVersion = "1.0.0",
  peakTempC = 78.4,
  avgTempC = 42.1,
  hotspots = [{ ref: "U1", tempC: 78.4 }],
  isOod = false,
}) => {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4 text-zinc-100">
      <div className="flex items-center justify-between pb-2 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <Activity className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-zinc-100">Physics-Informed Neural Network (PINN)</h3>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-950/60 text-amber-300 border border-amber-800">
          MODEL PREDICTION
        </span>
      </div>

      <div className="grid grid-cols-2 gap-3 font-mono text-xs">
        <div className="p-3 bg-zinc-950/60 border border-zinc-800 rounded-lg flex flex-col gap-1">
          <span className="text-zinc-500">Estimated Peak Temp</span>
          <span className="font-bold text-rose-400 text-base">{peakTempC.toFixed(1)} °C</span>
        </div>
        <div className="p-3 bg-zinc-950/60 border border-zinc-800 rounded-lg flex flex-col gap-1">
          <span className="text-zinc-500">Average Board Temp</span>
          <span className="font-bold text-amber-300 text-base">{avgTempC.toFixed(1)} °C</span>
        </div>
      </div>

      <div className="flex flex-col gap-2">
        <span className="text-xs font-bold text-zinc-400">Detected Hotspots:</span>
        <div className="flex flex-col gap-1.5 font-mono text-xs">
          {hotspots.map((h, idx) => (
            <div key={idx} className="p-2.5 bg-rose-950/20 border border-rose-900/60 rounded flex items-center justify-between text-rose-300">
              <div className="flex items-center gap-2">
                <Flame className="w-3.5 h-3.5 text-rose-400" />
                <span>Component <strong>{h.ref}</strong> (Power Regulator)</span>
              </div>
              <span className="font-bold">{h.tempC.toFixed(1)} °C</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
