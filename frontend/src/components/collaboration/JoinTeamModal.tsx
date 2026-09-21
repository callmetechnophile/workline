import React, { useState, useEffect } from "react";
import {
  Users,
  KeyRound,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  Clock,
  ArrowRight,
  ShieldAlert,
} from "lucide-react";

interface JoinTeamModalProps {
  isOpen: boolean;
  onClose: () => void;
  apiBase: string;
  onJoined: (teamData: any) => void;
}

interface TeamPreview {
  team_id: string;
  team_name: string;
  description?: string;
  member_count: number;
  require_join_approval: boolean;
  default_join_role: string;
  allowed_roles?: string[];
}

export const JoinTeamModal: React.FC<JoinTeamModalProps> = ({
  isOpen,
  onClose,
  apiBase,
  onJoined,
}) => {
  const [rawInput, setRawInput] = useState("");
  const [preview, setPreview] = useState<TeamPreview | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [previewError, setPreviewError] = useState<string | null>(null);

  const [joinLoading, setJoinLoading] = useState(false);
  const [joinResult, setJoinResult] = useState<{
    status: "JOINED" | "PENDING_APPROVAL" | "ERROR";
    message: string;
  } | null>(null);

  // Normalize input to uppercase, remove symbols
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let val = e.target.value.toUpperCase().replace(/[^A-Z0-9-]/g, "");
    if (!val.startsWith("WL-") && val.length > 0) {
      if (val.startsWith("WL")) {
        val = "WL-" + val.slice(2);
      } else if (!val.includes("-") && val.length <= 6) {
        // Allow typing 6 chars or WL-XXXXXX
      }
    }
    setRawInput(val);
    setPreview(null);
    setPreviewError(null);
    setJoinResult(null);
  };

  // Debounced preview check
  useEffect(() => {
    const clean = rawInput.trim();
    const effectiveCode = clean.startsWith("WL-") ? clean.slice(3) : clean;

    if (effectiveCode.length === 6) {
      setPreviewLoading(true);
      setPreviewError(null);

      const timer = setTimeout(async () => {
        try {
          const res = await fetch(`${apiBase}/api/teams/preview-code/${encodeURIComponent(clean)}`);
          if (res.ok) {
            const data = await res.json();
            setPreview(data);
          } else {
            setPreviewError("Invalid or expired team joining code.");
          }
        } catch (err) {
          setPreviewError("Failed to reach server to preview code.");
        } finally {
          setPreviewLoading(false);
        }
      }, 300);

      return () => clearTimeout(timer);
    } else {
      setPreview(null);
      setPreviewError(null);
    }
  }, [rawInput, apiBase]);

  const handleJoin = async (e: React.FormEvent) => {
    e.preventDefault();
    const clean = rawInput.trim();
    if (!clean) return;

    setJoinLoading(true);
    setJoinResult(null);

    try {
      const res = await fetch(`${apiBase}/api/teams/join`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code: clean }),
      });

      const data = await res.json();
      if (res.ok) {
        if (data.status === "PENDING_APPROVAL") {
          setJoinResult({
            status: "PENDING_APPROVAL",
            message: data.message || "Membership request submitted for administrator review.",
          });
        } else {
          setJoinResult({
            status: "JOINED",
            message: data.message || `Successfully joined ${data.team_name}!`,
          });
          setTimeout(() => {
            onJoined(data);
            onClose();
          }, 1500);
        }
      } else {
        setJoinResult({
          status: "ERROR",
          message: data.detail || "Failed to join team. Check code expiration.",
        });
      }
    } catch (err) {
      setJoinResult({
        status: "ERROR",
        message: "Network error joining team.",
      });
    } finally {
      setJoinLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
      <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 max-w-md w-full space-y-5 shadow-2xl text-zinc-100 text-xs">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-lg bg-cyan-950/60 border border-cyan-800/40 text-cyan-400">
              <KeyRound className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-zinc-100">Join Team Workspace</h3>
              <p className="text-[11px] text-zinc-400">Enter a secure WL-XXXXXX team joining code</p>
            </div>
          </div>
          <button onClick={onClose} className="text-zinc-500 hover:text-zinc-300">
            ✕
          </button>
        </div>

        <form onSubmit={handleJoin} className="space-y-4">
          <div>
            <label className="block text-zinc-400 font-mono mb-1.5">Team Joining Code</label>
            <input
              type="text"
              required
              placeholder="e.g. WL-7K4M2P or 7K4M2P"
              maxLength={9}
              value={rawInput}
              onChange={handleInputChange}
              className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2.5 text-center font-mono text-base tracking-widest text-cyan-400 placeholder-zinc-600 focus:outline-none focus:border-cyan-500"
            />
            <span className="text-[10px] text-zinc-500 font-mono mt-1 block">
              Format: WL-XXXXXX (case-insensitive, excludes ambiguous characters 0, 1, I, O)
            </span>
          </div>

          {/* Loading Indicator */}
          {previewLoading && (
            <div className="p-3 bg-zinc-950/60 rounded-lg border border-zinc-800 text-zinc-400 text-center font-mono animate-pulse">
              Verifying team credentials...
            </div>
          )}

          {/* Error Message */}
          {previewError && (
            <div className="p-3 bg-rose-950/30 border border-rose-800/40 rounded-lg text-rose-300 flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
              <span>{previewError}</span>
            </div>
          )}

          {/* Live Preview Card */}
          {preview && (
            <div className="p-3.5 bg-zinc-950/80 rounded-xl border border-cyan-800/40 space-y-2.5">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono text-cyan-400 uppercase tracking-wider">
                  Target Team Preview
                </span>
                <span className="px-2 py-0.5 rounded bg-zinc-800 text-zinc-300 font-mono text-[10px]">
                  {preview.member_count} member{preview.member_count === 1 ? "" : "s"}
                </span>
              </div>

              <div className="space-y-1">
                <div className="font-semibold text-sm text-zinc-100">{preview.team_name}</div>
                {preview.description && (
                  <p className="text-[11px] text-zinc-400 leading-relaxed">{preview.description}</p>
                )}
              </div>

              <div className="pt-2 border-t border-zinc-800 flex items-center justify-between text-[11px]">
                <span className="text-zinc-400">Assigned Role:</span>
                <span className="font-mono text-cyan-300 font-medium">{preview.default_join_role}</span>
              </div>

              {preview.require_join_approval && (
                <div className="p-2 bg-amber-950/40 border border-amber-800/30 rounded text-amber-300 flex items-center space-x-2 text-[11px]">
                  <ShieldAlert className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                  <span>Admin approval is required to activate membership.</span>
                </div>
              )}
            </div>
          )}

          {/* Result Feedback */}
          {joinResult && (
            <div
              className={`p-3 rounded-lg border text-xs flex items-start space-x-2 ${
                joinResult.status === "JOINED"
                  ? "bg-emerald-950/40 border-emerald-800/40 text-emerald-300"
                  : joinResult.status === "PENDING_APPROVAL"
                  ? "bg-amber-950/40 border-amber-800/40 text-amber-300"
                  : "bg-rose-950/40 border-rose-800/40 text-rose-300"
              }`}
            >
              {joinResult.status === "JOINED" ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              ) : joinResult.status === "PENDING_APPROVAL" ? (
                <Clock className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
              ) : (
                <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
              )}
              <span>{joinResult.message}</span>
            </div>
          )}

          <div className="flex justify-end space-x-2 pt-2 border-t border-zinc-800">
            <button
              type="button"
              onClick={onClose}
              className="px-3.5 py-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 rounded-lg text-xs"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={joinLoading || !preview}
              className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-zinc-950 font-medium rounded-lg text-xs flex items-center space-x-1.5"
            >
              {joinLoading ? "Joining..." : preview?.require_join_approval ? "Submit Request" : "Join Workspace"}
              <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
