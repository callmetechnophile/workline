import React, { useState } from 'react';

interface TeamInvitationPanelProps {
  teamId: string;
  teamName: string;
  memberCount?: number;
  apiBase?: string;
}

export const TeamInvitationPanel: React.FC<TeamInvitationPanelProps> = ({
  teamId,
  teamName,
  memberCount = 1,
  apiBase = '',
}) => {
  const [ttlDays, setTtlDays] = useState<number>(7);
  const [maxUses, setMaxUses] = useState<number>(10);
  const [role, setRole] = useState<string>('MEMBER');
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [invitationData, setInvitationData] = useState<any | null>(null);
  const [copyLinkFeedback, setCopyLinkFeedback] = useState<boolean>(false);
  const [copyMessageFeedback, setCopyMessageFeedback] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleCreateInvitation = async () => {
    setIsGenerating(true);
    setError(null);
    try {
      const res = await fetch(`${apiBase}/api/teams/${teamId}/invitations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          created_by: 'Team Owner',
          ttl_days: ttlDays,
          max_uses: maxUses,
          role,
        }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Failed to generate invitation');
      }

      const data = await res.json();
      setInvitationData(data);
    } catch (err: any) {
      setError(err.message || 'Invitation generation failed');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleRevoke = async () => {
    if (!invitationData) return;
    try {
      const res = await fetch(`${apiBase}/api/teams/${teamId}/invitations/${invitationData.invitation_id}/revoke`, {
        method: 'POST',
      });
      if (res.ok) {
        setInvitationData(null);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleRegenerate = async () => {
    if (!invitationData) return;
    setIsGenerating(true);
    try {
      const res = await fetch(`${apiBase}/api/teams/${teamId}/invitations/${invitationData.invitation_id}/regenerate`, {
        method: 'POST',
      });
      if (res.ok) {
        const data = await res.json();
        setInvitationData(data);
      }
    } catch (err: any) {
      setError(err.message || 'Regeneration failed');
    } finally {
      setIsGenerating(false);
    }
  };

  const copyToClipboard = (text: string, isMessage: boolean = false) => {
    navigator.clipboard.writeText(text).then(() => {
      if (isMessage) {
        setCopyMessageFeedback(true);
        setTimeout(() => setCopyMessageFeedback(false), 2000);
      } else {
        setCopyLinkFeedback(true);
        setTimeout(() => setCopyLinkFeedback(false), 2000);
      }
    });
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl text-slate-100 max-w-xl mx-auto space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <div className="text-xs uppercase tracking-wider text-slate-400">Team Collaboration</div>
          <h3 className="text-xl font-bold text-cyan-400">{teamName}</h3>
          <div className="text-xs text-slate-400 font-mono mt-0.5">Team ID: {teamId} • Members: {memberCount}</div>
        </div>
        <span className="px-3 py-1 bg-cyan-950 text-cyan-400 border border-cyan-800 rounded-full text-xs font-mono">
          SECURE INVITATION
        </span>
      </div>

      {!invitationData ? (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Expiration</label>
              <select
                value={ttlDays}
                onChange={(e) => setTtlDays(Number(e.target.value))}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-500"
              >
                <option value={1}>1 Day</option>
                <option value={7}>7 Days (Default)</option>
                <option value={30}>30 Days</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Max Uses</label>
              <select
                value={maxUses}
                onChange={(e) => setMaxUses(Number(e.target.value))}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-500"
              >
                <option value={1}>Single-Use (1)</option>
                <option value={5}>5 Uses</option>
                <option value={10}>10 Uses (Default)</option>
                <option value={50}>50 Uses</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Assigned Role</label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-500"
            >
              <option value="MEMBER">Member (Standard)</option>
              <option value="ENGINEER">Engineer (PCB/Hardware)</option>
              <option value="ADMIN">Admin</option>
            </select>
          </div>

          {error && (
            <div className="p-3 bg-red-950/60 border border-red-800 text-red-300 text-xs rounded-lg">{error}</div>
          )}

          <button
            onClick={handleCreateInvitation}
            disabled={isGenerating}
            className="w-full py-3 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white font-bold rounded-lg transition shadow-lg flex items-center justify-center gap-2 text-sm"
          >
            {isGenerating ? 'Generating Secure Link...' : 'Generate Secure Invitation Link'}
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400">Status: <strong className="text-emerald-400">{invitationData.status}</strong></span>
            <span className="text-slate-400">Expires: <strong className="text-white">{invitationData.expires_at?.substring(0, 10)}</strong></span>
          </div>

          <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg font-mono text-xs text-cyan-300 break-all select-all">
            {invitationData.join_url}
          </div>

          <p className="text-xs text-slate-400 italic">
            Copy the invitation link and send it to the person you want to invite.
          </p>

          <div className="grid grid-cols-2 gap-2 pt-2">
            <button
              onClick={() => copyToClipboard(invitationData.join_url, false)}
              className="py-2 px-3 bg-cyan-600 hover:bg-cyan-500 text-white font-bold rounded-lg text-xs transition flex items-center justify-center gap-1 shadow"
            >
              {copyLinkFeedback ? '✓ Link Copied!' : 'Copy Link'}
            </button>

            <button
              onClick={() => copyToClipboard(invitationData.message_template, true)}
              className="py-2 px-3 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-bold rounded-lg text-xs transition flex items-center justify-center gap-1"
            >
              {copyMessageFeedback ? '✓ Message Copied!' : 'Copy Message'}
            </button>
          </div>

          <div className="flex justify-between border-t border-slate-800 pt-3">
            <button
              onClick={handleRegenerate}
              disabled={isGenerating}
              className="text-xs text-yellow-400 hover:underline disabled:opacity-50"
            >
              Regenerate Link
            </button>
            <button
              onClick={handleRevoke}
              className="text-xs text-red-400 hover:underline"
            >
              Revoke Invitation
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
export default TeamInvitationPanel;
