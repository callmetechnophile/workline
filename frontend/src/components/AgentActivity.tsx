"use client";

import React, { useState, useEffect } from "react";
import { 
  Bot, 
  Activity, 
  CheckCircle2, 
  Clock, 
  AlertCircle, 
  Play, 
  Layers, 
  ArrowRight,
  RefreshCw
} from "lucide-react";

interface AgentEvent {
  timestamp: string;
  agent_id: string;
  event_type: string;
  summary: string;
  details?: Record<string, any>;
}

interface AgentState {
  execution_id: string;
  session_id: string;
  project_id: string;
  agent_id: string;
  stage: string;
  status: "PENDING" | "RUNNING" | "WAITING_FOR_USER" | "COMPLETED" | "FAILED" | "BLOCKED";
  output_summary?: string;
  requires_user_action?: boolean;
  action_prompt?: string;
  events: AgentEvent[];
  errors: string[];
}

interface AgentActivityProps {
  projectId: string;
  executionId?: string;
  onApproval?: (decision: string) => void;
}

export const AgentActivity: React.FC<AgentActivityProps> = ({
  projectId,
  executionId,
  onApproval,
}) => {
  const [state, setState] = useState<AgentState | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [submitting, setSubmitting] = useState<boolean>(false);

  useEffect(() => {
    if (!projectId && !executionId) return;

    const fetchStatus = async () => {
      try {
        if (executionId) {
          const res = await fetch(`/api/agents/executions/${executionId}`);
          if (res.ok) {
            const data = await res.json();
            setState(data);
          }
        } else if (projectId) {
          const res = await fetch(`/api/agents/project/${projectId}/status`);
          if (res.ok) {
            const data = await res.json();
            if (data.execution_id) {
              const execRes = await fetch(`/api/agents/executions/${data.execution_id}`);
              if (execRes.ok) {
                setState(await execRes.json());
              }
            }
          }
        }
      } catch (err) {
        console.error("Failed to poll agent status:", err);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 3000);
    return () => clearInterval(interval);
  }, [projectId, executionId]);

  if (!projectId && !executionId) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-8 text-center">
        <Activity className="w-8 h-8 text-slate-600 mx-auto mb-2" />
        <p className="text-xs text-slate-400">No activity data.</p>
        <p className="text-[10px] text-slate-500 mt-1">Create or select a project to view activity.</p>
      </div>
    );
  }

  const handleDecision = async (decision: string) => {
    if (!state?.execution_id) return;
    setSubmitting(true);
    try {
      const res = await fetch(`/api/agents/approval/${state.execution_id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ decision }),
      });
      if (res.ok) {
        const updated = await res.json();
        setState(updated);
        if (onApproval) onApproval(decision);
      }
    } catch (err) {
      console.error("Decision submission failed:", err);
    } finally {
      setSubmitting(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "COMPLETED":
        return <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"><CheckCircle2 className="w-3.5 h-3.5" /> Completed</span>;
      case "RUNNING":
        return <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 animate-pulse"><Activity className="w-3.5 h-3.5" /> Running</span>;
      case "WAITING_FOR_USER":
        return <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20"><AlertCircle className="w-3.5 h-3.5" /> Awaiting Decision</span>;
      case "FAILED":
        return <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20"><AlertCircle className="w-3.5 h-3.5" /> Failed</span>;
      default:
        return <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-500/10 text-slate-400 border border-slate-500/20"><Clock className="w-3.5 h-3.5" /> Idle</span>;
    }
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-2xl backdrop-blur-md">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-indigo-500/10 border border-indigo-500/20 rounded-lg text-indigo-400">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-slate-100">Workline Agent Activity</h3>
            <p className="text-xs text-slate-400">Google ADK Multi-Agent Orchestration</p>
          </div>
        </div>
        <div>
          {state ? getStatusBadge(state.status) : getStatusBadge("PENDING")}
        </div>
      </div>

      {state ? (
        <div className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
              <span className="text-[11px] text-slate-400 uppercase tracking-wider block mb-1">Current Agent</span>
              <span className="text-sm font-medium text-slate-200 capitalize">
                {state.agent_id.replace(/_/g, " ")}
              </span>
            </div>
            <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
              <span className="text-[11px] text-slate-400 uppercase tracking-wider block mb-1">Lifecycle Stage</span>
              <span className="text-sm font-medium text-cyan-400 capitalize">
                {state.stage.replace(/_/g, " ")}
              </span>
            </div>
            <div className="col-span-2 md:col-span-1 bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
              <span className="text-[11px] text-slate-400 uppercase tracking-wider block mb-1">Execution ID</span>
              <span className="text-xs font-mono text-slate-400 truncate block">
                {state.execution_id}
              </span>
            </div>
          </div>

          {state.output_summary && (
            <div className="p-3.5 bg-slate-950/80 border border-slate-800 rounded-lg text-xs text-slate-300 leading-relaxed">
              <span className="font-semibold text-slate-200 block mb-1">Summary</span>
              {state.output_summary}
            </div>
          )}

          {state.requires_user_action && (
            <div className="p-4 bg-amber-500/10 border border-amber-500/30 rounded-xl space-y-3">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
                <div>
                  <h4 className="text-sm font-semibold text-amber-300">Human Decision Checkpoint</h4>
                  <p className="text-xs text-slate-300 mt-1">{state.action_prompt || "Choose next step in engineering lifecycle."}</p>
                </div>
              </div>
              <div className="flex items-center gap-3 pt-2">
                <button
                  disabled={submitting}
                  onClick={() => handleDecision("START_BUILD")}
                  className="px-4 py-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs font-semibold rounded-lg shadow-lg transition-all flex items-center gap-2"
                >
                  <Play className="w-3.5 h-3.5" /> Start Building
                </button>
                <button
                  disabled={submitting}
                  onClick={() => handleDecision("CONTINUE_RESEARCH")}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-lg border border-slate-700 transition-all flex items-center gap-2"
                >
                  <RefreshCw className="w-3.5 h-3.5" /> Continue Research
                </button>
              </div>
            </div>
          )}

          <div className="space-y-2">
            <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-2">
              <Layers className="w-3.5 h-3.5" /> Recent Activity & Events
            </h4>
            <div className="max-h-48 overflow-y-auto space-y-1.5 pr-1 text-xs">
              {state.events && state.events.length > 0 ? (
                state.events.slice().reverse().map((ev, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2 rounded bg-slate-950/40 border border-slate-800/50">
                    <div className="flex items-center gap-2 truncate">
                      <span className="font-mono text-[10px] text-cyan-400 uppercase font-semibold">[{ev.event_type}]</span>
                      <span className="text-slate-300 truncate">{ev.summary}</span>
                    </div>
                    <span className="text-[10px] text-slate-500 font-mono shrink-0 ml-2">
                      {ev.timestamp ? ev.timestamp.slice(11, 19) : ""}
                    </span>
                  </div>
                ))
              ) : (
                <div className="text-slate-500 text-center py-4 text-xs">No activity logged yet.</div>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-8 text-slate-500 text-xs">
          No active agent execution for this project. Launch with <span className="font-mono text-cyan-400">wline agent run</span>.
        </div>
      )}
    </div>
  );
};
