"use client";

import React from "react";
import { AlertTriangle, ExternalLink } from "lucide-react";

interface ConflictWarningProps {
  conflicts?: string[];
  onReview?: () => void;
}

export const ConflictWarning: React.FC<ConflictWarningProps> = ({
  conflicts = [],
  onReview,
}) => {
  if (!conflicts || conflicts.length === 0) return null;

  return (
    <div className="p-4 bg-amber-950/30 border border-amber-800/80 rounded-lg flex items-center justify-between text-amber-200">
      <div className="flex items-center gap-3">
        <AlertTriangle className="w-5 h-5 text-amber-400 flex-shrink-0" />
        <div className="flex flex-col">
          <span className="text-xs font-bold">Conflicting Specifications Detected</span>
          <span className="text-[11px] text-amber-300/80 font-mono">
            {conflicts.length} conflicting claims found across candidate documents.
          </span>
        </div>
      </div>

      {onReview && (
        <button
          onClick={onReview}
          className="px-3 py-1 text-xs font-semibold bg-amber-900/60 hover:bg-amber-800/60 text-amber-100 rounded border border-amber-700 transition"
        >
          Review Sources
        </button>
      )}
    </div>
  );
};
