"use client";

import React from "react";
import { GitCommit, ArrowRight, CheckCircle2, RefreshCw, AlertCircle, Clock } from "lucide-react";
import { AgentTaskItem } from "./AgentTaskPanel";

interface TimelineStep {
  id: string;
  source: "INTERNAL_ADK" | "EXTERNAL_INTEROP";
  agent: string;
  action: string;
  status: "COMPLETED" | "RUNNING" | "FAILED" | "PENDING";
  timestamp: string;
  duration?: number;
}

interface AgentExecutionTimelineProps {
  internalStage?: string;
  externalTasks: AgentTaskItem[];
}

export const AgentExecutionTimeline: React.FC<AgentExecutionTimelineProps> = ({
  internalStage = "PCB Validation & Placement",
  externalTasks,
}) => {
  const steps: TimelineStep[] = [
    {
      id: "step-1",
      source: "INTERNAL_ADK",
      agent: "DomainResearcherAgent",
      action: "Identify thermal dissipation constraints and layer stackup requirements",
      status: "COMPLETED",
      timestamp: "10:14:02",
      duration: 1.2,
    },
    {
      id: "step-2",
      source: "INTERNAL_ADK",
      agent: "PCBAgent",
      action: `Synthesized PCB representation in ${internalStage}`,
      status: "COMPLETED",
      timestamp: "10:14:05",
      duration: 2.1,
    },
    ...externalTasks.map((t, idx) => ({
      id: `ext-${t.task_id}`,
      source: "EXTERNAL_INTEROP" as const,
      agent: `${t.target_agent} (${t.capability})`,
      action: t.error ? `Failed: ${t.error}` : `Executed ${t.capability}`,
      status: (t.status === "COMPLETED"
        ? "COMPLETED"
        : t.status === "RUNNING"
        ? "RUNNING"
        : t.status === "FAILED" || t.status === "REJECTED"
        ? "FAILED"
        : "PENDING") as TimelineStep["status"],
      timestamp: t.created_at.slice(11, 19),
      duration: t.provenance?.execution_duration,
    })),
  ];

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4">
      <div className="flex items-center gap-2">
        <GitCommit className="w-5 h-5 text-indigo-400" />
        <h3 className="text-base font-bold text-zinc-100">Multi-Agent Execution Timeline & Provenance</h3>
      </div>

      <div className="relative pl-6 border-l-2 border-zinc-800 flex flex-col gap-5 my-2">
        {steps.map((step) => (
          <div key={step.id} className="relative flex flex-col gap-1">
            <div className="absolute -left-[31px] top-0.5 w-4 h-4 rounded-full bg-zinc-950 border-2 border-indigo-500 flex items-center justify-center">
              {step.status === "COMPLETED" ? (
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              ) : step.status === "RUNNING" ? (
                <div className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-ping" />
              ) : (
                <div className="w-1.5 h-1.5 rounded-full bg-zinc-600" />
              )}
            </div>

            <div className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-zinc-200">{step.agent}</span>
                <span
                  className={`px-1.5 py-0.2 rounded text-[10px] font-mono ${
                    step.source === "EXTERNAL_INTEROP"
                      ? "bg-indigo-950 text-indigo-300 border border-indigo-800"
                      : "bg-zinc-800 text-zinc-400"
                  }`}
                >
                  {step.source.replace("_", " ")}
                </span>
              </div>
              <span className="font-mono text-zinc-500">{step.timestamp}</span>
            </div>

            <p className="text-xs text-zinc-400">{step.action}</p>

            {step.duration !== undefined && (
              <div className="text-[10px] font-mono text-zinc-500">
                Duration: {step.duration}s
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
