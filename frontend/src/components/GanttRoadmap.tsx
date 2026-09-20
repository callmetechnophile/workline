'use client';

import React, { useState } from 'react';
import { Calendar, CheckCircle2, ChevronRight } from 'lucide-react';
import GoogleCalendarExportModal from './GoogleCalendarExportModal';

interface GanttTask {
  id: string;
  name: string;
  start: string;
  end: string;
  progress: number;
  dependencies: string;
  deliverable: string;
}

interface RoadmapPhase {
  phase: number;
  title: string;
  description: string;
  duration_days: number;
  deliverable: string;
}

interface GanttRoadmapProps {
  roadmap: RoadmapPhase[];
  gantt: GanttTask[];
  projectId?: string | number;
  projectName?: string;
  apiBase?: string;
}

export default function GanttRoadmap({
  roadmap,
  gantt,
  projectId,
  projectName,
  apiBase
}: GanttRoadmapProps) {
  const [isExportModalOpen, setIsExportModalOpen] = useState(false);
  const [zoomMode, setZoomMode] = useState<'auto' | 'compact' | 'spacious'>('auto');
  const containerRef = React.useRef<HTMLDivElement>(null);
  const [containerWidth, setContainerWidth] = useState<number>(1100);

  React.useEffect(() => {
    const updateWidth = () => {
      if (containerRef.current) {
        setContainerWidth(containerRef.current.clientWidth);
      }
    };
    updateWidth();
    window.addEventListener('resize', updateWidth);
    return () => window.removeEventListener('resize', updateWidth);
  }, []);

  if (!roadmap || roadmap.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-slate-400">
        <Calendar className="w-12 h-12 mb-2 stroke-1 text-slate-600" />
        <p>No roadmap details generated yet.</p>
      </div>
    );
  }

  // Calculate coordinates for SVG Gantt Chart
  const taskHeight = 38;
  const gap = 16;
  const paddingLeft = 280; // Expanded to prevent truncation of phase names
  const chartHeight = Math.max(gantt.length * (taskHeight + gap) + 46, 220);

  // Time grid calculation
  const daysTotal = roadmap.reduce((sum, r) => sum + r.duration_days, 0) || 25;

  // Dynamic scaling to fill available space and keep it free
  let scale = 36;
  const availableTimelineWidth = Math.max(containerWidth - paddingLeft - 70, 450);

  if (zoomMode === 'auto') {
    scale = Math.max(34, Math.floor(availableTimelineWidth / Math.max(daysTotal, 1)));
  } else if (zoomMode === 'compact') {
    scale = 26;
  } else if (zoomMode === 'spacious') {
    scale = 55;
  }

  const timelineWidth = daysTotal * scale;
  const totalSvgWidth = Math.max(paddingLeft + timelineWidth + 60, containerWidth - 48);

  return (
    <div className="space-y-6">
      {/* Gantt Chart SVG */}
      <div ref={containerRef} className="glass-panel p-6 border border-blue-500/20 overflow-hidden w-full">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-4 border-b border-blue-900/40 pb-3">
          <div className="space-y-0.5">
            <h3 className="text-md font-semibold text-cyan-400 glow-cyan flex items-center gap-2">
              <Calendar className="w-5 h-5" />
              Execution Timeline (Gantt Schedule)
            </h3>
            <p className="text-[11px] text-slate-400">
              Deterministic critical-path milestones & deliverable dependencies
            </p>
          </div>

          <div className="flex items-center gap-3 flex-wrap">
            {/* Zoom / Viewport Mode Selector */}
            <div className="flex items-center bg-slate-950/80 p-0.5 rounded-lg border border-slate-800 text-[11px] font-mono">
              <button
                onClick={() => setZoomMode('auto')}
                className={`px-2.5 py-1 rounded transition cursor-pointer ${
                  zoomMode === 'auto' ? 'bg-cyan-600 text-white font-bold' : 'text-slate-400 hover:text-slate-200'
                }`}
                title="Automatically fits the timeline across the entire card width"
              >
                Auto-Fit
              </button>
              <button
                onClick={() => setZoomMode('compact')}
                className={`px-2.5 py-1 rounded transition cursor-pointer ${
                  zoomMode === 'compact' ? 'bg-cyan-600 text-white font-bold' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Compact
              </button>
              <button
                onClick={() => setZoomMode('spacious')}
                className={`px-2.5 py-1 rounded transition cursor-pointer ${
                  zoomMode === 'spacious' ? 'bg-cyan-600 text-white font-bold' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Spacious
              </button>
            </div>

            <button
              onClick={() => setIsExportModalOpen(true)}
              title="Export your engineering timeline directly to Google Calendar."
              className="bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold px-3 py-1.5 rounded transition-all flex items-center gap-1.5 cursor-pointer shadow-md shadow-cyan-900/10"
            >
              <Calendar className="w-3.5 h-3.5" />
              📅 Export to Google Calendar
            </button>
            <span className="text-[11px] text-slate-400 font-mono">
              Scale: 1d = {scale}px
            </span>
          </div>
        </div>

        <div className="overflow-x-auto pb-2 w-full">
          <svg width={totalSvgWidth} height={chartHeight} className="text-xs w-full block">
            {/* Grid Header Days */}
            {(() => {
              const textInterval = daysTotal > 40 ? 5 : (daysTotal > 15 ? 5 : 2);
              return Array.from({ length: daysTotal + 1 }).map((_, d) => {
                const x = paddingLeft + d * scale;
                const isMajor = d % textInterval === 0;
                return (
                  <g key={`grid-day-${d}`}>
                    <line
                      x1={x}
                      y1={28}
                      x2={x}
                      y2={chartHeight - 10}
                      stroke={isMajor ? "rgba(59, 130, 246, 0.18)" : "rgba(59, 130, 246, 0.05)"}
                      strokeWidth={isMajor ? 1.2 : 1}
                      strokeDasharray={isMajor ? "none" : "2 2"}
                    />
                    {isMajor && (
                      <text x={x} y={18} fill="#94a3b8" textAnchor="middle" className="font-mono text-[10px] font-semibold">
                        Day {d}
                      </text>
                    )}
                  </g>
                );
              });
            })()}

            {/* Gantt Rows */}
            {(() => {
              const parseDate = (dStr: string) => {
                const parts = dStr.split('-');
                return new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]));
              };
              const projectStart = gantt[0] ? parseDate(gantt[0].start) : new Date();

              return gantt.map((task, idx) => {
                const y = 32 + idx * (taskHeight + gap);
                const taskStart = parseDate(task.start);
                const taskEnd = parseDate(task.end);

                const dayOffset = Math.round((taskStart.getTime() - projectStart.getTime()) / (1000 * 3600 * 24));
                const duration = Math.max(Math.round((taskEnd.getTime() - taskStart.getTime()) / (1000 * 3600 * 24)), 1);

                const xStart = paddingLeft + dayOffset * scale;
                const barWidth = Math.max(duration * scale, 30);

                // Full title or clean title
                const displayName = task.name.length > 38 ? `${task.name.substring(0, 36)}...` : task.name;

                return (
                  <g key={task.id} className="group">
                    {/* Row hover highlight background */}
                    <rect
                      x={8}
                      y={y - 4}
                      width={totalSvgWidth - 16}
                      height={taskHeight + 8}
                      rx={6}
                      fill="transparent"
                      className="group-hover:fill-slate-800/30 transition-colors"
                    />

                    {/* Phase tag circle badge */}
                    <rect
                      x={10}
                      y={y + 8}
                      width={22}
                      height={20}
                      rx={4}
                      fill="rgba(6, 182, 212, 0.15)"
                      stroke="rgba(6, 182, 212, 0.4)"
                    />
                    <text
                      x={21}
                      y={y + 22}
                      textAnchor="middle"
                      fill="#38bdf8"
                      className="font-mono text-[9px] font-bold"
                    >
                      P{idx + 1}
                    </text>

                    {/* Task Name Label - Spacious, uncompressed */}
                    <text
                      x={38}
                      y={y + taskHeight / 2 + 4}
                      fill="#e2e8f0"
                      className="font-semibold text-[11px] select-none group-hover:fill-cyan-300 transition-colors"
                    >
                      {displayName}
                    </text>
                    <title>{task.name} ({duration} days)</title>

                    {/* Task bar container background */}
                    <rect
                      x={xStart}
                      y={y}
                      width={barWidth}
                      height={taskHeight}
                      rx={6}
                      fill="rgba(30, 58, 138, 0.2)"
                      stroke="rgba(59, 130, 246, 0.35)"
                      strokeWidth={1}
                    />

                    {/* Task progress fill */}
                    <rect
                      x={xStart}
                      y={y}
                      width={barWidth * Math.max((task.progress || 25) / 100, 0.2)}
                      height={taskHeight}
                      rx={6}
                      fill="url(#gantt-gradient)"
                    />

                    {/* Duration badge inside bar */}
                    <text
                      x={xStart + barWidth - 8}
                      y={y + taskHeight / 2 + 4}
                      fill="rgba(255, 255, 255, 0.85)"
                      textAnchor="end"
                      className="font-mono text-[10px] font-bold pointer-events-none"
                    >
                      {duration}d
                    </text>

                    {/* Progress Text overlay on hover */}
                    <text
                      x={xStart + barWidth / 2}
                      y={y + taskHeight / 2 + 4}
                      fill="#ffffff"
                      textAnchor="middle"
                      className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 text-[10px] font-mono font-bold drop-shadow"
                    >
                      {task.progress > 0 ? `${task.progress}% Complete` : `${duration} Days`}
                    </text>

                    {/* Connection line dependency arrow */}
                    {task.dependencies && (
                      <path
                        d={`M ${xStart - 12} ${y - gap} L ${xStart - 12} ${y + taskHeight / 2} L ${xStart} ${y + taskHeight / 2}`}
                        fill="none"
                        stroke="#f59e0b"
                        strokeWidth={1.5}
                        strokeDasharray="3 3"
                        className="opacity-80"
                      />
                    )}
                  </g>
                );
              });
            })()}

            {/* Defs for gradients */}
            <defs>
              <linearGradient id="gantt-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#2563eb" />
                <stop offset="100%" stopColor="#06b6d4" />
              </linearGradient>
            </defs>
          </svg>
        </div>
      </div>

      {/* Roadmap List View */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {roadmap.map((phase) => (
          <div key={`phase-${phase.phase}`} className="glass-panel p-5 border border-blue-500/10 hover:border-blue-500/30 transition-all duration-300 relative overflow-hidden group">
            {/* Cyber corner highlight */}
            <div className="absolute top-0 right-0 w-8 h-8 bg-blue-500/10 rounded-bl-3xl flex items-center justify-center border-l border-b border-blue-500/20 group-hover:bg-blue-500/20 transition-all duration-300">
              <span className="text-[10px] font-bold text-blue-400 font-mono">P{phase.phase}</span>
            </div>
            
            <h4 className="text-sm font-bold text-slate-100 flex items-center gap-2 mb-2 pr-6">
              <span className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-900/40 border border-blue-500/30 flex items-center justify-center text-xs text-cyan-400 font-mono">
                {phase.phase}
              </span>
              {phase.title}
            </h4>
            
            <p className="text-xs text-slate-400 leading-relaxed mb-3">
              {phase.description}
            </p>
            
            <div className="border-t border-slate-800/60 pt-3 mt-1 flex flex-col gap-2">
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-slate-500">Target Duration:</span>
                <span className="font-semibold text-amber-400 font-mono flex items-center gap-1">
                  {phase.duration_days} Days
                </span>
              </div>
              <div className="flex items-start gap-1.5 text-[11px]">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 flex-shrink-0 mt-0.5" />
                <div>
                  <span className="text-slate-500 block">Phase Deliverable:</span>
                  <span className="text-emerald-400 font-medium">{phase.deliverable}</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
      <GoogleCalendarExportModal
        isOpen={isExportModalOpen}
        onClose={() => setIsExportModalOpen(false)}
        projectId={projectId || 1}
        projectName={projectName || "WorkflowGuide Project"}
        ganttTasks={gantt}
        apiBase={apiBase}
      />
    </div>
  );
}
