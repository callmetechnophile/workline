"use client";

import React from "react";
import { 
  Network, 
  Bot, 
  GitFork, 
  Cpu, 
  Activity, 
  Search, 
  Sparkles, 
  FileText, 
  ShieldCheck, 
  Layers, 
  Zap, 
  CheckCircle,
  HelpCircle
} from "lucide-react";

interface AgentGraphProps {
  activeAgent?: string;
  stage?: string;
}

export const AgentGraph: React.FC<AgentGraphProps> = ({
  activeAgent = "root_orchestrator",
  stage = "ideation",
}) => {
  const isAgentActive = (id: string) => activeAgent === id;

  const getCardClasses = (id: string) => {
    const active = isAgentActive(id);
    return `relative p-3 rounded-lg border transition-all duration-300 flex flex-col gap-1.5 ${
      active 
        ? "bg-cyan-950/40 border-cyan-500 shadow-lg shadow-cyan-500/20 ring-1 ring-cyan-500 scale-[1.02]" 
        : "bg-slate-900/60 border-slate-800 hover:border-slate-700"
    }`;
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-2xl backdrop-blur-md">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-cyan-500/10 border border-cyan-500/20 rounded-lg text-cyan-400">
            <Network className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-slate-100">Multi-Agent Hierarchy</h3>
            <p className="text-xs text-slate-400">Google ADK Dynamic Specialist Tree</p>
          </div>
        </div>
        <div className="text-xs text-slate-400">
          Stage: <span className="text-cyan-400 font-medium capitalize">{stage.replace(/_/g, " ")}</span>
        </div>
      </div>

      <div className="space-y-6">
        {/* Root Level */}
        <div className="flex justify-center">
          <div className={`w-64 ${getCardClasses("root_orchestrator")}`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Bot className="w-4 h-4 text-cyan-400" />
                <span className="text-xs font-semibold text-slate-200">Root Orchestrator</span>
              </div>
              {isAgentActive("root_orchestrator") && (
                <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
              )}
            </div>
            <p className="text-[11px] text-slate-400">Lifecycle routing & delegation</p>
          </div>
        </div>

        {/* Level 1: Planning & Research Trees */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 relative">
          {/* Planning Sub-tree */}
          <div className="p-3.5 bg-slate-950/50 border border-slate-800/80 rounded-xl space-y-3">
            <span className="text-[11px] font-semibold text-indigo-400 uppercase tracking-wider block">
              Planning Sub-Tree
            </span>
            <div className="grid grid-cols-2 gap-2">
              <div className={getCardClasses("domain_researcher")}>
                <span className="text-xs font-medium text-slate-200">Domain Agent</span>
                <span className="text-[10px] text-slate-400">Requirements & Specs</span>
              </div>
              <div className={getCardClasses("timeline_agent")}>
                <span className="text-xs font-medium text-slate-200">Timeline Agent</span>
                <span className="text-[10px] text-slate-400">Task Graph & Gantt</span>
              </div>
            </div>
          </div>

          {/* Research Sub-tree */}
          <div className="p-3.5 bg-slate-950/50 border border-slate-800/80 rounded-xl space-y-3">
            <span className="text-[11px] font-semibold text-purple-400 uppercase tracking-wider block">
              Research Sub-Tree
            </span>
            <div className="grid grid-cols-2 gap-2">
              <div className={getCardClasses("research_agent")}>
                <span className="text-xs font-medium text-slate-200">Research Agent</span>
                <span className="text-[10px] text-slate-400">Qdrant & Literature</span>
              </div>
              <div className={getCardClasses("innovation_agent")}>
                <span className="text-xs font-medium text-slate-200">Innovation Agent</span>
                <span className="text-[10px] text-slate-400">Fact vs Inference</span>
              </div>
            </div>
          </div>
        </div>

        {/* Human Checkpoint */}
        <div className="flex justify-center">
          <div className="px-4 py-2 bg-amber-500/10 border border-amber-500/30 rounded-lg flex items-center gap-2 text-xs text-amber-300">
            <HelpCircle className="w-4 h-4 text-amber-400" />
            <span>Human Decision Checkpoint: <strong>[Continue Research]</strong> or <strong>[Start Building]</strong></span>
          </div>
        </div>

        {/* Hardware Builder Sub-Tree */}
        <div className="p-4 bg-slate-950/60 border border-slate-800 rounded-xl space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-semibold text-emerald-400 uppercase tracking-wider block">
              Hardware Builder Sub-Tree (10 Specialists)
            </span>
            {isAgentActive("builder_agent") && (
              <span className="text-[10px] text-emerald-400 font-mono">BUILDER ACTIVE</span>
            )}
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2.5">
            <div className={getCardClasses("listing_agent")}>
              <span className="text-xs font-medium text-slate-200">Listing</span>
              <span className="text-[10px] text-slate-400">Candidate discovery</span>
            </div>
            <div className={getCardClasses("sorting_agent")}>
              <span className="text-xs font-medium text-slate-200">Sorting</span>
              <span className="text-[10px] text-slate-400">Matrix ranking</span>
            </div>
            <div className={getCardClasses("finance_agent")}>
              <span className="text-xs font-medium text-slate-200">Finance</span>
              <span className="text-[10px] text-slate-400">Budget estimation</span>
            </div>
            <div className={getCardClasses("component_agent")}>
              <span className="text-xs font-medium text-slate-200">Component</span>
              <span className="text-[10px] text-slate-400">Datasheet validation</span>
            </div>
            <div className={getCardClasses("connection_agent")}>
              <span className="text-xs font-medium text-slate-200">Connection</span>
              <span className="text-[10px] text-slate-400">Pinouts & buses</span>
            </div>
            <div className={getCardClasses("power_agent")}>
              <span className="text-xs font-medium text-slate-200">Power</span>
              <span className="text-[10px] text-slate-400">Rails & thermal</span>
            </div>
            <div className={getCardClasses("firmware_agent")}>
              <span className="text-xs font-medium text-slate-200">Firmware</span>
              <span className="text-[10px] text-slate-400">FreeRTOS & HAL</span>
            </div>
            <div className={getCardClasses("pcb_agent")}>
              <span className="text-xs font-medium text-slate-200">PCB</span>
              <span className="text-[10px] text-slate-400">Layout rules</span>
            </div>
            <div className={getCardClasses("validation_agent")}>
              <span className="text-xs font-medium text-slate-200">Validation</span>
              <span className="text-[10px] text-slate-400">Pass/Warn/Fail</span>
            </div>
            <div className={getCardClasses("bom_agent")}>
              <span className="text-xs font-medium text-slate-200">BOM</span>
              <span className="text-[10px] text-slate-400">SurrealDB BOM</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
