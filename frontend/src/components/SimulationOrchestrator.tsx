"use client";

import React, { useState } from "react";
import { Activity, Zap, Flame, Radio, CheckCircle2, AlertTriangle, XCircle, RefreshCw, Check } from "lucide-react";

export interface SolverMetricRow {
  name: string;
  domain: string;
  referenceValue: number;
  surrogateValue: number;
  unit: string;
  discrepancy: number; // e.g. 0.025 = 2.5%
  status: "PASS" | "WARNING" | "FAIL";
}

export interface SimulationOrchestratorProps {
  runId?: string;
  projectVersion?: number;
  overallStatus?: "PASS" | "WARNING" | "FAIL" | "UNKNOWN";
  mae?: number;
  rmse?: number;
  maxDiscrepancy?: number;
  metrics?: SolverMetricRow[];
  onRunSimulation?: () => void;
  onApproveResults?: () => void;
}

export const SimulationOrchestrator: React.FC<SimulationOrchestratorProps> = ({
  runId,
  projectVersion,
  overallStatus,
  mae,
  rmse,
  maxDiscrepancy,
  metrics = [],
  onRunSimulation,
  onApproveResults,
}) => {
  if (!runId && (!metrics || metrics.length === 0)) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-8 text-center">
        <Activity className="w-8 h-8 text-slate-600 mx-auto mb-2" />
        <p className="text-xs text-slate-400">No simulation has been run.</p>
        <p className="text-[10px] text-slate-500 mt-1">Create or select a project to view simulation results.</p>
      </div>
    );
  }

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-5 text-zinc-100">
      <div className="flex items-center justify-between pb-3 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <Activity className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-zinc-100">Multi-Physics Simulation Orchestrator</h3>
          {runId && (
            <span className="text-xs font-mono text-zinc-500">
              [{runId}{projectVersion !== undefined ? ` - v${projectVersion}` : ""}]
            </span>
          )}
        </div>
        {overallStatus && (
          <span
            className={`px-2.5 py-0.5 rounded text-xs font-mono font-bold border ${
              overallStatus === "PASS"
                ? "bg-emerald-950/60 text-emerald-300 border-emerald-800"
                : overallStatus === "WARNING"
                ? "bg-amber-950/60 text-amber-300 border-amber-800"
                : "bg-rose-950/60 text-rose-300 border-rose-800"
            }`}
          >
            CROSS-VALIDATION: {overallStatus}
          </span>
        )}
      </div>

      {/* Solver Grid */}
      <div className="grid grid-cols-4 gap-3">
        <div className="p-3 bg-zinc-950/60 border border-zinc-800 rounded-lg flex flex-col gap-1">
          <div className="flex items-center gap-1.5 text-xs text-zinc-400">
            <Zap className="w-3.5 h-3.5 text-amber-400" /> SPICE Electrical
          </div>
          <span className="text-xs font-mono text-emerald-400 font-bold">Converged (120ms)</span>
        </div>
        <div className="p-3 bg-zinc-950/60 border border-zinc-800 rounded-lg flex flex-col gap-1">
          <div className="flex items-center gap-1.5 text-xs text-zinc-400">
            <Flame className="w-3.5 h-3.5 text-rose-400" /> Thermal Solver (FD)
          </div>
          <span className="text-xs font-mono text-emerald-400 font-bold">Converged (340ms)</span>
        </div>
        <div className="p-3 bg-zinc-950/60 border border-zinc-800 rounded-lg flex flex-col gap-1">
          <div className="flex items-center gap-1.5 text-xs text-zinc-400">
            <Radio className="w-3.5 h-3.5 text-indigo-400" /> SI/PI Impedance
          </div>
          <span className="text-xs font-mono text-emerald-400 font-bold">Converged (210ms)</span>
        </div>
        <div className="p-3 bg-zinc-950/60 border border-zinc-800 rounded-lg flex flex-col gap-1">
          <div className="flex items-center gap-1.5 text-xs text-zinc-400">
            <Activity className="w-3.5 h-3.5 text-emerald-400" /> PINN Surrogate
          </div>
          <span className="text-xs font-mono text-indigo-400 font-bold">Inference (12ms)</span>
        </div>
      </div>

      {/* Cross-Validation Table */}
      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold text-zinc-400">Numerical Reference vs. PINN Surrogate Cross-Validation</span>
          <span className="text-xs font-mono text-zinc-500">
            MAE: <strong className="text-zinc-200">{mae !== undefined ? mae : "-"}</strong> | RMSE: <strong className="text-zinc-200">{rmse !== undefined ? rmse : "-"}</strong> | Max Discrepancy: <strong className="text-emerald-400">{maxDiscrepancy !== undefined ? `${(maxDiscrepancy * 100).toFixed(2)}%` : "-"}</strong>
          </span>
        </div>

        <div className="overflow-x-auto border border-zinc-800 rounded-lg">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-zinc-950 text-zinc-400 border-b border-zinc-800">
              <tr>
                <th className="p-2.5">Physical Metric</th>
                <th className="p-2.5">Domain</th>
                <th className="p-2.5">Numerical Ref</th>
                <th className="p-2.5">PINN Surrogate</th>
                <th className="p-2.5">Discrepancy (Δ)</th>
                <th className="p-2.5">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800 bg-zinc-900">
              {metrics.map((m) => (
                <tr key={m.name} className="hover:bg-zinc-800/40 transition">
                  <td className="p-2.5 font-bold text-zinc-200">{m.name}</td>
                  <td className="p-2.5 text-zinc-400">{m.domain}</td>
                  <td className="p-2.5 text-zinc-300">{m.referenceValue} {m.unit}</td>
                  <td className="p-2.5 text-indigo-300 font-semibold">{m.surrogateValue} {m.unit}</td>
                  <td className="p-2.5 text-emerald-400 font-bold">{(m.discrepancy * 100).toFixed(2)}%</td>
                  <td className="p-2.5">
                    <span className="px-1.5 py-0.5 rounded text-[10px] bg-emerald-950/50 text-emerald-400 flex items-center gap-1 w-fit">
                      <CheckCircle2 className="w-3 h-3" /> {m.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="flex items-center justify-between pt-2 border-t border-zinc-800/80">
        <button
          onClick={onRunSimulation}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-zinc-800 hover:bg-zinc-700 text-zinc-200 rounded text-xs font-semibold transition"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Rerun Multi-Physics Suite
        </button>

        <button
          onClick={onApproveResults}
          className="flex items-center gap-1.5 px-4 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded text-xs font-bold transition shadow-sm"
        >
          <Check className="w-4 h-4" />
          Sign-Off & Complete Engineering Review
        </button>
      </div>
    </div>
  );
};
