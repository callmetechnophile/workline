"use client";

/**
 * ImageGenerationPanel — PaperBanana × Amazon Bedrock engineering visual generator.
 *
 * Architecture:
 *   User fills form → POST /api/generation/image (R1 → R2) → ArmourIQ → PaperBanana → Amazon Bedrock
 *
 * Security posture:
 *   - AWS credentials are NEVER in this file, never in any frontend file.
 *   - All generation happens server-side on R2 via Amazon Bedrock.
 *   - project_id is sourced from parent component's authenticated session.
 *   - user_id, agent_id, trust_level are NEVER accepted from UI.
 */

import React, { useState } from "react";
import {
  Image as ImageIcon,
  Sparkles,
  RefreshCw,
  CheckCircle2,
  XCircle,
  Shield,
  Cpu,
  Eye,
} from "lucide-react";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type GenerationState = "IDLE" | "QUEUED" | "GENERATING" | "COMPLETED" | "FAILED";

export interface GeneratedArtifact {
  image_id: string;
  artifact_id?: string;
  project_id: string;
  image_type: string;
  filename: string;
  format: string;
  width: number;
  height: number;
  sha256: string;
  provider: string;
  model: string;
  generation_version: number;
  created_at: string;
  content?: string; // SVG markup
  conversation_id?: string;
  title?: string;
}

interface ImageGenerationPanelProps {
  projectId: string;
  conversationId?: string;
  /** Called by the parent to POST to R1 → R2 → ArmourIQ → PaperBanana → Gemini */
  onGenerateImage?: (params: {
    project_id: string;
    purpose: string;
    prompt?: string;
    aspect_ratio: string;
    conversation_id?: string;
  }) => Promise<GeneratedArtifact>;
}

const IMAGE_TYPES = [
  { value: "ARCHITECTURE", label: "System Architecture" },
  { value: "ENGINEERING", label: "Engineering Subsystems" },
  { value: "PCB", label: "PCB Thermal & Placement" },
  { value: "WORKFLOW", label: "Lifecycle Workflow" },
  { value: "RESEARCH", label: "Research Figures" },
  { value: "DOCUMENTATION", label: "Technical Documentation" },
  { value: "FLOW_DIAGRAM", label: "Flow Diagram" },
  { value: "CONCEPT_RENDER", label: "Concept Render" },
  { value: "MECHANICAL_CONCEPT", label: "Mechanical Concept" },
  { value: "ELECTRONICS_CONCEPT", label: "Electronics Concept" },
];

const ASPECT_RATIOS = [
  { value: "16:9", label: "16:9 — Landscape / Deck" },
  { value: "4:3", label: "4:3 — Standard Document" },
  { value: "1:1", label: "1:1 — Square Figure" },
];

// ---------------------------------------------------------------------------
// State badge
// ---------------------------------------------------------------------------

const StateBadge: React.FC<{ state: GenerationState }> = ({ state }) => {
  const styles: Record<GenerationState, string> = {
    IDLE: "bg-zinc-800 text-zinc-400 border-zinc-700",
    QUEUED: "bg-amber-950 text-amber-300 border-amber-800",
    GENERATING: "bg-indigo-950 text-indigo-300 border-indigo-800",
    COMPLETED: "bg-emerald-950 text-emerald-300 border-emerald-800",
    FAILED: "bg-red-950 text-red-300 border-red-800",
  };
  return (
    <span
      className={`px-2 py-0.5 rounded text-xs font-mono border ${styles[state]}`}
    >
      {state}
    </span>
  );
};

// ---------------------------------------------------------------------------
// SVG Preview
// ---------------------------------------------------------------------------

const SvgPreview: React.FC<{ svgContent: string }> = ({ svgContent }) => (
  <div
    className="rounded-lg overflow-hidden border border-zinc-700 bg-zinc-950 flex items-center justify-center"
    style={{ minHeight: 200 }}
    dangerouslySetInnerHTML={{ __html: svgContent }}
  />
);

// ---------------------------------------------------------------------------
// Main Component
// ---------------------------------------------------------------------------

