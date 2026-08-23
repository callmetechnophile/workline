'use client';

import React from 'react';
import { Share2, Download, RefreshCw, Layers, Zap, CheckCircle2, Clock, Calendar } from 'lucide-react';
import EngineeringStatusBadge, { EngineeringStatus } from '../EngineeringStatusBadge';

interface ProjectHeaderProps {
  projectName: string;
  category?: string;
  teamName?: string;
  userRole?: string;
  status?: EngineeringStatus;
  targetDays?: number;
  lastUpdated?: string;
  onRefresh?: () => void;
  onExport?: () => void;
  onSave?: () => void;
  isSaving?: boolean;
}

export default function ProjectHeader({
  projectName,
  category = 'Hardware Systems Engineering',
  teamName = 'Engineering Core Team',
  userRole = 'MEMBER',
  status = 'PASS',
  targetDays = 30,
  lastUpdated = 'Just now',
  onRefresh,
  onExport,
  onSave,
  isSaving = false,
}: ProjectHeaderProps) {
  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-lg p-5 mb-6 backdrop-blur-sm">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Title & Metadata */}
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[11px] font-mono font-bold tracking-wider text-indigo-400 uppercase">
              {category}
            </span>
            <span className="text-slate-600">•</span>
            <span className="text-[11px] text-slate-400 font-mono">ID: PROJ-{projectName.slice(0, 4).toUpperCase()}</span>
            {teamName && (
              <>
                <span className="text-slate-600">•</span>
                <span className="text-[11px] font-mono text-cyan-400 bg-cyan-950/40 border border-cyan-800/40 px-2 py-0.5 rounded">
                  TEAM: {teamName}
                </span>
                <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-zinc-800 text-slate-300">
                  {userRole}
                </span>
              </>
            )}
          </div>
          <h1 className="text-xl font-bold text-slate-100 tracking-tight">
            {projectName}
          </h1>
        </div>

        {/* Project KPI Indicators */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Engineering Status */}
          <div className="flex items-center gap-2 bg-slate-950/60 px-3 py-1.5 rounded-md border border-slate-800">
            <span className="text-[10px] font-mono text-slate-500 uppercase">Status:</span>
            <EngineeringStatusBadge status={status} size="sm" />
          </div>

          {/* Target Timeline */}
          <div className="flex items-center gap-2 bg-slate-950/60 px-3 py-1.5 rounded-md border border-slate-800 text-xs font-mono text-slate-300">
            <Calendar className="w-3.5 h-3.5 text-slate-500" />
            <span>Target: <strong>{targetDays} Days</strong></span>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2">
            {onSave && (
              <button
                onClick={onSave}
                disabled={isSaving}
                className="px-3 py-1.5 rounded-md bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-semibold shadow-sm transition-all cursor-pointer flex items-center gap-1.5"
              >
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>{isSaving ? 'Saving...' : 'Save Spec'}</span>
              </button>
            )}

            {onExport && (
              <button
                onClick={onExport}
                className="px-3 py-1.5 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition-all cursor-pointer flex items-center gap-1.5"
                title="Export Engineering Package"
              >
                <Download className="w-3.5 h-3.5 text-slate-400" />
                <span>Export</span>
              </button>
            )}

            {onRefresh && (
              <button
                onClick={onRefresh}
                className="p-1.5 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 border border-slate-700 transition-all cursor-pointer"
                title="Re-run Engineering Analysis"
              >
                <RefreshCw className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
