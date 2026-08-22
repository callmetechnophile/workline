import React, { useState, useEffect } from 'react';

interface Alternative {
  name: string;
  description: string;
  rejection_reason?: string;
}

interface Evidence {
  title: string;
  source_type: string;
  claim: string;
}

interface Decision {
  decision_id: string;
  title: string;
  description: string;
  category: string;
  status: string;
  problem: string;
  rationale: string;
  selected_option: string;
  constraints: string[];
  alternatives: Alternative[];
  evidence: Evidence[];
  supersedes?: string;
  superseded_by?: string;
  project_version?: string;
  created_at: string;
}

interface DecisionPanelProps {
  projectId: string;
  apiBase?: string;
}

export const DecisionPanel: React.FC<DecisionPanelProps> = ({ projectId, apiBase = '' }) => {
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedDec, setSelectedDec] = useState<Decision | null>(null);

  const fetchDecisions = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${apiBase}/api/knowledge/decisions?project_id=${projectId}`);
      if (res.ok) {
        const data = await res.json();
        setDecisions(data);
        if (data.length > 0) setSelectedDec(data[0]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (projectId) {
      fetchDecisions();
    }
  }, [projectId, apiBase]);

  const handleApprove = async (decisionId: string) => {
    try {
      const res = await fetch(`${apiBase}/api/knowledge/decisions/${decisionId}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ actor_id: 'current_user', actor_type: 'HUMAN' }),
      });
      if (res.ok) fetchDecisions();
    } catch (err) {
      console.error(err);
    }
  };

  const handleReject = async (decisionId: string) => {
    try {
      const res = await fetch(`${apiBase}/api/knowledge/decisions/${decisionId}/reject`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ actor_id: 'current_user', actor_type: 'HUMAN', reason: 'Rejected by engineer' }),
      });
      if (res.ok) fetchDecisions();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl text-slate-100 space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <div className="text-xs uppercase tracking-wider text-slate-400">Engineering Knowledge</div>
          <h3 className="text-xl font-bold text-cyan-400">Decision Memory</h3>
        </div>
        <span className="px-3 py-1 bg-cyan-950 text-cyan-400 border border-cyan-800 rounded-full text-xs font-mono">
          {decisions.length} DECISIONS
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left column: List */}
        <div className="space-y-2 max-h-[500px] overflow-y-auto pr-1">
          {loading ? (
            <div className="text-xs text-slate-400 p-4">Loading decisions...</div>
          ) : decisions.length === 0 ? (
            <div className="text-xs text-slate-500 p-4">No decisions recorded.</div>
          ) : (
            decisions.map((d) => (
              <div
                key={d.decision_id}
                onClick={() => setSelectedDec(d)}
                className={`p-3 rounded-lg border text-xs cursor-pointer transition ${
                  selectedDec?.decision_id === d.decision_id
                    ? 'bg-slate-800 border-cyan-500 shadow-md'
                    : 'bg-slate-950/60 border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex justify-between items-center mb-1">
                  <span className="font-mono text-cyan-400 font-bold">{d.decision_id}</span>
                  <span
                    className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                      d.status === 'APPROVED' || d.status === 'VALIDATED'
                        ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                        : d.status === 'PROPOSED'
                        ? 'bg-yellow-950 text-yellow-400 border border-yellow-800'
                        : d.status === 'SUPERSEDED'
                        ? 'bg-slate-800 text-slate-400'
                        : 'bg-red-950 text-red-400 border border-red-800'
                    }`}
                  >
                    {d.status}
                  </span>
                </div>
                <div className="font-semibold text-slate-200 truncate">{d.title}</div>
                <div className="text-[11px] text-slate-400 mt-1">Selected: <strong className="text-white">{d.selected_option}</strong></div>
              </div>
            ))
          )}
        </div>

        {/* Right 2 columns: Detail */}
        <div className="md:col-span-2 bg-slate-950 border border-slate-800 rounded-xl p-5 space-y-4 text-xs">
          {selectedDec ? (
            <>
              <div className="flex justify-between items-start border-b border-slate-800 pb-3">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-cyan-400 font-bold text-sm">{selectedDec.decision_id}</span>
                    <span className="px-2 py-0.5 bg-slate-800 text-slate-300 rounded text-[10px] font-mono">{selectedDec.category}</span>
                  </div>
                  <h4 className="text-base font-bold text-white mt-1">{selectedDec.title}</h4>
                </div>
                {selectedDec.status === 'PROPOSED' && (
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleApprove(selectedDec.decision_id)}
                      className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded text-xs shadow"
                    >
                      Approve
                    </button>
                    <button
                      onClick={() => handleReject(selectedDec.decision_id)}
                      className="px-3 py-1.5 bg-red-600 hover:bg-red-500 text-white font-bold rounded text-xs"
                    >
                      Reject
                    </button>
                  </div>
                )}
              </div>

              {selectedDec.superseded_by && (
                <div className="p-2.5 bg-yellow-950/60 border border-yellow-800 rounded text-yellow-300">
                  ⚠ This decision was <strong>SUPERSEDED</strong> by <span className="font-mono underline">{selectedDec.superseded_by}</span>.
                </div>
              )}

              <div className="space-y-1">
                <span className="text-slate-400 font-semibold uppercase text-[10px] tracking-wider">Problem Statement</span>
                <p className="text-slate-200 bg-slate-900/60 p-2.5 rounded border border-slate-850">{selectedDec.problem || selectedDec.title}</p>
              </div>

              <div className="space-y-1">
                <span className="text-slate-400 font-semibold uppercase text-[10px] tracking-wider">Chosen Option & Rationale</span>
                <div className="bg-slate-900/60 p-2.5 rounded border border-slate-850 space-y-1.5">
                  <div className="text-cyan-300 font-bold text-sm">{selectedDec.selected_option}</div>
                  <p className="text-slate-300">{selectedDec.rationale}</p>
                </div>
              </div>

              {selectedDec.alternatives && selectedDec.alternatives.length > 0 && (
                <div className="space-y-1.5">
                  <span className="text-slate-400 font-semibold uppercase text-[10px] tracking-wider">Evaluated Alternatives</span>
                  <div className="space-y-1.5">
                    {selectedDec.alternatives.map((alt, idx) => (
                      <div key={idx} className="p-2 bg-slate-900/40 rounded border border-slate-850 flex justify-between">
                        <div>
                          <strong className="text-slate-200">{alt.name}</strong>: {alt.description}
                        </div>
                        {alt.rejection_reason && (
                          <span className="text-red-400 text-[11px] font-mono">Rejected: {alt.rejection_reason}</span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {selectedDec.evidence && selectedDec.evidence.length > 0 && (
                <div className="space-y-1.5">
                  <span className="text-slate-400 font-semibold uppercase text-[10px] tracking-wider">Evidence & Claims</span>
                  <div className="space-y-1">
                    {selectedDec.evidence.map((ev, idx) => (
                      <div key={idx} className="p-2 bg-slate-900/40 rounded border border-slate-850 flex items-center justify-between">
                        <div>
                          <span className="px-1.5 py-0.5 bg-slate-800 text-cyan-400 rounded text-[10px] font-mono mr-2">{ev.source_type}</span>
                          <strong className="text-slate-200">{ev.title}</strong> — {ev.claim}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="text-slate-500 text-center py-16">Select a decision from the list to view rationale.</div>
          )}
        </div>
      </div>
    </div>
  );
};
export default DecisionPanel;
