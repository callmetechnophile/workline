"use client";

import React from "react";
import { Sliders, Sparkles, TrendingDown, ArrowRight, CheckCircle2 } from "lucide-react";

export interface OptimizationStep {
  iteration: number;
  component_moved: string;
  previous_position: [number, number];
  new_position: [number, number];
  peak_temperature: number;
  temperature_reduction: number;
}

export interface OptimizationData {
  initial_peak_temperature: number;
  optimized_peak_temperature: number;
  temperature_reduction_celsius: number;
  iterations_evaluated: number;
  accepted_moves_count: number;
  history: OptimizationStep[];
}

interface PCBOptimizationPanelProps {
  optimizationResult?: OptimizationData | null;
  onRunOptimization: (iterations: number) => Promise<void>;
  isOptimizing?: boolean;
}

export const PCBOptimizationPanel: React.FC<PCBOptimizationPanelProps> = ({
  optimizationResult,
  onRunOptimization,
  isOptimizing = false,
}) => {
  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-2xl backdrop-blur-md space-y-4">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-amber-500/10 border border-amber-500/20 rounded-lg text-amber-400">
            <Sliders className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-100">THERMAL PLACEMENT OPTIMIZER</h3>
            <p className="text-xs text-slate-400">Bounded search minimizing peak junction and board temperatures</p>
          </div>
        </div>

        <button
          onClick={() => onRunOptimization(50)}
          disabled={isOptimizing}
          className="px-4 py-2 rounded-lg bg-amber-600 hover:bg-amber-500 text-white text-xs font-semibold flex items-center gap-1.5 transition-all shadow-lg shadow-amber-950/30 disabled:opacity-50"
        >
          {isOptimizing ? <Sparkles className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
          {isOptimizing ? "Optimizing Layout..." : "Run Thermal Optimization"}
        </button>
      </div>

      {optimizationResult ? (
        <div className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="bg-slate-950/60 p-3.5 rounded-lg border border-slate-800">
              <span className="text-[11px] text-slate-400">Initial Hotspot Temp:</span>
              <div className="font-mono text-xl font-bold text-rose-400 mt-0.5">
                {optimizationResult.initial_peak_temperature.toFixed(1)} °C
              </div>
            </div>
            <div className="bg-slate-950/60 p-3.5 rounded-lg border border-slate-800">
              <span className="text-[11px] text-slate-400">Optimized Peak Temp:</span>
              <div className="font-mono text-xl font-bold text-emerald-400 mt-0.5">
                {optimizationResult.optimized_peak_temperature.toFixed(1)} °C
              </div>
            </div>
            <div className="bg-slate-950/60 p-3.5 rounded-lg border border-slate-800">
              <span className="text-[11px] text-slate-400">Thermal Reduction:</span>
              <div className="font-mono text-xl font-bold text-cyan-400 mt-0.5 flex items-center gap-1">
                <TrendingDown className="w-5 h-5 text-emerald-400" />
                -{optimizationResult.temperature_reduction_celsius.toFixed(1)} °C
              </div>
            </div>
          </div>

          {/* Iteration History Table */}
          {optimizationResult.history.length > 0 && (
            <div className="space-y-2">
              <div className="text-xs font-semibold text-slate-300 uppercase tracking-wider text-[10px]">
                Accepted Relocation Moves ({optimizationResult.history.length})
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse font-mono">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider font-sans">
                      <th className="pb-2">Iter</th>
                      <th className="pb-2">Component</th>
                      <th className="pb-2">From Pos</th>
                      <th className="pb-2">To Pos</th>
                      <th className="pb-2 text-right">Resulting Peak</th>
                      <th className="pb-2 text-right">Delta</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {optimizationResult.history.map((step) => (
                      <tr key={step.iteration} className="hover:bg-slate-800/30">
                        <td className="py-2 text-slate-500">#{step.iteration}</td>
                        <td className="py-2 text-cyan-400 font-bold">{step.component_moved}</td>
                        <td className="py-2 text-slate-400">({step.previous_position[0].toFixed(1)}, {step.previous_position[1].toFixed(1)})</td>
                        <td className="py-2 text-emerald-400">({step.new_position[0].toFixed(1)}, {step.new_position[1].toFixed(1)})</td>
                        <td className="py-2 text-right text-rose-400 font-semibold">{step.peak_temperature.toFixed(1)} °C</td>
                        <td className="py-2 text-right text-emerald-400 font-semibold">-{step.temperature_reduction.toFixed(1)} °C</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="bg-slate-950/40 border border-slate-800 rounded-xl p-6 text-center text-xs text-slate-500">
          Click <strong>"Run Thermal Optimization"</strong> to relocate heat-dissipating ICs and minimize board hotspot temperatures.
        </div>
      )}
    </div>
  );
};

export default PCBOptimizationPanel;
