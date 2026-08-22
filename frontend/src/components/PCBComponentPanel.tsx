"use client";

import React from "react";
import { Cpu, Lock, Unlock, Layers, Box } from "lucide-react";
import { ComponentItem } from "./PCBBoardView";

interface PCBComponentPanelProps {
  components: ComponentItem[];
  onToggleLock?: (componentId: string) => void;
}

export const PCBComponentPanel: React.FC<PCBComponentPanelProps> = ({
  components,
  onToggleLock,
}) => {
  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-2xl backdrop-blur-md space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-cyan-500/10 border border-cyan-500/20 rounded-lg text-cyan-400">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-100">PCB COMPONENTS</h3>
            <p className="text-xs text-slate-400">Physical package footprint assignments and spatial layout</p>
          </div>
        </div>
        <span className="font-mono text-xs px-2.5 py-1 rounded bg-slate-800 text-slate-300">
          {components.length} Items
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider">
              <th className="pb-2">RefDes</th>
              <th className="pb-2">Value / Part</th>
              <th className="pb-2">Footprint</th>
              <th className="pb-2 text-right">X (mm)</th>
              <th className="pb-2 text-right">Y (mm)</th>
              <th className="pb-2 text-center">Layer</th>
              <th className="pb-2 text-center">Lock</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-mono">
            {components.map((comp) => (
              <tr key={comp.id} className="hover:bg-slate-800/30 transition-colors">
                <td className="py-2.5 font-bold text-cyan-400">{comp.reference_designator}</td>
                <td className="py-2.5 font-sans font-medium text-slate-200">{comp.value}</td>
                <td className="py-2.5 text-slate-400">{comp.footprint_id}</td>
                <td className="py-2.5 text-right text-emerald-400">{comp.x.toFixed(1)}</td>
                <td className="py-2.5 text-right text-emerald-400">{comp.y.toFixed(1)}</td>
                <td className="py-2.5 text-center">
                  <span className="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-slate-300">
                    {comp.layer}
                  </span>
                </td>
                <td className="py-2.5 text-center">
                  <button
                    onClick={() => onToggleLock && onToggleLock(comp.id)}
                    className={`p-1 rounded transition-colors ${
                      comp.locked ? "text-rose-400 hover:bg-rose-500/10" : "text-slate-500 hover:bg-slate-800"
                    }`}
                    title={comp.locked ? "Locked" : "Unlocked"}
                  >
                    {comp.locked ? <Lock className="w-3.5 h-3.5" /> : <Unlock className="w-3.5 h-3.5" />}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default PCBComponentPanel;
