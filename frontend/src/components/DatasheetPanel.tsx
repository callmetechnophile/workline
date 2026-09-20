"use client";

import React from "react";
import { 
  FileText, 
  ShieldCheck, 
  ExternalLink, 
  AlertCircle, 
  Download,
  CheckCircle,
  HelpCircle,
  Zap,
  RefreshCw,
  Cpu
} from "lucide-react";

export interface SingleDatasheet {
  datasheet_id?: string;
  url: string;
  manufacturer?: string;
  mpn?: string;
  title?: string;
  document_type?: string;
  verification_status?: string;
  extracted_text_chunks?: string[];
  component_name?: string;
  status?: string;
  highlights?: string[];
}

interface DatasheetPanelProps {
  datasheet?: SingleDatasheet;
  datasheets?: SingleDatasheet[];
  onFetchDatasheets?: () => void;
  isGenerating?: boolean;
}

export const DatasheetPanel: React.FC<DatasheetPanelProps> = ({
  datasheet,
  datasheets,
  onFetchDatasheets,
  isGenerating = false,
}) => {
  const list: SingleDatasheet[] = datasheets || (datasheet ? [datasheet] : []);

  if (list.length === 0) {
    return (
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-8 shadow-2xl text-center space-y-4">
        <div className="w-12 h-12 rounded-2xl bg-cyan-950/50 border border-cyan-700/40 flex items-center justify-center mx-auto text-cyan-400">
          <FileText className="w-6 h-6" />
        </div>
        <div className="max-w-md mx-auto space-y-1.5">
          <h4 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-mono">
            No Technical Datasheets Linked
          </h4>
          <p className="text-xs text-slate-400 leading-relaxed">
            Technical datasheets define electrical voltage/current thresholds, thermal ratings, and hardware pinouts. Access manufacturer datasheets through the Octopart / Nexar API.
          </p>
        </div>
        {onFetchDatasheets && (
          <div className="pt-2">
            <button
              onClick={onFetchDatasheets}
              disabled={isGenerating}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white text-xs font-bold font-mono transition-all cursor-pointer shadow-lg shadow-cyan-950/50"
            >
              {isGenerating ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  <span>Accessing Nexar Catalog...</span>
                </>
              ) : (
                <>
                  <Zap className="w-3.5 h-3.5" />
                  <span>Fetch Component Datasheets (Nexar API)</span>
                </>
              )}
            </button>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-2xl backdrop-blur-md space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3 flex-wrap gap-2">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-indigo-500/10 border border-indigo-500/20 rounded-lg text-indigo-400">
            <FileText className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-slate-100">Component Datasheets</h3>
            <p className="text-xs text-slate-400">Verified Technical Documents & Pinouts (Octopart / Nexar)</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {onFetchDatasheets && (
            <button
              onClick={onFetchDatasheets}
              disabled={isGenerating}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-cyan-400 text-xs font-mono font-semibold transition border border-zinc-700 cursor-pointer"
              title="Re-query Nexar for latest datasheets"
            >
              <RefreshCw className={`w-3 h-3 ${isGenerating ? 'animate-spin' : ''}`} />
              <span>Sync Datasheets</span>
            </button>
          )}
          <span className="text-xs text-slate-400 font-medium px-2 py-1 bg-slate-950 rounded border border-slate-800">
            {list.length} {list.length === 1 ? "document" : "documents"}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {list.map((ds, idx) => {
          const isVerified = (ds.verification_status || ds.status) === "VERIFIED" || (ds.verification_status || ds.status) === "Verified";
          const title = ds.title || ds.component_name || `${ds.manufacturer || ''} ${ds.mpn || ''}`.trim() || "Technical Datasheet";
          const docType = ds.document_type || "PDF Document";

          return (
            <div key={idx} className="bg-slate-950/60 p-3.5 rounded-lg border border-slate-800 flex flex-col justify-between space-y-2">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <h4 className="text-xs font-semibold text-slate-200">{title}</h4>
                  <p className="text-[10px] text-slate-400">{ds.manufacturer} {ds.mpn && `• ${ds.mpn}`}</p>
                </div>
                <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold shrink-0 ${
                  isVerified
                    ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                    : "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                }`}>
                  {isVerified ? <ShieldCheck className="w-3 h-3" /> : <HelpCircle className="w-3 h-3" />}
                  {ds.verification_status || ds.status || "VERIFIED"}
                </span>
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-slate-800/60 text-[11px] text-slate-400">
                <span className="font-mono">{docType}</span>
                {ds.url ? (
                  <a
                    href={ds.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-cyan-400 hover:text-cyan-300 inline-flex items-center gap-1 font-medium bg-slate-900 px-2.5 py-1 rounded border border-slate-800 hover:border-cyan-500/50 transition-all"
                  >
                    {docType.toLowerCase().includes("datasheet") ? "Open Datasheet" : "Open Document"} <ExternalLink className="w-3 h-3" />
                  </a>
                ) : (
                  <span className="text-slate-500">No URL</span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default DatasheetPanel;
