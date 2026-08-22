"use client";

import React, { useState } from "react";
import { Image as ImageIcon, Sparkles, RefreshCw, Eye, CheckCircle2 } from "lucide-react";

interface ImageGenerationPanelProps {
  projectId: string;
  onGenerateImage?: (params: {
    purpose: string;
    prompt?: string;
    ratio: string;
    provider: string;
  }) => Promise<any>;
}

export const ImageGenerationPanel: React.FC<ImageGenerationPanelProps> = ({
  projectId,
  onGenerateImage,
}) => {
  const [purpose, setPurpose] = useState("ARCHITECTURE");
  const [prompt, setPrompt] = useState("");
  const [ratio, setRatio] = useState("16:9");
  const [provider, setProvider] = useState("PaperBanana");
  const [generating, setGenerating] = useState(false);
  const [lastArtifact, setLastArtifact] = useState<any>(null);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!onGenerateImage) return;
    setGenerating(true);
    try {
      const art = await onGenerateImage({
        purpose,
        prompt: prompt.trim() ? prompt : undefined,
        ratio,
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
          <ImageIcon className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-zinc-100">Technical Visual Generator</h3>
        </div>
        <span className="px-2.5 py-0.5 rounded text-xs font-mono bg-indigo-950 text-indigo-300 border border-indigo-800">
          Provider: {provider}
        </span>
      </div>

      <form onSubmit={handleGenerate} className="flex flex-col gap-3 text-xs">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <label className="text-zinc-400 block mb-1">Visual Purpose</label>
            <select
              value={purpose}
              onChange={(e) => setPurpose(e.target.value)}
              className="w-full bg-zinc-950 border border-zinc-800 rounded px-3 py-2 text-zinc-200"
            >
              <option value="ARCHITECTURE">System Architecture</option>
              <option value="ENGINEERING">Engineering Subsystems</option>
              <option value="PCB">PCB Thermal & Placement</option>
              <option value="WORKFLOW">Lifecycle Workflow</option>
              <option value="RESEARCH">Research Figures</option>
              <option value="DOCUMENTATION">Technical Documentation</option>
            </select>
          </div>

          <div>
            <label className="text-zinc-400 block mb-1">Aspect Ratio</label>
            <select
              value={ratio}
              onChange={(e) => setRatio(e.target.value)}
              className="w-full bg-zinc-950 border border-zinc-800 rounded px-3 py-2 text-zinc-200"
            >
              <option value="16:9">16:9 (Landscape Deck)</option>
              <option value="4:3">4:3 (Standard Document)</option>
              <option value="1:1">1:1 (Square Figure)</option>
            </select>
          </div>
        </div>

        <div>
          <label className="text-zinc-400 block mb-1">Custom Technical Focus (Optional)</label>
          <input
            type="text"
            placeholder="e.g. Highlight PINN thermal loss boundaries and x402 payment flow..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="w-full bg-zinc-950 border border-zinc-800 rounded px-3 py-2 text-zinc-200 placeholder:text-zinc-600"
          />
        </div>

        <button
          type="submit"
          disabled={generating}
          className="flex items-center justify-center gap-2 mt-2 px-4 py-2.5 rounded font-semibold text-xs bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white transition"
        >
          {generating ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              Synthesizing Technical Visual...
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              Generate with Paper Banana
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
            {lastArtifact.filename} ({lastArtifact.width}x{lastArtifact.height})
          </span>
        </div>
      )}
    </div>
  );
};
