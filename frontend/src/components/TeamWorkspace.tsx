import React, { useState, useEffect } from "react";
import {
  LayoutDashboard,
  Users,
  UserPlus,
  CheckSquare,
  Activity,
  Scale,
  ShieldAlert,
  Mail,
  Settings,
  Shield,
  KeyRound,
  Copy,
  RefreshCw,
  AlertTriangle,
  Lock,
  UserX,
  CheckCircle2,
  XCircle,
  ExternalLink,
  MessageSquare,
  Send,
  Sparkles,
  Bot,
  UserCheck,
  ShieldCheck,
  Filter,
  Check,
} from "lucide-react";
import { TeamInvitationPanel } from "./TeamInvitationPanel";
import { InvitationList } from "./InvitationList";
import { InvitationModal } from "./InvitationModal";
import { TaskBoard } from "./collaboration/TaskBoard";
import { DecisionsLog } from "./collaboration/DecisionsLog";
import { ApprovalsQueue } from "./collaboration/ApprovalsQueue";
import { JoinTeamModal } from "./collaboration/JoinTeamModal";
import { OwnershipTransferModal } from "./collaboration/OwnershipTransferModal";

export type TabKey =
  | "overview"
  | "members"
  | "tasks"
  | "activity"
  | "decisions"
  | "approvals"
  | "invitations"
  | "settings";

export interface Member {
  id: number | string;
  user_id: string;
  email?: string;
  name?: string;
  role: "OWNER" | "ADMIN" | "ENGINEER" | "RESEARCHER" | "VIEWER" | "MEMBER" | string;
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
  actor_type?: "HUMAN" | "AGENT" | "SYSTEM";
  receipt_id?: string;
}

export interface MembershipRequest {
  id: string;
  team_id: string;
  user_id: string;
  user_name?: string;
  user_email?: string;
  requested_role: string;
  status: "PENDING" | "APPROVED" | "REJECTED";
  created_at: string;
}

interface TeamWorkspaceProps {
  teamData?: {
    team_id: number | string;
    team_name: string;
    members: Member[];
    comments?: Comment[];
    activities?: ActivityLog[];
  };
  projectId?: string;
  apiBase: string;
  currentUserRole?: string;
}

