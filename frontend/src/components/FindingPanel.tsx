import React, { useEffect, useState } from 'react';

interface Finding {
  finding_id: string;
  title: string;
  description: string;
  category: string;
  severity: string;
  status: string;
  resolution?: string;
  resolved_by_decision_id?: string;
  created_at: string;
}

interface FindingPanelProps {
  projectId: string;
  apiBase?: string;
}

export const FindingPanel: React.FC<FindingPanelProps> = ({ projectId, apiBase = '' }) => {
  const [findings, setFindings] = useState<Finding[]>([]);

  useEffect(() => {
    const fetchFindings = async () => {
      try {
        const res = await fetch(`${apiBase}/api/knowledge/findings?project_id=${projectId}`);
        if (res.ok) {
          const data = await res.json();
          setFindings(data);
        }
      } catch (err) {
        console.error(err);
      }
    };

    if (projectId) {
      fetchFindings();
    }
  }, [projectId, apiBase]);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl text-slate-100 space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <h3 className="text-sm font-bold uppercase tracking-wider text-yellow-400">Engineering Findings & Anomalies</h3>
        <span className="text-xs font-mono text-slate-400">{findings.length} findings</span>
      </div>

      <div className="space-y-3 max-h-96 overflow-y-auto">
        {findings.length === 0 ? (
          <div className="text-xs text-slate-500 py-6 text-center">No open findings recorded.</div>
        ) : (
          findings.map((f) => (
            <div key={f.finding_id} className="p-3.5 bg-slate-950/70 border border-slate-800 rounded-lg space-y-2 text-xs font-mono">
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-yellow-400">{f.finding_id}</span>
                  <span className="px-1.5 py-0.5 bg-red-950 text-red-400 rounded text-[10px] font-bold border border-red-900">
                    {f.severity}
                  </span>
                  <span className="px-1.5 py-0.5 bg-slate-800 text-slate-300 rounded text-[10px]">
                    {f.category}
                  </span>
                </div>
                <span className="text-slate-500 text-[10px]">{f.created_at?.substring(0, 10)}</span>
              </div>

              <div className="font-semibold text-slate-200 font-sans">{f.title}</div>
              <p className="text-slate-400 font-sans text-[11px]">{f.description}</p>

              {f.resolution && (
                <div className="p-2 bg-emerald-950/40 border border-emerald-900/60 rounded text-emerald-300 text-[11px]">
                  <strong>Resolution:</strong> {f.resolution}
                  {f.resolved_by_decision_id && (
                    <span className="ml-2 underline font-mono text-cyan-300">({f.resolved_by_decision_id})</span>
                  )}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};
export default FindingPanel;
