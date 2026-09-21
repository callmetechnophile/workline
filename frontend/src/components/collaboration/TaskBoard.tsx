import React, { useState, useEffect } from "react";
import {
  CheckSquare,
  Plus,
  Filter,
  Search,
  Clock,
  AlertCircle,
  Link2,
  User,
  ArrowRight,
  MoreVertical,
  CheckCircle2,
} from "lucide-react";

export type TaskStatus = "TODO" | "IN_PROGRESS" | "REVIEW" | "DONE";
export type TaskPriority = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export interface RelatedArtifact {
  artifact_type: string;
  artifact_id: string;
  artifact_name: string;
  metadata?: Record<string, any>;
}

export interface TaskItem {
  id: string;
  team_id: string;
  project_id: string;
  title: string;
  description?: string;
  status: TaskStatus;
  priority: TaskPriority;
  created_by: string;
  assignee_id?: string;
  assignee_name?: string;
  related_artifact?: RelatedArtifact;
  due_date?: string;
  created_at: string;
  updated_at: string;
}

interface TaskBoardProps {
  teamId: string;
  projectId?: string;
  apiBase: string;
  members: Array<{ user_id: string; name?: string; role: string }>;
  canCreateTask?: boolean;
}

const STATUS_COLUMNS: { key: TaskStatus; label: string; color: string }[] = [
  { key: "TODO", label: "To Do", color: "border-zinc-700 text-zinc-400" },
  { key: "IN_PROGRESS", label: "In Progress", color: "border-cyan-500/40 text-cyan-400" },
  { key: "REVIEW", label: "Gate / Review", color: "border-amber-500/40 text-amber-400" },
  { key: "DONE", label: "Done", color: "border-emerald-500/40 text-emerald-400" },
];

const PRIORITY_BADGES: Record<TaskPriority, { label: string; cls: string }> = {
  LOW: { label: "LOW", cls: "bg-zinc-800 text-zinc-400 border-zinc-700" },
  MEDIUM: { label: "MED", cls: "bg-cyan-950/60 text-cyan-400 border-cyan-800/40" },
  HIGH: { label: "HIGH", cls: "bg-amber-950/60 text-amber-300 border-amber-800/40" },
  CRITICAL: { label: "CRIT", cls: "bg-rose-950/60 text-rose-400 border-rose-800/40 font-bold animate-pulse" },
};

