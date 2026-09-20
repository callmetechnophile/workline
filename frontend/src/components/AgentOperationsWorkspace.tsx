"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  Globe,
  Cpu,
  ShieldCheck,
  Zap,
  Activity,
  RefreshCw,
  Play,
  Layers,
  Database,
  CheckCircle2,
} from "lucide-react";
import { ExternalAgentItem, AgentCapabilityItem } from "./ExternalAgentsPanel";
import { AgentRegistry } from "./AgentRegistry";
import { AgentCapabilityPanel } from "./AgentCapabilityPanel";
import { AgentTaskPanel, AgentTaskItem } from "./AgentTaskPanel";
import { AgentExecutionTimeline } from "./AgentExecutionTimeline";

interface AgentOperationsWorkspaceProps {
  apiBase: string;
  projectId?: string;
  projectName?: string;
  teamId?: string;
}

export const AgentOperationsWorkspace: React.FC<AgentOperationsWorkspaceProps> = ({
  apiBase,
  projectId = "proj_smart_battery_management_system_bms_for_4s",
  projectName = "Smart Battery Management System (BMS) for 4S",
  teamId = "default_team",
}) => {
  const [agents, setAgents] = useState<ExternalAgentItem[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<ExternalAgentItem | null>(null);
  const [selectedCapability, setSelectedCapability] = useState<AgentCapabilityItem | null>(null);
  const [tasks, setTasks] = useState<AgentTaskItem[]>([]);
  const [executions, setExecutions] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [clusterFilter, setClusterFilter] = useState<string>("ALL");
  const [quickRunning, setQuickRunning] = useState<string | null>(null);

  // Normalize project ID for API queries
  const resolvedProjectId = projectId || projectName.toLowerCase().replace(/[^a-z0-9]/g, "_");

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      // 1. Fetch Agents
      const agentsRes = await fetch(`${apiBase}/api/agents?project_id=${encodeURIComponent(resolvedProjectId)}`);
      if (agentsRes.ok) {
        const agentData: ExternalAgentItem[] = await agentsRes.json();
        setAgents(agentData);

        // Auto-select first agent if none selected
        if (!selectedAgent && agentData.length > 0) {
          setSelectedAgent(agentData[0]);
          if (agentData[0].capabilities && agentData[0].capabilities.length > 0) {
            setSelectedCapability(agentData[0].capabilities[0]);
          }
        }
      }

      // 2. Fetch Tasks
      const tasksRes = await fetch(`${apiBase}/api/agents/tasks?project_id=${encodeURIComponent(resolvedProjectId)}`);
      if (tasksRes.ok) {
        const taskData = await tasksRes.json();
        setTasks(taskData);
      }

      // 3. Fetch Executions
      const execsRes = await fetch(`${apiBase}/api/agents/executions?project_id=${encodeURIComponent(resolvedProjectId)}`);
      if (execsRes.ok) {
        const execData = await execsRes.json();
        setExecutions(execData);
      }
    } catch (err) {
      console.warn("Failed to load agent operations data:", err);
    } finally {
      setLoading(false);
    }
  }, [apiBase, resolvedProjectId, selectedAgent]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleSelectAgent = (agent: ExternalAgentItem) => {
    setSelectedAgent(agent);
    if (agent.capabilities && agent.capabilities.length > 0) {
      setSelectedCapability(agent.capabilities[0]);
    } else {
      setSelectedCapability(null);
    }
  };

  const handleRegisterAgent = async (manifest: Partial<ExternalAgentItem>) => {
    try {
      const res = await fetch(`${apiBase}/api/agents/register?project_id=${encodeURIComponent(resolvedProjectId)}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...manifest,
          cluster_tier: "EXTERNAL_INTEROP",
          version: manifest.version || "1.0.0",
        }),
      });
      if (res.ok) {
        await loadData();
      }
    } catch (err) {
      console.error("Agent registration failed:", err);
    }
  };

  const handleUnregisterAgent = async (agentId: string) => {
    try {
      const res = await fetch(`${apiBase}/api/agents/${agentId}`, {
        method: "DELETE",
      });
      if (res.ok) {
        if (selectedAgent?.agent_id === agentId) {
          setSelectedAgent(null);
          setSelectedCapability(null);
        }
        await loadData();
      }
    } catch (err) {
      console.error("Agent unregistration failed:", err);
    }
  };

  const handleSubmitTask = async (agentId: string, capabilityId: string, payload: any = {}) => {
    try {
      const res = await fetch(`${apiBase}/api/agents/tasks`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project_id: resolvedProjectId,
          team_id: teamId,
          target_agent: agentId,
          capability: capabilityId,
          payload: payload || {},
        }),
      });
      if (res.ok) {
        await loadData();
      }
    } catch (err) {
      console.error("Task submission failed:", err);
    }
  };

  const handleCancelTask = async (taskId: string) => {
    try {
      const res = await fetch(`${apiBase}/api/agents/tasks/${taskId}/cancel`, {
        method: "POST",
      });
      if (res.ok) {
        await loadData();
      }
    } catch (err) {
      console.error("Task cancel failed:", err);
    }
  };

  const runQuickAction = async (targetAgent: string, capability: string, payload: any, label: string) => {
    setQuickRunning(label);
    try {
      await handleSubmitTask(targetAgent, capability, payload);
    } finally {
      setQuickRunning(null);
    }
  };

  // Filter agents by selected cluster tier
  const filteredAgents = agents.filter((ag: any) => {
    if (clusterFilter === "ALL") return true;
    return ag.cluster_tier === clusterFilter;
  });

  return (
    <div className="space-y-6">
      {/* Top Header Card: Cluster Status & Project Association */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-md">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
            <h2 className="text-base font-bold text-zinc-100 tracking-wide">
              R1-R5 Multi-Agent Operations & Interoperability
            </h2>
            <span className="px-2 py-0.5 text-[10px] font-mono font-semibold rounded bg-indigo-950 text-indigo-300 border border-indigo-800">
              SurrealDB Live
            </span>
            <span className="px-2 py-0.5 text-[10px] font-mono font-semibold rounded bg-emerald-950 text-emerald-300 border border-emerald-800">
              ArmorIQ Governed
            </span>
          </div>
          <p className="text-xs text-zinc-400 font-mono">
            Active Project Scope: <span className="text-zinc-200 font-bold">{projectName}</span> ({resolvedProjectId})
          </p>
        </div>

        {/* Quick Action Triggers */}
        <div className="flex items-center gap-2">
          <button
            onClick={() =>
              runQuickAction(
                "EngineeringValidationAgent",
                "bms_validation",
                { pack_configuration: "4S", cell_chemistry: "Li-ion NMC", nominal_voltage: 14.8 },
                "BMS Validation"
              )
            }
            disabled={quickRunning !== null}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded transition shadow-sm"
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            {quickRunning === "BMS Validation" ? "Verifying BMS..." : "Trigger 4S BMS Validation"}
          </button>

          <button
            onClick={() =>
              runQuickAction(
                "ThermalSolver",
                "thermal_simulation",
                { board_width: 120, board_height: 80, components: [{ ref: "Q1_MOSFET", power_w: 3.5 }] },
                "Thermal Check"
              )
            }
            disabled={quickRunning !== null}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold bg-emerald-700 hover:bg-emerald-600 disabled:opacity-50 text-white rounded transition shadow-sm"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            {quickRunning === "Thermal Check" ? "Simulating..." : "Trigger Thermal Check"}
          </button>

          <button
            onClick={loadData}
            disabled={loading}
            aria-label="Refresh agent operations"
            className="p-1.5 text-zinc-400 hover:text-zinc-200 border border-zinc-800 rounded hover:bg-zinc-800 transition"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          </button>
        </div>
      </div>

      {/* Cluster Tier Filter Navigation */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs border-b border-zinc-800/80">
        {[
          { id: "ALL", label: `All Agents (${agents.length})` },
          { id: "R1_CORE", label: "R1: Core Orchestration" },
          { id: "R2_AI", label: "R2: Deep Research & Literature" },
          { id: "R3_KNOWLEDGE", label: "R3: Knowledge Graph" },
          { id: "R4_ENGINEERING", label: "R4: Engineering & Physics" },
          { id: "R5_PROCUREMENT", label: "R5: Sourcing & x402" },
          { id: "EXTERNAL_INTEROP", label: "External A2A Network" },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setClusterFilter(tab.id)}
            className={`px-3 py-1.5 font-medium rounded-t-md transition whitespace-nowrap ${
              clusterFilter === tab.id
                ? "bg-zinc-800 text-indigo-300 border-b-2 border-indigo-500 font-semibold"
                : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Agent Registry Panel */}
      <AgentRegistry
        agents={filteredAgents}
        selectedAgentId={selectedAgent?.agent_id}
        onSelectAgent={handleSelectAgent}
        onRegisterAgent={handleRegisterAgent}
        onUnregisterAgent={handleUnregisterAgent}
        onRefresh={loadData}
      />

      {/* Declared Capabilities & Risk Assessment Panel */}
      <AgentCapabilityPanel
        agent={selectedAgent}
        selectedCapabilityId={selectedCapability?.capability_id}
        onSelectCapability={(cap) => setSelectedCapability(cap)}
      />

      {/* Interoperability Tasks Panel */}
      <AgentTaskPanel
        tasks={tasks}
        selectedAgent={selectedAgent}
        selectedCapability={selectedCapability}
        onSubmitTask={handleSubmitTask}
        onCancelTask={handleCancelTask}
      />

      {/* Multi-Agent Execution Timeline & Cryptographic Provenance */}
      <AgentExecutionTimeline
        internalStage="R1-R5 Orchestration"
        externalTasks={tasks}
      />
    </div>
  );
};
