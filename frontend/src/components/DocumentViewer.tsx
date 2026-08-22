"use client";

import React from "react";
import { FileText, Table as TableIcon, Bookmark } from "lucide-react";

export interface TableData {
  tableId: string;
  pageNumber: number;
  sectionTitle: string;
  headers: string[];
  rows: string[][];
  caption?: string;
}

export interface SectionData {
  sectionId: string;
  heading: string;
  level: number;
  pageNumber: number;
  paragraphs: string[];
  tables: TableData[];
}

export interface DocumentViewerProps {
  documentId?: string;
  title?: string;
  sections?: SectionData[];
}

export const DocumentViewer: React.FC<DocumentViewerProps> = ({
  documentId = "DOC-101",
  title = "TPS62130 3A Step-Down Converter Datasheet",
  sections = [
    {
      sectionId: "sec_1",
      heading: "Electrical Characteristics",
      level: 1,
      pageNumber: 3,
      paragraphs: [
        "Operating junction temperature range: -40°C to 125°C. Supply voltage range VIN = 3V to 17V.",
        "Output current continuous: 3A maximum across all specified conditions.",
      ],
      tables: [
        {
          tableId: "tbl_1",
          pageNumber: 3,
          sectionTitle: "Electrical Characteristics",
          headers: ["Parameter", "Min", "Typ", "Max", "Unit"],
          rows: [
            ["Input Voltage (VIN)", "3.0", "-", "17.0", "V"],
            ["Output Current (IOUT)", "-", "-", "3.0", "A"],
            ["Quiescent Current", "-", "17", "30", "uA"],
          ],
          caption: "Electrical Specifications (VIN = 12V, TA = 25°C)",
        },
      ],
    },
  ],
}) => {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-5 text-zinc-100">
      <div className="flex items-center justify-between pb-3 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <FileText className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-zinc-100">{title}</h3>
        </div>
        <span className="px-2.5 py-0.5 rounded text-xs font-mono bg-zinc-800 text-zinc-400 border border-zinc-700">
          Docling Structural View ({documentId})
        </span>
      </div>

      <div className="flex flex-col gap-6">
        {sections.map((sec) => (
          <div key={sec.sectionId} className="flex flex-col gap-3">
            <div className="flex items-center justify-between">
              <h4
                className={`font-bold text-zinc-100 ${
                  sec.level === 1 ? "text-sm text-indigo-300" : "text-xs text-zinc-300"
                }`}
              >
                {sec.heading}
              </h4>
              <span className="flex items-center gap-1 text-[11px] font-mono text-zinc-500 bg-zinc-950 px-2 py-0.5 rounded border border-zinc-800">
                <Bookmark className="w-3 h-3 text-indigo-400" />
                Page {sec.pageNumber}
              </span>
            </div>

            {sec.paragraphs.map((p, idx) => (
              <p key={idx} className="text-xs text-zinc-300 leading-relaxed pl-2 border-l-2 border-zinc-800">
                {p}
              </p>
            ))}

            {sec.tables.map((tbl) => (
              <div key={tbl.tableId} className="mt-2 bg-zinc-950/70 border border-zinc-800 rounded-lg p-3">
                <div className="flex items-center gap-1.5 text-xs font-semibold text-zinc-300 mb-2">
                  <TableIcon className="w-3.5 h-3.5 text-purple-400" />
                  <span>{tbl.caption || `Table: ${tbl.sectionTitle}`}</span>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs font-mono">
                    <thead>
                      <tr className="border-b border-zinc-800 text-zinc-400">
                        {tbl.headers.map((h, i) => (
                          <th key={i} className="pb-1.5 px-2 font-semibold">
                            {h}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {tbl.rows.map((row, rIdx) => (
                        <tr key={rIdx} className="border-b border-zinc-900 hover:bg-zinc-900/50">
                          {row.map((cell, cIdx) => (
                            <td key={cIdx} className="py-1 px-2 text-zinc-300">
                              {cell}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
};
