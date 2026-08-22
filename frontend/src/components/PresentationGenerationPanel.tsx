"use client";

import React, { useState } from "react";
import { Presentation, Sparkles, RefreshCw, CheckCircle2 } from "lucide-react";

interface PresentationGenerationPanelProps {
  projectId: string;
  onGeneratePresentation?: (params: {
    title: string;
    audience: string;
    purpose: string;
    slideCount: number;
    provider: string;
  }) => Promise<any>;
}

export const PresentationGenerationPanel: React.FC<PresentationGenerationPanelProps> = ({
  projectId,
  onGeneratePresentation,
}) => {
  const [title, setTitle] = useState(`Workline Architecture & Review: ${projectId}`);
  const [audience, setAudience] = useState("Engineering Leads & Architects");
  const [purpose, setPurpose] = useState("TECHNICAL_DEEP_DIVE");
  const [slideCount, setSlideCount] = useState(8);
  const [provider, setProvider] = useState("Gamma");
  const [generating, setGenerating] = useState(false);
  const [lastArtifact, setLastArtifact] = useState<any>(null);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!onGeneratePresentation) return;
    setGenerating(true);
    try {
      const art = await onGeneratePresentation({
        title,
        audience,
        purpose,
        slideCount,
        provider,
      });
      setLastArtifact(art);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Presentation className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-zinc-100">Technical Presentation Generator</h3>
        </div>
        <span className="px-2.5 py-0.5 rounded text-xs font-mono bg-purple-950 text-purple-300 border border-purple-800">
          Provider: {provider}
        </span>
      </div>

      <form onSubmit={handleGenerate} className="flex flex-col gap-3 text-xs">
        <div>
          <label className="text-zinc-400 block mb-1">Presentation Title</label>
          <input
            type="text"
            required
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full bg-zinc-950 border border-zinc-800 rounded px-3 py-2 text-zinc-200"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div>
            <label className="text-zinc-400 block mb-1">Audience</label>
            <input
              type="text"
              value={audience}
              onChange={(e) => setAudience(e.target.value)}
              className="w-full bg-zinc-950 border border-zinc-800 rounded px-3 py-2 text-zinc-200"
            />
          </div>

          <div>
            <label className="text-zinc-400 block mb-1">Purpose</label>
            <select
              value={purpose}
              onChange={(e) => setPurpose(e.target.value)}
              className="w-full bg-zinc-950 border border-zinc-800 rounded px-3 py-2 text-zinc-200"
            >
              <option value="PROJECT_OVERVIEW">Project Overview</option>
              <option value="TECHNICAL_DEEP_DIVE">Technical Deep Dive</option>
              <option value="HACKATHON">Hackathon Pitch</option>
              <option value="ENGINEERING_REVIEW">Engineering Review</option>
              <option value="PROGRESS_REPORT">Progress Report</option>
            </select>
          </div>

          <div>
            <label className="text-zinc-400 block mb-1">Slide Count</label>
            <input
              type="number"
              min={3}
              max={20}
              value={slideCount}
              onChange={(e) => setSlideCount(parseInt(e.target.value, 10))}
              className="w-full bg-zinc-950 border border-zinc-800 rounded px-3 py-2 text-zinc-200"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={generating}
          className="flex items-center justify-center gap-2 mt-2 px-4 py-2.5 rounded font-semibold text-xs bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white transition"
        >
          {generating ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              Generating Grounded Presentation Outline...
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              Generate Presentation with Gamma
            </>
          )}
        </button>
      </form>

      {lastArtifact && (
        <div className="p-3.5 bg-zinc-950 border border-emerald-800/60 rounded-lg flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span className="text-xs font-mono text-zinc-200">{lastArtifact.artifact_id}</span>
          </div>
          <span className="text-xs text-zinc-400 font-mono">
            {lastArtifact.title} ({lastArtifact.slide_count} slides)
          </span>
        </div>
      )}
    </div>
  );
};
