"use client";

import React from "react";
import { Activity, Zap, Compass, Thermometer } from "lucide-react";

export interface FeaturePointData {
  x: number;
  y: number;
  normalized_x: number;
  normalized_y: number;
  power_density_w_per_mm2: number;
  effective_conductivity: number;
  convection_coefficient: number;
  ambient_temperature: number;
  distance_to_nearest_heat_source: number;
  distance_to_board_edge: number;
}

interface PCBPhysicsPanelProps {
  features: FeaturePointData[];
}

export const PCBPhysicsPanel: React.FC<PCBPhysicsPanelProps> = ({ features }) => {
  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-2xl backdrop-blur-md space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-purple-500/10 border border-purple-500/20 rounded-lg text-purple-400">
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-100">PHYSICS FEATURE ENGINE</h3>
            <p className="text-xs text-slate-400">Deterministic numerical spatial and thermal features across PCB mesh</p>
          </div>
        </div>
        <span className="font-mono text-xs px-2.5 py-1 rounded bg-slate-800 text-purple-400 font-semibold">
          {features.length} Field Nodes
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse font-mono">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider font-sans">
              <th className="pb-2">Coordinates (X, Y)</th>
              <th className="pb-2 text-right">Power Density (W/mm²)</th>
              <th className="pb-2 text-right">Eff. k (W/m·K)</th>
              <th className="pb-2 text-right">Conv. h (W/m²·K)</th>
              <th className="pb-2 text-right">Edge Dist (mm)</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {features.slice(0, 8).map((f, idx) => (
              <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                <td className="py-2.5 text-cyan-400">({f.x.toFixed(1)}, {f.y.toFixed(1)}) mm</td>
                <td className="py-2.5 text-right text-rose-400 font-semibold">{f.power_density_w_per_mm2.toFixed(5)}</td>
                <td className="py-2.5 text-right text-emerald-400">{f.effective_conductivity.toFixed(1)}</td>
                <td className="py-2.5 text-right text-amber-400">{f.convection_coefficient.toFixed(1)}</td>
                <td className="py-2.5 text-right text-slate-300">{f.distance_to_board_edge.toFixed(1)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default PCBPhysicsPanel;
