'use client';

import React, { useState, useEffect } from 'react';
import {
  Database, Folder, Trash2, Copy, History, Download,
  RefreshCw, Package, ShieldCheck, HardDrive, Layers,
  CheckCircle, AlertCircle, Loader, ChevronRight, Archive, FileLock2
} from 'lucide-react';

interface BundleMeta {
  id: number;
  name: string;
  description: string;
  checksum: string;
  bundle_size: number;
  field_count: number;
  version: number;
  saved_at: string;
}

interface WorkspaceDashboardProps {
  activeProjectName: string;
  currentData: any;
  onLoadProject: (data: any) => void;
  onSaveTrigger: (name: string) => Promise<void>;
  apiBase: string;
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

function formatDate(iso: string): string {
  try { return new Date(iso).toLocaleString(); } catch { return iso; }
}

export default function WorkspaceDashboard({
  activeProjectName,
  currentData,
  onLoadProject,
  apiBase
}: WorkspaceDashboardProps) {
  const [bundles, setBundles]               = useState<BundleMeta[]>([]);
  const [selectedBundle, setSelectedBundle] = useState<BundleMeta | null>(null);
  const [saveName, setSaveName]             = useState('');
  const [saveDesc, setSaveDesc]             = useState('');
  const [isLoading, setIsLoading]           = useState(false);
  const [isSaving, setIsSaving]             = useState(false);
  const [msg, setMsg]                       = useState<{ text: string; ok: boolean } | null>(null);

  const base = apiBase || 'https://workline-core-gateway.onrender.com';

  const showMsg = (text: string, ok: boolean) => {
    setMsg({ text, ok });
    setTimeout(() => setMsg(null), 4000);
  };

  // ── Fetch bundle list ──────────────────────────────────────────────────────
  const fetchBundles = async () => {
    setIsLoading(true);
    try {
      const res = await fetch(`${base}/api/workspace/bundles`);
      if (res.ok) setBundles(await res.json());
    } catch { showMsg('Failed to load bundles from database.', false); }
    finally { setIsLoading(false); }
  };

  useEffect(() => {
    fetchBundles();
    if (activeProjectName) setSaveName(activeProjectName);
  }, [activeProjectName]);

  // ── Save bundle ────────────────────────────────────────────────────────────
  const handleSaveBundle = async () => {
    if (!saveName.trim() || !currentData) return;
    setIsSaving(true);
    setMsg(null);
    try {
      const res = await fetch(`${base}/api/workspace/save-bundle`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name:          saveName.trim(),
          description:   saveDesc.trim() || `Saved on ${new Date().toLocaleDateString()}`,
          pipeline_data: currentData
        })
      });

