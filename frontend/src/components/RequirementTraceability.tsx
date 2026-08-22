import React, { useEffect, useState } from 'react';

interface Step {
  stage: string;
  identifier: string;
  title: string;
  status: string;
  details?: any;
}

interface TraceabilityChain {
  requirement_id: string;
  project_id: string;
  title: string;
  category: string;
  status: string;
  steps: Step[];
}

interface RequirementTraceabilityProps {
  projectId: string;
  apiBase?: string;
}

export const RequirementTraceability: React.FC<RequirementTraceabilityProps> = ({
  projectId,
  apiBase = '',
}) => {
  const [requirements, setRequirements] = useState<any[]>([]);
  const [selectedReqId, setSelectedReqId] = useState<string | null>(null);
  const [chain, setChain] = useState<TraceabilityChain | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    const fetchReqs = async () => {
      try {
        const res = await fetch(`${apiBase}/api/knowledge/requirements?project_id=${projectId}`);
        if (res.ok) {
          const data = await res.json();
          setRequirements(data);
          if (data.length > 0) {
            setSelectedReqId(data[0].requirement_id);
          }
        }
      } catch (err) {
        console.error(err);
      }
    };

    if (projectId) {
      fetchReqs();
    }
  }, [projectId, apiBase]);

  useEffect(() => {
    const fetchTraceability = async () => {
      if (!selectedReqId) return;
      setLoading(true);
      try {
        const res = await fetch(`${apiBase}/api/knowledge/traceability/${selectedReqId}`);
        if (res.ok) {
          const data = await res.json();
          setChain(data);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchTraceability();
  }, [selectedReqId, apiBase]);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl text-slate-100 space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <div className="text-xs uppercase tracking-wider text-slate-400">Engineering Verification</div>
          <h3 className="text-xl font-bold text-cyan-400">Requirement Traceability Graph</h3>
        </div>
        <select
          value={selectedReqId || ''}
          onChange={(e) => setSelectedReqId(e.target.value)}
          className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500"
        >
          {requirements.map((r) => (
            <option key={r.requirement_id} value={r.requirement_id}>
              {r.requirement_id}: {r.title}
            </option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="text-xs text-slate-400 p-8 text-center">Assembling traceability chain...</div>
      ) : chain ? (
        <div className="space-y-4 max-w-xl mx-auto py-4">
          {chain.steps.map((step, idx) => (
            <React.Fragment key={idx}>
              <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl space-y-1 font-mono text-xs shadow-lg">
                <div className="flex justify-between items-center text-[10px] text-slate-400 uppercase tracking-widest font-bold">
                  <span className="text-cyan-400">{step.stage}</span>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] ${
                      step.status === 'VERIFIED' || step.status === 'PASS' || step.status === 'APPROVED'
                        ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                        : 'bg-slate-800 text-slate-300'
                    }`}
                  >
                    {step.status}
                  </span>
                </div>
                <div className="font-bold text-white text-sm pt-1">{step.title}</div>
                <div className="text-slate-400 text-[11px] font-sans">{step.identifier}</div>
              </div>

              {idx < chain.steps.length - 1 && (
                <div className="flex justify-center my-1 text-cyan-500 font-bold text-lg">
                  ↓
                </div>
              )}
            </React.Fragment>
          ))}
        </div>
      ) : (
        <div className="text-slate-500 text-center py-12 text-xs">No traceability data available.</div>
      )}
    </div>
  );
};
export default RequirementTraceability;
