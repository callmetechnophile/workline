"use client";

import React from "react";
import { CheckCircle2, XCircle, HelpCircle, AlertTriangle, ShieldCheck, Bookmark } from "lucide-react";

export interface ConstraintResultItem {
  constraintId: string;
  property: string;
  requiredValue: string;
  actualValue: string;
  operator: string;
  status: "PASS" | "FAIL" | "UNKNOWN" | "CONFLICT" | "NOT_APPLICABLE";
  reason: string;
  sourceDocument?: string;
  page?: number;
}

export interface ValidationResultProps {
  candidateId?: string;
  requirementId?: string;
  overallStatus?: "PASS" | "FAIL" | "UNKNOWN" | "CONFLICT" | "NOT_APPLICABLE";
  constraintResults?: ConstraintResultItem[];
  ruleVersion?: string;
}

export const ValidationResult: React.FC<ValidationResultProps> = ({
  candidateId = "TPS62130",
  requirementId = "REQ-3V3-RAIL",
  overallStatus = "PASS",
  ruleVersion = "electrical_rules_v1",
  constraintResults = [
    {
      constraintId: "c1",
      property: "input_voltage",
      requiredValue: "= 5V",
      actualValue: "5V",
      operator: "=",
      status: "PASS",
      reason: "5V matches required 5V",
      sourceDocument: "TPS62130_Datasheet.pdf",
      page: 1,
    },
    {
      constraintId: "c2",
      property: "output_voltage",
      requiredValue: "= 3.3V",
      actualValue: "3.3V",
      operator: "=",
      status: "PASS",
      reason: "3.3V matches required 3.3V",
      sourceDocument: "TPS62130_Datasheet.pdf",
      page: 1,
    },
    {
      constraintId: "c3",
      property: "output_current",
      requiredValue: ">= 2A",
      actualValue: "3A",
      operator: ">=",
      status: "PASS",
      reason: "3A >= 2A",
      sourceDocument: "TPS62130_Datasheet.pdf",
      page: 1,
    },
  ],
}) => {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case "PASS":
        return <CheckCircle2 className="w-4 h-4 text-emerald-400" />;
      case "FAIL":
        return <XCircle className="w-4 h-4 text-rose-400" />;
      case "CONFLICT":
        return <AlertTriangle className="w-4 h-4 text-amber-400" />;
      default:
        return <HelpCircle className="w-4 h-4 text-zinc-400" />;
    }
  };

  const statusColor =
    overallStatus === "PASS"
      ? "bg-emerald-950/60 text-emerald-300 border-emerald-800"
      : overallStatus === "FAIL"
      ? "bg-rose-950/60 text-rose-300 border-rose-800"
      : "bg-amber-950/60 text-amber-300 border-amber-800";

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4 text-zinc-100">
      <div className="flex items-center justify-between pb-3 border-b border-zinc-800">
        <div>
          <h3 className="text-base font-bold text-zinc-100">Deterministic Engineering Validation</h3>
          <span className="text-xs text-zinc-400 font-mono">
            Candidate: <strong className="text-zinc-200">{candidateId}</strong> against <strong className="text-zinc-200">{requirementId}</strong>
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-mono text-zinc-500">{ruleVersion}</span>
          <span className={`flex items-center gap-1.5 px-3 py-1 rounded text-xs font-bold font-mono border ${statusColor}`}>
            {getStatusIcon(overallStatus)}
            {overallStatus}
          </span>
        </div>
      </div>

      <div className="flex flex-col gap-2.5">
        {constraintResults.map((cr) => (
          <div
            key={cr.constraintId}
            className="p-3 bg-zinc-950/60 border border-zinc-800 rounded-lg flex flex-col gap-1.5 text-xs font-mono"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="font-bold text-zinc-200">{cr.property}</span>
                <span className="text-zinc-500 font-normal">Req: {cr.requiredValue}</span>
                <span className="text-emerald-400 font-bold">Act: {cr.actualValue}</span>
              </div>
              <div className="flex items-center gap-1.5">
                {cr.sourceDocument && (
                  <span className="flex items-center gap-1 text-[10px] text-zinc-500 bg-zinc-900 px-1.5 py-0.5 rounded border border-zinc-800">
                    <Bookmark className="w-2.5 h-2.5" />
                    P.{cr.page}
                  </span>
                )}
                <span className="flex items-center gap-1">
                  {getStatusIcon(cr.status)}
                  {cr.status}
                </span>
              </div>
            </div>
            <p className="text-[11px] text-zinc-400 italic pl-2 border-l-2 border-zinc-800">{cr.reason}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
