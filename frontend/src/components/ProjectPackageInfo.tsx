import React, { useEffect, useState } from 'react';

interface ProjectPackageInfoProps {
  packagePath: string;
}

export const ProjectPackageInfo: React.FC<ProjectPackageInfoProps> = ({ packagePath }) => {
  const [data, setData] = useState<any | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchInfo = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`/api/project/package/info?package_file=${encodeURIComponent(packagePath)}`);
        if (!res.ok) {
          const errData = await res.json();
          throw new Error(errData.detail || 'Failed to inspect package');
        }
        const json = await res.json();
        setData(json);
      } catch (err: any) {
        setError(err.message || 'Inspection failed');
      } finally {
        setLoading(false);
      }
    };

    if (packagePath) {
      fetchInfo();
    }
  }, [packagePath]);

  if (loading) {
    return <div className="p-6 text-center text-slate-400 text-sm">Inspecting package container...</div>;
  }

  if (error) {
    return <div className="p-4 bg-red-950/60 border border-red-800 text-red-300 text-sm rounded-lg">{error}</div>;
  }

  if (!data) return null;

  const m = data.manifest;
  const sb = data.size_breakdown;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl text-slate-100 max-w-xl mx-auto space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div>
          <h3 className="text-lg font-bold text-cyan-400">{m.project_name}</h3>
          <p className="text-xs text-slate-400 font-mono">ID: {m.project_id} | Version: v{m.project_version}</p>
        </div>
        <span
          className={`px-3 py-1 text-xs font-bold font-mono rounded-full border ${
            data.integrity_status === 'VALID'
              ? 'bg-emerald-950 text-emerald-400 border-emerald-800'
              : 'bg-red-950 text-red-400 border-red-800'
          }`}
        >
          {data.integrity_status}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-3 text-xs font-mono">
        <div className="p-3 bg-slate-800/60 rounded-lg border border-slate-700/50">
          <div className="text-slate-400">Components</div>
          <div className="text-base font-bold text-white mt-1">{m.components_count}</div>
        </div>
        <div className="p-3 bg-slate-800/60 rounded-lg border border-slate-700/50">
          <div className="text-slate-400">Nets</div>
          <div className="text-base font-bold text-white mt-1">{m.nets_count}</div>
        </div>
        <div className="p-3 bg-slate-800/60 rounded-lg border border-slate-700/50">
          <div className="text-slate-400">BOM Items</div>
          <div className="text-base font-bold text-white mt-1">{m.bom_count}</div>
        </div>
        <div className="p-3 bg-slate-800/60 rounded-lg border border-slate-700/50">
          <div className="text-slate-400">Artifacts</div>
          <div className="text-base font-bold text-white mt-1">{m.artifacts_count}</div>
        </div>
      </div>

      <div>
        <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Package Size Breakdown</h4>
        <div className="p-3 bg-slate-800/40 rounded-lg border border-slate-700/50 text-xs space-y-1 font-mono">
          <div className="flex justify-between">
            <span className="text-slate-400">Total Size:</span>
            <span className="font-bold text-white">{(sb.total_package_size_bytes / (1024 * 1024)).toFixed(2)} MB</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Project State:</span>
            <span>{(sb.project_state_size_bytes / 1024).toFixed(1)} KB</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Documentation:</span>
            <span>{(sb.documentation_size_bytes / 1024).toFixed(1)} KB</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Artifacts:</span>
            <span>{(sb.artifacts_size_bytes / (1024 * 1024)).toFixed(2)} MB</span>
          </div>
        </div>
      </div>

      <div className="text-xs text-slate-400 font-mono flex justify-between pt-2 border-t border-slate-800">
        <span>Git Commit: {m.git.current_commit?.substring(0, 7) || 'None'}</span>
        <span>Format Version: v{m.format_version}</span>
      </div>
    </div>
  );
};
export default ProjectPackageInfo;
