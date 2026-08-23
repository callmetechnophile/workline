import React, { useState, useEffect } from "react";
import {
  Users,
  UserPlus,
  MessageSquare,
  Send,
  Activity,
  Shield,
  CheckCircle2,
  Link as LinkIcon,
  KeyRound,
  Copy,
  RefreshCw,
  AlertTriangle,
  Lock,
  UserX,
  ShieldAlert,
} from "lucide-react";
import { TeamInvitationPanel } from "./TeamInvitationPanel";
import { InvitationList } from "./InvitationList";
import { InvitationModal } from "./InvitationModal";

export interface Member {
  id: number | string;
  user_id: string;
  email?: string;
  name?: string;
  role: "OWNER" | "ADMIN" | "MEMBER" | string;
  joined_at: string;
}

export interface Comment {
  id: number;
  section: string;
  author: string;
  content: string;
  timestamp: string;
}

export interface ActivityLog {
  id: number | string;
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
  currentUserRole?: "OWNER" | "ADMIN" | "MEMBER" | string;
}

export default function TeamWorkspace({
  teamData,
  projectId,
  apiBase,
  currentUserRole = "OWNER",
}: TeamWorkspaceProps) {
  const [teamName, setTeamName] = useState<string>(teamData?.team_name || "PCB Research");
  const [teamId, setTeamId] = useState<string>(String(teamData?.team_id || "team_pcb_research"));
  const [members, setMembers] = useState<Member[]>(
    teamData?.members || [
      { id: 1, user_id: "user_lead_01", name: "Engineering Lead", role: "OWNER", joined_at: "2026-08-01" },
      { id: 2, user_id: "user_pcb_02", name: "Hardware Engineer", role: "ADMIN", joined_at: "2026-08-10" },
      { id: 3, user_id: "user_sim_03", name: "Simulation Specialist", role: "MEMBER", joined_at: "2026-08-15" },
    ]
  );
  const [comments, setComments] = useState<Comment[]>(teamData?.comments || []);
  const [activities, setActivities] = useState<ActivityLog[]>(teamData?.activities || []);

  // Modal / Form States
  const [isInviteModalOpen, setIsInviteModalOpen] = useState(false);
  const [showCreateTeam, setShowCreateTeam] = useState(!teamData?.team_name);
  const [newTeamNameInput, setNewTeamNameInput] = useState("");
  const [newTeamDescInput, setNewTeamDescInput] = useState("");

  // Join Code States
  const [joinCodeInput, setJoinCodeInput] = useState("");
  const [joinStatus, setJoinStatus] = useState<string | null>(null);
  const [joinLoading, setJoinLoading] = useState(false);
  const [createdJoinCode, setCreatedJoinCode] = useState<string | null>(null);
  const [codeStatus, setCodeStatus] = useState<"ACTIVE" | "EXPIRED" | "REVOKED">("ACTIVE");
  const [copiedCode, setCopiedCode] = useState(false);

  const [newComment, setNewComment] = useState("");
  const [commentSection, setCommentSection] = useState("General");

  const isAuthorizedManager = currentUserRole === "OWNER" || currentUserRole === "ADMIN";

  const handleCreateTeam = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTeamNameInput.trim()) return;
    try {
      const res = await fetch(`${apiBase}/api/teams`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: newTeamNameInput.trim(),
          description: newTeamDescInput.trim(),
        }),
      });
      if (res.ok) {
        const created = await res.json();
        setTeamName(created.name);
        setTeamId(String(created.team_id || created.id || created.uuid));
        setCreatedJoinCode(created.join_code);
        setCodeStatus("ACTIVE");
        setShowCreateTeam(false);
        fetchLogs();
      }
    } catch (err) {
      console.error("Create team error:", err);
    }
  };

  const handleJoinTeam = async (e: React.FormEvent) => {
    e.preventDefault();
    const clean = joinCodeInput.trim().toUpperCase().replace(/[^A-Z0-9]/g, "");
    if (clean.length !== 6) {
      setJoinStatus("Enter a valid 6-character alphanumeric code.");
      return;
    }
    setJoinLoading(true);
    setJoinStatus(null);
    try {
      const res = await fetch(`${apiBase}/api/teams/join`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code: clean }),
      });
      const data = await res.json();
      if (res.ok) {
        setJoinStatus(`Joined ${data.team_name || "team"} successfully.`);
        setTeamName(data.team_name);
        setTeamId(data.team_id);
        setJoinCodeInput("");
        fetchLogs();
      } else {
        setJoinStatus("Invalid or expired team code.");
      }
    } catch (err) {
      setJoinStatus("Invalid or expired team code.");
    } finally {
      setJoinLoading(false);
    }
  };

  const handleRotateCode = async () => {
    try {
      const res = await fetch(`${apiBase}/api/teams/${teamId}/join-code/rotate`, {
        method: "POST",
      });
      if (res.ok) {
        const data = await res.json();
        setCreatedJoinCode(data.join_code);
        setCodeStatus("ACTIVE");
        fetchLogs();
      }
    } catch (err) {
      console.error("Rotate join code failed", err);
    }
  };

  const handleRevokeCode = async () => {
    try {
      const res = await fetch(`${apiBase}/api/teams/${teamId}/join-code/revoke`, {
        method: "POST",
      });
      if (res.ok) {
        setCreatedJoinCode(null);
        setCodeStatus("REVOKED");
        fetchLogs();
      }
    } catch (err) {
      console.error("Revoke join code failed", err);
    }
  };

  const handleUpdateRole = async (memberId: string | number, newRole: string) => {
    try {
      setMembers((prev) =>
        prev.map((m) => (m.id === memberId ? { ...m, role: newRole } : m))
      );
      await fetch(`${apiBase}/api/teams/${teamId}/members/${memberId}/role`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ role: newRole }),
      });
      fetchLogs();
    } catch (err) {
      console.error("Update role failed", err);
    }
  };

  const handleRemoveMember = async (memberId: string | number) => {
    try {
      setMembers((prev) => prev.filter((m) => m.id !== memberId));
      await fetch(`${apiBase}/api/teams/${teamId}/members/${memberId}`, {
        method: "DELETE",
      });
      fetchLogs();
    } catch (err) {
      console.error("Remove member failed", err);
    }
  };

  const handleAddComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim()) return;
    try {
      const res = await fetch(`${apiBase}/api/collaboration/comments`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project_id: projectId || "BionicHand_System",
          section: commentSection,
          author: "current_user",
          content: newComment.trim(),
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
      const res = await fetch(`${apiBase}/api/teams/${teamId}/activity`);
      if (res.ok) {
        const logs = await res.json();
        setActivities(
          logs.map((l: any) => ({
            id: l.event_id,
            user_id: l.actor_user_id,
            action: l.event_type,
            details: JSON.stringify(l.metadata || {}),
            timestamp: l.timestamp,
          }))
        );
      }
    } catch (err) {
      // Offline fallback
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedCode(true);
    setTimeout(() => setCopiedCode(false), 3000);
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
        {/* Left Column: Team Details, Join Codes & Actions */}
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

          {/* Join Code Banner if newly created or rotated */}
          {createdJoinCode && (
            <div className="p-4 bg-emerald-950/40 border border-emerald-800/60 rounded-lg space-y-2 font-mono">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-emerald-400 flex items-center gap-1.5">
                  <KeyRound className="w-4 h-4" /> Secure 6-Character Join Code
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded font-bold bg-emerald-900/60 text-emerald-300">
                  {codeStatus}
                </span>
              </div>
              <div className="flex items-center justify-between bg-zinc-950 p-2.5 rounded border border-emerald-900/60">
                <span className="text-xl font-bold tracking-widest text-emerald-300 font-mono">
                  {createdJoinCode}
                </span>
                <button
                  onClick={() => copyToClipboard(createdJoinCode)}
                  className="px-3 py-1 bg-emerald-700 hover:bg-emerald-600 text-white rounded text-xs font-bold flex items-center gap-1 transition cursor-pointer"
                >
                  <Copy className="w-3.5 h-3.5" />
                  {copiedCode ? "Copied!" : "Copy Code"}
                </button>
              </div>
              <p className="text-[11px] text-zinc-400 leading-tight">
                Share this code only with trusted collaborators.
              </p>
            </div>
          )}

          {showCreateTeam ? (
            <form onSubmit={handleCreateTeam} className="bg-zinc-900/60 p-4 border border-zinc-800 rounded-lg space-y-3">
              <div className="text-xs font-mono font-bold text-slate-400 uppercase tracking-widest">
                Create Team
              </div>
              <input
                type="text"
                required
                placeholder="Team Name"
                value={newTeamNameInput}
                onChange={(e) => setNewTeamNameInput(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-800 rounded px-3 py-2 text-xs font-mono text-slate-100 focus:outline-none focus:border-cyan-500"
              />
              <input
                type="text"
                placeholder="Description"
                value={newTeamDescInput}
                onChange={(e) => setNewTeamDescInput(e.target.value)}
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
              {/* Join Code Entry Form */}
              <form onSubmit={handleJoinTeam} className="bg-zinc-900/40 p-3.5 border border-zinc-800 rounded-lg space-y-2.5">
                <span className="text-xs font-mono font-bold text-zinc-300 flex items-center gap-1.5">
                  <KeyRound className="w-3.5 h-3.5 text-cyan-400" /> Join a Team
                </span>
                <p className="text-[11px] text-slate-400 font-mono">Enter your 6-character team code</p>
                <div className="flex gap-2">
                  <input
                    type="text"
                    maxLength={6}
                    placeholder="------"
                    value={joinCodeInput}
                    onChange={(e) =>
                      setJoinCodeInput(e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, ""))
                    }
                    className="w-32 bg-zinc-950 border border-zinc-800 rounded px-3 py-1.5 text-xs font-mono font-bold tracking-widest text-center text-cyan-300 uppercase focus:outline-none focus:border-cyan-500"
                  />
                  <button
                    type="submit"
                    disabled={joinLoading || joinCodeInput.length !== 6}
                    className="flex-1 bg-cyan-600 hover:bg-cyan-500 disabled:bg-zinc-800 disabled:text-zinc-500 text-white font-mono text-xs font-bold py-1.5 px-3 rounded transition cursor-pointer"
                  >
                    {joinLoading ? "Joining team..." : "Join Team"}
                  </button>
                </div>
                {joinStatus && (
                  <p className="text-[11px] font-mono text-cyan-400">{joinStatus}</p>
                )}
              </form>

              {/* Owner/Admin Join Code Controls */}
              {isAuthorizedManager && (
                <div className="space-y-2 pt-1 border-t border-zinc-850">
                  <div className="text-[11px] font-mono font-bold text-zinc-400 uppercase">
                    Team Join Code Management
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={handleRotateCode}
                      className="flex-1 py-1.5 px-3 bg-zinc-800 hover:bg-zinc-700 text-zinc-200 font-mono text-xs font-semibold rounded transition flex items-center justify-center gap-1.5 cursor-pointer"
                    >
                      <RefreshCw className="w-3.5 h-3.5" /> Rotate Code
                    </button>
                    <button
                      onClick={handleRevokeCode}
                      className="py-1.5 px-3 bg-rose-950/40 hover:bg-rose-900/60 text-rose-300 border border-rose-800/40 font-mono text-xs font-semibold rounded transition cursor-pointer"
                    >
                      Revoke
                    </button>
                  </div>
                </div>
              )}

              <button
                onClick={() => setIsInviteModalOpen(true)}
                className="w-full py-2.5 px-4 bg-zinc-800 hover:bg-zinc-700 text-zinc-200 font-mono text-xs font-bold rounded-lg transition flex items-center justify-center gap-2 border border-zinc-700 cursor-pointer"
              >
                <LinkIcon className="w-4 h-4 text-cyan-400" />
                Generate Encrypted Link (AES-GCM)
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
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-bold text-slate-400 uppercase tracking-widest">
                Team Members ({members.length})
              </span>
              {isAuthorizedManager && (
                <span className="text-[10px] font-mono text-indigo-400">Admin Controls Active</span>
              )}
            </div>
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {members.map((m, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-2.5 bg-zinc-900/40 rounded border border-zinc-850 text-xs font-mono gap-2"
                >
                  <div className="truncate">
                    <div className="text-slate-200 font-bold truncate">{m.name || m.user_id}</div>
                    <div className="text-[10px] text-slate-500">Joined: {m.joined_at?.slice(0, 10) || "2026-08"}</div>
                  </div>

                  <div className="flex items-center gap-2 flex-shrink-0">
                    {isAuthorizedManager && m.role !== "OWNER" ? (
                      <select
                        value={m.role}
                        onChange={(e) => handleUpdateRole(m.id, e.target.value)}
                        className="bg-zinc-950 border border-zinc-800 rounded px-2 py-0.5 text-[10px] font-bold font-mono text-cyan-300 focus:outline-none"
                      >
                        <option value="ADMIN">ADMIN</option>
                        <option value="MEMBER">MEMBER</option>
                      </select>
                    ) : (
                      <span className="px-2 py-0.5 bg-zinc-800 text-cyan-400 rounded text-[10px] font-bold">
                        {m.role}
                      </span>
                    )}

                    {isAuthorizedManager && m.role !== "OWNER" && (
                      <button
                        onClick={() => handleRemoveMember(m.id)}
                        className="p-1 text-zinc-500 hover:text-rose-400 transition cursor-pointer"
                        title="Remove Member"
                      >
                        <UserX className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Center Column: Project Comments */}
        <div className="glass-panel p-5 border border-zinc-800 bg-zinc-950/60 rounded-xl space-y-4">
          <div className="flex items-center gap-2 border-b border-zinc-800 pb-3">
            <MessageSquare className="w-5 h-5 text-cyan-400" />
            <h3 className="text-lg font-mono font-bold tracking-wider text-slate-100 uppercase">
              Project Comments
            </h3>
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
                placeholder="Write a project note..."
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                className="flex-1 bg-zinc-950 border border-zinc-800 rounded px-3 py-1.5 text-xs font-mono text-slate-100 focus:outline-none focus:border-cyan-500"
              />
              <button
                type="submit"
                className="bg-cyan-600 hover:bg-cyan-500 text-white px-3 py-1.5 rounded text-xs font-mono font-bold flex items-center gap-1 cursor-pointer"
              >
                <Send className="w-3.5 h-3.5" />
              </button>
            </div>
          </form>

          <div className="space-y-2.5 max-h-96 overflow-y-auto">
            {comments.map((c, idx) => (
              <div
                key={idx}
                className="p-3 bg-zinc-900/40 border border-zinc-850 rounded text-xs font-mono space-y-1"
              >
                <div className="flex items-center justify-between text-slate-400 text-[10px]">
                  <span>
                    {c.author} • [{c.section}]
                  </span>
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
            <h3 className="text-lg font-mono font-bold tracking-wider text-slate-100 uppercase">
              Team Activity & Audit Visibility
            </h3>
          </div>

          <div className="space-y-2 max-h-[480px] overflow-y-auto font-mono text-xs">
            {activities.length === 0 ? (
              <div className="p-4 bg-zinc-900/20 border border-zinc-850 rounded text-center text-slate-500">
                No recent activity events recorded.
              </div>
            ) : (
              activities.map((a, idx) => (
                <div
                  key={idx}
                  className="p-2.5 bg-zinc-900/40 border border-zinc-850 rounded space-y-1"
                >
                  <div className="flex items-center justify-between text-[10px] text-cyan-400 font-bold">
                    <span>{a.action}</span>
                    <span className="text-slate-500">{a.timestamp?.slice(0, 19)}</span>
                  </div>
                  <div className="text-[11px] text-slate-300">Actor: {a.user_id}</div>
                  {a.details && a.details !== "{}" && (
                    <div className="text-[10px] text-slate-500 break-all">{a.details}</div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </>
  );
}
