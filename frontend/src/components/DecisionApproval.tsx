"use client";

import React, { useState } from "react";
import { ShieldCheck, UserCheck, CheckCircle2, AlertOctagon } from "lucide-react";

export interface DecisionApprovalProps {
  decisionId?: string;
  candidateName?: string;
  onConfirmApprove?: (actor: string, role: string) => void;
  onReject?: (actor: string, reason: string) => void;
}

export const DecisionApproval: React.FC<DecisionApprovalProps> = ({
  decisionId = "DEC-3V3-REG",
  candidateName = "TPS62130",
  onConfirmApprove,
  onReject,
}) => {
  const [actorName, setActorName] = useState("lead_engineer");
  const [role, setRole] = useState("ENGINEER");
  const [rejectionReason, setRejectionReason] = useState("");

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4 text-zinc-100">
      <div className="flex items-center gap-2 pb-2 border-b border-zinc-800">
        <ShieldCheck className="w-5 h-5 text-emerald-400" />
        <h3 className="text-base font-bold text-zinc-100">Engineering Approval & Sign-Off</h3>
      </div>

      <div className="p-3 bg-amber-950/20 border border-amber-800/60 rounded-lg flex items-start gap-2 text-xs text-amber-300">
        <AlertOctagon className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
        <span>
          <strong>Human Authorization Required:</strong> Workline decisions cannot be automatically approved by autonomous agents without human sign-off.
        </span>
      </div>

      <div className="flex flex-col gap-3 text-xs">
        <div className="flex flex-col gap-1">
          <label className="text-zinc-400">Approving Engineer:</label>
          <input
            type="text"
            value={actorName}
            onChange={(e) => setActorName(e.target.value)}
            className="p-2 bg-zinc-950 border border-zinc-800 rounded text-zinc-100 font-mono"
          />
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-zinc-400">Role:</label>
          <select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            className="p-2 bg-zinc-950 border border-zinc-800 rounded text-zinc-100 font-mono"
          >
            <option value="ENGINEER">ENGINEER</option>
            <option value="OWNER">OWNER</option>
            <option value="REVIEWER">REVIEWER</option>
          </select>
        </div>

        <div className="flex items-center gap-3 pt-2">
          <button
            onClick={() => onConfirmApprove && onConfirmApprove(actorName, role)}
            className="flex items-center gap-1.5 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded font-bold text-xs transition"
          >
            <CheckCircle2 className="w-4 h-4" />
            Sign & Approve ({candidateName})
          </button>
        </div>
      </div>
    </div>
  );
};
