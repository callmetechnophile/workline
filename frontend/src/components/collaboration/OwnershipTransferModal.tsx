import React, { useState } from "react";
import {
  ShieldAlert,
  AlertTriangle,
  ArrowRight,
  UserCheck,
} from "lucide-react";

interface Member {
  id: string | number;
  user_id: string;
  name?: string;
  role: string;
}

interface OwnershipTransferModalProps {
  isOpen: boolean;
  onClose: () => void;
  teamId: string;
  teamName: string;
  currentUserId: string;
  members: Member[];
  apiBase: string;
  onSuccess: () => void;
}

export const OwnershipTransferModal: React.FC<OwnershipTransferModalProps> = ({
  isOpen,
  onClose,
  teamId,
  teamName,
  currentUserId,
  members,
  apiBase,
  onSuccess,
}) => {
  const [selectedTarget, setSelectedTarget] = useState("");
  const [confirmationInput, setConfirmationInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  // Eligible members excluding current owner
  const eligibleMembers = members.filter((m) => m.user_id !== currentUserId);

  const isConfirmed = confirmationInput.trim() === teamName.trim();

  const handleTransfer = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedTarget || !isConfirmed) return;

    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${apiBase}/api/teams/${teamId}/transfer-ownership`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          target_user_id: selectedTarget,
          confirmation_phrase: confirmationInput.trim(),
        }),
      });

      const data = await res.json();
      if (res.ok) {
        onSuccess();
        onClose();
      } else {
        setError(data.detail || "Failed to transfer ownership.");
      }
    } catch (err) {
      setError("Network error during ownership transfer.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 text-zinc-100 text-xs">
      <div className="bg-zinc-900 border border-rose-800/60 rounded-2xl p-6 max-w-md w-full space-y-5 shadow-2xl">
        {/* Header */}
        <div className="flex items-center space-x-3 pb-3 border-b border-zinc-800">
          <div className="p-2 rounded-xl bg-rose-950/60 border border-rose-800/40 text-rose-400">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-zinc-100">Transfer Team Ownership</h3>
            <p className="text-[11px] text-zinc-400 font-mono">Irreversible governance action</p>
          </div>
        </div>

        {/* Warning Callout */}
        <div className="p-3 bg-rose-950/30 border border-rose-800/40 rounded-xl space-y-2 text-rose-300">
          <div className="flex items-center space-x-2 font-semibold text-rose-400">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span>Caution: Ownership Cannot Be Undone</span>
          </div>
          <p className="text-[11px] leading-relaxed text-zinc-300">
            You are handing complete administrative authority of <strong className="text-zinc-100">{teamName}</strong> to another engineer.
            Your role will be demoted to <strong className="text-amber-300 font-mono">ADMIN</strong>. Only the new owner can transfer it back.
          </p>
        </div>

        <form onSubmit={handleTransfer} className="space-y-4">
          {/* Target Member Selector */}
          <div>
            <label className="block text-zinc-400 font-mono mb-1">
              Select New Team Owner *
            </label>
            <select
              required
              value={selectedTarget}
              onChange={(e) => setSelectedTarget(e.target.value)}
              className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-zinc-100 focus:outline-none focus:border-rose-500"
            >
              <option value="">-- Choose active member --</option>
              {eligibleMembers.map((m) => (
                <option key={m.user_id} value={m.user_id}>
                  {m.name || m.user_id} ({m.role})
                </option>
              ))}
            </select>
          </div>

          {/* Typing confirmation */}
          <div>
            <label className="block text-zinc-400 font-mono mb-1">
              Type <span className="text-zinc-100 font-bold font-mono select-all">"{teamName}"</span> to confirm:
            </label>
            <input
              type="text"
              required
              placeholder={teamName}
              value={confirmationInput}
              onChange={(e) => setConfirmationInput(e.target.value)}
              className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 font-mono text-zinc-100 focus:outline-none focus:border-rose-500"
            />
          </div>

          {error && (
            <div className="p-2.5 bg-rose-950/40 border border-rose-800/40 rounded text-rose-300 text-[11px]">
              {error}
            </div>
          )}

          {/* Buttons */}
          <div className="flex justify-end space-x-2 pt-2 border-t border-zinc-800">
            <button
              type="button"
              onClick={onClose}
              className="px-3 py-1.5 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 rounded-lg"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || !selectedTarget || !isConfirmed}
              className="px-4 py-1.5 bg-rose-600 hover:bg-rose-500 disabled:opacity-50 text-zinc-100 font-medium rounded-lg flex items-center space-x-1.5"
            >
              <UserCheck className="w-4 h-4" />
              <span>{loading ? "Transferring..." : "Confirm Transfer"}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
