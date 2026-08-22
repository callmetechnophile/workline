"use client";

import React from "react";
import { Bookmark } from "lucide-react";
import { EngineeringStatusBadge } from "./EngineeringStatusBadge";

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
  return (
    <div className="bg-surface border border-border rounded-lg p-5 flex flex-col gap-4 text-foreground">
      <div className="flex items-center justify-between pb-3 border-b border-border">
        <div>
          <h3 className="text-base font-bold text-foreground">Deterministic Engineering Validation</h3>
          <span className="text-xs text-muted-foreground font-mono">
            Candidate: <strong className="text-foreground">{candidateId}</strong> against <strong className="text-foreground">{requirementId}</strong>
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-mono text-muted-foreground">{ruleVersion}</span>
          <EngineeringStatusBadge status={overallStatus} size="md" />
        </div>
      </div>

      <div className="flex flex-col gap-2.5">
        {constraintResults.map((cr) => (
          <div
            key={cr.constraintId}
            className="p-3 bg-surface-secondary/40 border border-border rounded-lg flex flex-col gap-1.5 text-xs font-mono"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="font-bold text-foreground">{cr.property}</span>
                <span className="text-muted-foreground font-normal">Req: {cr.requiredValue}</span>
                <span className="text-emerald-400 font-bold">Act: {cr.actualValue}</span>
              </div>
              <div className="flex items-center gap-2">
                {cr.sourceDocument && (
                  <span className="flex items-center gap-1 text-[10px] text-muted-foreground bg-surface px-1.5 py-0.5 rounded border border-border">
                    <Bookmark className="w-2.5 h-2.5" />
                    P.{cr.page}
                  </span>
                )}
                <EngineeringStatusBadge status={cr.status} size="sm" />
              </div>
            </div>
            <p className="text-[11px] text-muted-foreground italic pl-2 border-l-2 border-border">{cr.reason}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
