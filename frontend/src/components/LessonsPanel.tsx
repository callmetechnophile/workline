import React, { useEffect, useState } from 'react';

interface Lesson {
  lesson_id: string;
  title: string;
  description: string;
  context: string;
  cause: string;
  impact: string;
  recommendation: string;
  created_at: string;
}

interface LessonsPanelProps {
  projectId: string;
  apiBase?: string;
}

export const LessonsPanel: React.FC<LessonsPanelProps> = ({ projectId, apiBase = '' }) => {
  const [lessons, setLessons] = useState<Lesson[]>([]);

  useEffect(() => {
    const fetchLessons = async () => {
      try {
        const res = await fetch(`${apiBase}/api/knowledge/lessons?project_id=${projectId}`);
        if (res.ok) {
          const data = await res.json();
          setLessons(data);
        }
      } catch (err) {
        console.error(err);
      }
    };

    if (projectId) {
      fetchLessons();
    }
  }, [projectId, apiBase]);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl text-slate-100 space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <h3 className="text-sm font-bold uppercase tracking-wider text-emerald-400">Engineering Lessons Learned</h3>
        <span className="text-xs font-mono text-slate-400">{lessons.length} lessons</span>
      </div>

      <div className="space-y-4 max-h-96 overflow-y-auto">
        {lessons.length === 0 ? (
          <div className="text-xs text-slate-500 py-6 text-center">No lessons recorded yet.</div>
        ) : (
          lessons.map((l) => (
            <div key={l.lesson_id} className="p-4 bg-slate-950/70 border border-slate-800 rounded-lg space-y-2 text-xs">
              <div className="flex justify-between items-center font-mono">
                <span className="font-bold text-cyan-400">{l.lesson_id}</span>
                <span className="text-slate-500 text-[10px]">{l.created_at?.substring(0, 10)}</span>
              </div>
              <h4 className="font-bold text-white text-sm">{l.title}</h4>
              <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-300 font-mono pt-1">
                <div><span className="text-slate-500 font-semibold">Context:</span> {l.context}</div>
                <div><span className="text-slate-500 font-semibold">Cause:</span> {l.cause}</div>
              </div>
              <div className="p-2.5 bg-emerald-950/40 border border-emerald-900/60 rounded text-emerald-300 font-sans text-xs">
                <strong>Recommendation:</strong> {l.recommendation}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
export default LessonsPanel;
