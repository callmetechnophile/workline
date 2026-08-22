"use client";

import React, { useState } from "react";
import { Play, Clock, CheckCircle2, XCircle, AlertCircle, RefreshCw, ShieldAlert, StopCircle } from "lucide-react";
import { ExternalAgentItem, AgentCapabilityItem } from "./ExternalAgentsPanel";

export interface AgentTaskItem {
  task_id: string;
  project_id: string;
  team_id: string;
  requesting_agent: string;
  target_agent: string;
  capability: string;
  status: "PENDING" | "AUTHORIZED" | "RUNNING" | "COMPLETED" | "FAILED" | "CANCELLED" | "TIMEOUT" | "REJECTED";
  risk_level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  created_at: string;
  started_at?: string;
  completed_at?: string;
  timeout: number;
  error?: string;
  output_reference?: any;
  provenance?: {
    execution_duration: number;
    input_hash: string;
    output_hash: string;
  };
}

interface AgentTaskPanelProps {
  tasks: AgentTaskItem[];
  selectedAgent?: ExternalAgentItem | null;
  selectedCapability?: AgentCapabilityItem | null;
  onSubmitTask?: (agentId: string, capabilityId: string, payload: any) => Promise<void>;
  onCancelTask?: (taskId: string) => Promise<void>;
}

export const AgentTaskPanel: React.FC<AgentTaskPanelProps> = ({
  tasks,
  selectedAgent,
  selectedCapability,
  onSubmitTask,
  onCancelTask,
}) => {
  const [submitting, setSubmitting] = useState(false);

  const handleLaunch = async () => {
    if (!selectedAgent || !selectedCapability || !onSubmitTask) return;
    setSubmitting(true);
    try {
      await onSubmitTask(selectedAgent.agent_id, selectedCapability.capability_id, {
        board_width: 100.0,
        board_height: 80.0,
        components: [{ name: "U1", power_dissipation_watts: 1.2 }],
      });
    } finally {
      setSubmitting(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "COMPLETED":
        return <CheckCircle2 className="w-4 h-4 text-emerald-400" />;
      case "RUNNING":
      case "AUTHORIZED":
        return <RefreshCw className="w-4 h-4 text-amber-400 animate-spin" />;
      case "REJECTED":
      case "FAILED":
        return <XCircle className="w-4 h-4 text-rose-400" />;
      case "CANCELLED":
        return <StopCircle className="w-4 h-4 text-zinc-400" />;
      case "TIMEOUT":
      default:
        return <Clock className="w-4 h-4 text-zinc-400" />;
    }
  };

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Clock className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-zinc-100">Interoperability Tasks</h3>
        </div>
        {selectedAgent && selectedCapability && (
          <button
            onClick={handleLaunch}
            disabled={submitting}
            className="flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white rounded transition"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            {submitting ? "Delegating..." : `Run ${selectedCapability.capability_id}`}
          </button>
        )}
      </div>

      <div className="flex flex-col gap-2.5 max-h-[360px] overflow-y-auto">
        {tasks.length === 0 ? (
          <div className="p-6 text-center text-zinc-500 text-xs">No active or historical tasks.</div>
        ) : (
          tasks.map((t) => (
            <div
              key={t.task_id}
              className="p-3.5 bg-zinc-950/60 border border-zinc-800/80 rounded-lg flex flex-col gap-2"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {getStatusIcon(t.status)}
                  <span className="font-mono text-xs font-semibold text-zinc-200">{t.task_id}</span>
                  <span className="text-xs text-zinc-400">
                    &rarr; {t.target_agent} ({t.capability})
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 text-[11px] font-mono rounded bg-zinc-800 text-zinc-300">
                    {t.status}
                  </span>
                  {["PENDING", "RUNNING", "AUTHORIZED"].includes(t.status) && onCancelTask && (
                    <button
                      onClick={() => onCancelTask(t.task_id)}
                      className="px-2 py-0.5 text-[11px] rounded bg-rose-950 text-rose-400 hover:bg-rose-900 border border-rose-800 transition"
                    >
                      Cancel
                    </button>
                  )}
                </div>
              </div>

              {t.provenance && (
                <div className="flex items-center justify-between text-[11px] font-mono text-zinc-500 border-t border-zinc-800/40 pt-1.5">
                  <span>Duration: {t.provenance.execution_duration}s</span>
                  <span>Hash: {t.provenance.output_hash.slice(0, 12)}...</span>
                </div>
              )}

              {t.error && (
                <div className="text-xs text-rose-400 bg-rose-950/40 border border-rose-900/60 rounded p-2">
                  {t.error}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};
