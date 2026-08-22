import React, { useEffect, useState } from 'react';

interface InvitationPreviewProps {
  token: string;
  currentUserId?: string;
  currentUserName?: string;
  apiBase?: string;
  onJoined?: (teamData: any) => void;
  onCancel?: () => void;
}

export const InvitationPreview: React.FC<InvitationPreviewProps> = ({
  token,
  currentUserId,
  currentUserName,
  apiBase = '',
  onJoined,
  onCancel,
}) => {
  const [loading, setLoading] = useState<boolean>(true);
  const [preview, setPreview] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isJoining, setIsJoining] = useState<boolean>(false);
  const [joinSuccess, setJoinSuccess] = useState<string | null>(null);

  useEffect(() => {
    const fetchPreview = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`${apiBase}/api/invitations/${encodeURIComponent(token)}/preview`);
        if (!res.ok) {
          throw new Error('This invitation is invalid or no longer available.');
        }
        const data = await res.json();
        setPreview(data);
      } catch (err: any) {
        setError(err.message || 'This invitation is invalid or no longer available.');
      } finally {
        setLoading(false);
      }
    };

    if (token) {
      fetchPreview();
    }
  }, [token, apiBase]);

  const handleJoin = async () => {
    if (!currentUserId) {
      // Redirect to login preserving token
      window.location.href = `/login?redirect=/team/join/${encodeURIComponent(token)}`;
      return;
    }

    setIsJoining(true);
    setError(null);
    try {
      const res = await fetch(`${apiBase}/api/invitations/${encodeURIComponent(token)}/accept`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: currentUserId,
          user_name: currentUserName || currentUserId,
        }),
      });

      if (!res.ok) {
        throw new Error('This invitation is invalid or no longer available.');
      }

      const result = await res.json();
      setJoinSuccess(result.message || 'Successfully joined team.');
      if (onJoined) onJoined(result);
    } catch (err: any) {
      setError(err.message || 'Failed to join team.');
    } finally {
      setIsJoining(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 max-w-md mx-auto text-center text-slate-400 text-sm">
        Validating secure invitation token...
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 max-w-md mx-auto text-center space-y-4">
        <div className="w-12 h-12 rounded-full bg-red-950/60 border border-red-800 text-red-400 flex items-center justify-center mx-auto text-xl font-bold">
          ✕
        </div>
        <h3 className="text-lg font-bold text-white">Invitation Unavailable</h3>
        <p className="text-xs text-slate-400">{error}</p>
        <button
          onClick={onCancel || (() => (window.location.href = '/'))}
          className="py-2 px-4 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-xs font-semibold"
        >
          Return to Dashboard
        </button>
      </div>
    );
  }

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-2xl text-slate-100 max-w-md mx-auto space-y-6">
      <div className="text-center space-y-1">
        <div className="text-xs font-bold uppercase tracking-wider text-cyan-400">Team Invitation</div>
        <h2 className="text-2xl font-black text-white">{preview?.team_name}</h2>
        <p className="text-xs text-slate-400">You have been invited to collaborate on Workline.</p>
      </div>

      <div className="p-4 bg-slate-800/60 rounded-lg border border-slate-700/50 space-y-2 text-xs font-mono">
        <div className="flex justify-between">
          <span className="text-slate-400">Members:</span>
          <span className="text-white font-bold">{preview?.member_count}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">Invited By:</span>
          <span className="text-white">{preview?.invited_by}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">Role:</span>
          <span className="text-cyan-400 font-bold">{preview?.role}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-slate-400">Expires:</span>
          <span className="text-slate-300">{preview?.expires_at?.substring(0, 10)}</span>
        </div>
      </div>

      {joinSuccess ? (
        <div className="p-4 bg-emerald-950/60 border border-emerald-800 text-emerald-300 text-xs rounded-lg text-center font-bold">
          ✓ {joinSuccess}
        </div>
      ) : (
        <div className="space-y-2">
          <button
            onClick={handleJoin}
            disabled={isJoining}
            className="w-full py-3 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white font-bold rounded-lg transition shadow-lg text-sm"
          >
            {isJoining ? 'Joining Team...' : 'Join Team'}
          </button>
          {onCancel && (
            <button
              onClick={onCancel}
              className="w-full py-2 bg-transparent hover:bg-slate-800 text-slate-400 hover:text-white rounded-lg text-xs transition"
            >
              Cancel
            </button>
          )}
        </div>
      )}
    </div>
  );
};
export default InvitationPreview;
