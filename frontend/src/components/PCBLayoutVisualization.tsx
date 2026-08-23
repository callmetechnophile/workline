"use client";

import React, { useState, useEffect } from "react";
import { CircuitBoard, Sparkles, RefreshCw, AlertTriangle, Shield, Layers } from "lucide-react";

export interface PCBLayoutVisualizationProps {
  projectId?: string;
  projectName?: string;
  engineeringGoal?: string;
  components?: any[];
  powerAnalysis?: any;
  thermalAnalysis?: any[];
  apiBase?: string;
}

export interface VisualizationRecord {
  id: string;
  project_id: string;
  image_url?: string;
  image_data?: string;
  model: string;
  status: "NOT_GENERATED" | "GENERATING" | "COMPLETED" | "FAILED";
  created_at?: string;
  updated_at?: string;
  metadata?: {
    project_name?: string;
    components_count?: number;
    width?: number;
    height?: number;
    format?: string;
    sha256?: string;
  };
}

export const PCBLayoutVisualization: React.FC<PCBLayoutVisualizationProps> = ({
  projectId,
  projectName,
  engineeringGoal,
  components = [],
  powerAnalysis,
  thermalAnalysis,
  apiBase = "http://localhost:8000",
}) => {
  const [visRecord, setVisRecord] = useState<VisualizationRecord | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const currentProjId = (projectId || projectName || "").trim();

  // Strict Project Isolation: Reset and fetch visualization whenever current project changes
  useEffect(() => {
    if (!currentProjId) {
      setVisRecord(null);
      setErrorMessage(null);
      return;
    }

    let isMounted = true;
    const fetchVisualization = async () => {
      setIsLoading(true);
      setErrorMessage(null);
      try {
        const res = await fetch(`${apiBase}/api/projects/${encodeURIComponent(currentProjId)}/pcb/visualization`);
        if (res.ok) {
          const data = await res.json();
          if (isMounted) setVisRecord(data);
        } else if (res.status === 404) {
          if (isMounted) setVisRecord(null);
        } else {
          const err = await res.json().catch(() => ({ detail: "Failed to fetch PCB visualization" }));
          if (isMounted) setErrorMessage(err.detail || "Unable to retrieve visualization record");
        }
      } catch (err: any) {
        if (isMounted) setVisRecord(null);
      } finally {
        if (isMounted) setIsLoading(false);
      }
    };

    fetchVisualization();

    return () => {
      isMounted = false;
    };
  }, [currentProjId, apiBase]);

  const [generationStep, setGenerationStep] = useState<number>(0);

  const steps = [
    "Reading project requirements",
    "Loading component placement",
    "Building engineering visualization prompt",
    "Generating PCB image",
    "Validating image",
    "Complete",
  ];

  const handleGenerate = async () => {
    if (!currentProjId) return;

    setIsGenerating(true);
    setGenerationStep(0);
    setErrorMessage(null);

    // Stage progression ticker
    const timer1 = setTimeout(() => setGenerationStep(1), 300);
    const timer2 = setTimeout(() => setGenerationStep(2), 700);
    const timer3 = setTimeout(() => setGenerationStep(3), 1200);

    try {
      const payload = {
        project_id: currentProjId,
        project_name: projectName || currentProjId,
        engineering_goal: engineeringGoal || "",
        components: components,
        power_analysis: powerAnalysis,
        thermal_analysis: thermalAnalysis,
        board_width: 100.0,
        board_height: 80.0,
      };

      const res = await fetch(`${apiBase}/api/projects/${encodeURIComponent(currentProjId)}/pcb/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      setGenerationStep(4);

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({ detail: "Generation failed" }));
        throw new Error(errJson.detail || "PCB layout visualization generation failed.");
      }

      const generated = await res.json();
      setGenerationStep(5);
      setVisRecord(generated);
    } catch (err: any) {
      setErrorMessage(err.message || "PCB visualization generation encountered an unexpected error.");
    } finally {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      setIsGenerating(false);
    }
  };

  const hasContext = Boolean(currentProjId && (components.length > 0 || engineeringGoal));

  return (
    <div className="glass-panel p-5 border border-zinc-800 bg-zinc-950/70 rounded-xl space-y-5">
      {/* Header & Architectural Disclaimer */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-zinc-850 pb-3">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 bg-emerald-950/40 border border-emerald-800/50 rounded text-emerald-400">
            <CircuitBoard className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <h3 className="text-base font-mono font-bold tracking-wider text-slate-100 uppercase">
              PCB LAYOUT VISUALIZATION
            </h3>
            <p className="text-xs font-mono text-slate-400">
              True 2D orthographic top-down layout visualization powered by PaperBanana.
            </p>
          </div>
        </div>

        {/* Disclaimer Pill */}
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-900 border border-slate-800 text-[10px] font-mono text-slate-400">
          <Shield className="w-3.5 h-3.5 text-cyan-400" />
          <span>VISUALIZATION ONLY · AUTHORITATIVE CAD IN STRUCTURED DATA</span>
        </div>
      </div>

      {/* Main Visualizer Area */}
      <div className="relative w-full rounded-lg border border-zinc-800 bg-zinc-950/90 overflow-hidden flex flex-col items-center justify-center min-h-[380px] p-2">
        {isGenerating ? (
          <div className="flex flex-col items-center justify-center p-8 space-y-5 text-center max-w-lg">
            <RefreshCw className="w-10 h-10 text-emerald-400 animate-spin mx-auto" />
            <div className="space-y-2">
              <div className="text-sm font-mono font-bold text-slate-200 tracking-wider">
                Generating 2D PCB Layout
              </div>
              <div className="bg-zinc-900/80 border border-zinc-800 rounded-lg p-3 text-left space-y-1.5 font-mono text-xs">
                {steps.map((s, idx) => (
                  <div
                    key={idx}
                    className={`flex items-center gap-2 ${
                      idx < generationStep
                        ? "text-emerald-400"
                        : idx === generationStep
                        ? "text-cyan-300 font-bold"
                        : "text-slate-600"
                    }`}
                  >
                    <span>{idx < generationStep ? "✓" : "→"}</span>
                    <span>{s}</span>
                    {idx === generationStep && <span className="animate-pulse">...</span>}
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : errorMessage ? (

          <div className="flex flex-col items-center justify-center p-8 space-y-4 text-center">
            <AlertTriangle className="w-10 h-10 text-rose-500" />
            <div className="space-y-1">
              <div className="text-sm font-mono font-bold text-rose-400 tracking-wider">
                PCB VISUALIZATION FAILED
              </div>
              <p className="text-xs font-mono text-slate-400 max-w-md">
                {errorMessage}
              </p>
            </div>
            <button
              onClick={handleGenerate}
              className="px-4 py-1.5 bg-rose-900/50 hover:bg-rose-800/60 border border-rose-700 text-rose-200 text-xs font-mono font-bold rounded cursor-pointer transition-colors"
            >
              Retry Generation
            </button>
          </div>
        ) : visRecord && (visRecord.image_data || visRecord.image_url) ? (
          <div className="w-full flex flex-col items-center justify-center space-y-2">
            {visRecord.image_data && visRecord.image_data.includes("<svg") ? (
              <div
                className="w-full max-h-[500px] overflow-hidden rounded flex items-center justify-center"
                dangerouslySetInnerHTML={{ __html: visRecord.image_data }}
              />
            ) : (
              <img
                src={visRecord.image_url || `data:image/svg+xml;utf8,${encodeURIComponent(visRecord.image_data || "")}`}
                alt="PaperBanana PCB Layout"
                className="w-full max-h-[500px] object-contain rounded"
              />
            )}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center p-8 space-y-3 text-center">
            <Layers className="w-10 h-10 text-slate-700" />
            <div className="text-sm font-mono font-bold text-slate-400 uppercase tracking-wider">
              No PCB Visualization Generated
            </div>
            <p className="text-xs font-mono text-slate-500 max-w-md">
              Generate a project-grounded PCB layout diagram showing component placement, power rails, and copper routing for [{projectName || currentProjId || "Active Project"}].
            </p>
          </div>
        )}
      </div>

      {/* Metadata & Controls Bar */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 rounded-lg bg-zinc-900/40 border border-zinc-850 text-xs font-mono">
        <div className="space-y-1">
          <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Project</div>
          <div className="text-slate-200 font-bold truncate">{projectName || currentProjId || "—"}</div>
        </div>

        <div className="space-y-1">
          <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Board Status</div>
          <div className="flex items-center gap-1.5">
            <span className={`w-2 h-2 rounded-full ${visRecord?.status === "COMPLETED" ? "bg-emerald-400" : isGenerating ? "bg-amber-400 animate-ping" : "bg-slate-500"}`} />
            <span className="text-slate-300 font-semibold">
              {isGenerating ? "Generating..." : visRecord?.status === "COMPLETED" ? "Generated" : "Not Generated"}
            </span>
          </div>
        </div>

        <div className="space-y-1">
          <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Components / Model</div>
          <div className="text-slate-300">
            <span className="text-indigo-400 font-bold">{visRecord?.metadata?.components_count ?? components.length}</span> Parts · <span className="text-emerald-400 font-semibold">PaperBanana</span>
          </div>
        </div>

        <div className="space-y-1">
          <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Generated Timestamp</div>
          <div className="text-slate-400 truncate">
            {visRecord?.updated_at ? new Date(visRecord.updated_at).toLocaleString() : "Not yet generated"}
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-wrap items-center justify-end gap-3 pt-1 border-t border-zinc-850">
        <button
          onClick={() => {
            if (currentProjId) {
              setIsLoading(true);
              fetch(`${apiBase}/api/projects/${encodeURIComponent(currentProjId)}/pcb/visualization`)
                .then((r) => (r.ok ? r.json() : null))
                .then((d) => setVisRecord(d))
                .catch(() => {})
                .finally(() => setIsLoading(false));
            }
          }}
          disabled={isLoading || isGenerating}
          className="px-3 py-2 bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 rounded text-xs font-mono flex items-center gap-1.5 cursor-pointer disabled:opacity-50 transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin" : ""}`} />
          <span>Refresh</span>
        </button>

        {visRecord ? (
          <button
            onClick={handleGenerate}
            disabled={isGenerating || !hasContext}
            className="px-4 py-2 bg-amber-600 hover:bg-amber-500 text-white rounded text-xs font-mono font-bold flex items-center gap-1.5 cursor-pointer disabled:opacity-50 transition-colors shadow-sm"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>{isGenerating ? "Regenerating..." : "Regenerate"}</span>
          </button>
        ) : (
          <button
            onClick={handleGenerate}
            disabled={isGenerating || !hasContext}
            className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded text-xs font-mono font-bold flex items-center gap-1.5 cursor-pointer disabled:opacity-50 transition-colors shadow-sm"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>{isGenerating ? "Generating..." : "Generate PCB Visualization"}</span>
          </button>
        )}
      </div>
    </div>
  );
};
