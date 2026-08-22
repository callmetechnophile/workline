import React, { useEffect, useState } from 'react';

interface InvitationListProps {
  teamId: string;
  apiBase?: string;
}

export const InvitationList: React.FC<InvitationListProps> = ({ teamId, apiBase = '' }) => {
  const [invitations, setInvitations] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchInvitations = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${apiBase}/api/teams/${teamId}/invitations`);
      if (res.ok) {
        const data = await res.json();
        setInvitations(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (teamId) {
      fetchInvitations();
    }
  }, [teamId, apiBase]);

  const handleRevoke = async (invitationId: string) => {
    try {
      const res = await fetch(`${apiBase}/api/teams/${teamId}/invitations/${invitationId}/revoke`, {
        method: 'POST',
      });
      if (res.ok) {
        fetchInvitations();
      }
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return <div className="text-xs text-slate-400 p-4 text-center">Loading invitations...</div>;
  }

  if (invitations.length === 0) {
    return <div className="text-xs text-slate-500 p-4 text-center">No invitations created yet.</div>;
  }

  return (
    <div className="space-y-3">
      <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">Team Invitations</h4>
      <div className="space-y-2">
        {invitations.map((inv) => (
          <div
            key={inv.invitation_id}
            className="p-3 bg-slate-800/60 rounded-lg border border-slate-700/50 flex items-center justify-between text-xs font-mono"
          >
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-white">{inv.invitation_id}</span>
                <span
                  className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    inv.status === 'ACTIVE'
                      ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                      : 'bg-slate-750 text-slate-400'
                  }`}
                >
                  {inv.status}
                </span>
              </div>
              <div className="text-slate-400 text-[11px] mt-1">
                Uses: {inv.use_count} / {inv.max_uses} • Expires: {inv.expires_at?.substring(0, 10)} • Role: {inv.role}
              </div>
            </div>
            {inv.status === 'ACTIVE' && (
              <button
                onClick={() => handleRevoke(inv.invitation_id)}
                className="text-red-400 hover:text-red-300 text-xs hover:underline font-sans font-semibold"
              >
                Revoke
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
export default InvitationList;
