import React, { useState, useEffect } from "react";
import { Users, UserPlus, MessageSquare, Send, Activity, Shield, CheckCircle2, Link as LinkIcon } from "lucide-react";
import { TeamInvitationPanel } from "./TeamInvitationPanel";
import { InvitationList } from "./InvitationList";
import { InvitationModal } from "./InvitationModal";

interface Member {
  id: number;
  user_id: string;
  email?: string;
  name?: string;
  role: string;
  joined_at: string;
}

interface Comment {
  id: number;
  section: string;
  author: string;
  content: string;
  timestamp: string;
}

interface ActivityLog {
  id: number;
  user_id: string;
  action: string;
  details: string;
  timestamp: string;
}

interface TeamWorkspaceProps {
  teamData?: {
    team_id: number | string;
    team_name: string;
    members: Member[];
    comments: Comment[];
    activities: ActivityLog[];
  };
  projectId?: string;
  apiBase: string;
}

export default function TeamWorkspace({ teamData, projectId, apiBase }: TeamWorkspaceProps) {
  const [teamName, setTeamName] = useState<string>(teamData?.team_name || "PCB Research");
  const [teamId, setTeamId] = useState<string>(String(teamData?.team_id || "team_pcb_research"));
  const [members, setMembers] = useState<Member[]>(teamData?.members || []);
  const [comments, setComments] = useState<Comment[]>(teamData?.comments || []);
  const [activities, setActivities] = useState<ActivityLog[]>(teamData?.activities || []);
  
  const [isInviteModalOpen, setIsInviteModalOpen] = useState(false);
  const [showCreateTeam, setShowCreateTeam] = useState(!teamData?.team_name);
  const [newTeamNameInput, setNewTeamNameInput] = useState("");
  
  const [newComment, setNewComment] = useState("");
  const [commentSection, setCommentSection] = useState("General");

  const handleCreateTeam = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTeamNameInput.trim()) return;
    try {
      const res = await fetch(`${apiBase}/api/teams`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: newTeamNameInput.trim() }),
      });
      if (res.ok) {
        const created = await res.json();
        setTeamName(created.name);
        setTeamId(String(created.id || created.uuid || "team_1"));
        setShowCreateTeam(false);
        setIsInviteModalOpen(true);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleAddComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment) return;
    try {
      const res = await fetch(`${apiBase}/api/collaboration/comments`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project_id: projectId || "BionicHand_System",
          section: commentSection,
          author: "current_user",
          content: newComment,
        }),
      });
      if (res.ok) {
        const added = await res.json();
        setComments([...comments, added]);
        setNewComment("");
        fetchLogs();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const fetchLogs = async () => {
    try {
      const res = await fetch(`${apiBase}/api/collaboration/activity/${teamId}`);
      if (res.ok) {
        const logs = await res.json();
        setActivities(logs);
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <>
      <InvitationModal
        isOpen={isInviteModalOpen}
        onClose={() => setIsInviteModalOpen(false)}
        teamId={teamId}
        teamName={teamName}
        memberCount={members.length}
        apiBase={apiBase}
      />

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 p-4">
        {/* Left Column: Team Details & Invitations */}
        <div className="glass-panel p-5 border border-zinc-800 bg-zinc-950/60 rounded-xl space-y-6">
          <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
            <div className="flex items-center gap-2">
              <Users className="w-5 h-5 text-cyan-400" />
              <h3 className="text-lg font-mono font-bold tracking-wider text-slate-100 uppercase">
                {teamName}
              </h3>
            </div>
            <span className="text-xs font-mono text-cyan-400 bg-cyan-950/40 border border-cyan-800/40 px-2 py-0.5 rounded">
              ID: {teamId}
            </span>
          </div>

          {showCreateTeam ? (
            <form onSubmit={handleCreateTeam} className="bg-zinc-900/60 p-4 border border-zinc-800 rounded-lg space-y-3">
              <div className="text-xs font-mono font-bold text-slate-400 uppercase tracking-widest">
                Create New Team
              </div>
              <input
                type="text"
                required
                placeholder="Team Name (e.g. PCB Research)"
                value={newTeamNameInput}
                onChange={(e) => setNewTeamNameInput(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-800 rounded px-3 py-2 text-xs font-mono text-slate-100 focus:outline-none focus:border-cyan-500"
              />
              <button
                type="submit"
                className="w-full bg-cyan-600 hover:bg-cyan-500 text-white font-mono text-xs font-bold px-4 py-2 rounded transition-all cursor-pointer"
              >
                Create Team
              </button>
            </form>
          ) : (
            <div className="space-y-4">
              <button
                onClick={() => setIsInviteModalOpen(true)}
                className="w-full py-2.5 px-4 bg-cyan-600 hover:bg-cyan-500 text-white font-mono text-xs font-bold rounded-lg transition flex items-center justify-center gap-2 shadow"
              >
                <LinkIcon className="w-4 h-4" />
                Generate Secure Invitation Link
              </button>

              <TeamInvitationPanel
                teamId={teamId}
                teamName={teamName}
                memberCount={members.length}
                apiBase={apiBase}
              />

              <InvitationList teamId={teamId} apiBase={apiBase} />
            </div>
          )}

          {/* Members List */}
          <div className="space-y-3 pt-4 border-t border-zinc-800">
            <div className="text-xs font-mono font-bold text-slate-400 uppercase tracking-widest">
              Active Members ({members.length})
            </div>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {members.map((m, idx) => (
                <div key={idx} className="flex items-center justify-between p-2.5 bg-zinc-900/40 rounded border border-zinc-850 text-xs font-mono">
                  <div>
                    <div className="text-slate-200 font-bold">{m.name || m.user_id}</div>
                    <div className="text-[10px] text-slate-500">{m.email || 'Workline Member'}</div>
                  </div>
                  <span className="px-2 py-0.5 bg-zinc-800 text-cyan-400 rounded text-[10px] font-bold">
                    {m.role}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Center Column: Project Comments */}
        <div className="glass-panel p-5 border border-zinc-800 bg-zinc-950/60 rounded-xl space-y-4">
          <div className="flex items-center gap-2 border-b border-zinc-800 pb-3">
            <MessageSquare className="w-5 h-5 text-cyan-400" />
            <h3 className="text-lg font-mono font-bold tracking-wider text-slate-100 uppercase">Project Comments</h3>
          </div>

          <form onSubmit={handleAddComment} className="space-y-2">
            <div className="flex gap-2">
              <select
                value={commentSection}
                onChange={(e) => setCommentSection(e.target.value)}
                className="bg-zinc-950 border border-zinc-800 rounded px-2.5 py-1.5 text-xs font-mono text-slate-300 focus:outline-none focus:border-cyan-500"
              >
                <option value="General">General</option>
                <option value="PCB">PCB Layout</option>
                <option value="Schematic">Schematics</option>
                <option value="BOM">BOM / Procurement</option>
              </select>
              <input
                type="text"
                placeholder="Write a project note or comment..."
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                className="flex-1 bg-zinc-950 border border-zinc-800 rounded px-3 py-1.5 text-xs font-mono text-slate-100 focus:outline-none focus:border-cyan-500"
              />
              <button
                type="submit"
                className="bg-cyan-600 hover:bg-cyan-500 text-white px-3 py-1.5 rounded text-xs font-mono font-bold flex items-center gap-1"
              >
                <Send className="w-3.5 h-3.5" />
              </button>
            </div>
          </form>

          <div className="space-y-2.5 max-h-96 overflow-y-auto">
            {comments.map((c, idx) => (
              <div key={idx} className="p-3 bg-zinc-900/40 border border-zinc-850 rounded text-xs font-mono space-y-1">
                <div className="flex items-center justify-between text-slate-400 text-[10px]">
                  <span>{c.author} • [{c.section}]</span>
                  <span>{c.timestamp?.substring(11, 19)}</span>
                </div>
                <div className="text-slate-200">{c.content}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Column: Audit Trail & Activity */}
        <div className="glass-panel p-5 border border-zinc-800 bg-zinc-950/60 rounded-xl space-y-4">
          <div className="flex items-center gap-2 border-b border-zinc-800 pb-3">
            <Activity className="w-5 h-5 text-cyan-400" />
            <h3 className="text-lg font-mono font-bold tracking-wider text-slate-100 uppercase">Audit Trail</h3>
          </div>

          <div className="space-y-2 max-h-[480px] overflow-y-auto font-mono text-xs">
            {activities.map((a, idx) => (
              <div key={idx} className="p-2.5 bg-zinc-900/30 border border-zinc-850/60 rounded space-y-1">
                <div className="flex justify-between text-[10px]">
                  <span className="text-cyan-400 font-bold">{a.action}</span>
                  <span className="text-slate-500">{a.timestamp?.substring(11, 19)}</span>
                </div>
                <div className="text-slate-300 text-[11px]">{a.details}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}
