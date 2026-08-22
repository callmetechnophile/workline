"use client";

import React, { useState } from "react";
import { FileText, Upload, RefreshCw, Trash2, CheckCircle2, AlertCircle, Layers } from "lucide-react";

export interface DocumentItem {
  documentId: string;
  projectId: string;
  filename: string;
  title: string;
  sourceType: string;
  status: "DISCOVERED" | "INGESTING" | "PARSED" | "ENRICHED" | "INDEXED" | "FAILED" | "STALE";
  sectionsCount: number;
  updatedAt: number;
}

interface DocumentLibraryProps {
  documents?: DocumentItem[];
  selectedDocId?: string;
  onSelectDocument?: (docId: string) => void;
  onIngestFile?: (file: File) => Promise<void>;
  onReindex?: (docId: string) => Promise<void>;
  onDelete?: (docId: string) => Promise<void>;
}

export const DocumentLibrary: React.FC<DocumentLibraryProps> = ({
  documents = [
    {
      documentId: "DOC-101",
      projectId: "rover_v2",
      filename: "TPS62130_Datasheet.pdf",
      title: "TPS62130 3A Step-Down Converter",
      sourceType: "DATASHEET",
      status: "INDEXED",
      sectionsCount: 14,
      updatedAt: Date.now() - 3600000,
    },
    {
      documentId: "DOC-102",
      projectId: "rover_v2",
      filename: "Thermal_Architecture_Paper.pdf",
      title: "PINN Thermal Physics for High-Power PCBs",
      sourceType: "RESEARCH_PAPER",
      status: "INDEXED",
      sectionsCount: 8,
      updatedAt: Date.now() - 7200000,
    },
  ],
  selectedDocId = "DOC-101",
  onSelectDocument,
  onIngestFile,
  onReindex,
  onDelete,
}) => {
  const [isUploading, setIsUploading] = useState(false);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && onIngestFile) {
      setIsUploading(true);
      try {
        await onIngestFile(file);
      } finally {
        setIsUploading(false);
      }
    }
  };

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4 text-zinc-100">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FileText className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-zinc-100">Document Intelligence Library</h3>
        </div>
        <label className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white rounded cursor-pointer transition">
          <Upload className="w-3.5 h-3.5" />
          <span>{isUploading ? "Ingesting..." : "Ingest Document"}</span>
          <input type="file" className="hidden" onChange={handleFileUpload} accept=".pdf,.md,.txt,.html" />
        </label>
      </div>

      <div className="flex flex-col gap-2">
        {documents.map((doc) => {
          const isSelected = doc.documentId === selectedDocId;
          return (
            <div
              key={doc.documentId}
              onClick={() => onSelectDocument && onSelectDocument(doc.documentId)}
              className={`p-3 rounded-lg border transition cursor-pointer flex items-center justify-between ${
                isSelected
                  ? "bg-indigo-950/40 border-indigo-500/80 text-zinc-100"
                  : "bg-zinc-950/60 border-zinc-800 hover:border-zinc-700 text-zinc-300"
              }`}
            >
              <div className="flex items-center gap-3">
                <div className="p-2 rounded bg-zinc-900 border border-zinc-800">
                  <FileText className="w-4 h-4 text-indigo-400" />
                </div>
                <div className="flex flex-col">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold text-zinc-100">{doc.title}</span>
                    <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-zinc-800 text-zinc-400 border border-zinc-700">
                      {doc.sourceType}
                    </span>
                  </div>
                  <span className="text-xs text-zinc-500 font-mono">
                    {doc.documentId} • {doc.filename} • {doc.sectionsCount} sections
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <span
                  className={`flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-mono border ${
                    doc.status === "INDEXED"
                      ? "bg-emerald-950/60 text-emerald-300 border-emerald-800"
                      : "bg-amber-950/60 text-amber-300 border-amber-800"
                  }`}
                >
                  <CheckCircle2 className="w-3 h-3" />
                  {doc.status}
                </span>

                {onReindex && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onReindex(doc.documentId);
                    }}
                    title="Reindex Document"
                    className="p-1.5 text-zinc-400 hover:text-zinc-200 border border-zinc-800 rounded hover:bg-zinc-800 transition"
                  >
                    <RefreshCw className="w-3.5 h-3.5" />
                  </button>
                )}

                {onDelete && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onDelete(doc.documentId);
                    }}
                    title="Delete Document"
                    className="p-1.5 text-rose-400 hover:text-rose-200 border border-zinc-800 rounded hover:bg-rose-950/60 transition"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
