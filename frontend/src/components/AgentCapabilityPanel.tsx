"use client";

import React from "react";
import { Wrench, AlertTriangle, ShieldCheck, DollarSign, Layers } from "lucide-react";
import { AgentCapabilityItem, ExternalAgentItem } from "./ExternalAgentsPanel";

interface AgentCapabilityPanelProps {
  agent: ExternalAgentItem | null;
  selectedCapabilityId?: string | null;
  onSelectCapability?: (cap: AgentCapabilityItem) => void;
}

export const AgentCapabilityPanel: React.FC<AgentCapabilityPanelProps> = ({
  agent,
  selectedCapabilityId,
  onSelectCapability,
}) => {
  if (!agent) {
    return (
      <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6 flex flex-col items-center justify-center text-center text-zinc-500 min-h-[220px]">
        <Wrench className="w-8 h-8 mb-2 opacity-40" />
        <p className="text-sm">Select an agent to inspect its capabilities and security risk levels.</p>
      </div>
    );
  }

  const getRiskBadge = (risk: string) => {
    switch (risk) {
      case "CRITICAL":
        return <span className="px-2 py-0.5 text-xs font-semibold rounded bg-rose-950 text-rose-400 border border-rose-800">CRITICAL RISK</span>;
      case "HIGH":
        return <span className="px-2 py-0.5 text-xs font-semibold rounded bg-orange-950 text-orange-400 border border-orange-800">HIGH RISK</span>;
      case "MEDIUM":
        return <span className="px-2 py-0.5 text-xs font-semibold rounded bg-amber-950 text-amber-400 border border-amber-800">MEDIUM RISK</span>;
      case "LOW":
      default:
        return <span className="px-2 py-0.5 text-xs font-semibold rounded bg-emerald-950 text-emerald-400 border border-emerald-800">LOW RISK</span>;
    }
  };

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Wrench className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-zinc-100">
            Declared Capabilities: <span className="text-indigo-400">{agent.name}</span>
          </h3>
        </div>
        <span className="text-xs text-zinc-400 font-mono">v{agent.version}</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {agent.capabilities.map((cap) => {
          const isSelected = selectedCapabilityId === cap.capability_id;
          return (
            <div
              key={cap.capability_id}
              onClick={() => onSelectCapability?.(cap)}
              className={`p-4 rounded-lg border cursor-pointer transition flex flex-col justify-between gap-3 ${
                isSelected
                  ? "bg-zinc-800/80 border-indigo-500 shadow-sm shadow-indigo-500/20"
                  : "bg-zinc-950/60 border-zinc-800/80 hover:border-zinc-700"
              }`}
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-1">
                  <h4 className="font-semibold text-zinc-100 text-sm">{cap.name}</h4>
                  {getRiskBadge(cap.risk_level)}
                </div>
                <p className="text-xs text-zinc-400">{cap.description}</p>
              </div>

              <div className="flex items-center justify-between text-xs text-zinc-400 pt-2 border-t border-zinc-800/60 font-mono">
                <span className="flex items-center gap-1 text-emerald-400">
                  <DollarSign className="w-3.5 h-3.5" />
                  ${cap.estimated_cost.toFixed(2)} est.
                </span>
                <span className="text-zinc-500">{cap.capability_type}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