      if (res.ok) {
        const data = await res.json();
        showMsg(
          `✓ Bundle saved — v${data.version} · ${formatBytes(data.bundle_size)} · ${data.field_count} fields · checksum ${data.checksum}`,
          true
        );
        fetchBundles();
        setSelectedBundle(null);
      } else {
        const err = await res.json().catch(() => ({}));
        showMsg(`Save failed: ${err.detail || res.statusText}`, false);
      }
    } catch (e: any) {
      showMsg(`Network error: ${e.message}`, false);
    } finally {
      setIsSaving(false);
    }
  };

  // ── Load bundle ────────────────────────────────────────────────────────────
  const handleLoadBundle = async (id: number) => {
    setIsLoading(true);
    try {
      const res = await fetch(`${base}/api/workspace/bundle/${id}`);
      if (res.ok) {
        const data = await res.json();
        onLoadProject(data.pipeline);
        showMsg(`Loaded bundle "${data.name}" v${data.version}`, true);
      } else {
        showMsg('Failed to load bundle.', false);
      }
    } catch { showMsg('Network error loading bundle.', false); }
    finally { setIsLoading(false); }
  };

  // ── Delete bundle ──────────────────────────────────────────────────────────
  const handleDeleteBundle = async (id: number, name: string) => {
    if (!confirm(`Delete bundle "${name}"?`)) return;
    try {
      const res = await fetch(`${base}/api/workspace/bundle/${id}`, { method: 'DELETE' });
      if (res.ok) {
        showMsg('Bundle deleted.', true);
        if (selectedBundle?.id === id) setSelectedBundle(null);
        fetchBundles();
      }
    } catch { showMsg('Delete failed.', false); }
  };

  // Group bundles by name (latest version shown in list, all versions in detail)
  const uniqueNames = Array.from(new Set(bundles.map(b => b.name)));
  const latestByName: Record<string, BundleMeta> = {};
  bundles.forEach(b => {
    if (!latestByName[b.name] || b.version > latestByName[b.name].version) {
      latestByName[b.name] = b;
    }
  });
  const versionsBySelected = selectedBundle
    ? bundles.filter(b => b.name === selectedBundle.name).sort((a, b) => b.version - a.version)
    : [];

  return (
    <div className="space-y-6 font-mono">

      {/* Toast message */}
      {msg && (
        <div className={`flex items-start gap-2 p-3 rounded border text-xs transition-all ${
          msg.ok
            ? 'border-emerald-500/30 bg-emerald-950/20 text-emerald-300'
            : 'border-red-500/30 bg-red-950/20 text-red-300'
        }`}>
          {msg.ok
            ? <CheckCircle className="w-3.5 h-3.5 mt-0.5 shrink-0 text-emerald-400" />
            : <AlertCircle className="w-3.5 h-3.5 mt-0.5 shrink-0 text-red-400" />}
          <span className="leading-normal">{msg.text}</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* ── LEFT: Save panel + bundle list ── */}
        <div className="lg:col-span-1 space-y-5">

          {/* Save Workspace Bundle */}
          <div className="glass-panel p-5 border border-cyan-500/20 bg-zinc-950/40 space-y-4">
            <h3 className="text-xs font-bold text-cyan-400 uppercase tracking-wider flex items-center gap-1.5">
              <Archive className="w-4 h-4" />
              Save Workspace Bundle
            </h3>
            <p className="text-[10px] text-slate-400 leading-relaxed">
              Saves the full pipeline — BOM, power, schematics, papers, Gantt, code, audit trail — as a single gzip-compressed bundle in SQLite.
            </p>

            <div className="space-y-2">
              <input
                type="text"
                value={saveName}
                onChange={e => setSaveName(e.target.value)}
                placeholder="Bundle name…"
                className="w-full bg-slate-950 border border-slate-800 text-xs px-3 py-2 rounded text-slate-200 outline-none focus:border-cyan-700 transition-colors"
              />
              <input
                type="text"
                value={saveDesc}
                onChange={e => setSaveDesc(e.target.value)}
                placeholder="Description (optional)"
                className="w-full bg-slate-950 border border-slate-800 text-xs px-3 py-2 rounded text-slate-400 outline-none focus:border-slate-600 transition-colors"
              />
            </div>

            {/* Bundle contents preview */}
            {currentData && (
              <div className="bg-slate-900/60 border border-slate-800 rounded p-3 space-y-1.5">
                <div className="text-[9px] text-slate-500 uppercase tracking-widest mb-2">Bundle will include</div>
                {[
                  ['Components (BOM)',   currentData.components?.length ?? 0,       'items'],
                  ['Research Papers',    currentData.research_papers?.length ?? 0,   'papers'],
                  ['Gantt Tasks',        currentData.gantt?.length ?? 0,             'tasks'],
                  ['Roadmap Phases',     currentData.roadmap?.length ?? 0,           'phases'],
                  ['Audit Trail Entries',currentData.audit_trail?.length ?? 0,       'logs'],
                  ['Agents Delegated',   currentData.decision_trace?.length ?? 0,    'agents'],
                ].map(([label, count, unit]) => (
                  <div key={label as string} className="flex justify-between text-[10px]">
                    <span className="text-slate-400">{label}</span>
                    <span className={`font-bold ${Number(count) > 0 ? 'text-cyan-400' : 'text-slate-600'}`}>
                      {count} {unit}
                    </span>
                  </div>
                ))}
              </div>
            )}

            <button
              onClick={handleSaveBundle}
              disabled={isSaving || !saveName.trim() || !currentData}
              className="w-full flex items-center justify-center gap-2 bg-cyan-950 hover:bg-cyan-900 border border-cyan-700 text-cyan-300 py-2.5 rounded text-xs font-bold tracking-wider uppercase transition-all cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {isSaving
                ? <><Loader className="w-3.5 h-3.5 animate-spin" /> Compressing & Saving…</>
                : <><Database className="w-3.5 h-3.5" /> Save the Idea</>}
            </button>
          </div>

          {/* Saved Bundles List */}
          <div className="glass-panel p-5 border border-blue-500/20 bg-zinc-950/40 space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-xs font-bold text-cyan-400 uppercase tracking-wider flex items-center gap-1.5">
                <Folder className="w-4 h-4" />
                Saved Bundles
              </h3>
              <button onClick={fetchBundles} className="text-slate-500 hover:text-slate-200 cursor-pointer transition-colors">
                <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
              </button>
            </div>

            {uniqueNames.length === 0 ? (
              <div className="text-center py-8 border border-slate-900 border-dashed rounded text-[10px] text-slate-600 italic">
                No bundles saved yet.
              </div>
            ) : (
              <div className="space-y-2 max-h-[280px] overflow-y-auto pr-1">
                {uniqueNames.map(name => {
                  const latest = latestByName[name];
                  const isSelected = selectedBundle?.name === name;
                  return (
                    <div
                      key={name}
                      onClick={() => setSelectedBundle(latest)}
                      className={`p-3 rounded border cursor-pointer transition-all ${
                        isSelected
                          ? 'bg-cyan-950/20 border-cyan-500/40'
                          : 'bg-slate-900/10 border-slate-900 hover:border-slate-700'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className={`text-xs font-bold truncate ${isSelected ? 'text-cyan-300' : 'text-slate-200'}`}>
                          {name}
                        </span>
                        <ChevronRight className={`w-3.5 h-3.5 shrink-0 ${isSelected ? 'text-cyan-400' : 'text-slate-600'}`} />
                      </div>
                      <div className="flex gap-3 mt-1.5 text-[9px] text-slate-500">
                        <span>v{latest.version}</span>
                        <span>{formatBytes(latest.bundle_size)}</span>
                        <span>{latest.field_count} fields</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* ── RIGHT: Bundle detail + versions ── */}
        <div className="lg:col-span-2">
          <div className="glass-panel p-6 border border-blue-500/20 bg-zinc-950/40 h-full space-y-5">
            <h3 className="text-xs font-bold text-cyan-400 uppercase tracking-wider flex items-center gap-1.5">
              <Package className="w-4 h-4" />
              Bundle Version History
              {selectedBundle && <span className="text-slate-500 font-normal ml-1">[{selectedBundle.name}]</span>}
            </h3>

            {!selectedBundle ? (
              <div className="flex flex-col items-center justify-center h-[320px] border border-slate-900 border-dashed rounded text-xs text-slate-500 italic gap-2">
                <FileLock2 className="w-8 h-8 text-slate-700 stroke-1" />
                Select a bundle on the left to inspect its version history.
              </div>
            ) : (
              <div className="space-y-3 overflow-y-auto max-h-[420px] pr-1">
                {versionsBySelected.map(bundle => (
                  <div
                    key={bundle.id}
                    className="p-4 bg-slate-900/20 border border-slate-800 hover:border-slate-700 rounded-lg transition-all"
                  >
                    {/* Header row */}
                    <div className="flex items-start justify-between gap-4">
                      <div className="space-y-2 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-xs bg-slate-950 border border-slate-800 text-cyan-400 px-2 py-0.5 rounded font-bold">
                            v{bundle.version}
                          </span>
                          <span className="text-[10px] text-slate-500">{formatDate(bundle.saved_at)}</span>
                        </div>

                        {bundle.description && (
                          <p className="text-[10px] text-slate-300 italic">"{bundle.description}"</p>
                        )}

                        {/* Bundle stats grid */}
                        <div className="grid grid-cols-3 gap-2 mt-2">
                          {[
                            { icon: HardDrive,   label: 'Compressed Size', value: formatBytes(bundle.bundle_size) },
                            { icon: Layers,       label: 'Fields',          value: `${bundle.field_count} fields` },
                            { icon: ShieldCheck,  label: 'SHA-256',         value: bundle.checksum },
                          ].map(({ icon: Icon, label, value }) => (
                            <div key={label} className="bg-slate-950/60 border border-slate-900 rounded p-2 space-y-0.5">
                              <div className="flex items-center gap-1 text-[9px] text-slate-500 uppercase tracking-wider">
                                <Icon className="w-3 h-3" />
                                {label}
                              </div>
                              <div className="text-[10px] text-slate-200 font-bold font-mono truncate">{value}</div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex flex-col gap-2 shrink-0">
                        <button
                          onClick={() => handleLoadBundle(bundle.id)}
                          className="flex items-center gap-1.5 text-[10px] bg-cyan-950/50 border border-cyan-800 hover:bg-cyan-900/50 px-3 py-1.5 rounded text-cyan-400 font-bold transition-all cursor-pointer"
                        >
                          <Download className="w-3 h-3" />
                          Restore
                        </button>
                        <button
                          onClick={() => handleDeleteBundle(bundle.id, bundle.name)}
                          className="flex items-center gap-1.5 text-[10px] border border-red-900/50 bg-red-950/10 hover:bg-red-900/20 px-3 py-1.5 rounded text-red-400 cursor-pointer transition-all"
                        >
                          <Trash2 className="w-3 h-3" />
                          Delete
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
