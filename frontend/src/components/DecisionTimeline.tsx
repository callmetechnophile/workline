import React, { useEffect, useState } from 'react';

interface TimelineEvent {
  decision_id: string;
  title: string;
  selected_option: string;
  status: string;
  created_at: string;
  supersedes?: string;
  superseded_by?: string;
  project_version?: string;
}

interface DecisionTimelineProps {
  projectId: string;
  apiBase?: string;
}

export const DecisionTimeline: React.FC<DecisionTimelineProps> = ({ projectId, apiBase = '' }) => {
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);

  useEffect(() => {
    const fetchTimeline = async () => {
      try {
        const res = await fetch(`${apiBase}/api/knowledge/decisions?project_id=${projectId}`);
        if (res.ok) {
          const data = await res.json();
          setTimeline(data);
        }
      } catch (err) {
        console.error(err);
      }
    };

    if (projectId) {
      fetchTimeline();
    }
  }, [projectId, apiBase]);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl text-slate-100 space-y-4">
      <h3 className="text-sm font-bold uppercase tracking-wider text-cyan-400">Chronological Decision Timeline</h3>
      <div className="relative pl-6 space-y-6 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800">
        {timeline.map((d, idx) => {
          const isSuperseded = d.status === 'SUPERSEDED' || !!d.superseded_by;
          const statusIcon = isSuperseded ? '⟲' : '✓';
          const statusBg = isSuperseded ? 'bg-slate-700 text-slate-400' : 'bg-emerald-600 text-white';

          return (
            <div key={idx} className="relative group">
              <div
                className={`absolute -left-6 top-1.5 w-4 h-4 rounded-full ${statusBg} flex items-center justify-center text-[10px] font-bold`}
              >
                {statusIcon}
              </div>

              <div className="p-3 bg-slate-950/60 rounded-lg border border-slate-800 space-y-1 font-mono text-xs">
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-cyan-400">{d.decision_id}</span>
                    <span className="text-white font-sans font-semibold">{d.title}</span>
                  </div>
                  <span className="text-slate-500 text-[10px]">{d.created_at?.substring(0, 10)}</span>
                </div>

                <div className="text-slate-300">
                  Selected: <strong className="text-cyan-300">{d.selected_option}</strong>
                  {d.project_version && <span className="ml-2 px-1.5 py-0.2 bg-slate-800 text-slate-400 rounded text-[10px]">v{d.project_version}</span>}
                </div>

                {d.supersedes && (
                  <div className="text-slate-400 text-[11px]">
                    ↳ Superseded <span className="text-yellow-400">{d.supersedes}</span>
                  </div>
                )}
                {d.superseded_by && (
                  <div className="text-yellow-400 text-[11px]">
                    ↳ Superseded by <span className="underline">{d.superseded_by}</span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
export default DecisionTimeline;
