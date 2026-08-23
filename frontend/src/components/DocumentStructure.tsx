"use client";

import React from "react";
import { Layers, Folder, FileText, Table, Image, ChevronRight } from "lucide-react";
import { SectionData } from "./DocumentViewer";

interface DocumentStructureProps {
  documentId?: string;
  sections?: SectionData[];
  onSelectSection?: (sectionId: string) => void;
}

export const DocumentStructure: React.FC<DocumentStructureProps> = ({
  documentId,
  sections = [],
  onSelectSection,
}) => {
  if (!sections || (Array.isArray(sections) && sections.length === 0)) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-8 text-center">
        <Layers className="w-8 h-8 text-slate-600 mx-auto mb-2" />
        <p className="text-xs text-slate-400">No document structure available.</p>
        <p className="text-[10px] text-slate-500 mt-1">Create or select a project to view document structure.</p>
      </div>
    );
  }
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4 text-zinc-100">
      <div className="flex items-center gap-2 pb-2 border-b border-zinc-800">
        <Layers className="w-5 h-5 text-indigo-400" />
        <h3 className="text-base font-bold text-zinc-100">Document Structure Hierarchy</h3>
      </div>

      <div className="flex flex-col gap-2">
        {sections.map((sec) => (
          <div
            key={sec.sectionId}
            onClick={() => onSelectSection && onSelectSection(sec.sectionId)}
            className="p-3 bg-zinc-950/60 border border-zinc-800 rounded-lg flex flex-col gap-2 hover:border-zinc-700 transition cursor-pointer"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-semibold text-zinc-200">
                <Folder className="w-3.5 h-3.5 text-indigo-400" />
                <span>{sec.heading}</span>
              </div>
              <span className="text-[10px] font-mono text-zinc-500">Page {sec.pageNumber}</span>
            </div>

            <div className="flex items-center gap-3 text-[11px] font-mono text-zinc-400 pl-4 border-l border-zinc-800">
              <span className="flex items-center gap-1">
                <FileText className="w-3 h-3 text-zinc-500" />
                {sec.paragraphs.length} Paragraphs
              </span>
              <span className="flex items-center gap-1">
                <Table className="w-3 h-3 text-purple-400" />
                {sec.tables.length} Tables
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
