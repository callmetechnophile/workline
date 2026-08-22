import React, { useState } from 'react';

interface ProjectExportPanelProps {
  projectId: string;
  projectName: string;
  projectVersion: string;
  onExportComplete?: (manifest: any) => void;
}

export const ProjectExportPanel: React.FC<ProjectExportPanelProps> = ({
  projectId,
  projectName,
  projectVersion,
  onExportComplete,
}) => {
  const [includeArtifacts, setIncludeArtifacts] = useState<boolean>(false);
  const [includeVectors, setIncludeVectors] = useState<boolean>(false);
  const [includeGitHistory, setIncludeGitHistory] = useState<boolean>(false);
  const [force, setForce] = useState<boolean>(false);
  const [isExporting, setIsExporting] = useState<boolean>(false);
  const [exportResult, setExportResult] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleExport = async () => {
    setIsExporting(true);
    setError(null);
    try {
      const response = await fetch('/api/project/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: projectId,
          include_artifacts: includeArtifacts,
          include_vectors: includeVectors,
          include_git_history: includeGitHistory,
          force,
        }),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Export failed');
      }

      const manifest = await response.json();
      setExportResult(manifest);
      if (onExportComplete) onExportComplete(manifest);
    } catch (err: any) {
      setError(err.message || 'Export failed');
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl text-slate-100 max-w-2xl mx-auto">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-6">
        <div>
          <h2 className="text-xl font-bold text-cyan-400">Export Workline Package (.wlipjt)</h2>
          <p className="text-xs text-slate-400 mt-1">
            Package <span className="text-white font-medium">{projectName}</span> (v{projectVersion}) into a portable archive.
          </p>
        </div>
        <span className="px-3 py-1 bg-cyan-950 text-cyan-400 border border-cyan-800 rounded-full text-xs font-mono">
          FORMAT v1
        </span>
      </div>

      <div className="space-y-4 mb-6">
        <label className="flex items-center justify-between p-3 bg-slate-800/60 rounded-lg border border-slate-700/50 cursor-pointer hover:bg-slate-800 transition">
          <div>
            <div className="font-semibold text-sm">Include Large Artifact Payloads</div>
            <div className="text-xs text-slate-400">Embed simulation models, trained PINN weights, and binary artifacts</div>
          </div>
          <input
            type="checkbox"
            checked={includeArtifacts}
            onChange={(e) => setIncludeArtifacts(e.target.checked)}
            className="w-5 h-5 accent-cyan-500 rounded cursor-pointer"
          />
        </label>

        <label className="flex items-center justify-between p-3 bg-slate-800/60 rounded-lg border border-slate-700/50 cursor-pointer hover:bg-slate-800 transition">
          <div>
            <div className="font-semibold text-sm">Include Vector Embeddings</div>
            <div className="text-xs text-slate-400">Embed dense Qdrant vector arrays (default: metadata and hashes only)</div>
          </div>
          <input
            type="checkbox"
            checked={includeVectors}
            onChange={(e) => setIncludeVectors(e.target.checked)}
            className="w-5 h-5 accent-cyan-500 rounded cursor-pointer"
          />
        </label>

        <label className="flex items-center justify-between p-3 bg-slate-800/60 rounded-lg border border-slate-700/50 cursor-pointer hover:bg-slate-800 transition">
          <div>
            <div className="font-semibold text-sm">Include Full Git History Bundle</div>
            <div className="text-xs text-slate-400">Embed commit objects (default: version, commit SHA, branch metadata only)</div>
          </div>
          <input
            type="checkbox"
            checked={includeGitHistory}
            onChange={(e) => setIncludeGitHistory(e.target.checked)}
            className="w-5 h-5 accent-cyan-500 rounded cursor-pointer"
          />
        </label>

        <label className="flex items-center justify-between p-3 bg-slate-800/60 rounded-lg border border-slate-700/50 cursor-pointer hover:bg-slate-800 transition">
          <div>
            <div className="font-semibold text-sm">Force Export</div>
            <div className="text-xs text-slate-400">Bypass soft validation warnings</div>
          </div>
          <input
            type="checkbox"
            checked={force}
            onChange={(e) => setForce(e.target.checked)}
            className="w-5 h-5 accent-yellow-500 rounded cursor-pointer"
          />
        </label>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-950/60 border border-red-800 text-red-300 text-sm rounded-lg">
          {error}
        </div>
      )}

      {exportResult && (
        <div className="mb-6 p-4 bg-emerald-950/50 border border-emerald-800 rounded-lg text-emerald-200 text-sm">
          <div className="font-bold flex items-center gap-2 mb-2 text-emerald-400">
            ✓ Export Successful (.wlipjt)
          </div>
          <div className="grid grid-cols-2 gap-2 text-xs font-mono">
            <div>Components: {exportResult.components_count}</div>
            <div>Nets: {exportResult.nets_count}</div>
            <div>BOM Items: {exportResult.bom_count}</div>
            <div>Artifacts: {exportResult.artifacts_count}</div>
            <div className="col-span-2 truncate">Integrity SHA: {exportResult.checksum || 'Verified'}</div>
          </div>
        </div>
      )}

      <button
        onClick={handleExport}
        disabled={isExporting}
        className="w-full py-3 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white font-bold rounded-lg transition shadow-lg flex items-center justify-center gap-2"
      >
        {isExporting ? 'Generating Package...' : `Export ${projectId}.wlipjt`}
      </button>
    </div>
  );
};
export default ProjectExportPanel;
