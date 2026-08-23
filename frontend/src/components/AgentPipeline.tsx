'use client';

import React from 'react';
import { ShieldCheck, ShieldAlert, Cpu, CheckCircle2, AlertTriangle, Play, Pause } from 'lucide-react';

interface AuditLog {
  agent: string;
  action: string;
  allowed_scope: string[];
  tool_invoked: string | null;
  status: string;
  details: string;
  receipt_id: string | null;
  parent_receipt_id: string | null;
}

interface AgentPipelineProps {
  logs?: AuditLog[];
  activeAgent?: string | null;
  isProcessing?: boolean;
  agents?: { name: string; desc: string }[];
}

export default function AgentPipeline({ logs = [], activeAgent = null, isProcessing = false, agents = [] }: AgentPipelineProps) {
  if (!agents || agents.length === 0) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-8 text-center">
        <Cpu className="w-8 h-8 text-slate-600 mx-auto mb-2" />
        <p className="text-xs text-slate-400">No pipeline configured.</p>
        <p className="text-[10px] text-slate-500 mt-1">Create or select a project to view pipeline.</p>
      </div>
    );
  }

  // Determine the status of an agent based on audit logs
  const getAgentStatus = (agentName: string) => {
    if (activeAgent === agentName && isProcessing) {
      return "ACTIVE";
    }
    
    const agentLogs = logs.filter(l => l.agent === agentName);
    if (agentLogs.length === 0) {
      return "IDLE";
    }
    
    if (agentLogs.some(l => l.status === "BLOCKED")) {
      return "VIOLATION";
    }
    
    if (agentLogs.some(l => l.status === "FAILED")) {
      return "FAILED";
    }
    
    if (agentLogs.some(l => l.status === "SUCCESS")) {
      return "COMPLETE";
    }
    
    return "IDLE";
  };

  return (
    <div className="glass-panel p-6 border border-blue-500/20">
      <div className="flex justify-between items-center mb-6 border-b border-blue-900/40 pb-3">
        <h3 className="text-md font-semibold text-cyan-400 glow-cyan flex items-center gap-2">
          <Cpu className="w-5 h-5" />
          Autonomous Multi-Agent Pipeline
        </h3>
        <span className="text-[10px] font-mono flex items-center gap-1 bg-blue-950/40 px-2 py-1 border border-blue-900/30 rounded text-cyan-400">
          <ShieldCheck className="w-3.5 h-3.5 text-cyan-500" />
          ARMORIQ CRYPTO-VERIFIED
        </span>
      </div>

      {/* Grid of Agent Nodes */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {agents.map((agent) => {
          const status = getAgentStatus(agent.name);
          
          let cardBorder = "border-slate-800/80";
          let statusText = "Idle";
          let statusColor = "text-slate-500";
          let badgeIcon = <Pause className="w-3 h-3 text-slate-500" />;
          let bgGradient = "bg-slate-900/10";
          
          if (status === "ACTIVE") {
            cardBorder = "border-cyan-500/50 glow-border-cyan animate-pulse";
            statusText = "Active";
            statusColor = "text-cyan-400";
            badgeIcon = <Play className="w-3 h-3 text-cyan-400" />;
            bgGradient = "bg-cyan-950/20";
          } else if (status === "COMPLETE") {
            cardBorder = "border-emerald-500/30";
            statusText = "Secure";
            statusColor = "text-emerald-400";
            badgeIcon = <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />;
            bgGradient = "bg-emerald-950/10";
          } else if (status === "VIOLATION") {
            cardBorder = "border-red-500/50 glow-border-red";
            statusText = "Blocked";
            statusColor = "text-red-400 font-extrabold";
            badgeIcon = <ShieldAlert className="w-3.5 h-3.5 text-red-500" />;
            bgGradient = "bg-red-950/25";
          }

          return (
            <div 
              key={agent.name} 
              className={`p-4 border ${cardBorder} ${bgGradient} rounded-lg transition-all duration-300 relative overflow-hidden`}
            >
              {/* Crypto indicator background lock */}
              {status === "COMPLETE" && (
                <div className="absolute right-2 bottom-2 text-emerald-500/5 pointer-events-none">
                  <ShieldCheck className="w-16 h-16 stroke-[0.5]" />
                </div>
              )}
              
              <div className="flex justify-between items-start gap-2 mb-2">
                <span className="text-xs font-bold text-slate-100">{agent.name}</span>
                <span className={`text-[10px] font-mono font-bold flex items-center gap-1 ${statusColor}`}>
                  {badgeIcon}
                  {statusText}
                </span>
              </div>
              
              <p className="text-[10px] text-slate-400 leading-snug">
                {agent.desc}
              </p>
              
              {/* Log preview */}
              {status !== "IDLE" && (
                <div className="mt-3 bg-black/60 border border-slate-800/80 rounded p-2 text-[9px] font-mono text-slate-400 leading-normal max-h-16 overflow-y-auto">
                  {logs
                    .filter(l => l.agent === agent.name)
                    .map((l, i) => (
                      <div key={i} className="mb-1 last:mb-0">
                        <span className={l.status === "BLOCKED" ? "text-red-400" : "text-cyan-400"}>
                          &gt; {l.action}:
                        </span>{" "}
                        {l.details.length > 50 ? `${l.details.substring(0, 47)}...` : l.details}
                      </div>
                    ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
