'use client';

import React from 'react';
import { MessageSquare, Clock, ArrowRight, FolderKanban, Trash2 } from 'lucide-react';

interface ConversationsWorkspaceProps {
  savedHistory: any[];
  onLoadHistory: (item: any) => void;
  onOpenNewProject: () => void;
}

export default function ConversationsWorkspace({
  savedHistory = [],
  onLoadHistory,
  onOpenNewProject,
}: ConversationsWorkspaceProps) {
  if (!savedHistory || savedHistory.length === 0) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-12 text-center max-w-xl mx-auto my-12 space-y-4">
        <div className="w-10 h-10 rounded-full bg-slate-800 text-slate-400 flex items-center justify-center mx-auto">
          <MessageSquare className="w-5 h-5" />
        </div>
        <div className="space-y-1">
          <h3 className="text-sm font-bold text-slate-200">No Engineering Sessions Saved</h3>
          <p className="text-xs text-slate-400">
            Initialize an engineering project to generate spec packages and conversational trace logs.
          </p>
        </div>
        <button
          onClick={onOpenNewProject}
          className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-md text-xs font-semibold shadow transition-all cursor-pointer inline-flex items-center gap-1.5"
        >
          <span>New Engineering Session</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-base font-bold text-slate-100">Engineering Session History</h2>
        <p className="text-xs text-slate-400">
          Saved project specifications, design traces, and optimization records linked to your profile.
        </p>
      </div>

      <div className="space-y-3">
        {savedHistory.map((item, idx) => (
          <div
            key={idx}
            className="bg-slate-900/80 hover:bg-slate-850 border border-slate-800 hover:border-slate-700 rounded-lg p-4 flex items-center justify-between transition-all"
          >
            <div className="space-y-1 max-w-2xl">
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-950/80 text-indigo-300 border border-indigo-800/40">
                  PROJECT SPEC
                </span>
                <span className="text-[11px] text-slate-500 font-mono flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  <span>{item.created_at ? new Date(item.created_at).toLocaleDateString() : 'Recent'}</span>
                </span>
              </div>
              <h3 className="text-xs font-bold text-slate-200 truncate">
                {item.intent || 'Unnamed Engineering Project'}
              </h3>
              <div className="flex items-center gap-4 text-[11px] font-mono text-slate-400 pt-1">
                <span>Readiness: <strong className="text-emerald-400">{item.readiness_score != null ? `${item.readiness_score}%` : '—'}</strong></span>
                <span>Risk: <strong className="text-amber-400">{item.risk_score != null ? `${item.risk_score}%` : '—'}</strong></span>
                <span>Optimization: <strong className="text-cyan-400">{item.optimization_score != null ? `${item.optimization_score}%` : '—'}</strong></span>
              </div>
            </div>

            <button
              onClick={() => onLoadHistory(item)}
              className="px-3.5 py-1.5 bg-slate-800 hover:bg-indigo-600 text-slate-200 hover:text-white rounded-md text-xs font-medium transition-all flex items-center gap-1.5 cursor-pointer flex-shrink-0"
            >
              <span>Load Workspace</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
