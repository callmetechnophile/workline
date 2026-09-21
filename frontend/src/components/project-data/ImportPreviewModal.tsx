'use client';

import React, { useState } from 'react';
import { ImportPreviewStats, ImportResolutionStrategy } from '@/lib/workline-filesystem/types';
import {
  X,
  Package,
  Layers,
  CheckSquare,
  BookOpen,
  FileText,
  ListTodo,
  GitCommit,
  AlertTriangle,
  ArrowRight,
  ShieldCheck,
} from 'lucide-react';

interface ImportPreviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  stats: ImportPreviewStats;
  warnings?: string[];
  onConfirmImport: (strategy: ImportResolutionStrategy) => void;
}

export default function ImportPreviewModal({
  isOpen,
  onClose,
  stats,
  warnings = [],
  onConfirmImport,
}: ImportPreviewModalProps) {
  const [strategy, setStrategy] = useState<ImportResolutionStrategy>('MERGE');

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-xl shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950/80">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-emerald-950/80 border border-emerald-700/50 rounded-lg text-emerald-400">
              <Package className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-100">
                Import WORKLINE Project
              </h3>
              <p className="text-xs text-slate-400 font-mono">
                Verified .wl Filesystem Architecture
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-100 hover:bg-slate-800 rounded-lg transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-6 overflow-y-auto max-h-[70vh]">
          {/* Project Header Info */}
          <div className="p-4 bg-slate-950/70 border border-slate-800 rounded-lg space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono text-slate-400">PROJECT IDENTITY</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-indigo-950 text-indigo-300 border border-indigo-800">
                Schema {stats.schemaVersion}
              </span>
            </div>
            <div className="text-lg font-bold text-slate-100">{stats.projectName}</div>
            <div className="flex flex-wrap items-center gap-4 text-xs font-mono text-slate-400 pt-1">
              <span>ID: <span className="text-slate-200">{stats.projectId}</span></span>
              <span>Version: <span className="text-indigo-400">{stats.version}</span></span>
              <span>Exported: <span className="text-slate-300">{new Date(stats.generatedAt).toLocaleDateString()}</span></span>
            </div>
          </div>

          {/* Warnings if any */}
          {warnings.length > 0 && (
            <div className="p-3 bg-amber-950/30 border border-amber-600/40 rounded-lg space-y-1">
              <div className="flex items-center gap-2 text-xs font-bold text-amber-400">
                <AlertTriangle className="w-4 h-4" />
                <span>Notice</span>
              </div>
              {warnings.map((w, idx) => (
                <p key={idx} className="text-xs text-amber-300/80 pl-6">
                  {w}
                </p>
              ))}
            </div>
          )}

          {/* Resource Stat Grid */}
          <div className="space-y-2">
            <div className="text-xs font-mono font-semibold text-slate-400 uppercase tracking-wider">
              Discovered Engineering Resources
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg space-y-1">
                <div className="flex items-center gap-2 text-indigo-400 text-xs font-mono">
                  <CheckSquare className="w-3.5 h-3.5" />
                  <span>Requirements</span>
                </div>
                <div className="text-xl font-bold font-mono text-slate-100">{stats.requirementsCount}</div>
              </div>

              <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg space-y-1">
                <div className="flex items-center gap-2 text-indigo-400 text-xs font-mono">
                  <Layers className="w-3.5 h-3.5" />
                  <span>Components</span>
                </div>
                <div className="text-xl font-bold font-mono text-slate-100">{stats.componentsCount}</div>
              </div>

              <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg space-y-1">
                <div className="flex items-center gap-2 text-indigo-400 text-xs font-mono">
                  <BookOpen className="w-3.5 h-3.5" />
                  <span>Research Papers</span>
                </div>
                <div className="text-xl font-bold font-mono text-slate-100">{stats.researchPapersCount}</div>
              </div>

              <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg space-y-1">
                <div className="flex items-center gap-2 text-indigo-400 text-xs font-mono">
                  <FileText className="w-3.5 h-3.5" />
                  <span>Documents</span>
                </div>
                <div className="text-xl font-bold font-mono text-slate-100">{stats.documentsCount}</div>
              </div>

              <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg space-y-1">
                <div className="flex items-center gap-2 text-indigo-400 text-xs font-mono">
                  <Layers className="w-3.5 h-3.5" />
                  <span>BOM Line Items</span>
                </div>
                <div className="text-xl font-bold font-mono text-slate-100">{stats.bomItemsCount}</div>
              </div>

              <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg space-y-1">
                <div className="flex items-center gap-2 text-indigo-400 text-xs font-mono">
                  <ListTodo className="w-3.5 h-3.5" />
                  <span>Tasks</span>
                </div>
                <div className="text-xl font-bold font-mono text-slate-100">{stats.tasksCount}</div>
              </div>

              <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg space-y-1">
                <div className="flex items-center gap-2 text-indigo-400 text-xs font-mono">
                  <GitCommit className="w-3.5 h-3.5" />
                  <span>Decisions (ADR)</span>
                </div>
                <div className="text-xl font-bold font-mono text-slate-100">{stats.decisionsCount}</div>
              </div>

              <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg space-y-1">
                <div className="flex items-center gap-2 text-indigo-400 text-xs font-mono">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  <span>Agents / Scope</span>
                </div>
                <div className="text-xl font-bold font-mono text-slate-100">{stats.agentsCount}</div>
              </div>
            </div>
          </div>

          {/* Import Collision & Merge Strategy */}
          <div className="space-y-3">
            <div className="text-xs font-mono font-semibold text-slate-400 uppercase tracking-wider">
              Project Restoration Strategy
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <button
                type="button"
                onClick={() => setStrategy('MERGE')}
                className={`p-3.5 rounded-lg border text-left transition-all cursor-pointer ${
                  strategy === 'MERGE'
                    ? 'bg-indigo-950/60 border-indigo-500 text-slate-100 shadow-md ring-1 ring-indigo-500/50'
                    : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="font-semibold text-xs text-indigo-300 mb-1">Merge (Recommended)</div>
                <div className="text-[11px] text-slate-400 leading-tight">
                  Blends new requirements and components while preserving existing project state.
                </div>
              </button>

              <button
                type="button"
                onClick={() => setStrategy('CREATE_NEW')}
                className={`p-3.5 rounded-lg border text-left transition-all cursor-pointer ${
                  strategy === 'CREATE_NEW'
                    ? 'bg-indigo-950/60 border-indigo-500 text-slate-100 shadow-md ring-1 ring-indigo-500/50'
                    : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="font-semibold text-xs text-indigo-300 mb-1">Create New Project</div>
                <div className="text-[11px] text-slate-400 leading-tight">
                  Initializes as a separate workspace copy without modifying the current project.
                </div>
              </button>

              <button
                type="button"
                onClick={() => setStrategy('REPLACE')}
                className={`p-3.5 rounded-lg border text-left transition-all cursor-pointer ${
                  strategy === 'REPLACE'
                    ? 'bg-rose-950/40 border-rose-500 text-slate-100 shadow-md ring-1 ring-rose-500/50'
                    : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="font-semibold text-xs text-rose-400 mb-1">Replace Project</div>
                <div className="text-[11px] text-slate-400 leading-tight">
                  Completely overwrites current project memory with this imported package.
                </div>
              </button>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-6 py-4 border-t border-slate-800 bg-slate-950/80">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-semibold cursor-pointer transition-colors"
          >
            Cancel
          </button>

          <button
            onClick={() => onConfirmImport(strategy)}
            className="flex items-center gap-2 px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold shadow-lg shadow-indigo-600/20 cursor-pointer transition-all"
          >
            <span>Confirm & Import Project</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
