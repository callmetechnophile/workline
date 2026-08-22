import React, { useState } from 'react';

interface ProjectBackupPanelProps {
  projectId: string;
  projectName: string;
}

export const ProjectBackupPanel: React.FC<ProjectBackupPanelProps> = ({ projectId, projectName }) => {
  const [includeArtifacts, setIncludeArtifacts] = useState<boolean>(false);
  const [isBackingUp, setIsBackingUp] = useState<boolean>(false);
  const [backupResult, setBackupResult] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleBackup = async () => {
    setIsBackingUp(true);
    setError(null);
    setBackupResult(null);
    try {
      const res = await fetch('/api/project/backup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: projectId,
          include_artifacts: includeArtifacts,
        }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Backup failed');
      }

      const data = await res.json();
      setBackupResult(data);
    } catch (err: any) {
      setError(err.message || 'Backup failed');
    } finally {
      setIsBackingUp(false);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl text-slate-100 max-w-xl mx-auto">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-5">
        <div>
          <h3 className="text-lg font-bold text-cyan-400">Timestamped Project Backup</h3>
          <p className="text-xs text-slate-400">Creates a non-destructive point-in-time .wlipjt archive in project-backups/</p>
        </div>
      </div>

      <div className="space-y-4 mb-5">
        <label className="flex items-center justify-between p-3 bg-slate-800/60 rounded-lg border border-slate-700/50 cursor-pointer">
          <div>
            <div className="font-semibold text-sm">Include Full Artifact Payloads</div>
            <div className="text-xs text-slate-400">Save complete binary weights and models into backup package</div>
          </div>
          <input
            type="checkbox"
            checked={includeArtifacts}
            onChange={(e) => setIncludeArtifacts(e.target.checked)}
            className="w-5 h-5 accent-cyan-500 rounded cursor-pointer"
          />
        </label>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-950/60 border border-red-800 text-red-300 text-sm rounded-lg">{error}</div>
      )}

      {backupResult && (
        <div className="mb-5 p-4 bg-emerald-950/50 border border-emerald-800 rounded-lg text-xs font-mono space-y-1">
          <div className="font-bold text-emerald-400 flex items-center gap-1 mb-1">
            ✓ Backup Created Successfully
          </div>
          <div className="truncate text-slate-300">File: {backupResult.backup_file}</div>
          <div className="text-slate-400">Timestamp: {backupResult.manifest?.exported_at?.replace('T', ' ')}</div>
        </div>
      )}

      <button
        onClick={handleBackup}
        disabled={isBackingUp}
        className="w-full py-3 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white font-bold rounded-lg transition shadow-lg"
      >
        {isBackingUp ? 'Creating Backup...' : 'Create Backup (.wlipjt)'}
      </button>
    </div>
  );
};
export default ProjectBackupPanel;
