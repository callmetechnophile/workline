'use client';

import React, { use, useState, useEffect } from 'react';
import { Users, Shield, MessageSquare, ListTodo, Plus, Info, Home, UserPlus, CheckCircle2 } from 'lucide-react';
import { useAuth } from '@clerk/nextjs';

export const dynamic = 'force-dynamic';

interface TeamPageProps {
  params: Promise<{ uuid: string }>;
}

export default function TeamWorkspacePage({ params }: TeamPageProps) {
  const { uuid } = use(params);
  const { isLoaded, isSignedIn, userId } = useAuth();
  
  const [team, setTeam] = useState<any>(null);
  const [members, setMembers] = useState<any[]>([]);
  const [activities, setActivities] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Modal state for invites
  const [inviteModalOpen, setInviteModalOpen] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState('Engineer');
  const [inviteTeamName, setInviteTeamName] = useState('');
  const [inviteResult, setInviteResult] = useState<any>(null);
  const [showToast, setShowToast] = useState(false);

  useEffect(() => {
    async function loadTeamData() {
      if (!uuid) return;
      setLoading(true);
      try {
        const resTeam = await fetch(`/api/collaboration/teams/uuid/${uuid}`);
        if (!resTeam.ok) throw new Error("Team workspace not found.");
        const teamData = await resTeam.json();
        setTeam(teamData);
        setInviteTeamName(teamData.name || '');

        // Fetch members
        const resMembers = await fetch(`/api/collaboration/members/${teamData.id}`);
        if (resMembers.ok) setMembers(await resMembers.json());

        // Fetch activities
        const resActs = await fetch(`/api/collaboration/activity/${teamData.id}`);
        if (resActs.ok) setActivities(await resActs.json());
      } catch (err: any) {
        setError(err.message || "Could not load workspace");
      } finally {
        setLoading(false);
      }
    }

    if (uuid) {
      loadTeamData();
    }
  }, [uuid]);

  const handleSendInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inviteEmail || !inviteTeamName) return;
    try {
      const res = await fetch(`/api/collaboration/teams/invite-collaborator`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ team_name: inviteTeamName, email: inviteEmail, role: inviteRole })
      });
      if (!res.ok) throw new Error("Failed to generate invitation link.");
      const result = await res.json();
      setInviteResult(result);
      setShowToast(true);
      setTimeout(() => setShowToast(false), 6000);
      // Refresh activity log
      if (team) {
        const resActs = await fetch(`/api/collaboration/activity/${team.id}`);
        if (resActs.ok) setActivities(await resActs.json());
      }
    } catch (err: any) {
      alert(err.message || "Failed to create invitation");
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-zinc-950 text-slate-400 font-mono">
        <Users className="w-10 h-10 mb-2 stroke-1 text-cyan-400 animate-spin" />
        <span className="text-xs">Loading Team Workspace...</span>
      </div>
    );
  }

  if (error || !team) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-zinc-950 text-slate-400 font-mono p-4">
        <Shield className="w-10 h-10 mb-2 text-red-500" />
        <span className="text-xs text-red-400 mb-4">{error || "Workspace not found."}</span>
        <button
          onClick={() => window.location.href = "/"}
          className="bg-slate-900 border border-slate-800 text-white text-xs px-4 py-2 rounded font-bold cursor-pointer"
        >
          Return to Dashboard
        </button>
      </div>
    );
  }

  return (
    <>
      {showToast && (
        <div className="fixed top-6 right-6 z-50 flex items-center gap-3 bg-zinc-950/95 border border-cyan-500/40 p-4 rounded-xl shadow-2xl animate-fade-in font-mono max-w-sm">
          <div className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-ping absolute -top-1 -right-1" />
          <CheckCircle2 className="w-5 h-5 text-cyan-400 shrink-0" />
          <div>
            <span className="text-[10px] text-cyan-400 font-extrabold uppercase tracking-widest block">Notification</span>
            <p className="text-[11px] font-bold text-slate-100 uppercase tracking-wide mt-0.5 leading-normal">
              EMAIL SENT CHECK YOU JUNK/SPAM FOLDER
            </p>
          </div>
        </div>
      )}
      <div className="min-h-screen bg-zinc-950 text-slate-100 font-mono p-6 flex flex-col justify-between">
      <div className="max-w-6xl w-full mx-auto space-y-6">
        {/* Header navigation */}
        <div className="flex items-center justify-between border-b border-slate-900 pb-4">
          <div className="flex items-center gap-3">
            <Users className="w-6 h-6 text-cyan-400" />
            <div>
              <h1 className="text-md font-bold uppercase tracking-wider text-slate-200">
                {team.name}
              </h1>
              <span className="text-[9px] text-slate-500 uppercase font-bold tracking-widest block mt-0.5">
                Workspace UUID: {team.uuid}
              </span>
            </div>
          </div>
          
          <div className="flex gap-2">
            <button
              onClick={() => setInviteModalOpen(true)}
              className="bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold px-4 py-1.5 rounded transition-all flex items-center gap-1.5 cursor-pointer"
            >
              <UserPlus className="w-4 h-4" />
              Invite Member
            </button>
            <button
              onClick={() => window.location.href = "/"}
              className="bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-400 hover:text-white text-xs font-bold px-4 py-1.5 rounded transition-all flex items-center gap-1.5 cursor-pointer"
            >
              <Home className="w-4 h-4" />
              Dashboard
            </button>
          </div>
        </div>

        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Members List Panel */}
          <div className="glass-panel p-5 border border-slate-850 bg-zinc-900/10 space-y-4">
            <h3 className="text-xs font-bold text-cyan-400 uppercase tracking-wider flex items-center gap-1.5 border-b border-slate-850 pb-2">
              <Users className="w-4 h-4" />
              Team Collaborators
            </h3>
            
            <div className="space-y-3.5">
              {members.map((member: any) => (
                <div key={member.id} className="flex items-center justify-between text-xs border-b border-slate-900/60 pb-2">
                  <div>
                    <span className="text-slate-300 font-bold block">{member.email}</span>
                    <span className="text-[9px] text-slate-500 block">Joined: {new Date(member.joined_at).toLocaleDateString()}</span>
                  </div>
                  <span className="bg-slate-900 px-2 py-0.5 border border-slate-800 rounded text-[9px] text-cyan-400 font-bold uppercase tracking-wider">
                    {member.role}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Activity Log Panel */}
          <div className="lg:col-span-2 glass-panel p-5 border border-slate-850 bg-zinc-900/10 space-y-4">
            <h3 className="text-xs font-bold text-cyan-400 uppercase tracking-wider flex items-center gap-1.5 border-b border-slate-850 pb-2">
              <ListTodo className="w-4 h-4" />
              Immutable Activity Logs
            </h3>
            
            <div className="space-y-3.5 max-h-[380px] overflow-y-auto pr-2 scrollbar-none">
              {activities.length > 0 ? (
                activities.map((act: any) => (
                  <div key={act.id} className="text-xs space-y-1 border-b border-slate-900 pb-2.5">
                    <div className="flex items-center justify-between text-[9px]">
                      <span className="text-cyan-400 font-bold uppercase tracking-widest">{act.action}</span>
                      <span className="text-slate-500">{new Date(act.timestamp).toLocaleString()}</span>
                    </div>
                    <p className="text-slate-300 font-medium">{act.details}</p>
                    <span className="text-[8px] text-slate-500 font-semibold uppercase">Actor: {act.user_id}</span>
                  </div>
                ))
              ) : (
                <div className="text-xs text-slate-500 italic p-4 text-center">
                  No activity logs created yet.
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Invite Modal */}
      {inviteModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
          <div className="glass-panel p-6 border border-cyan-800/20 bg-zinc-950/95 max-w-lg w-full rounded-xl relative space-y-5">
            <h3 className="text-xs font-bold text-cyan-400 uppercase tracking-widest border-b border-slate-850 pb-2">
              Generate Hyperlink Invitation
            </h3>
            
            {!inviteResult ? (
              <form onSubmit={handleSendInvite} className="space-y-4 text-xs font-mono">
                <div className="space-y-1.5">
                  <label className="text-[10px] text-slate-400 uppercase">New Team Name</label>
                  <input
                    type="text"
                    required
                    value={inviteTeamName}
                    onChange={(e) => setInviteTeamName(e.target.value)}
                    placeholder="Engineering Alpha"
                    className="w-full bg-slate-900 border border-slate-800 rounded px-3 py-2 text-white outline-none focus:border-cyan-500"
                  />
                </div>
                
                <div className="space-y-1.5">
                  <label className="text-[10px] text-slate-400 uppercase">Invitee Email Address</label>
                  <input
                    type="email"
                    required
                    value={inviteEmail}
                    onChange={(e) => setInviteEmail(e.target.value)}
                    placeholder="engineer@workline.ai"
                    className="w-full bg-slate-900 border border-slate-800 rounded px-3 py-2 text-white outline-none focus:border-cyan-500"
                  />
                </div>
                
                <div className="space-y-1.5">
                  <label className="text-[10px] text-slate-400 uppercase">Collaborator Role</label>
                  <select
                    value={inviteRole}
                    onChange={(e) => setInviteRole(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 rounded px-3 py-2 text-white outline-none focus:border-cyan-500"
                  >
                    <option value="Engineer">Engineer</option>
                    <option value="Reviewer">Reviewer</option>
                    <option value="Viewer">Viewer</option>
                  </select>
                </div>
                
                <div className="flex gap-2 justify-end pt-2">
                  <button
                    type="button"
                    onClick={() => setInviteModalOpen(false)}
                    className="bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-400 px-4 py-1.5 rounded cursor-pointer font-bold"
                  >
                    Close
                  </button>
                  <button
                    type="submit"
                    className="bg-cyan-600 hover:bg-cyan-500 text-white px-4 py-1.5 rounded cursor-pointer font-bold"
                  >
                    Generate Link
                  </button>
                </div>
              </form>
            ) : (
              <div className="space-y-4 text-xs font-mono">
                <div className="space-y-1">
                  <span className="text-[10px] text-slate-500 uppercase">Generated Numeric Team ID</span>
                  <div className="bg-slate-900 border border-slate-800 p-2 rounded text-slate-200 font-bold select-all text-xs">
                    {inviteResult.team_id_numeric}
                  </div>
                </div>

                <div className="space-y-1">
                  <span className="text-[10px] text-slate-500 uppercase">Secure Joining Link</span>
                  <div className="bg-slate-900 border border-slate-800 p-2 rounded text-cyan-400 font-bold select-all text-[11px] truncate">
                    {inviteResult.invite_url}
                  </div>
                </div>

                <div className="space-y-1">
                  <span className="text-[10px] text-slate-500 uppercase">Email Subject</span>
                  <div className="bg-slate-900 border border-slate-800 p-2 rounded text-slate-200 font-bold select-all">
                    {inviteResult.email_subject}
                  </div>
                </div>

                <div className="space-y-1">
                  <span className="text-[10px] text-slate-500 uppercase">Email Body Template</span>
                  <pre className="bg-slate-900 border border-slate-800 p-3 rounded text-slate-300 font-mono whitespace-pre-wrap overflow-y-auto max-h-[160px] select-all">
                    {inviteResult.email_body}
                  </pre>
                </div>

                <div className="flex justify-end gap-2 pt-2">
                  <button
                    onClick={() => {
                      setInviteResult(null);
                      setInviteEmail('');
                      setInviteModalOpen(false);
                    }}
                    className="bg-cyan-600 hover:bg-cyan-500 text-white font-bold px-5 py-1.5 rounded cursor-pointer"
                  >
                    Done
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
    </>
  );
}
