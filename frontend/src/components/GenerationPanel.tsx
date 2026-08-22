"use client";

import React, { useState } from "react";
import { Sparkles, Image as ImageIcon, Presentation, History } from "lucide-react";
import { ImageGenerationPanel } from "./ImageGenerationPanel";
import { PresentationGenerationPanel } from "./PresentationGenerationPanel";
import { GenerationHistory, GenerationArtifactSummary } from "./GenerationHistory";
import { ArtifactPreview } from "./ArtifactPreview";

interface GenerationPanelProps {
  projectId: string;
}

export const GenerationPanel: React.FC<GenerationPanelProps> = ({ projectId }) => {
  const [activeTab, setActiveTab] = useState<"visuals" | "presentations" | "history">("visuals");
  const [artifacts, setArtifacts] = useState<GenerationArtifactSummary[]>([
    {
      artifact_id: "art_img_rover_arch",
      project_id: projectId,
      format: "svg",
      provider: "PaperBanana",
      title: "Rover Autonomous Architecture",
      created_at: "2026-08-22T10:15:00Z",
      sha256: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    },
  ]);
  const [previewArtifact, setPreviewArtifact] = useState<any | null>(null);

  const handleGenerateImage = async (params: any) => {
    // Simulated or API dispatch
    const newArt: GenerationArtifactSummary = {
      artifact_id: `art_img_${Date.now().toString(36)}`,
      project_id: projectId,
      format: "svg",
      provider: params.provider || "PaperBanana",
      title: `${projectId} - ${params.purpose}`,
      created_at: new Date().toISOString(),
      sha256: "8f480329ac6146b300909486ce962261b7f01e69b502432d0c0317d74f88c207",
    };
    setArtifacts((prev) => [newArt, ...prev]);
    return newArt;
  };

  const handleGeneratePresentation = async (params: any) => {
    // Simulated or API dispatch
    const newArt: GenerationArtifactSummary = {
      artifact_id: `art_pres_${Date.now().toString(36)}`,
      project_id: projectId,
      format: "markdown",
      provider: params.provider || "Gamma",
      title: params.title,
      created_at: new Date().toISOString(),
      sha256: "17b7c25091a1d12b109e9921609139ccf8e3305fa4f971b3060f6fb39f604b90",
    };
    setArtifacts((prev) => [newArt, ...prev]);
    return { ...newArt, slide_count: params.slideCount };
  };

  return (
    <div className="flex flex-col gap-5 p-6 bg-zinc-950 min-h-screen text-zinc-100">
      <div className="flex items-center justify-between border-b border-zinc-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-indigo-600/20 text-indigo-400 border border-indigo-500/30">
            <Sparkles className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-zinc-100">Generation & Media Studio</h1>
            <p className="text-xs text-zinc-400">
              Technical visual synthesis via <span className="text-indigo-400 font-semibold">Paper Banana</span> and presentation generation via <span className="text-purple-400 font-semibold">Gamma</span>
            </p>
          </div>
        </div>

        <div className="flex items-center gap-1 bg-zinc-900 border border-zinc-800 p-1 rounded-lg">
          <button
            onClick={() => setActiveTab("visuals")}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded transition ${
              activeTab === "visuals"
                ? "bg-indigo-600 text-white"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            <ImageIcon className="w-3.5 h-3.5" />
            Visuals
          </button>
          <button
            onClick={() => setActiveTab("presentations")}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded transition ${
              activeTab === "presentations"
                ? "bg-indigo-600 text-white"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            <Presentation className="w-3.5 h-3.5" />
            Presentations
          </button>
          <button
            onClick={() => setActiveTab("history")}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded transition ${
              activeTab === "history"
                ? "bg-indigo-600 text-white"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            <History className="w-3.5 h-3.5" />
            Artifacts ({artifacts.length})
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-5">
        {activeTab === "visuals" && (
          <ImageGenerationPanel
            projectId={projectId}
            onGenerateImage={handleGenerateImage}
          />
        )}

        {activeTab === "presentations" && (
          <PresentationGenerationPanel
            projectId={projectId}
            onGeneratePresentation={handleGeneratePresentation}
          />
        )}

        {activeTab === "history" && (
          <GenerationHistory
            artifacts={artifacts}
            onSelectArtifact={(id) => {
              const found = artifacts.find((a) => a.artifact_id === id);
              if (found) setPreviewArtifact(found);
            }}
          />
        )}
      </div>

      {previewArtifact && (
        <ArtifactPreview
          artifact={previewArtifact}
          onClose={() => setPreviewArtifact(null)}
        />
      )}
    </div>
  );
};
