"use client";

import React, { useState } from "react";
import { Bot, Cpu, ShieldCheck, Zap, Activity, ExternalLink } from "lucide-react";

export interface AgentCapabilityItem {
  capability_id: string;
  name: string;
  description: string;
  capability_type: string;
  risk_level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  estimated_cost: number;
  availability: boolean;
  version: string;
}

export interface ExternalAgentItem {
  agent_id: string;
  name: string;
  description: string;
  provider: string;
  protocol: string;
  endpoint?: string;
  version: string;
  status: "AVAILABLE" | "BUSY" | "OFFLINE" | "UNKNOWN" | "DISABLED";
  capabilities: AgentCapabilityItem[];
  trust_score?: number;
}

interface ExternalAgentsPanelProps {
  agents: ExternalAgentItem[];
  selectedAgentId?: string | null;
  onSelectAgent?: (agent: ExternalAgentItem) => void;
  onDiscover?: () => void;
}

export const ExternalAgentsPanel: React.FC<ExternalAgentsPanelProps> = ({
  agents,
  selectedAgentId,
  onSelectAgent,
  onDiscover,
}) => {
  const [filterProtocol, setFilterProtocol] = useState<string>("ALL");

  const filtered = agents.filter((a) => {
    if (filterProtocol === "ALL") return true;
    return a.protocol.toUpperCase() === filterProtocol.toUpperCase();
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "AVAILABLE":
        return <span className="px-2 py-0.5 text-xs font-semibold rounded bg-emerald-950 text-emerald-400 border border-emerald-800">AVAILABLE</span>;
      case "BUSY":
        return <span className="px-2 py-0.5 text-xs font-semibold rounded bg-amber-950 text-amber-400 border border-amber-800">BUSY</span>;
      case "OFFLINE":
      default:
        return <span className="px-2 py-0.5 text-xs font-semibold rounded bg-zinc-800 text-zinc-400 border border-zinc-700">{status}</span>;
    }
  };

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Bot className="w-5 h-5 text-indigo-400" />
          <h2 className="text-lg font-bold text-zinc-100">External Agents</h2>
          <span className="px-2 py-0.5 text-xs rounded bg-zinc-800 text-zinc-300">
            {filtered.length} Connected
          </span>
        </div>
        <div className="flex items-center gap-2">
          <select
            aria-label="Filter protocol"
            className="bg-zinc-950 border border-zinc-800 text-xs text-zinc-300 rounded px-2 py-1.5 focus:outline-none focus:border-indigo-500"
            value={filterProtocol}
            onChange={(e) => setFilterProtocol(e.target.value)}
          >
            <option value="ALL">All Protocols</option>
            <option value="BINDU_A2A">Bindu A2A</option>
            <option value="CORSAIR">Corsair</option>
          </select>
          {onDiscover && (
            <button
              onClick={onDiscover}
              className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium bg-indigo-600 hover:bg-indigo-500 text-white rounded transition"
            >
              <Zap className="w-3.5 h-3.5" />
              Discover
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {filtered.map((ag) => {
          const isSelected = selectedAgentId === ag.agent_id;
          return (
            <div
              key={ag.agent_id}
              onClick={() => onSelectAgent?.(ag)}
              className={`p-4 rounded-lg border cursor-pointer transition flex flex-col justify-between gap-3 ${
                isSelected
                  ? "bg-zinc-800/80 border-indigo-500 shadow-sm shadow-indigo-500/20"
                  : "bg-zinc-950/60 border-zinc-800/80 hover:border-zinc-700"
              }`}
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-1.5">
                  <div className="flex items-center gap-2">
                    <Cpu className="w-4 h-4 text-indigo-400" />
                    <h3 className="font-semibold text-zinc-100 text-sm">{ag.name}</h3>
                  </div>
                  {getStatusBadge(ag.status)}
                </div>
                <p className="text-xs text-zinc-400 line-clamp-2">{ag.description}</p>
              </div>

              <div className="border-t border-zinc-800/60 pt-2 flex items-center justify-between text-xs text-zinc-400">
                <span className="font-mono text-zinc-300">{ag.protocol.replace("_", " ")}</span>
                <div className="flex items-center gap-1.5">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="text-zinc-200 font-mono">
                    {ag.trust_score !== undefined ? `${(ag.trust_score * 100).toFixed(0)}% Trust` : "95% Trust"}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
