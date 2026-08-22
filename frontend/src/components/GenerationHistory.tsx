"use client";

import React from "react";
import { History, Image as ImageIcon, Presentation, ExternalLink, Hash } from "lucide-react";

export interface GenerationArtifactSummary {
  artifact_id: string;
  project_id: string;
  format: string;
  provider: string;
  created_at: string;
  sha256: string;
  title?: string;
  filename?: string;
}

interface GenerationHistoryProps {
  artifacts: GenerationArtifactSummary[];
  onSelectArtifact?: (artifactId: string) => void;
}

export const GenerationHistory: React.FC<GenerationHistoryProps> = ({
  artifacts,
  onSelectArtifact,
}) => {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4">
      <div className="flex items-center gap-2">
        <History className="w-5 h-5 text-indigo-400" />
        <h3 className="text-base font-bold text-zinc-100">Generation Artifact History & Provenance</h3>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-zinc-300">
          <thead className="bg-zinc-950/80 text-zinc-400 uppercase font-mono border-b border-zinc-800">
            <tr>
              <th className="px-3 py-2">Type</th>
              <th className="px-3 py-2">Artifact ID</th>
              <th className="px-3 py-2">Title / Filename</th>
              <th className="px-3 py-2">Provider</th>
              <th className="px-3 py-2">SHA-256</th>
              <th className="px-3 py-2 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800/60 font-mono">
            {artifacts.length === 0 ? (
              <tr>
                <td colSpan={6} className="text-center py-6 text-zinc-500">
                  No generated visuals or presentations in this project.
                </td>
              </tr>
            ) : (
              artifacts.map((art) => {
                const isImg = art.format === "svg" || art.format === "png";
                return (
                  <tr key={art.artifact_id} className="hover:bg-zinc-950/40">
                    <td className="px-3 py-2.5">
                      {isImg ? (
                        <ImageIcon className="w-4 h-4 text-emerald-400" />
                      ) : (
                        <Presentation className="w-4 h-4 text-purple-400" />
                      )}
                    </td>
                    <td className="px-3 py-2.5 font-semibold text-zinc-200">{art.artifact_id}</td>
                    <td className="px-3 py-2.5 text-zinc-300 truncate max-w-[200px]">
                      {art.title || art.filename}
                    </td>
                    <td className="px-3 py-2.5 text-zinc-400">{art.provider}</td>
                    <td className="px-3 py-2.5 text-zinc-500 text-[11px]">
                      {art.sha256.slice(0, 10)}...
                    </td>
                    <td className="px-3 py-2.5 text-right">
                      {onSelectArtifact && (
                        <button
                          onClick={() => onSelectArtifact(art.artifact_id)}
                          className="px-2 py-1 text-[11px] rounded bg-indigo-950 text-indigo-300 hover:bg-indigo-900 border border-indigo-800 transition"
                        >
                          Preview
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
