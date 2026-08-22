import React, { useState } from 'react';
import { DecisionPanel } from './DecisionPanel';
import { DecisionTimeline } from './DecisionTimeline';
import { RequirementTraceability } from './RequirementTraceability';
import { FindingPanel } from './FindingPanel';
import { LessonsPanel } from './LessonsPanel';

interface EngineeringKnowledgeProps {
  projectId?: string;
  apiBase?: string;
}

export const EngineeringKnowledge: React.FC<EngineeringKnowledgeProps> = ({
  projectId = 'default_project',
  apiBase = '',
}) => {
  const [activeTab, setActiveTab] = useState<'decisions' | 'timeline' | 'traceability' | 'findings' | 'lessons'>('decisions');

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4">
      <div className="flex items-center justify-between bg-slate-900 border border-slate-800 p-4 rounded-xl shadow-lg">
        <div>
          <h2 className="text-xl font-black text-white">Engineering Knowledge & Decision Memory</h2>
          <p className="text-xs text-slate-400 font-mono">Project ID: {projectId}</p>
        </div>
        <div className="flex gap-2 bg-slate-950 p-1 rounded-lg border border-slate-800 text-xs font-semibold">
          <button
            onClick={() => setActiveTab('decisions')}
            className={`px-3 py-1.5 rounded-md transition ${activeTab === 'decisions' ? 'bg-cyan-600 text-white' : 'text-slate-400 hover:text-white'}`}
          >
            Decisions
          </button>
          <button
            onClick={() => setActiveTab('timeline')}
            className={`px-3 py-1.5 rounded-md transition ${activeTab === 'timeline' ? 'bg-cyan-600 text-white' : 'text-slate-400 hover:text-white'}`}
          >
            Timeline
          </button>
          <button
            onClick={() => setActiveTab('traceability')}
            className={`px-3 py-1.5 rounded-md transition ${activeTab === 'traceability' ? 'bg-cyan-600 text-white' : 'text-slate-400 hover:text-white'}`}
          >
            Traceability
          </button>
          <button
            onClick={() => setActiveTab('findings')}
            className={`px-3 py-1.5 rounded-md transition ${activeTab === 'findings' ? 'bg-cyan-600 text-white' : 'text-slate-400 hover:text-white'}`}
          >
            Findings
          </button>
          <button
            onClick={() => setActiveTab('lessons')}
            className={`px-3 py-1.5 rounded-md transition ${activeTab === 'lessons' ? 'bg-cyan-600 text-white' : 'text-slate-400 hover:text-white'}`}
          >
            Lessons
          </button>
        </div>
      </div>

      {activeTab === 'decisions' && <DecisionPanel projectId={projectId} apiBase={apiBase} />}
      {activeTab === 'timeline' && <DecisionTimeline projectId={projectId} apiBase={apiBase} />}
      {activeTab === 'traceability' && <RequirementTraceability projectId={projectId} apiBase={apiBase} />}
      {activeTab === 'findings' && <FindingPanel projectId={projectId} apiBase={apiBase} />}
      {activeTab === 'lessons' && <LessonsPanel projectId={projectId} apiBase={apiBase} />}
    </div>
  );
};
export default EngineeringKnowledge;
