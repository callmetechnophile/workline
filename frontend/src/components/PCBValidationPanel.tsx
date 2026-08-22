"use client";

import React from "react";
import { ShieldCheck, AlertTriangle, XCircle, CheckCircle2, RefreshCw } from "lucide-react";

export interface ViolationData {
  violation_id: string;
  category: string;
  severity: "PASS" | "WARN" | "FAIL";
  component?: string;
  net?: string;
  description: string;
  evidence: string;
  recommendation: string;
}

export interface ValidationReportData {
  status: string;
  passed: boolean;
  summary: string;
  error_count: number;
  warning_count: number;
  violations: ViolationData[];
}

interface PCBValidationPanelProps {
  report: ValidationReportData;
  onRevalidate?: () => Promise<void>;
  isValidating?: boolean;
}

export const PCBValidationPanel: React.FC<PCBValidationPanelProps> = ({
  report,
  onRevalidate,
  isValidating = false,
}) => {
  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-2xl backdrop-blur-md space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg border ${
            report.passed ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400" : "bg-rose-500/10 border-rose-500/20 text-rose-400"
          }`}>
            {report.passed ? <CheckCircle2 className="w-5 h-5" /> : <XCircle className="w-5 h-5" />}
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
              PCB DRC VALIDATION
              <span className={`px-2 py-0.5 rounded text-xs font-semibold ${
                report.passed ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30" : "bg-rose-500/10 text-rose-400 border border-rose-500/30"
              }`}>
                {report.status}
              </span>
            </h3>
            <p className="text-xs text-slate-400">{report.summary}</p>
          </div>
        </div>

        {onRevalidate && (
          <button
            onClick={onRevalidate}
            disabled={isValidating}
            className="px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-1.5 transition-all border border-slate-700 disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isValidating ? "animate-spin" : ""}`} /> Run 12-Check DRC
          </button>
        )}
      </div>

      {/* Violations List */}
      {report.violations.length > 0 ? (
        <div className="space-y-2.5">
          {report.violations.map((v) => (
            <div
              key={v.violation_id}
              className={`p-3.5 rounded-lg border text-xs space-y-1.5 ${
                v.severity === "FAIL"
                  ? "bg-rose-950/30 border-rose-500/30 text-rose-200"
                  : "bg-amber-950/30 border-amber-500/30 text-amber-200"
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className={`px-1.5 py-0.5 rounded font-mono font-bold text-[10px] ${
                    v.severity === "FAIL" ? "bg-rose-500/20 text-rose-400" : "bg-amber-500/20 text-amber-400"
                  }`}>
                    {v.severity}
                  </span>
                  <span className="font-semibold text-slate-100">{v.category}</span>
                  {(v.component || v.net) && (
                    <span className="font-mono text-cyan-300">({v.component || v.net})</span>
                  )}
                </div>
              </div>
              <p className="text-slate-300">{v.description}</p>
              <div className="text-[11px] text-slate-400 bg-slate-950/60 p-2 rounded border border-slate-800/80 space-y-1">
                <div><strong>Evidence:</strong> {v.evidence}</div>
                <div><strong className="text-amber-400">Recommendation:</strong> {v.recommendation}</div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-emerald-500/10 border border-emerald-500/20 p-4 rounded-xl text-center text-xs text-emerald-300">
          <CheckCircle2 className="w-6 h-6 text-emerald-400 mx-auto mb-1.5" />
          Zero DRC Violations! Board boundaries, clearances, netlists, footprints, and thermal ceilings are all compliant.
        </div>
      )}
    </div>
  );
};

export default PCBValidationPanel;
