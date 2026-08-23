'use client';

import React, { useState, useEffect } from 'react';
import { Calendar, X, Check, Loader2, ExternalLink, AlertTriangle } from 'lucide-react';

interface GanttTask {
  id: string;
  name: string;
  start?: string;
  end?: string;
  progress?: number;
  dependencies?: string;
  deliverable?: string;
}

interface GoogleCalendarExportModalProps {
  isOpen: boolean;
  onClose: () => void;
  projectId: number;
  projectName: string;
  ganttTasks: GanttTask[];
}

export default function GoogleCalendarExportModal({
  isOpen,
  onClose,
  projectId,
  projectName,
  ganttTasks = []
}: GoogleCalendarExportModalProps) {
  const [selectedTaskIds, setSelectedTaskIds] = useState<string[]>([]);
  const [selectAll, setSelectAll] = useState(true);
  const [timezone, setTimezone] = useState('UTC');
  const [loading, setLoading] = useState(false);

  // Detect browser timezone
  useEffect(() => {
    if (isOpen && typeof window !== 'undefined') {
      try {
        const detectedTz = Intl.DateTimeFormat().resolvedOptions().timeZone;
        if (detectedTz) {
          setTimezone(detectedTz);
        }
      } catch (e) {
        console.error('Failed to detect timezone:', e);
      }
    }
  }, [isOpen]);

  // Pre-select all tasks initially
  useEffect(() => {
    if (isOpen && ganttTasks.length > 0) {
      const allIds = ganttTasks.map(t => t.id || t.name).filter(Boolean);
      setSelectedTaskIds(allIds);
      setSelectAll(true);
    }
  }, [isOpen, ganttTasks]);

  if (!isOpen) return null;

  // Error check: No tasks or missing start date
  const hasNoTasks = !ganttTasks || ganttTasks.length === 0;
  const missingStartDate = ganttTasks.some(t => !t.start);
  const isExportDisabled = hasNoTasks || missingStartDate;

  const handleSelectAllToggle = () => {
    if (selectAll) {
      setSelectedTaskIds([]);
      setSelectAll(false);
    } else {
      const allIds = ganttTasks.map(t => t.id || t.name).filter(Boolean);
      setSelectedTaskIds(allIds);
      setSelectAll(true);
    }
  };

  const handleTaskToggle = (taskId: string) => {
    if (selectedTaskIds.includes(taskId)) {
      const updated = selectedTaskIds.filter(id => id !== taskId);
      setSelectedTaskIds(updated);
      setSelectAll(updated.length === ganttTasks.length);
    } else {
      const updated = [...selectedTaskIds, taskId];
      setSelectedTaskIds(updated);
      setSelectAll(updated.length === ganttTasks.length);
    }
  };

  // Preview properties of the first selected task
  const firstSelectedTask = ganttTasks.find(t => selectedTaskIds.includes(t.id || t.name));

  const handleExport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isExportDisabled || selectedTaskIds.length === 0) return;

    // Check count boundary limit (max 10 tabs)
    if (selectedTaskIds.length > 10) {
      const confirmed = window.confirm(
        `You have selected ${selectedTaskIds.length} tasks. Opening more than 10 tabs might trigger your browser's popup blocker. Do you want to proceed?`
      );
      if (!confirmed) return;
    }

    setLoading(true);
    try {
      const apiBase = process.env.NEXT_PUBLIC_API_URL || 'https://workline-core-gateway.onrender.com';
      const res = await fetch(`${apiBase}/api/calendar/generate-links`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: projectId,
          task_ids: selectedTaskIds,
          timezone: timezone
        })
      });

      if (!res.ok) {
        throw new Error('Failed to generate calendar links.');
      }

      const links = await res.json();
      
      if (links && links.length > 0) {
        // Open each link in a new browser tab
        links.forEach((item: any, idx: number) => {
          // Add a minor delayed timeout to minimize popup blocker triggers
          setTimeout(() => {
            window.open(item.google_calendar_link, '_blank');
          }, idx * 250);
        });
      }

      setLoading(false);
      onClose();
    } catch (err: any) {
      alert(err.message || 'Failed to complete export.');
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-xs p-4">
      <div className="glass-panel border border-cyan-500/20 bg-zinc-950/95 max-w-lg w-full rounded-xl relative p-6 space-y-5 shadow-2xl animate-fade-in font-mono text-xs text-slate-300">
        
        {/* Header */}
        <div className="flex items-center justify-between border-b border-zinc-900 pb-3">
          <div className="flex items-center gap-2 text-cyan-400">
            <Calendar className="w-5 h-5" />
            <h3 className="text-xs font-bold uppercase tracking-widest">
              Export Execution Timeline
            </h3>
          </div>
          <button
            onClick={onClose}
            className="text-slate-500 hover:text-white transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Warning message if disabled */}
        {isExportDisabled ? (
          <div className="bg-red-950/20 border border-red-900/40 p-4 rounded-lg flex items-start gap-2.5 text-red-400">
            <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
            <div>
              <p className="font-bold uppercase tracking-wider text-[10px]">Export Blocked</p>
              <p className="text-[10px] leading-normal mt-1">
                Execution Timeline must be generated before exporting to Google Calendar. Ensure all tasks have assigned start dates.
              </p>
            </div>
          </div>
        ) : (
          <div className="text-[10px] text-slate-400 leading-relaxed">
            Select which tasks you would like to export. Each selected task will open pre-filled in a new Google Calendar tab.
          </div>
        )}

        {!isExportDisabled && (
          <form onSubmit={handleExport} className="space-y-4">
            
            {/* Task Checklist Selector */}
            <div className="space-y-2">
              <div className="flex items-center justify-between border-b border-zinc-900 pb-1.5">
                <label className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Select Tasks</label>
                <label className="flex items-center gap-1.5 cursor-pointer text-[10px] font-bold text-cyan-400">
                  <input
                    type="checkbox"
                    checked={selectAll}
                    onChange={handleSelectAllToggle}
                    className="rounded bg-zinc-950 border-zinc-800 text-cyan-600 focus:ring-0 focus:ring-offset-0 w-3.5 h-3.5"
                  />
                  Select All
                </label>
              </div>

              <div className="max-h-[160px] overflow-y-auto space-y-1.5 pr-1 border border-zinc-900/50 rounded-lg p-2 bg-zinc-900/10">
                {ganttTasks.map((task) => {
                  const taskId = task.id || task.name;
                  const isChecked = selectedTaskIds.includes(taskId);
                  return (
                    <label key={taskId} className="flex items-start gap-2.5 p-1.5 hover:bg-zinc-900/40 rounded cursor-pointer select-none">
                      <input
                        type="checkbox"
                        checked={isChecked}
                        onChange={() => handleTaskToggle(taskId)}
                        className="rounded bg-zinc-950 border-zinc-800 text-cyan-600 focus:ring-0 focus:ring-offset-0 w-3.5 h-3.5 mt-0.5"
                      />
                      <div>
                        <span className="text-[10px] text-slate-200 font-bold block">{task.name}</span>
                        {task.start && (
                          <span className="text-[8px] text-slate-500 block mt-0.5">
                            Duration: {task.start} to {task.end || 'N/A'}
                          </span>
                        )}
                      </div>
                    </label>
                  );
                })}
              </div>
            </div>

            {/* Event Preview Container */}
            {firstSelectedTask && (
              <div className="space-y-1.5">
                <label className="text-[10px] text-slate-400 uppercase font-bold tracking-wider block">Preview Event</label>
                <div className="bg-zinc-900/30 border border-zinc-850 p-3 rounded-lg space-y-2 font-mono text-[9px] text-slate-400 leading-normal">
                  <div>
                    <span className="text-slate-500 font-bold block uppercase tracking-widest text-[8px]">Event Title</span>
                    <span className="text-slate-200 font-bold text-[10px]">{projectName} - {firstSelectedTask.name}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 font-bold block uppercase tracking-widest text-[8px]">Description Snippet</span>
                    <pre className="text-slate-350 whitespace-pre-wrap mt-0.5 max-h-[80px] overflow-y-auto">
                      Project: {projectName}
                      {"\n"}Task: {firstSelectedTask.name}
                      {"\n"}Dependencies: {firstSelectedTask.dependencies || 'None'}
                      {"\n"}Location: WorkflowGuide AI
                    </pre>
                  </div>
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-2 justify-end pt-3 border-t border-zinc-900">
              <button
                type="button"
                onClick={onClose}
                className="bg-zinc-900 hover:bg-zinc-850 border border-zinc-800 text-slate-400 px-4 py-2 rounded cursor-pointer font-bold"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading || selectedTaskIds.length === 0}
                className="bg-cyan-600 hover:bg-cyan-500 text-white px-5 py-2 rounded cursor-pointer font-bold flex items-center gap-1.5 disabled:opacity-40 shadow-lg shadow-cyan-900/20"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    Opening Tabs...
                  </>
                ) : (
                  <>
                    <ExternalLink className="w-3.5 h-3.5" />
                    Open Google Calendar
                  </>
                )}
              </button>
            </div>

          </form>
        )}

        {isExportDisabled && (
          <div className="flex justify-end pt-1">
            <button
              onClick={onClose}
              className="bg-zinc-900 hover:bg-zinc-850 border border-zinc-800 text-slate-400 px-5 py-2 rounded cursor-pointer font-bold"
            >
              Close
            </button>
          </div>
        )}

      </div>
    </div>
  );
}
