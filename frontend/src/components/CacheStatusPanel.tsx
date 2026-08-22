"use client";

import React, { useState } from "react";
import { Database, HardDrive, Cpu, RefreshCw, Trash2, ShieldCheck, Activity } from "lucide-react";

export interface CacheStatusMetrics {
  status: string;
  l1Entries: number;
  l2Entries: number;
  l2SizeBytes: number;
  hits: number;
  misses: number;
  hitRate: number;
  missRate: number;
  expired: number;
  invalidations: number;
}

interface CacheStatusPanelProps {
  metrics?: CacheStatusMetrics;
  onCleanExpired?: () => Promise<void>;
  onClearCache?: () => Promise<void>;
  onRefresh?: () => Promise<void>;
}

export const CacheStatusPanel: React.FC<CacheStatusPanelProps> = ({
  metrics = {
    status: "HEALTHY",
    l1Entries: 128,
    l2Entries: 642,
    l2SizeBytes: 3145728, // ~3 MB
    hits: 1840,
    misses: 260,
    hitRate: 87.6,
    missRate: 12.4,
    expired: 48,
    invalidations: 12,
  },
  onCleanExpired,
  onClearCache,
  onRefresh,
}) => {
  const [cleaning, setCleaning] = useState(false);
  const [clearing, setClearing] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  const handleClean = async () => {
    if (!onCleanExpired) return;
    setCleaning(true);
    try {
      await onCleanExpired();
    } finally {
      setCleaning(false);
    }
  };

  const handleClear = async () => {
    if (!onClearCache) return;
    setClearing(true);
    try {
      await onClearCache();
      setShowConfirm(false);
    } finally {
      setClearing(false);
    }
  };

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4 text-zinc-100">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Database className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-zinc-100">Knowledge & Retrieval Cache Layer</h3>
        </div>
        <div className="flex items-center gap-2">
          <span className="flex items-center gap-1.5 px-2.5 py-0.5 rounded text-xs font-mono bg-emerald-950 text-emerald-300 border border-emerald-800">
            <ShieldCheck className="w-3.5 h-3.5" />
            {metrics.status} (Non-Authoritative)
          </span>
          {onRefresh && (
            <button
              onClick={onRefresh}
              aria-label="Refresh cache metrics"
              className="p-1.5 text-zinc-400 hover:text-zinc-200 border border-zinc-800 rounded hover:bg-zinc-800 transition"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs font-mono">
        <div className="p-3 bg-zinc-950/60 border border-zinc-800/80 rounded-lg flex flex-col gap-1">
          <div className="flex items-center gap-1.5 text-zinc-400">
            <Cpu className="w-3.5 h-3.5 text-indigo-400" />
            <span>L1 Memory Cache</span>
          </div>
          <div className="text-lg font-bold text-zinc-100">{metrics.l1Entries} entries</div>
          <span className="text-[11px] text-zinc-500">In-Process LRU (max 2,000)</span>
        </div>

        <div className="p-3 bg-zinc-950/60 border border-zinc-800/80 rounded-lg flex flex-col gap-1">
          <div className="flex items-center gap-1.5 text-zinc-400">
            <HardDrive className="w-3.5 h-3.5 text-purple-400" />
            <span>L2 Persistent Disk</span>
          </div>
          <div className="text-lg font-bold text-zinc-100">{metrics.l2Entries} entries</div>
          <span className="text-[11px] text-zinc-500">
            {(metrics.l2SizeBytes / (1024 * 1024)).toFixed(2)} MB in .workline/cache
          </span>
        </div>

        <div className="p-3 bg-zinc-950/60 border border-zinc-800/80 rounded-lg flex flex-col gap-1">
          <div className="flex items-center gap-1.5 text-zinc-400">
            <Activity className="w-3.5 h-3.5 text-emerald-400" />
            <span>Hit Rate</span>
          </div>
          <div className="text-lg font-bold text-emerald-400">{metrics.hitRate.toFixed(1)}%</div>
          <span className="text-[11px] text-zinc-500">
            {metrics.hits} Hits / {metrics.misses} Misses
          </span>
        </div>

        <div className="p-3 bg-zinc-950/60 border border-zinc-800/80 rounded-lg flex flex-col gap-1">
          <div className="flex items-center gap-1.5 text-zinc-400">
            <RefreshCw className="w-3.5 h-3.5 text-amber-400" />
            <span>Invalidations</span>
          </div>
          <div className="text-lg font-bold text-amber-400">{metrics.invalidations}</div>
          <span className="text-[11px] text-zinc-500">{metrics.expired} Expired items pruned</span>
        </div>
      </div>

      <div className="flex items-center justify-between pt-2 border-t border-zinc-800">
        <p className="text-[11px] text-zinc-500">
          SurrealDB remains authoritative for all engineering decisions and requirements.
        </p>

        <div className="flex items-center gap-2">
          {onCleanExpired && (
            <button
              onClick={handleClean}
              disabled={cleaning}
              className="px-3 py-1.5 text-xs rounded bg-zinc-800 text-zinc-300 hover:bg-zinc-700 transition"
            >
              {cleaning ? "Cleaning..." : "Clean Expired"}
            </button>
          )}

          {onClearCache && (
            <button
              onClick={() => setShowConfirm(true)}
              className="px-3 py-1.5 text-xs rounded bg-rose-950 text-rose-300 hover:bg-rose-900 border border-rose-800 transition flex items-center gap-1"
            >
              <Trash2 className="w-3.5 h-3.5" />
              Flush Cache
            </button>
          )}
        </div>
      </div>

      {showConfirm && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50">
          <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6 max-w-md flex flex-col gap-3 shadow-xl">
            <h4 className="text-sm font-bold text-zinc-100">Flush Knowledge Cache?</h4>
            <p className="text-xs text-zinc-400">
              This will clear all non-authoritative L1 and L2 cache entries. SurrealDB state, Qdrant vectors, and Git history will NOT be affected.
            </p>
            <div className="flex items-center justify-end gap-2 mt-3">
              <button
                onClick={() => setShowConfirm(false)}
                className="px-3 py-1.5 text-xs text-zinc-400 hover:text-zinc-200 transition"
              >
                Cancel
              </button>
              <button
                onClick={handleClear}
                disabled={clearing}
                className="px-4 py-1.5 text-xs font-semibold bg-rose-600 hover:bg-rose-500 text-white rounded transition"
              >
                {clearing ? "Flushing..." : "Confirm Flush"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
