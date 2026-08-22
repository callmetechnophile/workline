"use client";

import React from "react";
import { X, Download, Copy, Check } from "lucide-react";

interface ArtifactPreviewProps {
  artifact: any | null;
  onClose: () => void;
}

export const ArtifactPreview: React.FC<ArtifactPreviewProps> = ({ artifact, onClose }) => {
  const [copied, setCopied] = React.useState(false);

  if (!artifact) return null;

  const isSvg = artifact.format === "svg" || artifact.content?.includes("<svg");

  const handleCopy = () => {
    if (artifact.content) {
      navigator.clipboard.writeText(artifact.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
      <div className="bg-zinc-900 border border-zinc-800 rounded-lg w-full max-w-4xl max-h-[85vh] flex flex-col shadow-2xl overflow-hidden">
        <div className="flex items-center justify-between p-4 border-b border-zinc-800 bg-zinc-950/60">
          <div className="flex items-center gap-2 font-mono text-xs">
            <span className="font-bold text-zinc-100">{artifact.artifact_id}</span>
            <span className="text-zinc-500">|</span>
            <span className="text-zinc-400">{artifact.title || artifact.filename}</span>
            <span className="text-zinc-500">({artifact.provider})</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleCopy}
              className="flex items-center gap-1 px-2.5 py-1 text-xs rounded bg-zinc-800 text-zinc-300 hover:bg-zinc-700 transition"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              {copied ? "Copied" : "Copy Content"}
            </button>
            <button
              onClick={onClose}
              className="p-1 text-zinc-400 hover:text-zinc-200 rounded hover:bg-zinc-800 transition"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        <div className="p-5 overflow-y-auto flex-1 bg-zinc-950">
          {isSvg && artifact.content ? (
            <div
              className="w-full flex items-center justify-center rounded-lg border border-zinc-800 p-2 bg-zinc-900"
              dangerouslySetInnerHTML={{ __html: artifact.content }}
            />
          ) : (
            <pre className="text-xs font-mono text-zinc-300 whitespace-pre-wrap">
              {artifact.content || JSON.stringify(artifact, null, 2)}
            </pre>
          )}
        </div>
      </div>
    </div>
  );
};
