"use client";

import React, { useState } from "react";
import { PlusCircle, Trash2, Globe, Shield, RefreshCw } from "lucide-react";
import { ExternalAgentItem } from "./ExternalAgentsPanel";

interface AgentRegistryProps {
  agents: ExternalAgentItem[];
  onRegisterAgent?: (newAgent: Partial<ExternalAgentItem>) => Promise<void>;
  onUnregisterAgent?: (agentId: string) => Promise<void>;
  onRefresh?: () => void;
}

export const AgentRegistry: React.FC<AgentRegistryProps> = ({
  agents,
  onRegisterAgent,
  onUnregisterAgent,
  onRefresh,
}) => {
  const [showModal, setShowModal] = useState(false);
  const [agentId, setAgentId] = useState("");
  const [name, setName] = useState("");
  const [protocol, setProtocol] = useState("BINDU_A2A");
  const [endpoint, setEndpoint] = useState("");
  const [description, setDescription] = useState("");

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!agentId || !name || !onRegisterAgent) return;
    await onRegisterAgent({
      agent_id: agentId,
      name,
      protocol,
      endpoint,
      description,
      status: "AVAILABLE",
      capabilities: [],
    });
    setShowModal(false);
    setAgentId("");
    setName("");
    setEndpoint("");
    setDescription("");
  };

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Globe className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-zinc-100">Agent Network & Integrations</h3>
        </div>
        <div className="flex items-center gap-2">
          {onRefresh && (
            <button
              onClick={onRefresh}
              aria-label="Refresh agent network"
              className="p-1.5 text-zinc-400 hover:text-zinc-200 border border-zinc-800 rounded hover:bg-zinc-800 transition"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          )}
          <button
            onClick={() => setShowModal(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white rounded transition"
          >
            <PlusCircle className="w-3.5 h-3.5" />
            Register Agent
          </button>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-zinc-300">
          <thead className="bg-zinc-950/80 text-zinc-400 uppercase font-mono border-b border-zinc-800">
            <tr>
              <th className="px-3 py-2">Agent</th>
              <th className="px-3 py-2">Protocol</th>
              <th className="px-3 py-2">Endpoint</th>
              <th className="px-3 py-2">Status</th>
              <th className="px-3 py-2 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800/60">
            {agents.map((ag) => (
              <tr key={ag.agent_id} className="hover:bg-zinc-950/40">
                <td className="px-3 py-2.5 font-semibold text-zinc-100">{ag.name}</td>
                <td className="px-3 py-2.5 font-mono text-zinc-400">{ag.protocol}</td>
                <td className="px-3 py-2.5 font-mono text-zinc-500">{ag.endpoint || "Internal Mock"}</td>
                <td className="px-3 py-2.5">
                  <span className="px-2 py-0.5 rounded text-[11px] bg-zinc-800 text-zinc-300 font-mono">
                    {ag.status}
                  </span>
                </td>
                <td className="px-3 py-2.5 text-right">
                  {onUnregisterAgent && (
                    <button
                      onClick={() => onUnregisterAgent(ag.agent_id)}
                      className="text-zinc-500 hover:text-rose-400 transition"
                      title="Unregister Agent"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50">
          <form
            onSubmit={handleRegister}
            className="bg-zinc-900 border border-zinc-800 rounded-lg p-6 w-full max-w-md flex flex-col gap-4 shadow-xl"
          >
            <h4 className="text-sm font-bold text-zinc-100">Register External Agent Manifest</h4>
            <div className="flex flex-col gap-3 text-xs">
              <div>
                <label className="text-zinc-400 block mb-1">Agent ID</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. ThermalSolver"
                  className="w-full bg-zinc-950 border border-zinc-800 rounded px-3 py-2 text-zinc-200"
                  value={agentId}
                  onChange={(e) => setAgentId(e.target.value)}
                />
              </div>
              <div>
                <label className="text-zinc-400 block mb-1">Display Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Thermal Placement Engine"
                  className="w-full bg-zinc-950 border border-zinc-800 rounded px-3 py-2 text-zinc-200"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
              </div>
              <div>
                <label className="text-zinc-400 block mb-1">Protocol</label>
                <select
                  className="w-full bg-zinc-950 border border-zinc-800 rounded px-3 py-2 text-zinc-200"
                  value={protocol}
                  onChange={(e) => setProtocol(e.target.value)}
                >
                  <option value="BINDU_A2A">Bindu A2A</option>
                  <option value="CORSAIR">Corsair</option>
                </select>
              </div>
              <div>
                <label className="text-zinc-400 block mb-1">Endpoint URI</label>
                <input
                  type="text"
                  placeholder="e.g. bindu://network/solver"
                  className="w-full bg-zinc-950 border border-zinc-800 rounded px-3 py-2 text-zinc-200"
                  value={endpoint}
                  onChange={(e) => setEndpoint(e.target.value)}
                />
              </div>
              <div>
                <label className="text-zinc-400 block mb-1">Description</label>
                <textarea
                  rows={2}
                  placeholder="Agent domain summary..."
                  className="w-full bg-zinc-950 border border-zinc-800 rounded px-3 py-2 text-zinc-200"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-2 border-t border-zinc-800">
              <button
                type="button"
                onClick={() => setShowModal(false)}
                className="px-3 py-1.5 text-xs text-zinc-400 hover:text-zinc-200 transition"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-1.5 text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white rounded transition"
              >
                Register
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};
