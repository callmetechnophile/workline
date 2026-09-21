import React, { useEffect, useState } from 'react';
import { getGatewayBearerToken } from '../lib/cognito';
import { API_BASE_URL } from '../lib/api';

interface InvitationListProps {
  teamId: string;
  apiBase?: string;
}

export const InvitationList: React.FC<InvitationListProps> = ({ teamId, apiBase = '' }) => {
  const [invitations, setInvitations] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const getEffectiveBase = () => {
    return (apiBase || API_BASE_URL || '').replace(/\/$/, '');
  };

  const getCachedInvitations = (): any[] => {
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        const raw = localStorage.getItem(`workline_team_invitations_${teamId}`);
        return raw ? JSON.parse(raw) : [];
      }
    } catch {}
    return [];
  };

  const fetchInvitations = async () => {
    setLoading(true);
    const cached = getCachedInvitations();
    try {
      const effectiveBase = getEffectiveBase();
      const token = await getGatewayBearerToken().catch(() => null);
      const headers: Record<string, string> = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      if (effectiveBase) {
        const res = await fetch(`${effectiveBase}/api/teams/${teamId}/invitations`, { headers });
        if (res.ok) {
          const apiData = await res.json();
          // Merge API data with any local cached invitations not yet in backend
          const apiIds = new Set(apiData.map((x: any) => x.invitation_id));
          const uniqueLocal = cached.filter((x: any) => !apiIds.has(x.invitation_id));
          setInvitations([...apiData, ...uniqueLocal]);
          return;
        }
      }
      setInvitations(cached);
    } catch (err) {
      console.warn('Failed to fetch remote invitations, using cached:', err);
      setInvitations(cached);
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
      const effectiveBase = getEffectiveBase();
      const token = await getGatewayBearerToken().catch(() => null);
      const headers: Record<string, string> = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      if (effectiveBase) {
        await fetch(`${effectiveBase}/api/teams/${teamId}/invitations/${invitationId}/revoke`, {
          method: 'POST',
          headers,
        }).catch(() => {});
      }
    } catch (err) {
      console.error(err);
    } finally {
      // Update local storage
      try {
        if (typeof window !== 'undefined' && window.localStorage) {
          const key = `workline_team_invitations_${teamId}`;
          const existingRaw = localStorage.getItem(key);
          if (existingRaw) {
            const list = JSON.parse(existingRaw);
            const updated = list.map((item: any) =>
              item.invitation_id === invitationId ? { ...item, status: 'REVOKED' } : item
            );
            localStorage.setItem(key, JSON.stringify(updated));
          }
        }
      } catch {}
      fetchInvitations();
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
