'use client';

import React from 'react';
import { ProjectDiffSummary, CloudProviderState } from '@/lib/workline-filesystem/types';
import {
  X,
  GitCompare,
  ArrowUpRight,
  ArrowDownLeft,
  PlusCircle,
  Edit3,
  MinusCircle,
  ShieldCheck,
  CheckCircle2,
} from 'lucide-react';

interface DiffSyncModalProps {
  isOpen: boolean;
  onClose: () => void;
  provider: CloudProviderState;
  diff: ProjectDiffSummary;
  onSyncLocalToRemote: () => void;
  onPullRemoteToLocal: () => void;
  isSyncing?: boolean;
}

export default function DiffSyncModal({
  isOpen,
  onClose,
  provider,
  diff,
  onSyncLocalToRemote,
  onPullRemoteToLocal,
  isSyncing = false,
}: DiffSyncModalProps) {
  if (!isOpen) return null;

  const renderBadge = (type: 'ADDED' | 'MODIFIED' | 'REMOVED') => {
    switch (type) {
      case 'ADDED':
        return (
          <span className="flex items-center gap-1 text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-950/80 text-emerald-400 border border-emerald-800/50">
            <PlusCircle className="w-3 h-3" />
            <span>+ ADDED</span>
          </span>
        );
      case 'MODIFIED':
        return (
          <span className="flex items-center gap-1 text-[10px] font-mono px-1.5 py-0.5 rounded bg-amber-950/80 text-amber-400 border border-amber-800/50">
            <Edit3 className="w-3 h-3" />
            <span>~ MODIFIED</span>
          </span>
        );
      case 'REMOVED':
        return (
          <span className="flex items-center gap-1 text-[10px] font-mono px-1.5 py-0.5 rounded bg-rose-950/80 text-rose-400 border border-rose-800/50">
            <MinusCircle className="w-3 h-3" />
            <span>- REMOVED</span>
          </span>
        );
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="w-full max-w-3xl bg-slate-900 border border-slate-800 rounded-xl shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950/80">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-indigo-950/80 border border-indigo-700/50 rounded-lg text-indigo-400">
              <GitCompare className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-100">
                Synchronization & Diff Preview
              </h3>
              <p className="text-xs text-slate-400 font-mono">
                {provider.name} • {provider.target || provider.account}
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
          {/* Commit Message info */}
          <div className="p-3 bg-slate-950/80 border border-slate-800 rounded-lg flex items-center justify-between text-xs font-mono">
            <span className="text-slate-400">Commit Message:</span>
            <span className="text-indigo-300 font-semibold">
              WORKLINE: sync project {provider.localVersion || 'v1.0'}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Local Changes Column */}
            <div className="p-4 bg-slate-950/60 border border-slate-800 rounded-lg space-y-3">
              <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                <span className="text-xs font-mono font-bold text-indigo-400 uppercase tracking-wider">
                  Local Changes (Outgoing)
                </span>
                <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                  {diff.localChanges.length} items
                </span>
              </div>

              {diff.localChanges.length === 0 ? (
                <div className="p-6 text-center space-y-1 text-slate-500 text-xs font-mono">
                  <CheckCircle2 className="w-5 h-5 mx-auto text-emerald-500/70" />
                  <p>Up to date with remote</p>
                </div>
              ) : (
                <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
                  {diff.localChanges.map((item) => (
                    <div key={item.id} className="p-2.5 bg-slate-900 border border-slate-800/80 rounded space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-semibold text-slate-200">{item.name}</span>
                        {renderBadge(item.type)}
                      </div>
                      <p className="text-[11px] text-slate-400 leading-tight">{item.details}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Remote Changes Column */}
            <div className="p-4 bg-slate-950/60 border border-slate-800 rounded-lg space-y-3">
              <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                <span className="text-xs font-mono font-bold text-emerald-400 uppercase tracking-wider">
                  Remote Changes (Incoming)
                </span>
                <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                  {diff.remoteChanges.length} items
                </span>
              </div>

              {diff.remoteChanges.length === 0 ? (
                <div className="p-6 text-center space-y-1 text-slate-500 text-xs font-mono">
                  <CheckCircle2 className="w-5 h-5 mx-auto text-emerald-500/70" />
                  <p>No new remote commits</p>
                </div>
              ) : (
                <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
                  {diff.remoteChanges.map((item) => (
                    <div key={item.id} className="p-2.5 bg-slate-900 border border-slate-800/80 rounded space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-semibold text-slate-200">{item.name}</span>
                        {renderBadge(item.type)}
                      </div>
                      <p className="text-[11px] text-slate-400 leading-tight">{item.details}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="p-3 bg-slate-950/40 border border-slate-800 rounded-lg flex items-center gap-3 text-xs text-slate-400">
            <ShieldCheck className="w-4 h-4 text-indigo-400 flex-shrink-0" />
            <span>
              Security check: Zero credentials or private tokens will be pushed to {provider.name}. All sensitive configurations sanitized to <code className="text-indigo-300">credentials: NOT_EXPORTED</code>.
            </span>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-between px-6 py-4 border-t border-slate-800 bg-slate-950/80">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-semibold cursor-pointer transition-colors"
          >
            Cancel
          </button>

          <div className="flex items-center gap-3">
            <button
              onClick={onPullRemoteToLocal}
              disabled={isSyncing || diff.remoteChanges.length === 0}
              className="flex items-center gap-1.5 px-4 py-2 bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-200 rounded-lg text-xs font-semibold cursor-pointer transition-colors"
            >
              <ArrowDownLeft className="w-4 h-4" />
              <span>Pull Remote → Local</span>
            </button>

            <button
              onClick={onSyncLocalToRemote}
              disabled={isSyncing}
              className="flex items-center gap-1.5 px-5 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-lg text-xs font-semibold shadow-lg shadow-indigo-600/20 cursor-pointer transition-all"
            >
              <ArrowUpRight className="w-4 h-4" />
              <span>Sync Local → Remote</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
