import React, { useState } from 'react';

interface ProjectImportPanelProps {
  onImportComplete?: (importedInfo: any) => void;
}

export const ProjectImportPanel: React.FC<ProjectImportPanelProps> = ({ onImportComplete }) => {
  const [packageFile, setPackageFile] = useState<string>('');
  const [targetName, setTargetName] = useState<string>('');
  const [strategy, setStrategy] = useState<'NEW_PROJECT' | 'RESTORE' | 'MERGE'>('RESTORE');
  const [overwrite, setOverwrite] = useState<boolean>(false);
  const [isVerifying, setIsVerifying] = useState<boolean>(false);
  const [isImporting, setIsImporting] = useState<boolean>(false);
  const [inspectionData, setInspectionData] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleInspect = async () => {
    if (!packageFile.trim()) {
      setError('Please provide a package file path.');
      return;
    }
    setIsVerifying(true);
    setError(null);
    try {
      const res = await fetch(`/api/project/package/info?package_file=${encodeURIComponent(packageFile)}`);
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Package inspection failed');
      }
      const data = await res.json();
      setInspectionData(data);
    } catch (err: any) {
      setError(err.message || 'Inspection failed');
    } finally {
      setIsVerifying(false);
    }
  };

  const handleImport = async () => {
    if (!packageFile.trim()) {
      setError('Please provide a package file path.');
      return;
    }
    setIsImporting(true);
    setError(null);
    setSuccess(null);
    try {
      const res = await fetch('/api/project/import', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          package_file: packageFile,
          target_name: targetName.trim() || undefined,
          strategy,
          overwrite,
        }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Import failed');
      }

      const result = await res.json();
      setSuccess(`Project '${result.project_name}' successfully imported and activated.`);
      if (onImportComplete) onImportComplete(result);
    } catch (err: any) {
      setError(err.message || 'Import failed');
    } finally {
      setIsImporting(false);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl text-slate-100 max-w-2xl mx-auto">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-6">
        <div>
          <h2 className="text-xl font-bold text-emerald-400">Import Workline Package (.wlipjt)</h2>
          <p className="text-xs text-slate-400 mt-1">
            Restore project engineering state, PCB models, BOMs, and Git metadata from an archive.
          </p>
        </div>
        <span className="px-3 py-1 bg-emerald-950 text-emerald-400 border border-emerald-800 rounded-full text-xs font-mono">
          PORTABILITY ENGINE
        </span>
      </div>

      <div className="space-y-4 mb-6">
        <div>
          <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Package File Path</label>
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="/path/to/project-name.wlipjt"
              value={packageFile}
              onChange={(e) => setPackageFile(e.target.value)}
              className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-500"
            />
            <button
              onClick={handleInspect}
              disabled={isVerifying || !packageFile}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-cyan-400 border border-slate-700 font-semibold text-sm rounded-lg transition"
            >
              {isVerifying ? 'Verifying...' : 'Inspect'}
            </button>
          </div>
        </div>

        {inspectionData && (
          <div className="p-4 bg-slate-800/80 rounded-lg border border-slate-700 text-xs font-mono space-y-1">
            <div className="font-bold text-cyan-400">{inspectionData.manifest.project_name} (v{inspectionData.manifest.project_version})</div>
            <div>Integrity: <span className="text-emerald-400 font-bold">{inspectionData.integrity_status}</span></div>
            <div>Components: {inspectionData.manifest.components_count} | Nets: {inspectionData.manifest.nets_count} | BOM: {inspectionData.manifest.bom_count}</div>
            <div>Git SHA: {inspectionData.manifest.git.current_commit?.substring(0, 7) || 'None'}</div>
          </div>
        )}

        <div>
          <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Target Project Name Override (Optional)</label>
          <input
            type="text"
            placeholder="e.g. Rover V2 Fork"
            value={targetName}
            onChange={(e) => setTargetName(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-500"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Import Strategy</label>
          <div className="grid grid-cols-3 gap-2">
            {(['NEW_PROJECT', 'RESTORE', 'MERGE'] as const).map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => setStrategy(s)}
                className={`py-2 px-3 rounded-lg text-xs font-bold transition border ${
                  strategy === s
                    ? 'bg-cyan-600 text-white border-cyan-400'
                    : 'bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-750'
                }`}
              >
                {s}
              </button>
            ))}
          </div>
        </div>

        <label className="flex items-center justify-between p-3 bg-slate-800/60 rounded-lg border border-slate-700/50 cursor-pointer">
          <div>
            <div className="font-semibold text-sm">Overwrite Existing Project</div>
            <div className="text-xs text-slate-400">Allows replacement if destination project folder already exists</div>
          </div>
          <input
            type="checkbox"
            checked={overwrite}
            onChange={(e) => setOverwrite(e.target.checked)}
            className="w-5 h-5 accent-red-500 rounded cursor-pointer"
          />
        </label>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-950/60 border border-red-800 text-red-300 text-sm rounded-lg">
          {error}
        </div>
      )}

      {success && (
        <div className="mb-4 p-3 bg-emerald-950/60 border border-emerald-800 text-emerald-300 text-sm rounded-lg">
          {success}
        </div>
      )}

      <button
        onClick={handleImport}
        disabled={isImporting || !packageFile}
        className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-bold rounded-lg transition shadow-lg"
      >
        {isImporting ? 'Restoring Project...' : 'Import Project Package'}
      </button>
    </div>
  );
};
export default ProjectImportPanel;