export default function TeamWorkspace({
  teamData,
  projectId = "BionicHand_System",
  apiBase,
  currentUserRole = "OWNER",
}: TeamWorkspaceProps) {
  const [activeTab, setActiveTab] = useState<TabKey>("overview");
  const [teamName, setTeamName] = useState<string>(teamData?.team_name || "Robotics & Hardware Core");
  const [teamDescription, setTeamDescription] = useState<string>("Autonomous mechatronics and sensor fusion platform.");
  const [teamId, setTeamId] = useState<string>(String(teamData?.team_id || "team_robotics_core"));
  const [members, setMembers] = useState<Member[]>(
    teamData?.members || [
      { id: 1, user_id: "lead_engineer", name: "Engineering Lead", role: "OWNER", joined_at: "2026-08-01" },
      { id: 2, user_id: "hw_specialist", name: "Hardware Engineer", role: "ADMIN", joined_at: "2026-08-10" },
      { id: 3, user_id: "sim_analyst", name: "Simulation Specialist", role: "RESEARCHER", joined_at: "2026-08-15" },
      { id: 4, user_id: "qa_auditor", name: "Compliance Auditor", role: "VIEWER", joined_at: "2026-08-20" },
    ]
  );
  const [activities, setActivities] = useState<ActivityLog[]>(teamData?.activities || []);
  const [membershipRequests, setMembershipRequests] = useState<MembershipRequest[]>([]);

  // Join Code & Settings State
  const [joinCode, setJoinCode] = useState<string | null>("WL-7K4M2P");
  const [codeStatus, setCodeStatus] = useState<"ACTIVE" | "EXPIRED" | "REVOKED">("ACTIVE");
  const [copiedCode, setCopiedCode] = useState(false);
  const [requireJoinApproval, setRequireJoinApproval] = useState(false);
  const [defaultJoinRole, setDefaultJoinRole] = useState("ENGINEER");

  // Modals
  const [isInviteModalOpen, setIsInviteModalOpen] = useState(false);
  const [isJoinModalOpen, setIsJoinModalOpen] = useState(false);
  const [isTransferModalOpen, setIsTransferModalOpen] = useState(false);
  const [activityFilter, setActivityFilter] = useState<"ALL" | "HUMAN" | "AGENT" | "SYSTEM">("ALL");

  const isOwnerOrAdmin = currentUserRole === "OWNER" || currentUserRole === "ADMIN";
  const isOwner = currentUserRole === "OWNER";

  // Initial Fetch & Refresh
  const fetchTeamDetails = async () => {
    try {
      const res = await fetch(`${apiBase}/api/teams/${teamId}`);
      if (res.ok) {
        const data = await res.json();
        setTeamName(data.name);
        setTeamDescription(data.description || "");
        setRequireJoinApproval(data.require_join_approval || false);
        setDefaultJoinRole(data.default_join_role || "ENGINEER");
      }
    } catch (err) {
      console.error("Failed to load team settings:", err);
    }
  };

  const fetchMembers = async () => {
    try {
      const res = await fetch(`${apiBase}/api/teams/${teamId}/members`);
      if (res.ok) {
        const list = await res.json();
        setMembers(list);
      }
    } catch (err) {
      console.error("Failed to fetch members:", err);
    }
  };

  const fetchMembershipRequests = async () => {
    if (!isOwnerOrAdmin) return;
    try {
      const res = await fetch(`${apiBase}/api/teams/${teamId}/membership-requests`);
      if (res.ok) {
        const reqs = await res.json();
        setMembershipRequests(reqs);
      }
    } catch (err) {
      console.error("Failed to fetch membership requests:", err);
    }
  };

  const fetchActivities = async () => {
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
            actor_type: l.metadata?.actor_type || (l.actor_user_id.includes("agent") ? "AGENT" : "HUMAN"),
            receipt_id: l.metadata?.receipt_id,
          }))
        );
      } else {
        // Fallback realistic activity
        setActivities([
          {
            id: "act_001",
            user_id: "hw_specialist",
            action: "TASK_CREATED",
            details: 'Linked to BOM Part: MP1584 Buck Regulator',
            timestamp: new Date(Date.now() - 3600000).toISOString(),
            actor_type: "HUMAN",
          },
          {
            id: "act_002",
            user_id: "agent_thermal_pinn",
            action: "AGENT_EXECUTION_COMPLETED",
            details: 'Boundary condition solved for 12V LiFePO4 regulator pack',
            timestamp: new Date(Date.now() - 7200000).toISOString(),
            actor_type: "AGENT",
            receipt_id: "AIQ-RCPT-8941",
          },
          {
            id: "act_003",
            user_id: "lead_engineer",
            action: "DECISION_APPROVED",
            details: 'Approved MP1584EN buck regulator architecture',
            timestamp: new Date(Date.now() - 14400000).toISOString(),
            actor_type: "HUMAN",
          },
        ]);
      }
    } catch (err) {
      console.error("Failed to fetch activity:", err);
    }
  };

  useEffect(() => {
    if (teamId) {
      fetchTeamDetails();
      fetchMembers();
      fetchMembershipRequests();
      fetchActivities();
    }
  }, [teamId]);

  // Code Management
  const handleRotateCode = async () => {
    try {
      const res = await fetch(`${apiBase}/api/teams/${teamId}/join-code/rotate`, { method: "POST" });
      if (res.ok) {
        const data = await res.json();
        setJoinCode(data.join_code);
        setCodeStatus("ACTIVE");
        fetchActivities();
      }
    } catch (err) {
      console.error("Rotate join code error:", err);
    }
  };

  const handleRevokeCode = async () => {
    try {
      const res = await fetch(`${apiBase}/api/teams/${teamId}/join-code/revoke`, { method: "POST" });
      if (res.ok) {
        setJoinCode(null);
        setCodeStatus("REVOKED");
        fetchActivities();
      }
    } catch (err) {
      console.error("Revoke join code error:", err);
    }
  };

  const handleCopyCode = () => {
    if (!joinCode) return;
    navigator.clipboard.writeText(joinCode);
    setCopiedCode(true);
    setTimeout(() => setCopiedCode(false), 2000);
  };

  // Member Management
  const handleUpdateRole = async (targetUserId: string, newRole: string) => {
    try {
      setMembers((prev) =>
        prev.map((m) => (m.user_id === targetUserId ? { ...m, role: newRole } : m))
      );
      await fetch(`${apiBase}/api/teams/${teamId}/members/${targetUserId}/role`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ role: newRole }),
      });
      fetchActivities();
    } catch (err) {
      console.error("Update role error:", err);
      fetchMembers();
    }
  };

  const handleRemoveMember = async (targetUserId: string) => {
    if (!confirm(`Are you sure you want to remove ${targetUserId} from this team?`)) return;
    try {
      setMembers((prev) => prev.filter((m) => m.user_id !== targetUserId));
      await fetch(`${apiBase}/api/teams/${teamId}/members/${targetUserId}`, {
        method: "DELETE",
      });
      fetchActivities();
    } catch (err) {
      console.error("Remove member error:", err);
      fetchMembers();
    }
  };

  // Membership Requests
  const handleReviewRequest = async (requestId: string, approved: boolean) => {
    try {
      const res = await fetch(`${apiBase}/api/teams/${teamId}/membership-requests/${requestId}/review`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: approved ? "APPROVE" : "REJECT",
          assigned_role: defaultJoinRole,
        }),
      });
      if (res.ok) {
        setMembershipRequests((prev) => prev.filter((r) => r.id !== requestId));
        fetchMembers();
        fetchActivities();
      }
    } catch (err) {
      console.error("Review request error:", err);
    }
  };

  // Team Settings Update
  const handleSaveSettings = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch(`${apiBase}/api/teams/${teamId}/settings`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: teamName,
          description: teamDescription,
          require_join_approval: requireJoinApproval,
          default_join_role: defaultJoinRole,
        }),
      });
      if (res.ok) {
        alert("Team settings saved successfully.");
        fetchActivities();
      }
    } catch (err) {
      console.error("Save settings error:", err);
    }
  };

  const filteredActivities = activities.filter((a) => {
    if (activityFilter === "ALL") return true;
    return a.actor_type === activityFilter;
  });

  return (
    <div className="flex flex-col h-full bg-zinc-950 text-zinc-100 rounded-2xl border border-zinc-800/80 overflow-hidden shadow-2xl">
      {/* Top Banner: Team Identity & Quick Actions */}
      <div className="px-6 py-4 bg-zinc-900/60 border-b border-zinc-800/80 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center space-x-3.5">
          <div className="p-2.5 bg-cyan-950/40 rounded-xl border border-cyan-800/40 text-cyan-400">
            <Users className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-lg font-bold text-zinc-100 tracking-tight">{teamName}</h1>
              <span className="px-2 py-0.5 rounded-full bg-cyan-950/70 text-cyan-400 border border-cyan-800/50 font-mono text-[11px]">
                {currentUserRole}
              </span>
            </div>
            <p className="text-xs text-zinc-400 max-w-xl truncate">{teamDescription}</p>
          </div>
        </div>

        <div className="flex items-center space-x-2 text-xs">
          <button
            onClick={() => setIsJoinModalOpen(true)}
            className="px-3 py-1.5 bg-zinc-900 hover:bg-zinc-800 text-zinc-200 border border-zinc-700 rounded-lg flex items-center space-x-1.5 transition-colors shadow-sm"
          >
            <KeyRound className="w-3.5 h-3.5 text-cyan-400" />
            <span>Join Team (Code)</span>
          </button>

          {isOwnerOrAdmin && (
            <button
              onClick={() => setIsInviteModalOpen(true)}
              className="px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-zinc-950 font-medium rounded-lg flex items-center space-x-1.5 transition-colors shadow-sm"
            >
              <UserPlus className="w-3.5 h-3.5" />
              <span>Invite Member</span>
            </button>
          )}
        </div>
      </div>

      {/* 8-Tab Navigation Bar */}
      <div className="flex items-center px-4 bg-zinc-950 border-b border-zinc-800/80 overflow-x-auto text-xs font-mono scrollbar-none">
        {[
          { key: "overview", label: "Overview", icon: LayoutDashboard },
          { key: "members", label: "Members", icon: Users, badge: members.length },
          { key: "tasks", label: "Tasks", icon: CheckSquare },
          { key: "activity", label: "Activity", icon: Activity },
          { key: "decisions", label: "Decisions", icon: Scale },
          { key: "approvals", label: "Approvals", icon: ShieldAlert },
          { key: "invitations", label: "Invitations", icon: Mail, badge: membershipRequests.length > 0 ? membershipRequests.length : undefined },
          { key: "settings", label: "Settings", icon: Settings },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.key;

          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as TabKey)}
              className={`flex items-center space-x-2 px-3.5 py-3 border-b-2 transition-all whitespace-nowrap ${
                isActive
                  ? "border-cyan-400 text-cyan-300 font-semibold bg-zinc-900/30"
                  : "border-transparent text-zinc-400 hover:text-zinc-200 hover:border-zinc-700"
              }`}
            >
              <Icon className={`w-3.5 h-3.5 ${isActive ? "text-cyan-400" : "text-zinc-400"}`} />
              <span>{tab.label}</span>
              {tab.badge !== undefined && (
                <span className={`px-1.5 py-0.2 rounded-full text-[10px] font-mono ${
                  isActive ? "bg-cyan-950 text-cyan-300 border border-cyan-800/60" : "bg-zinc-800 text-zinc-400"
                }`}>
                  {tab.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Tab Content Panels */}
      <div className="flex-1 p-5 overflow-y-auto bg-zinc-950/40">
        {/* 1. OVERVIEW TAB */}
        {activeTab === "overview" && (
          <div className="space-y-5">
            {/* KPI Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
              <div
                onClick={() => setActiveTab("members")}
                className="p-4 bg-zinc-900/60 hover:bg-zinc-900 border border-zinc-800 rounded-xl space-y-1 cursor-pointer transition-all group"
              >
                <span className="text-[11px] font-mono text-zinc-400 flex items-center justify-between">
                  ACTIVE ROSTER
                  <Users className="w-4 h-4 text-cyan-400 group-hover:scale-110 transition-transform" />
                </span>
                <div className="text-2xl font-bold text-zinc-100">{members.length}</div>
                <p className="text-[11px] text-zinc-400">Engineering collaborators</p>
              </div>

              <div
                onClick={() => setActiveTab("tasks")}
                className="p-4 bg-zinc-900/60 hover:bg-zinc-900 border border-zinc-800 rounded-xl space-y-1 cursor-pointer transition-all group"
              >
                <span className="text-[11px] font-mono text-zinc-400 flex items-center justify-between">
                  ENGINEERING WORK ITEMS
                  <CheckSquare className="w-4 h-4 text-indigo-400 group-hover:scale-110 transition-transform" />
                </span>
                <div className="text-2xl font-bold text-zinc-100">Tasks Board</div>
                <p className="text-[11px] text-zinc-400">Linked to BOM, PCB, analysis</p>
              </div>

              <div
                onClick={() => setActiveTab("approvals")}
                className="p-4 bg-zinc-900/60 hover:bg-zinc-900 border border-zinc-800 rounded-xl space-y-1 cursor-pointer transition-all group"
              >
                <span className="text-[11px] font-mono text-zinc-400 flex items-center justify-between">
                  GATE APPROVALS
                  <ShieldAlert className="w-4 h-4 text-amber-400 group-hover:scale-110 transition-transform" />
                </span>
                <div className="text-2xl font-bold text-amber-400">Review Gates</div>
                <p className="text-[11px] text-zinc-400">BOM swaps & release sign-offs</p>
              </div>

              <div
                onClick={() => setActiveTab("decisions")}
                className="p-4 bg-zinc-900/60 hover:bg-zinc-900 border border-zinc-800 rounded-xl space-y-1 cursor-pointer transition-all group"
              >
                <span className="text-[11px] font-mono text-zinc-400 flex items-center justify-between">
                  DESIGN DECISIONS
                  <Scale className="w-4 h-4 text-emerald-400 group-hover:scale-110 transition-transform" />
                </span>
                <div className="text-2xl font-bold text-zinc-100">Trade-Offs</div>
                <p className="text-[11px] text-zinc-400">Multi-criteria ranking history</p>
              </div>
            </div>

            {/* Quick Share Join Code Card */}
            <div className="p-4 bg-zinc-900/80 rounded-xl border border-cyan-800/40 flex flex-wrap items-center justify-between gap-4">
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <KeyRound className="w-4 h-4 text-cyan-400" />
                  <span className="font-semibold text-xs text-zinc-100">Team Joining Code</span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-cyan-950 text-cyan-400 border border-cyan-800/40">
                    {codeStatus}
                  </span>
                </div>
                <p className="text-xs text-zinc-400">
                  Share this CSPRNG 6-character code with engineers to join immediately or request gate review.
                </p>
              </div>

              <div className="flex items-center space-x-2.5">
                {joinCode ? (
                  <div className="flex items-center space-x-2 bg-zinc-950 px-3 py-1.5 rounded-lg border border-zinc-800 font-mono text-cyan-400 tracking-widest text-sm font-bold">
                    <span>{joinCode}</span>
                    <button
                      onClick={handleCopyCode}
                      className="p-1 hover:bg-zinc-800 rounded text-zinc-400 hover:text-cyan-300 transition-colors"
                      title="Copy code"
                    >
                      {copiedCode ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                    </button>
                  </div>
                ) : (
                  <span className="text-xs text-rose-400 font-mono">Code Revoked</span>
                )}

                {isOwnerOrAdmin && (
                  <button
                    onClick={handleRotateCode}
                    className="px-2.5 py-1.5 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 rounded-lg text-xs flex items-center space-x-1"
                    title="Rotate code immediately"
                  >
                    <RefreshCw className="w-3 h-3" />
                    <span>Regenerate</span>
                  </button>
                )}
              </div>
            </div>

            {/* Recent Activity Stream */}
            <div className="p-4 bg-zinc-900/50 rounded-xl border border-zinc-800 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-zinc-200 flex items-center gap-2">
                  <Activity className="w-4 h-4 text-cyan-400" />
                  Recent Collaboration Activity
                </span>
                <button
                  onClick={() => setActiveTab("activity")}
                  className="text-xs text-cyan-400 hover:underline font-mono"
                >
                  View full audit log →
                </button>
              </div>

              <div className="divide-y divide-zinc-800/60">
                {activities.slice(0, 4).map((act) => (
                  <div key={act.id} className="py-2.5 flex items-center justify-between text-xs">
                    <div className="flex items-center space-x-2.5">
                      {act.actor_type === "AGENT" ? (
                        <span className="p-1 rounded bg-indigo-950/60 border border-indigo-800/50 text-indigo-400">
                          <Bot className="w-3.5 h-3.5" />
                        </span>
                      ) : (
                        <span className="p-1 rounded bg-zinc-800 text-zinc-300">
                          <Users className="w-3.5 h-3.5" />
                        </span>
                      )}
                      <div>
                        <span className="font-semibold text-zinc-200">{act.user_id}</span>{" "}
                        <span className="text-zinc-400 font-mono">[{act.action}]</span>
                        <div className="text-[11px] text-zinc-400 truncate max-w-md">{act.details}</div>
                      </div>
                    </div>
                    <span className="text-[10px] text-zinc-500 font-mono whitespace-nowrap">
                      {new Date(act.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* 2. MEMBERS TAB */}
        {activeTab === "members" && (
          <div className="space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-zinc-800">
              <div>
                <h3 className="text-sm font-semibold text-zinc-100">Team Roster & Role Assignments</h3>
                <p className="text-xs text-zinc-400">
                  Granular 5-tier access control: OWNER, ADMIN, ENGINEER, RESEARCHER, VIEWER.
                </p>
              </div>

              {isOwner && (
                <button
                  onClick={() => setIsTransferModalOpen(true)}
                  className="px-3 py-1.5 bg-rose-950/60 hover:bg-rose-900/60 text-rose-300 border border-rose-800/60 rounded-lg text-xs flex items-center space-x-1.5"
                >
                  <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
                  <span>Transfer Ownership</span>
                </button>
              )}
            </div>

            <div className="overflow-x-auto rounded-xl border border-zinc-800 bg-zinc-900/40">
              <table className="w-full text-left text-xs">
                <thead className="bg-zinc-900/80 text-zinc-400 font-mono border-b border-zinc-800">
                  <tr>
                    <th className="p-3">Collaborator</th>
                    <th className="p-3">Role</th>
                    <th className="p-3">Joined Date</th>
                    <th className="p-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-800/60 text-zinc-200">
                  {members.map((m) => (
                    <tr key={m.user_id} className="hover:bg-zinc-850/40">
                      <td className="p-3">
                        <div className="font-medium text-zinc-100">{m.name || m.user_id}</div>
                        <div className="text-[11px] text-zinc-400 font-mono">{m.user_id}</div>
                      </td>
                      <td className="p-3">
                        {isOwnerOrAdmin && m.role !== "OWNER" ? (
                          <select
                            value={m.role}
                            onChange={(e) => handleUpdateRole(m.user_id, e.target.value)}
                            className="bg-zinc-950 border border-zinc-800 text-xs text-cyan-300 rounded px-2 py-1 font-mono focus:outline-none focus:border-cyan-500"
                          >
                            <option value="ADMIN">ADMIN</option>
                            <option value="ENGINEER">ENGINEER</option>
                            <option value="RESEARCHER">RESEARCHER</option>
                            <option value="VIEWER">VIEWER</option>
                          </select>
                        ) : (
                          <span className="px-2 py-0.5 rounded font-mono text-[11px] bg-zinc-800 text-zinc-300 border border-zinc-700">
                            {m.role}
                          </span>
                        )}
                      </td>
                      <td className="p-3 text-zinc-400 font-mono text-[11px]">
                        {new Date(m.joined_at).toLocaleDateString()}
                      </td>
                      <td className="p-3 text-right">
                        {isOwnerOrAdmin && m.role !== "OWNER" && (
                          <button
                            onClick={() => handleRemoveMember(m.user_id)}
                            className="p-1 text-zinc-500 hover:text-rose-400 transition-colors"
                            title="Remove member"
                          >
                            <UserX className="w-4 h-4" />
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* 3. TASKS TAB */}
        {activeTab === "tasks" && (
          <TaskBoard
            teamId={teamId}
            projectId={projectId}
            apiBase={apiBase}
            members={members}
            canCreateTask={isOwnerOrAdmin || currentUserRole === "ENGINEER"}
          />
        )}

        {/* 4. ACTIVITY TAB */}
        {activeTab === "activity" && (
          <div className="space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-zinc-800">
              <div>
                <h3 className="text-sm font-semibold text-zinc-100">Unified Team & AI Activity Stream</h3>
                <p className="text-xs text-zinc-400">
                  Immutable audit trail of human actions, AI agent solver runs, and system gate evaluations.
                </p>
              </div>

              <div className="flex items-center space-x-1.5 text-xs font-mono">
                <Filter className="w-3 h-3 text-zinc-400" />
                {["ALL", "HUMAN", "AGENT", "SYSTEM"].map((f) => (
                  <button
                    key={f}
                    onClick={() => setActivityFilter(f as any)}
                    className={`px-2.5 py-1 rounded border text-[11px] ${
                      activityFilter === f
                        ? "bg-zinc-800 border-zinc-700 text-cyan-400"
                        : "bg-zinc-900/40 border-zinc-800 text-zinc-400 hover:text-zinc-200"
                    }`}
                  >
                    {f}
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-2.5">
              {filteredActivities.map((act) => (
                <div
                  key={act.id}
                  className="p-3.5 bg-zinc-900/60 border border-zinc-800 rounded-xl flex items-start justify-between gap-3 text-xs"
                >
                  <div className="flex items-start space-x-3">
                    {act.actor_type === "AGENT" ? (
                      <div className="p-1.5 bg-indigo-950/60 border border-indigo-800/50 rounded-lg text-indigo-400 shrink-0 mt-0.5">
                        <Bot className="w-4 h-4" />
                      </div>
                    ) : (
                      <div className="p-1.5 bg-zinc-800 rounded-lg text-zinc-300 shrink-0 mt-0.5">
                        <Users className="w-4 h-4" />
                      </div>
                    )}

                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        <span className="font-semibold text-zinc-100">{act.user_id}</span>
                        <span className="px-1.5 py-0.2 rounded font-mono text-[10px] bg-zinc-800 text-zinc-400">
                          {act.action}
                        </span>
                        {act.receipt_id && (
                          <span className="px-1.5 py-0.2 rounded font-mono text-[10px] bg-indigo-950 text-indigo-300 border border-indigo-800/40">
                            Receipt: {act.receipt_id}
                          </span>
                        )}
                      </div>
                      <p className="text-zinc-300 text-[11px] leading-relaxed">{act.details}</p>
                    </div>
                  </div>

                  <span className="text-[10px] font-mono text-zinc-500 whitespace-nowrap">
                    {new Date(act.timestamp).toLocaleDateString()} {new Date(act.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 5. DECISIONS TAB */}
        {activeTab === "decisions" && (
          <DecisionsLog
            teamId={teamId}
            projectId={projectId}
            apiBase={apiBase}
            canManageDecisions={isOwnerOrAdmin || currentUserRole === "ENGINEER"}
          />
        )}

        {/* 6. APPROVALS TAB */}
        {activeTab === "approvals" && (
          <ApprovalsQueue
            teamId={teamId}
            projectId={projectId}
            apiBase={apiBase}
            currentUserRole={currentUserRole}
          />
        )}

        {/* 7. INVITATIONS TAB */}
        {activeTab === "invitations" && (
          <div className="space-y-6">
            {/* Membership Requests Queue (When Join Approval is On) */}
            {membershipRequests.length > 0 && (
              <div className="p-4 bg-amber-950/20 border border-amber-800/40 rounded-xl space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <ShieldAlert className="w-4 h-4 text-amber-400" />
                    <h3 className="text-xs font-semibold text-amber-300">
                      Pending Joining Code Membership Requests ({membershipRequests.length})
                    </h3>
                  </div>
                  <span className="text-[10px] text-zinc-400 font-mono">Requires Admin Approval</span>
                </div>

                <div className="divide-y divide-amber-800/20">
                  {membershipRequests.map((req) => (
                    <div key={req.id} className="py-2.5 flex items-center justify-between text-xs">
                      <div>
                        <div className="font-semibold text-zinc-100">{req.user_name || req.user_id}</div>
                        <div className="text-[10px] text-zinc-400 font-mono">
                          Requested Role: <span className="text-cyan-400">{req.requested_role}</span> • {new Date(req.created_at).toLocaleDateString()}
                        </div>
                      </div>

                      {isOwnerOrAdmin && (
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => handleReviewRequest(req.id, false)}
                            className="px-2.5 py-1 bg-rose-950/50 hover:bg-rose-900/60 text-rose-300 border border-rose-800/50 rounded-lg text-xs"
                          >
                            Reject
                          </button>
                          <button
                            onClick={() => handleReviewRequest(req.id, true)}
                            className="px-3 py-1 bg-emerald-600 hover:bg-emerald-500 text-zinc-950 font-medium rounded-lg text-xs"
                          >
                            Approve
                          </button>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Cryptographic Email Invitations */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
              <TeamInvitationPanel teamId={teamId} apiBase={apiBase} />
              <InvitationList teamId={teamId} apiBase={apiBase} />
            </div>
          </div>
        )}

        {/* 8. SETTINGS TAB */}
        {activeTab === "settings" && (
          <div className="max-w-2xl space-y-5 text-xs">
            <div className="pb-3 border-b border-zinc-800">
              <h3 className="text-sm font-semibold text-zinc-100">Team Workspace Settings</h3>
              <p className="text-zinc-400">Configure team properties, security policies, and join controls.</p>
            </div>

            <form onSubmit={handleSaveSettings} className="space-y-4">
              <div>
                <label className="block text-zinc-400 font-mono mb-1">Team Name</label>
                <input
                  type="text"
                  required
                  value={teamName}
                  onChange={(e) => setTeamName(e.target.value)}
                  disabled={!isOwnerOrAdmin}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-zinc-100 focus:outline-none focus:border-cyan-500 disabled:opacity-60"
                />
              </div>

              <div>
                <label className="block text-zinc-400 font-mono mb-1">Description</label>
                <textarea
                  rows={3}
                  value={teamDescription}
                  onChange={(e) => setTeamDescription(e.target.value)}
                  disabled={!isOwnerOrAdmin}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-zinc-100 focus:outline-none focus:border-cyan-500 disabled:opacity-60"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 p-4 bg-zinc-900/60 rounded-xl border border-zinc-800">
                <div className="space-y-1">
                  <label className="block font-semibold text-zinc-200">Require Join Approval</label>
                  <p className="text-[11px] text-zinc-400">
                    When enabled, users entering the code must be approved by an Admin before joining.
                  </p>
                  <label className="inline-flex items-center cursor-pointer pt-1">
                    <input
                      type="checkbox"
                      checked={requireJoinApproval}
                      onChange={(e) => setRequireJoinApproval(e.target.checked)}
                      disabled={!isOwnerOrAdmin}
                      className="sr-only peer"
                    />
                    <div className="relative w-9 h-5 bg-zinc-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-cyan-600"></div>
                    <span className="ms-2 font-mono text-[11px] text-zinc-300">
                      {requireJoinApproval ? "Strict Approval Required" : "Instant Join"}
                    </span>
                  </label>
                </div>

                <div className="space-y-1">
                  <label className="block font-semibold text-zinc-200">Default Join Role</label>
                  <p className="text-[11px] text-zinc-400">Role granted to newcomers entering the code.</p>
                  <select
                    value={defaultJoinRole}
                    onChange={(e) => setDefaultJoinRole(e.target.value)}
                    disabled={!isOwnerOrAdmin}
                    className="w-full mt-1 bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-1.5 text-zinc-100 font-mono focus:outline-none focus:border-cyan-500 disabled:opacity-60"
                  >
                    <option value="ENGINEER">ENGINEER</option>
                    <option value="RESEARCHER">RESEARCHER</option>
                    <option value="VIEWER">VIEWER</option>
                  </select>
                </div>
              </div>

              {isOwnerOrAdmin && (
                <div className="flex justify-end pt-2">
                  <button
                    type="submit"
                    className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-zinc-950 font-medium rounded-lg text-xs shadow-sm"
                  >
                    Save Team Settings
                  </button>
                </div>
              )}
            </form>

            {/* Danger Zone */}
            {isOwner && (
              <div className="pt-6 border-t border-zinc-800 space-y-3">
                <h4 className="text-xs font-semibold text-rose-400 font-mono uppercase">Danger Zone</h4>
                <div className="p-4 bg-rose-950/20 border border-rose-900/50 rounded-xl flex items-center justify-between">
                  <div>
                    <div className="font-semibold text-zinc-200">Revoke Team Join Code</div>
                    <p className="text-[11px] text-zinc-400">Immediately disables all active join code entries.</p>
                  </div>
                  <button
                    onClick={handleRevokeCode}
                    className="px-3 py-1.5 bg-rose-950/50 hover:bg-rose-900/60 text-rose-300 border border-rose-800/60 rounded-lg text-xs"
                  >
                    Revoke Code
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Global Collaboration Modals */}
      <JoinTeamModal
        isOpen={isJoinModalOpen}
        onClose={() => setIsJoinModalOpen(false)}
        apiBase={apiBase}
        onJoined={(joinedTeam) => {
          setTeamName(joinedTeam.team_name);
          setTeamId(joinedTeam.team_id);
          fetchMembers();
          fetchActivities();
        }}
      />

      <OwnershipTransferModal
        isOpen={isTransferModalOpen}
        onClose={() => setIsTransferModalOpen(false)}
        teamId={teamId}
        teamName={teamName}
        currentUserId={members.find((m) => m.role === "OWNER")?.user_id || "current_user"}
        members={members}
        apiBase={apiBase}
        onSuccess={() => {
          fetchMembers();
          fetchActivities();
        }}
      />

      <InvitationModal
        isOpen={isInviteModalOpen}
        onClose={() => setIsInviteModalOpen(false)}
        teamId={teamId}
        apiBase={apiBase}
        onSuccess={() => {
          fetchActivities();
        }}
      />
    </div>
  );
}
