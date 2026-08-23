"use client";

import React, { useState } from "react";
import { GitBranch, Zap, ArrowRight, Shield } from "lucide-react";

export interface NetExplorerItem {
  netId: string;
  name: string;
  type: string;
  voltage?: number;
  current?: number;
  pins: string[];
}

export interface NetExplorerProps {
  nets?: NetExplorerItem[];
}

export const NetExplorer: React.FC<NetExplorerProps> = ({
  nets = [],
}) => {
  if (!nets || (Array.isArray(nets) && nets.length === 0)) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-8 text-center">
        <GitBranch className="w-8 h-8 text-slate-600 mx-auto mb-2" />
        <p className="text-xs text-slate-400">No net data available.</p>
        <p className="text-[10px] text-slate-500 mt-1">Create or select a project to view net data.</p>
      </div>
    );
  }

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4 text-zinc-100">
      <div className="flex items-center gap-2 pb-2 border-b border-zinc-800">
        <GitBranch className="w-5 h-5 text-indigo-400" />
        <h3 className="text-base font-bold text-zinc-100">Electrical Nets & Connectivity</h3>
      </div>

      <div className="flex flex-col gap-2">
        {nets.map((net) => (
          <div key={net.netId} className="p-3 bg-zinc-950/60 border border-zinc-800 rounded-lg flex flex-col gap-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="font-mono font-bold text-indigo-300">{net.name}</span>
                <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-zinc-800 text-zinc-400">
                  {net.type}
                </span>
              </div>
              {net.voltage !== undefined && (
                <span className="text-xs font-mono font-bold text-emerald-400">
                  {net.voltage}V @ {net.current || 0}A
                </span>
              )}
            </div>

            <div className="flex items-center gap-2 text-xs font-mono text-zinc-400">
              <span>Connected Pins:</span>
              <div className="flex items-center gap-1.5 flex-wrap">
                {net.pins.map((p, idx) => (
                  <span key={idx} className="px-1.5 py-0.5 bg-zinc-900 border border-zinc-800 rounded text-zinc-300">
                    {p}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