export const ImageGenerationPanel: React.FC<ImageGenerationPanelProps> = ({
  projectId,
  conversationId,
  onGenerateImage,
}) => {
  const [purpose, setPurpose] = useState("ARCHITECTURE");
  const [prompt, setPrompt] = useState("");
  const [ratio, setRatio] = useState("16:9");
  const [state, setState] = useState<GenerationState>("IDLE");
  const [artifact, setArtifact] = useState<GeneratedArtifact | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showPreview, setShowPreview] = useState(false);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!onGenerateImage) return;

    setState("QUEUED");
    setError(null);
    setArtifact(null);

    try {
      setState("GENERATING");
      const result = await onGenerateImage({
        project_id: projectId,
        purpose,
        prompt: prompt.trim() || undefined,
        aspect_ratio: ratio,
        conversation_id: conversationId,
      });
      setArtifact(result);
      setState("COMPLETED");
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Image generation failed";
      setError(msg);
      setState("FAILED");
    }
  };

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ImageIcon className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-zinc-100">
            Generate Engineering Visual
          </h3>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 rounded text-xs font-mono bg-violet-950 text-violet-300 border border-violet-800 flex items-center gap-1">
            <Shield className="w-3 h-3" />
            ArmourIQ
          </span>
          <span className="px-2 py-0.5 rounded text-xs font-mono bg-blue-950 text-blue-300 border border-blue-800 flex items-center gap-1">
            <Cpu className="w-3 h-3" />
            Gemini
          </span>
          <StateBadge state={state} />
        </div>
      </div>

      {/* Form */}
      <form onSubmit={handleGenerate} className="flex flex-col gap-3 text-xs">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <label className="text-zinc-400 block mb-1">Image Type</label>
            <select
              value={purpose}
              onChange={(e) => setPurpose(e.target.value)}
              className="w-full bg-zinc-950 border border-zinc-800 rounded px-3 py-2 text-zinc-200"
            >
              {IMAGE_TYPES.map((t) => (
                <option key={t.value} value={t.value}>
                  {t.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-zinc-400 block mb-1">Aspect Ratio</label>
            <select
              value={ratio}
              onChange={(e) => setRatio(e.target.value)}
              className="w-full bg-zinc-950 border border-zinc-800 rounded px-3 py-2 text-zinc-200"
            >
              {ASPECT_RATIOS.map((r) => (
                <option key={r.value} value={r.value}>
                  {r.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className="text-zinc-400 block mb-1">
            Description{" "}
            <span className="text-zinc-600">(optional — adds to project context)</span>
          </label>
          <textarea
            rows={2}
            placeholder="e.g. Generate a block diagram for the 48V → 12V synchronous buck converter, highlighting the PINN thermal solver and ArmourIQ authorization layers."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="w-full bg-zinc-950 border border-zinc-800 rounded px-3 py-2 text-zinc-200 placeholder:text-zinc-600 resize-none"
          />
        </div>

        {/* Project Context chips */}
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-zinc-500 text-xs">Context:</span>
          {["Project requirements", "Architecture", "ADK agents"].map((c) => (
            <span
              key={c}
              className="px-2 py-0.5 rounded text-xs bg-zinc-800 text-zinc-400 border border-zinc-700"
            >
              ✓ {c}
            </span>
          ))}
        </div>

        <button
          type="submit"
          disabled={state === "GENERATING" || state === "QUEUED"}
          className="flex items-center justify-center gap-2 mt-1 px-4 py-2.5 rounded font-semibold text-xs bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white transition"
        >
          {state === "GENERATING" || state === "QUEUED" ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              {state === "QUEUED"
                ? "Queued — awaiting ArmourIQ..."
                : "Generating engineering visual..."}
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              Generate
            </>
          )}
        </button>
      </form>

      {/* Error */}
      {state === "FAILED" && error && (
        <div className="flex items-start gap-2 p-3 bg-red-950/40 border border-red-800/60 rounded-lg">
          <XCircle className="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
          <p className="text-xs text-red-300">{error}</p>
        </div>
      )}

      {/* Success — artifact card */}
      {state === "COMPLETED" && artifact && (
        <div className="flex flex-col gap-3">
          <div className="p-3.5 bg-zinc-950 border border-emerald-800/60 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span className="text-xs font-mono text-zinc-200">
                  {artifact.image_id}
                </span>
                <span className="text-xs text-zinc-600">
                  v{artifact.generation_version}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono text-zinc-500">
                  {artifact.model}
                </span>
                {artifact.content && (
                  <button
                    onClick={() => setShowPreview((p) => !p)}
                    className="flex items-center gap-1 text-xs text-indigo-400 hover:text-indigo-300 transition"
                  >
                    <Eye className="w-3.5 h-3.5" />
                    {showPreview ? "Hide" : "Preview"}
                  </button>
                )}
              </div>
            </div>
            <div className="grid grid-cols-3 gap-2 text-xs">
              <span className="text-zinc-400">
                Type:{" "}
                <span className="text-zinc-200">{artifact.image_type}</span>
              </span>
              <span className="text-zinc-400">
                Format:{" "}
                <span className="text-zinc-200 uppercase">{artifact.format}</span>
              </span>
              <span className="text-zinc-400">
                Provider:{" "}
                <span className="text-zinc-200">{artifact.provider}</span>
              </span>
            </div>
            {artifact.conversation_id && (
              <p className="mt-1 text-xs text-zinc-600 font-mono">
                Attached to conversation: {artifact.conversation_id}
              </p>
            )}
          </div>

          {/* SVG Preview */}
          {showPreview && artifact.content && (
            <SvgPreview svgContent={artifact.content} />
          )}
        </div>
      )}
    </div>
  );
};

export default ImageGenerationPanel;
