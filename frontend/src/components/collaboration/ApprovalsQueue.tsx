import React, { useState, useEffect } from "react";
import {
  ShieldAlert,
  CheckCircle2,
  XCircle,
  Clock,
  FileDiff,
  User,
  AlertTriangle,
  ArrowRight,
  Filter,
} from "lucide-react";

export type ApprovalStatus = "PENDING" | "APPROVED" | "REJECTED" | "CANCELLED";

export interface ApprovalItem {
  id: string;
  project_id: string;
  team_id?: string;
  requester_id: string;
  requester_name?: string;
  approver_id?: string;
  approver_name?: string;
  artifact_type: string;
  artifact_id: string;
  action: string;
  reason?: string;
  diff_summary?: string;
  metadata?: Record<string, any>;
  status: ApprovalStatus;
  created_at: string;
  resolved_at?: string;
  resolution_notes?: string;
}

interface ApprovalsQueueProps {
  teamId: string;
  projectId?: string;
  apiBase: string;
  currentUserRole?: string;
}

const STATUS_CONFIG: Record<ApprovalStatus, { label: string; cls: string }> = {
  PENDING: { label: "PENDING GATE", cls: "bg-amber-950/60 text-amber-300 border-amber-800/40 animate-pulse" },
  APPROVED: { label: "APPROVED", cls: "bg-emerald-950/60 text-emerald-300 border-emerald-800/40" },
  REJECTED: { label: "REJECTED", cls: "bg-rose-950/60 text-rose-400 border-rose-800/40" },
  CANCELLED: { label: "CANCELLED", cls: "bg-zinc-800 text-zinc-400 border-zinc-700" },
};

