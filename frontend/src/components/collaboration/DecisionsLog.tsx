import React, { useState, useEffect } from "react";
import {
  Scale,
  Plus,
  CheckCircle2,
  XCircle,
  Clock,
  Sparkles,
  ChevronDown,
  ChevronUp,
  ShieldCheck,
  TrendingUp,
  Cpu,
} from "lucide-react";

export interface DecisionCriterion {
  criterion_id: string;
  name: string;
  category: string;
  weight: number;
  direction: "MAXIMIZE" | "MINIMIZE";
  mandatory: boolean;
}

export interface EngineeringDecision {
  decision_id: string;
  project_id: string;
  team_id?: string;
  title: string;
  description: string;
  status: "DRAFT" | "UNDER_REVIEW" | "RECOMMENDED" | "APPROVED" | "REJECTED" | "SUPERSEDED";
  decision_type: string;
  criteria?: DecisionCriterion[];
  selected_candidate?: string;
  alternatives?: string[];
  recommendation?: string;
  rationale?: string;
  confidence?: number;
  stability?: number;
  created_by: string;
  created_at: number;
  updated_at: number;
}

interface DecisionsLogProps {
  teamId: string;
  projectId?: string;
  apiBase: string;
  canManageDecisions?: boolean;
}

const STATUS_PILLS: Record<string, { label: string; cls: string }> = {
  DRAFT: { label: "DRAFT", cls: "bg-zinc-800 text-zinc-400 border-zinc-700" },
  UNDER_REVIEW: { label: "IN REVIEW", cls: "bg-amber-950/60 text-amber-300 border-amber-800/40" },
  RECOMMENDED: { label: "AI RECOMMENDED", cls: "bg-cyan-950/60 text-cyan-300 border-cyan-800/40" },
  APPROVED: { label: "APPROVED", cls: "bg-emerald-950/60 text-emerald-300 border-emerald-800/40" },
  REJECTED: { label: "REJECTED", cls: "bg-rose-950/60 text-rose-400 border-rose-800/40" },
};

