"use client";

import React, { useState } from "react";
import { Flame, Thermometer, AlertTriangle, ShieldCheck, RefreshCw } from "lucide-react";

export interface ThermalHotspot {
  component: string;
  x: number;
  y: number;
  predicted_temp: number;
}

export interface ThermalAnalysisData {
  ambient_temperature: number;
  predicted_peak_temperature: number;
  predicted_min_temperature: number;
  predicted_avg_temperature: number;
  hotspots: ThermalHotspot[];
}

interface ThermalAnalysisPanelProps {
  thermalData: ThermalAnalysisData;
  onRunInference?: () => Promise<void>;
  isRunning?: boolean;
}

export const ThermalAnalysisPanel: React.FC<ThermalAnalysisPanelProps> = ({
  thermalData,
  onRunInference,
  isRunning = false,
}) => {
  const isHot = thermalData.predicted_peak_temperature > 70.0;

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-2xl backdrop-blur-md space-y-4">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-rose-500/10 border border-rose-500/20 rounded-lg text-rose-400">
            <Flame className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
              STEADY-STATE THERMAL ANALYSIS
              <span className="text-[10px] font-mono bg-rose-500/10 text-rose-400 px-2 py-0.5 rounded border border-rose-500/20 font-semibold">
                PINN PREDICTION
              </span>
            </h3>
            <p className="text-xs text-slate-400">Conduction-convection heat equation field solution</p>
          </div>
        </div>

        {onRunInference && (
          <button
            onClick={onRunInference}
            disabled={isRunning}
            className="px-3.5 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold flex items-center gap-1.5 transition-all shadow-lg shadow-rose-950/30 disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRunning ? "animate-spin" : ""}`} /> Recalculate PINN Field
          </button>
        )}
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="bg-slate-950/60 p-3.5 rounded-lg border border-slate-800">
          <span className="text-[11px] text-slate-400">Peak Board Temp:</span>
          <div className="font-mono text-xl font-bold text-rose-400">
            {thermalData.predicted_peak_temperature.toFixed(1)} °C
          </div>
        </div>
        <div className="bg-slate-950/60 p-3.5 rounded-lg border border-slate-800">
          <span className="text-[11px] text-slate-400">Ambient Temp:</span>
          <div className="font-mono text-xl font-bold text-cyan-400">
            {thermalData.ambient_temperature.toFixed(1)} °C
          </div>
        </div>
        <div className="bg-slate-950/60 p-3.5 rounded-lg border border-slate-800">
          <span className="text-[11px] text-slate-400">Average Temp:</span>
          <div className="font-mono text-xl font-bold text-slate-200">
            {thermalData.predicted_avg_temperature.toFixed(1)} °C
          </div>
        </div>
        <div className="bg-slate-950/60 p-3.5 rounded-lg border border-slate-800">
          <span className="text-[11px] text-slate-400">Thermal Status:</span>
          <div className={`font-bold text-sm mt-1 flex items-center gap-1 ${
            isHot ? "text-amber-400" : "text-emerald-400"
          }`}>
            {isHot ? <AlertTriangle className="w-4 h-4" /> : <ShieldCheck className="w-4 h-4" />}
            {isHot ? "Hotspot Warning" : "Optimal"}
          </div>
        </div>
      </div>

      {/* Hotspots Breakdown */}
      {thermalData.hotspots.length > 0 && (
        <div className="space-y-2 pt-2">
          <div className="text-xs font-semibold text-slate-300 uppercase tracking-wider text-[10px]">
            Localized Hotspot Components
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {thermalData.hotspots.map((h, i) => (
              <div
                key={i}
                className="bg-slate-950/40 border border-slate-800 p-2.5 rounded-lg flex items-center justify-between text-xs"
              >
                <div>
                  <span className="font-bold text-slate-200">{h.component}</span>
                  <span className="text-[10px] text-slate-500 font-mono ml-2">({h.x.toFixed(1)}, {h.y.toFixed(1)}mm)</span>
                </div>
                <div className="font-mono font-bold text-rose-400">
                  {h.predicted_temp.toFixed(1)} °C
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ThermalAnalysisPanel;
