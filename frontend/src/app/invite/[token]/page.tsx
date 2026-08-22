'use client';

import React, { use, useState, useEffect } from 'react';
import { useAuth } from '@clerk/nextjs';
import { Users, Shield, Calendar, Layers, Clock, AlertOctagon, CheckCircle2, ChevronRight } from 'lucide-react';

export const dynamic = 'force-dynamic';

interface InvitePageProps {
  params: Promise<{ token: string }>;
}

export default function InvitePage({ params }: InvitePageProps) {
  const { token } = use(params);
  const { isLoaded, isSignedIn, userId } = useAuth();
  const [inviteData, setInviteData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState(false);

  // Authentication check & Redirect
  useEffect(() => {
    if (isLoaded && !isSignedIn) {
      // Redirect to login page, preserving invite link
      const currentPath = window.location.pathname;
      window.location.href = `/login?redirect=${encodeURIComponent(currentPath)}`;
    }
  }, [isLoaded, isSignedIn]);

  // Fetch Invitation Metadata
  useEffect(() => {
    async function fetchInvitation() {
      if (!isSignedIn) return;
      setLoading(true);
      try {
        const apiBase = ""; // relative
        const res = await fetch(`${apiBase}/api/collaboration/invitations/${token}`);
        if (!res.ok) {
          const detail = await res.json().catch(() => ({}));
          throw new Error(detail.detail || "Invalid or expired invitation token.");
        }
        const data = await res.json();
        setInviteData(data);
      } catch (err: any) {
        setError(err.message || "An error occurred");
      } finally {
        setLoading(false);
      }
    }
    
    if (isSignedIn && token) {
      fetchInvitation();
    }
  }, [isSignedIn, token]);

  const handleJoinTeam = async () => {
    if (!userId) return;
    setActionLoading(true);
    try {
      const res = await fetch(`/api/collaboration/invitations/${token}/accept`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId })
      });
      if (!res.ok) {
        const detail = await res.json().catch(() => ({}));
        throw new Error(detail.detail || "Failed to join team");
      }
      const result = await res.json();
      // Redirect to `/team/<team_uuid>`
      window.location.href = `/team/${result.team_uuid}`;
    } catch (err: any) {
      alert(err.message || "Could not join team");
      setActionLoading(false);
    }
  };

  const handleDeclineInvitation = async () => {
    setActionLoading(true);
    try {
      const res = await fetch(`/api/collaboration/invitations/${token}/decline`, {
        method: 'POST'
      });
      if (!res.ok) throw new Error("Failed to decline invitation");
      // Redirect to dashboard
      window.location.href = "/";
    } catch (err: any) {
      alert(err.message || "Could not decline invitation");
      setActionLoading(false);
    }
  };

  if (!isLoaded || (isSignedIn && loading)) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-zinc-950 text-slate-400 font-mono">
        <Users className="w-10 h-10 mb-2 stroke-1 text-cyan-400 animate-spin" />
        <span className="text-xs">Validating secure invitation token...</span>
      </div>
    );
  }

  // Handle Invalid Tokens
  if (error || (inviteData && (inviteData.status === 'Expired' || inviteData.status === 'Accepted' || inviteData.status === 'Declined' || inviteData.status === 'Revoked'))) {
    const status = inviteData?.status || "Invalid";
    let reason = "Expired";
    if (status === 'Accepted') reason = "Already Used";
    if (status === 'Declined' || status === 'Revoked') reason = "Revoked";
    if (error && error.includes("Invalid")) reason = "Expired";

    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-zinc-950 text-slate-100 p-4 font-mono">
        <div className="glass-panel p-8 border border-red-500/20 bg-zinc-950/80 rounded-xl max-w-md w-full flex flex-col items-center shadow-2xl space-y-6">
          <AlertOctagon className="w-12 h-12 text-red-500 animate-pulse" />
          
          <div className="text-center space-y-2">
            <h2 className="text-sm font-extrabold uppercase tracking-wider text-red-400">
              Invitation Invalid
            </h2>
            <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">
              Reason: {reason}
            </p>
          </div>

          {status === 'Expired' && (
            <p className="text-xs text-slate-400 text-center leading-relaxed">
              Contact the Team Owner for a new invitation.
            </p>
          )}

          <button
            onClick={() => window.location.href = "/"}
            className="w-full bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 text-white font-bold text-xs py-2.5 rounded transition-all cursor-pointer"
          >
            Return to Dashboard
          </button>
        </div>
      </div>
    );
  }

  if (!inviteData) return null;

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-zinc-950 text-slate-100 p-4 font-mono">
      <div className="glass-panel p-8 border border-cyan-800/20 bg-zinc-950/80 rounded-xl max-w-md w-full flex flex-col shadow-2xl relative overflow-hidden space-y-6">
        {/* Sweeping top cyan highlight bar */}
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-cyan-500 to-blue-500" />
        
        <div className="text-center space-y-1">
          <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest block">
            You've been invited to join
          </span>
          <h1 className="text-lg font-extrabold uppercase tracking-wide text-cyan-400">
            {inviteData.team_name.toUpperCase()}
          </h1>
        </div>

        {/* Team Details Panel */}
        <div className="border border-slate-850 bg-zinc-900/40 p-4 rounded space-y-3.5 text-xs">
          <div>
            <span className="text-[9px] text-slate-500 uppercase block font-semibold">Description</span>
            <p className="text-slate-300 font-medium leading-relaxed">{inviteData.description}</p>
          </div>

          <div className="grid grid-cols-2 gap-4 border-t border-slate-850 pt-3">
            <div>
              <span className="text-[9px] text-slate-500 uppercase block font-semibold">Owner</span>
              <span className="text-slate-200 font-bold">{inviteData.owner}</span>
            </div>
            <div>
              <span className="text-[9px] text-slate-500 uppercase block font-semibold">Members</span>
              <span className="text-slate-200 font-bold">{inviteData.members.length} Collaborators</span>
            </div>
          </div>

          <div className="border-t border-slate-850 pt-3">
            <span className="text-[9px] text-slate-500 uppercase block font-semibold">Projects</span>
            <div className="flex flex-wrap gap-1.5 mt-1">
              {inviteData.projects.map((proj: string, idx: number) => (
                <span key={idx} className="bg-slate-900/60 border border-slate-800 px-2 py-0.5 rounded text-[10px] text-slate-400">
                  {proj}
                </span>
              ))}
            </div>
          </div>

          <div className="border-t border-slate-850 pt-3 flex items-center justify-between text-[10px] text-slate-500">
            <span>Created On:</span>
            <span className="font-bold text-slate-350">{new Date(inviteData.created_on).toLocaleDateString()}</span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="space-y-2 pt-2">
          <button
            onClick={handleJoinTeam}
            disabled={actionLoading}
            className="w-full bg-cyan-600 hover:bg-cyan-500 text-white font-extrabold text-xs py-3 rounded transition-all cursor-pointer flex items-center justify-center gap-1.5 shadow-lg shadow-cyan-950/20 active:scale-98"
          >
            <CheckCircle2 className="w-4 h-4" />
            Join Team
          </button>
          
          <button
            onClick={handleDeclineInvitation}
            disabled={actionLoading}
            className="w-full bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 text-slate-400 hover:text-slate-200 font-bold text-xs py-2.5 rounded transition-all cursor-pointer"
          >
            Decline Invitation
          </button>
        </div>

        {/* Expiration Clock Display */}
        <div className="border-t border-slate-850 pt-4 flex items-center justify-center gap-2 text-slate-500">
          <Clock className="w-4 h-4 text-cyan-500/70" />
          <span className="text-[10px] uppercase font-bold tracking-wider">
            Invitation expires in: <span className="text-cyan-400 font-extrabold">{inviteData.days_left} Days</span>
          </span>
        </div>
      </div>
    </div>
  );
}