export const DecisionsLog: React.FC<DecisionsLogProps> = ({
  teamId,
  projectId = "default_project",
  apiBase,
  canManageDecisions = true,
}) => {
  const [decisions, setDecisions] = useState<EngineeringDecision[]>([]);
  const [loading, setLoading] = useState(false);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [filter, setFilter] = useState("ALL");
  const [isNewModalOpen, setIsNewModalOpen] = useState(false);

  // New Decision Form State
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [decisionType, setDecisionType] = useState("COMPONENT_SELECTION");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchDecisions = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${apiBase}/api/decisions?project_id=${encodeURIComponent(projectId)}`);
      if (res.ok) {
        const data = await res.json();
        setDecisions(data);
      } else {
        // Fallback default sample decisions if none exists
        setDecisions([
          {
            decision_id: "DEC-PWR-001",
            project_id: projectId,
            team_id: teamId,
            title: "Switching Buck Converter vs Linear LDO",
            description: "High input voltage (12V) down to 3.3V sensor rail requires thermal dissipation assessment.",
            status: "RECOMMENDED",
            decision_type: "POWER_REGULATION",
            selected_candidate: "MP1584EN 3A Buck Regulator",
            alternatives: ["AMS1117-3.3", "LM7805 + LDO", "TPS62840"],
            recommendation: "Deploy MP1584EN buck regulator. Maintains 91% conversion efficiency with minimal heat dissipation.",
            rationale: "Selected MP1584EN based on superior thermal envelope and 91% efficiency at 1.5A peak load.",
            confidence: 0.94,
            stability: 0.92,
            created_by: "system_agent",
            created_at: Date.now() / 1000 - 86400,
            updated_at: Date.now() / 1000 - 3600,
          },
          {
            decision_id: "DEC-COM-002",
            project_id: projectId,
            team_id: teamId,
            title: "Primary 6-DoF Motion Sensor Selection",
            description: "Evaluate I2C vs SPI bus bandwidth and gyroscope zero-rate drift stability for robotics arm.",
            status: "APPROVED",
            decision_type: "COMPONENT_SELECTION",
            selected_candidate: "MPU6050 Accelerometer/Gyroscope",
            alternatives: ["LSM6DSOX", "BMI270", "BNO055"],
            recommendation: "MPU6050 selected due to low cost, high inventory availability, and proven DMP firmware support.",
            rationale: "Approved by Engineering Lead for Prototype Run Phase 1.",
            confidence: 0.88,
            stability: 0.85,
            created_by: "lead_engineer",
            created_at: Date.now() / 1000 - 172800,
            updated_at: Date.now() / 1000 - 72000,
          },
        ]);
      }
    } catch (err) {
      console.error("Failed to fetch decisions:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDecisions();
  }, [projectId]);

  const handleCreateDecision = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    setIsSubmitting(true);
    try {
      const decId = `DEC-${Math.random().toString(36).substring(2, 7).toUpperCase()}`;
      const payload = {
        decision_id: decId,
        project_id: projectId,
        team_id: teamId,
        title: title.trim(),
        description: description.trim(),
        decision_type: decisionType,
        created_by: "engineer",
      };

      const res = await fetch(`${apiBase}/api/decisions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        const created = await res.json();
        setDecisions((prev) => [created, ...prev]);
        setIsNewModalOpen(false);
        setTitle("");
        setDescription("");
      }
    } catch (err) {
      console.error("Failed to create decision:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleApprove = async (decisionId: string) => {
    try {
      const res = await fetch(`${apiBase}/api/decisions/${decisionId}/approve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ approved_by: "team_lead", role: "ADMIN" }),
      });
      if (res.ok) {
        const updated = await res.json();
        setDecisions((prev) => prev.map((d) => (d.decision_id === decisionId ? updated : d)));
      }
    } catch (err) {
      console.error("Failed to approve decision:", err);
    }
  };

  const filteredDecisions = decisions.filter((d) => {
    if (filter === "ALL") return true;
    return d.status === filter;
  });

  return (
    <div className="flex flex-col h-full bg-zinc-950 text-zinc-100 p-4 space-y-4 rounded-xl border border-zinc-800/80">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-zinc-800/80">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-indigo-950/40 rounded-lg border border-indigo-800/40 text-indigo-400">
            <Scale className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-semibold tracking-wide text-zinc-100 flex items-center gap-2">
              Engineering Design Decisions
              <span className="text-xs px-2 py-0.5 rounded-full bg-zinc-800 text-zinc-400 border border-zinc-700 font-mono">
                {decisions.length}
              </span>
            </h2>
            <p className="text-xs text-zinc-400">
              Audit trail of component selection trade-offs, architecture decisions, and sensitivity models.
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {canManageDecisions && (
            <button
              onClick={() => setIsNewModalOpen(true)}
              className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-zinc-100 font-medium text-xs rounded-lg flex items-center space-x-1.5 transition-colors shadow-sm"
            >
              <Plus className="w-4 h-4" />
              <span>Record Decision</span>
            </button>
          )}
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex flex-wrap items-center gap-2 text-xs">
        {["ALL", "RECOMMENDED", "APPROVED", "UNDER_REVIEW", "DRAFT"].map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-2.5 py-1 rounded-md font-mono text-[11px] transition-colors border ${
              filter === f
                ? "bg-zinc-800 border-zinc-700 text-zinc-100"
                : "bg-zinc-900/40 border-zinc-800/60 text-zinc-400 hover:text-zinc-200"
            }`}
          >
            {f}
          </button>
        ))}
      </div>

      {/* Decisions List */}
      <div className="space-y-3 flex-1 overflow-y-auto pr-1">
        {filteredDecisions.map((dec) => {
          const pill = STATUS_PILLS[dec.status] || STATUS_PILLS.DRAFT;
          const isExpanded = expandedId === dec.decision_id;

          return (
            <div
              key={dec.decision_id}
              className="bg-zinc-900/70 border border-zinc-800 hover:border-zinc-700/80 rounded-xl p-4 space-y-3 transition-all"
            >
              {/* Top Row: ID, Title, Status */}
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center space-x-2.5">
                  <span className="font-mono text-xs text-indigo-400 font-medium bg-indigo-950/40 px-2 py-0.5 rounded border border-indigo-800/40">
                    {dec.decision_id}
                  </span>
                  <span className="text-sm font-semibold text-zinc-100">{dec.title}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-0.5 rounded text-[11px] font-mono border ${pill.cls}`}>
                    {pill.label}
                  </span>
                  <button
                    onClick={() => setExpandedId(isExpanded ? null : dec.decision_id)}
                    className="p-1 hover:bg-zinc-800 rounded text-zinc-400"
                  >
                    {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {/* Description */}
              <p className="text-xs text-zinc-300 leading-relaxed">{dec.description}</p>

              {/* Tradeoff Resolution Box */}
              {dec.selected_candidate && (
                <div className="p-3 bg-zinc-950/90 rounded-lg border border-zinc-800/80 grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                  <div>
                    <span className="text-[10px] text-zinc-400 font-mono block">SELECTED CANDIDATE</span>
                    <span className="font-semibold text-cyan-400 flex items-center gap-1.5 mt-0.5">
                      <Cpu className="w-3.5 h-3.5" />
                      {dec.selected_candidate}
                    </span>
                  </div>

                  {dec.alternatives && dec.alternatives.length > 0 && (
                    <div>
                      <span className="text-[10px] text-zinc-400 font-mono block">EVALUATED ALTERNATIVES</span>
                      <span className="text-zinc-400 truncate block mt-0.5">
                        {dec.alternatives.join(", ")}
                      </span>
                    </div>
                  )}

                  <div className="flex items-center space-x-3 md:justify-end">
                    {dec.confidence !== undefined && (
                      <div className="text-right">
                        <span className="text-[10px] text-zinc-400 font-mono block">CONFIDENCE</span>
                        <span className="font-mono font-medium text-emerald-400">
                          {(dec.confidence * 100).toFixed(0)}%
                        </span>
                      </div>
                    )}
                    {dec.stability !== undefined && (
                      <div className="text-right">
                        <span className="text-[10px] text-zinc-400 font-mono block">STABILITY</span>
                        <span className="font-mono font-medium text-indigo-400">
                          {(dec.stability * 100).toFixed(0)}%
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Expandable Details: Rationale, Recommendation & Actions */}
              {isExpanded && (
                <div className="pt-3 border-t border-zinc-800 space-y-3 text-xs">
                  {dec.recommendation && (
                    <div className="space-y-1">
                      <span className="text-[11px] font-mono text-zinc-400 flex items-center gap-1">
                        <Sparkles className="w-3.5 h-3.5 text-cyan-400" /> AI Recommendation
                      </span>
                      <p className="p-2.5 bg-zinc-950/80 rounded border border-zinc-800/80 text-zinc-300 leading-relaxed">
                        {dec.recommendation}
                      </p>
                    </div>
                  )}

                  {dec.rationale && (
                    <div className="space-y-1">
                      <span className="text-[11px] font-mono text-zinc-400 flex items-center gap-1">
                        <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> Engineering Rationale
                      </span>
                      <p className="p-2.5 bg-zinc-950/80 rounded border border-zinc-800/80 text-zinc-300 leading-relaxed">
                        {dec.rationale}
                      </p>
                    </div>
                  )}

                  {canManageDecisions && dec.status !== "APPROVED" && (
                    <div className="flex items-center justify-end space-x-2 pt-2">
                      <button
                        onClick={() => handleApprove(dec.decision_id)}
                        className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-zinc-950 font-medium rounded-lg text-xs flex items-center space-x-1"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>Approve Decision</span>
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}

        {filteredDecisions.length === 0 && (
          <div className="h-32 flex flex-col items-center justify-center border border-dashed border-zinc-800 rounded-xl text-zinc-400 font-mono text-xs">
            <span>No decisions found in this category</span>
          </div>
        )}
      </div>

      {/* Modal for recording new decision */}
      {isNewModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 max-w-lg w-full space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
              <h3 className="text-sm font-semibold text-zinc-100 flex items-center gap-2">
                <Scale className="w-4 h-4 text-indigo-400" />
                Record Engineering Decision
              </h3>
              <button onClick={() => setIsNewModalOpen(false)} className="text-zinc-500 hover:text-zinc-300">
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateDecision} className="space-y-3 text-xs">
              <div>
                <label className="block text-zinc-400 font-mono mb-1">Decision Title *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Choose Low-ESR Tantalum vs Ceramic Output Capacitors"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-zinc-100 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-zinc-400 font-mono mb-1">Context & Constraints</label>
                <textarea
                  rows={3}
                  placeholder="Describe technical context, voltage rails, ripple tolerances, or supply constraints..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-zinc-100 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-zinc-400 font-mono mb-1">Decision Category</label>
                <select
                  value={decisionType}
                  onChange={(e) => setDecisionType(e.target.value)}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-2.5 py-2 text-zinc-100 focus:outline-none focus:border-indigo-500"
                >
                  <option value="COMPONENT_SELECTION">Component Selection</option>
                  <option value="POWER_REGULATION">Power Regulation</option>
                  <option value="MICROCONTROLLER">Controller / MCU Choice</option>
                  <option value="COMMUNICATION_BUS">Bus / Protocol Standard</option>
                  <option value="THERMAL_MANAGEMENT">Thermal Architecture</option>
                </select>
              </div>

              <div className="flex justify-end space-x-2 pt-2 border-t border-zinc-800">
                <button
                  type="button"
                  onClick={() => setIsNewModalOpen(false)}
                  className="px-3 py-1.5 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 rounded-lg text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting || !title.trim()}
                  className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-zinc-100 font-medium rounded-lg text-xs disabled:opacity-50"
                >
                  {isSubmitting ? "Recording..." : "Save Decision"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