export const ApprovalsQueue: React.FC<ApprovalsQueueProps> = ({
  teamId,
  projectId = "default_project",
  apiBase,
  currentUserRole = "ENGINEER",
}) => {
  const [approvals, setApprovals] = useState<ApprovalItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState<string>("PENDING");
  const [actionModal, setActionModal] = useState<{
    open: boolean;
    item: ApprovalItem | null;
    actionType: "APPROVED" | "REJECTED";
  }>({ open: false, item: null, actionType: "APPROVED" });
  const [notes, setNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const canApprove = currentUserRole === "OWNER" || currentUserRole === "ADMIN";

  const fetchApprovals = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${apiBase}/api/approvals?project_id=${encodeURIComponent(projectId)}`);
      if (res.ok) {
        const data = await res.json();
        setApprovals(Array.isArray(data) ? data : []);
      } else {
        setApprovals([]);
      }
    } catch (err) {
      console.error("Failed to fetch approvals:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApprovals();
  }, [projectId]);

  const handleResolve = async () => {
    if (!actionModal.item) return;
    setSubmitting(true);
    try {
      const res = await fetch(`${apiBase}/api/approvals/${actionModal.item.id}/resolve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          status: actionModal.actionType,
          notes: notes.trim() || undefined,
        }),
      });

      if (res.ok) {
        const resolved = await res.json();
        setApprovals((prev) =>
          prev.map((a) => (a.id === actionModal.item!.id ? resolved : a))
        );
        setActionModal({ open: false, item: null, actionType: "APPROVED" });
        setNotes("");
      }
    } catch (err) {
      console.error("Resolve approval failed:", err);
    } finally {
      setSubmitting(false);
    }
  };

  const filteredApprovals = approvals.filter((a) => {
    if (filter === "ALL") return true;
    return a.status === filter;
  });

  return (
    <div className="flex flex-col h-full bg-zinc-950 text-zinc-100 p-4 space-y-4 rounded-xl border border-zinc-800/80">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-zinc-800/80">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-amber-950/40 rounded-lg border border-amber-800/40 text-amber-400">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-semibold tracking-wide text-zinc-100 flex items-center gap-2">
              Sensitive Approvals Queue
              <span className="text-xs px-2 py-0.5 rounded-full bg-zinc-800 text-zinc-400 border border-zinc-700 font-mono">
                {approvals.filter((a) => a.status === "PENDING").length} pending
              </span>
            </h2>
            <p className="text-xs text-zinc-400">
              Mandatory engineering review gates for BOM modifications, component swaps, and release sign-offs.
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {["ALL", "PENDING", "APPROVED", "REJECTED"].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-2.5 py-1 rounded-md font-mono text-[11px] transition-colors border ${
                filter === f
                  ? "bg-zinc-800 border-zinc-700 text-zinc-100 font-semibold"
                  : "bg-zinc-900/40 border-zinc-800/60 text-zinc-400 hover:text-zinc-200"
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {/* Approvals List */}
      <div className="space-y-3 flex-1 overflow-y-auto pr-1">
        {filteredApprovals.map((item) => {
          const cfg = STATUS_CONFIG[item.status] || STATUS_CONFIG.PENDING;

          return (
            <div
              key={item.id}
              className="bg-zinc-900/70 border border-zinc-800 hover:border-zinc-700 rounded-xl p-4 space-y-3 transition-all"
            >
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center space-x-2">
                  <span className="font-mono text-xs text-amber-400 bg-amber-950/40 px-2 py-0.5 rounded border border-amber-800/40 font-medium">
                    {item.id}
                  </span>
                  <span className="text-xs px-2 py-0.5 rounded bg-zinc-800 text-zinc-300 font-mono text-[10px]">
                    {item.artifact_type}
                  </span>
                  <span className="text-sm font-semibold text-zinc-100">{item.action}</span>
                </div>
                <span className={`px-2 py-0.5 rounded text-[11px] font-mono border ${cfg.cls}`}>
                  {cfg.label}
                </span>
              </div>

              {/* Rationale / Reason */}
              {item.reason && (
                <p className="text-xs text-zinc-300 leading-relaxed">
                  <span className="text-zinc-400 font-mono">Reason: </span>
                  {item.reason}
                </p>
              )}

              {/* Diff Summary */}
              {item.diff_summary && (
                <div className="p-2.5 bg-zinc-950/90 rounded-lg border border-zinc-800/80 font-mono text-xs text-zinc-300 flex items-start gap-2">
                  <FileDiff className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                  <div className="truncate">
                    <span className="text-zinc-400 text-[10px] block">PROPOSED CHANGE DIFF:</span>
                    <span className="text-cyan-300">{item.diff_summary}</span>
                  </div>
                </div>
              )}

              {/* Metadata Footer */}
              <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-zinc-800/60 text-[11px] text-zinc-400 font-mono">
                <div className="flex items-center space-x-3">
                  <span className="flex items-center gap-1">
                    <User className="w-3 h-3 text-zinc-400" />
                    Requested by: <strong className="text-zinc-300 font-normal">{item.requester_name || item.requester_id}</strong>
                  </span>
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3 text-zinc-400" />
                    {new Date(item.created_at).toLocaleDateString()} {new Date(item.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                  </span>
                </div>

                {/* Approver / Resolution Notes */}
                {item.approver_id && (
                  <span className="text-emerald-400">
                    Reviewed by: {item.approver_name || item.approver_id}
                    {item.resolution_notes && ` ("${item.resolution_notes}")`}
                  </span>
                )}

                {/* Review Gate Controls */}
                {item.status === "PENDING" && (
                  <div className="flex items-center space-x-2">
                    {canApprove ? (
                      <>
                        <button
                          onClick={() => setActionModal({ open: true, item, actionType: "REJECTED" })}
                          className="px-2.5 py-1 bg-rose-950/50 hover:bg-rose-900/60 text-rose-300 border border-rose-800/50 rounded-lg text-xs flex items-center space-x-1"
                        >
                          <XCircle className="w-3.5 h-3.5" />
                          <span>Reject</span>
                        </button>
                        <button
                          onClick={() => setActionModal({ open: true, item, actionType: "APPROVED" })}
                          className="px-3 py-1 bg-emerald-600 hover:bg-emerald-500 text-zinc-950 font-medium rounded-lg text-xs flex items-center space-x-1 shadow-sm"
                        >
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          <span>Approve Gate</span>
                        </button>
                      </>
                    ) : (
                      <span className="text-[11px] text-zinc-400 italic">
                        Requires Lead / Admin approval
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {filteredApprovals.length === 0 && (
          <div className="h-32 flex flex-col items-center justify-center border border-dashed border-zinc-800 rounded-xl text-zinc-400 font-mono text-xs">
            <span>No approval requests found in this view</span>
          </div>
        )}
      </div>

      {/* Confirmation Modal */}
      {actionModal.open && actionModal.item && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 max-w-md w-full space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
              <h3 className="text-sm font-semibold text-zinc-100 flex items-center gap-2">
                {actionModal.actionType === "APPROVED" ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                ) : (
                  <XCircle className="w-4 h-4 text-rose-400" />
                )}
                {actionModal.actionType === "APPROVED" ? "Approve Engineering Change" : "Reject Engineering Change"}
              </h3>
              <button onClick={() => setActionModal({ open: false, item: null, actionType: "APPROVED" })} className="text-zinc-500 hover:text-zinc-300">
                ✕
              </button>
            </div>

            <p className="text-xs text-zinc-300">
              You are resolving gate request <strong className="text-zinc-100 font-mono">{actionModal.item.id}</strong>:
              <br />
              <span className="italic text-zinc-400">"{actionModal.item.action}"</span>
            </p>

            <div>
              <label className="block text-zinc-400 font-mono text-xs mb-1">
                Review Notes / Condition of Acceptance
              </label>
              <textarea
                rows={3}
                placeholder="Optional comments or sign-off condition..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-xs text-zinc-100 focus:outline-none focus:border-amber-500"
              />
            </div>

            <div className="flex justify-end space-x-2 pt-2 border-t border-zinc-800 text-xs">
              <button
                type="button"
                onClick={() => setActionModal({ open: false, item: null, actionType: "APPROVED" })}
                className="px-3 py-1.5 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 rounded-lg"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={submitting}
                onClick={handleResolve}
                className={`px-4 py-1.5 rounded-lg font-medium text-xs ${
                  actionModal.actionType === "APPROVED"
                    ? "bg-emerald-600 hover:bg-emerald-500 text-zinc-950"
                    : "bg-rose-600 hover:bg-rose-500 text-zinc-100"
                }`}
              >
                {submitting ? "Processing..." : actionModal.actionType === "APPROVED" ? "Confirm Approval" : "Confirm Rejection"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