export const TaskBoard: React.FC<TaskBoardProps> = ({
  teamId,
  projectId = "default_project",
  apiBase,
  members,
  canCreateTask = true,
}) => {
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [priorityFilter, setPriorityFilter] = useState<string>("ALL");
  const [assigneeFilter, setAssigneeFilter] = useState<string>("ALL");
  const [isCreateOpen, setIsCreateOpen] = useState(false);

  // New task form state
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<TaskPriority>("MEDIUM");
  const [assigneeId, setAssigneeId] = useState("");
  const [artifactType, setArtifactType] = useState("BOM");
  const [artifactName, setArtifactName] = useState("");
  const [artifactId, setArtifactId] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchTasks = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${apiBase}/api/tasks?team_id=${encodeURIComponent(teamId)}`);
      if (res.ok) {
        const data = await res.json();
        setTasks(data);
      }
    } catch (err) {
      console.error("Failed to fetch tasks:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (teamId) {
      fetchTasks();
    }
  }, [teamId]);

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    setIsSubmitting(true);
    try {
      const payload: any = {
        team_id: teamId,
        project_id: projectId,
        title: title.trim(),
        description: description.trim(),
        priority,
        assignee_id: assigneeId || null,
      };

      if (artifactName.trim()) {
        payload.related_artifact = {
          artifact_type: artifactType,
          artifact_id: artifactId.trim() || `art_${Date.now()}`,
          artifact_name: artifactName.trim(),
        };
      }

      const res = await fetch(`${apiBase}/api/tasks`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        const created = await res.json();
        setTasks((prev) => [created, ...prev]);
        setIsCreateOpen(false);
        setTitle("");
        setDescription("");
        setArtifactName("");
        setArtifactId("");
      }
    } catch (err) {
      console.error("Error creating task:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleUpdateStatus = async (taskId: string, newStatus: TaskStatus) => {
    // Optimistic UI update
    setTasks((prev) =>
      prev.map((t) => (t.id === taskId ? { ...t, status: newStatus } : t))
    );

    try {
      await fetch(`${apiBase}/api/tasks/${taskId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus }),
      });
    } catch (err) {
      console.error("Failed to update status:", err);
      fetchTasks();
    }
  };

  const filteredTasks = tasks.filter((task) => {
    const matchesSearch =
      task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (task.description && task.description.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (task.related_artifact && task.related_artifact.artifact_name.toLowerCase().includes(searchQuery.toLowerCase()));

    const matchesPriority = priorityFilter === "ALL" || task.priority === priorityFilter;
    const matchesAssignee = assigneeFilter === "ALL" || task.assignee_id === assigneeFilter;

    return matchesSearch && matchesPriority && matchesAssignee;
  });

  return (
    <div className="flex flex-col h-full bg-zinc-950 text-zinc-100 p-4 space-y-4 rounded-xl border border-zinc-800/80">
      {/* Header Controls */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-zinc-800/80">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-cyan-950/40 rounded-lg border border-cyan-800/40 text-cyan-400">
            <CheckSquare className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-semibold tracking-wide text-zinc-100 flex items-center gap-2">
              Engineering Work Items
              <span className="text-xs px-2 py-0.5 rounded-full bg-zinc-800 text-zinc-400 border border-zinc-700 font-mono">
                {tasks.length}
              </span>
            </h2>
            <p className="text-xs text-zinc-400">
              Link tasks directly to BOM parts, design decisions, datasheets, and hardware analyses.
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {canCreateTask && (
            <button
              onClick={() => setIsCreateOpen(true)}
              className="px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-zinc-950 font-medium text-xs rounded-lg flex items-center space-x-1.5 transition-colors shadow-sm"
            >
              <Plus className="w-4 h-4" />
              <span>Create Work Item</span>
            </button>
          )}
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="flex flex-wrap items-center gap-3 text-xs bg-zinc-900/60 p-2.5 rounded-lg border border-zinc-800/60">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-zinc-400" />
          <input
            type="text"
            placeholder="Search work items or artifacts..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-zinc-950/80 border border-zinc-800 rounded-md pl-8 pr-3 py-1.5 text-xs text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-cyan-500"
          />
        </div>

        <div className="flex items-center space-x-1.5">
          <span className="text-zinc-400 flex items-center gap-1 font-mono">
            <Filter className="w-3 h-3" /> Priority:
          </span>
          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="bg-zinc-950 border border-zinc-800 text-zinc-300 rounded px-2 py-1 text-xs focus:outline-none focus:border-cyan-500"
          >
            <option value="ALL">All Priorities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>
        </div>

        <div className="flex items-center space-x-1.5">
          <span className="text-zinc-400 flex items-center gap-1 font-mono">
            <User className="w-3 h-3" /> Assignee:
          </span>
          <select
            value={assigneeFilter}
            onChange={(e) => setAssigneeFilter(e.target.value)}
            className="bg-zinc-950 border border-zinc-800 text-zinc-300 rounded px-2 py-1 text-xs focus:outline-none focus:border-cyan-500"
          >
            <option value="ALL">All Engineers</option>
            {members.map((m) => (
              <option key={m.user_id} value={m.user_id}>
                {m.name || m.user_id} ({m.role})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Kanban Board Columns */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3 flex-1 min-h-[450px]">
        {STATUS_COLUMNS.map((col) => {
          const colTasks = filteredTasks.filter((t) => t.status === col.key);

          return (
            <div
              key={col.key}
              className="flex flex-col bg-zinc-900/40 rounded-xl border border-zinc-800/80 p-3 space-y-3"
            >
              {/* Column Header */}
              <div className="flex items-center justify-between pb-2 border-b border-zinc-800/60">
                <span className={`text-xs font-mono font-semibold uppercase tracking-wider ${col.color}`}>
                  {col.label}
                </span>
                <span className="text-xs px-2 py-0.5 rounded-full bg-zinc-800/80 text-zinc-400 font-mono text-[11px]">
                  {colTasks.length}
                </span>
              </div>

              {/* Tasks List */}
              <div className="flex-1 space-y-2.5 overflow-y-auto max-h-[560px] pr-1">
                {colTasks.map((task) => {
                  const pBadge = PRIORITY_BADGES[task.priority] || PRIORITY_BADGES.MEDIUM;

                  return (
                    <div
                      key={task.id}
                      className="p-3 bg-zinc-900/90 hover:bg-zinc-850 border border-zinc-800 rounded-lg space-y-2 transition-all group shadow-sm hover:border-zinc-700"
                    >
                      {/* Priority & ID */}
                      <div className="flex items-center justify-between text-[10px]">
                        <span className="font-mono text-zinc-400">{task.id}</span>
                        <span className={`px-1.5 py-0.5 rounded border text-[10px] font-mono ${pBadge.cls}`}>
                          {pBadge.label}
                        </span>
                      </div>

                      {/* Task Title */}
                      <div className="text-xs font-medium text-zinc-200 leading-snug">
                        {task.title}
                      </div>

                      {/* Description */}
                      {task.description && (
                        <p className="text-[11px] text-zinc-400 line-clamp-2 leading-relaxed">
                          {task.description}
                        </p>
                      )}

                      {/* Linked Engineering Artifact Chip */}
                      {task.related_artifact && (
                        <div className="flex items-center gap-1.5 px-2 py-1 bg-zinc-950/90 border border-zinc-800/90 rounded text-[11px] text-cyan-400 font-mono">
                          <Link2 className="w-3 h-3 text-cyan-500 shrink-0" />
                          <span className="text-[10px] text-zinc-400 uppercase">
                            [{task.related_artifact.artifact_type}]
                          </span>
                          <span className="truncate">{task.related_artifact.artifact_name}</span>
                        </div>
                      )}

                      {/* Assignee & Controls */}
                      <div className="flex items-center justify-between pt-1 border-t border-zinc-800/50 text-[11px] text-zinc-400">
                        <div className="flex items-center gap-1">
                          <User className="w-3 h-3 text-zinc-400" />
                          <span className="truncate max-w-[100px] text-zinc-300">
                            {task.assignee_name || task.assignee_id || "Unassigned"}
                          </span>
                        </div>

                        {/* Status Quick-Transition Dropdown */}
                        <select
                          value={task.status}
                          onChange={(e) => handleUpdateStatus(task.id, e.target.value as TaskStatus)}
                          className="bg-zinc-950 border border-zinc-800 text-[10px] text-zinc-300 rounded px-1.5 py-0.5 focus:outline-none focus:border-cyan-500"
                        >
                          <option value="TODO">To Do</option>
                          <option value="IN_PROGRESS">In Prog</option>
                          <option value="REVIEW">Review</option>
                          <option value="DONE">Done</option>
                        </select>
                      </div>
                    </div>
                  );
                })}

                {colTasks.length === 0 && (
                  <div className="h-24 flex items-center justify-center border border-dashed border-zinc-800/60 rounded-lg text-zinc-400 text-xs font-mono">
                    No work items
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Create Task Modal */}
      {isCreateOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 max-w-lg w-full space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
              <h3 className="text-sm font-semibold text-zinc-100 flex items-center gap-2">
                <CheckSquare className="w-4 h-4 text-cyan-400" />
                Create Engineering Work Item
              </h3>
              <button
                onClick={() => setIsCreateOpen(false)}
                className="text-zinc-500 hover:text-zinc-300 text-sm"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateTask} className="space-y-3.5 text-xs">
              <div>
                <label className="block text-zinc-400 font-mono mb-1">Task Title *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Verify voltage regulation and ripple on LM7805"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-zinc-100 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="block text-zinc-400 font-mono mb-1">Description</label>
                <textarea
                  rows={3}
                  placeholder="Provide technical criteria, tolerances, or test guidelines..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-zinc-100 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-zinc-400 font-mono mb-1">Priority</label>
                  <select
                    value={priority}
                    onChange={(e) => setPriority(e.target.value as TaskPriority)}
                    className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-2.5 py-2 text-zinc-100 focus:outline-none focus:border-cyan-500"
                  >
                    <option value="LOW">Low</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="HIGH">High</option>
                    <option value="CRITICAL">Critical</option>
                  </select>
                </div>

                <div>
                  <label className="block text-zinc-400 font-mono mb-1">Assignee</label>
                  <select
                    value={assigneeId}
                    onChange={(e) => setAssigneeId(e.target.value)}
                    className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-2.5 py-2 text-zinc-100 focus:outline-none focus:border-cyan-500"
                  >
                    <option value="">Unassigned</option>
                    {members.map((m) => (
                      <option key={m.user_id} value={m.user_id}>
                        {m.name || m.user_id} ({m.role})
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Artifact Linking Section */}
              <div className="p-3 bg-zinc-950/80 rounded-lg border border-zinc-800/80 space-y-2.5">
                <span className="text-[11px] font-mono text-cyan-400 flex items-center gap-1.5">
                  <Link2 className="w-3.5 h-3.5" /> Link Engineering Artifact
                </span>
                <div className="grid grid-cols-3 gap-2">
                  <select
                    value={artifactType}
                    onChange={(e) => setArtifactType(e.target.value)}
                    className="bg-zinc-900 border border-zinc-800 rounded px-2 py-1.5 text-zinc-200 text-xs"
                  >
                    <option value="BOM">BOM Part</option>
                    <option value="COMPONENT">Component</option>
                    <option value="ANALYSIS">Analysis</option>
                    <option value="DATASHEET">Datasheet</option>
                    <option value="WIRING">Wiring</option>
                    <option value="DECISION">Decision</option>
                  </select>
                  <input
                    type="text"
                    placeholder="Artifact Name (e.g. MPU6050)"
                    value={artifactName}
                    onChange={(e) => setArtifactName(e.target.value)}
                    className="col-span-2 bg-zinc-900 border border-zinc-800 rounded px-2.5 py-1.5 text-zinc-200 text-xs"
                  />
                </div>
              </div>

              <div className="flex justify-end space-x-2 pt-2 border-t border-zinc-800">
                <button
                  type="button"
                  onClick={() => setIsCreateOpen(false)}
                  className="px-3 py-1.5 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 rounded-lg text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting || !title.trim()}
                  className="px-4 py-1.5 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-zinc-950 font-medium rounded-lg text-xs"
                >
                  {isSubmitting ? "Creating..." : "Save Work Item"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
