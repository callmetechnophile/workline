"use client";

import React, { useState } from "react";
import { Sliders, Plus, Trash2, ShieldAlert } from "lucide-react";

export interface ConstraintItem {
  constraintId: string;
  property: string;
  operator: string;
  requiredValue: string;
  dimension?: string;
  unit?: string;
  severity?: "CRITICAL" | "ERROR" | "WARNING" | "INFO";
  requirementId?: string;
  source?: string;
}

interface ConstraintEditorProps {
  constraints?: ConstraintItem[];
  onChangeConstraints?: (updated: ConstraintItem[]) => void;
  availableRequirementIds?: string[];
}

export const ConstraintEditor: React.FC<ConstraintEditorProps> = ({
  constraints = [],
  onChangeConstraints,
  availableRequirementIds = [],
}) => {
  const [property, setProperty] = useState("output_voltage");
  const [operator, setOperator] = useState(">=");
  const [value, setValue] = useState("");
  const [unit, setUnit] = useState("V");
  const [severity, setSeverity] = useState<"CRITICAL" | "ERROR" | "WARNING" | "INFO">("CRITICAL");
  const [linkedReq, setLinkedReq] = useState("");

  const handleAdd = () => {
    if (!value.trim()) return;
    const newConstraint: ConstraintItem = {
      constraintId: `con_${Date.now()}`,
      property,
      operator,
      requiredValue: value,
      unit: unit || undefined,
      dimension: property.includes("current") ? "CURRENT" : property.includes("temp") ? "TEMPERATURE" : "VOLTAGE",
      severity,
      requirementId: linkedReq || undefined,
    };
    if (onChangeConstraints) {
      onChangeConstraints([...constraints, newConstraint]);
    }
    setValue("");
  };

  const handleRemove = (id: string) => {
    if (onChangeConstraints) {
      onChangeConstraints(constraints.filter((c) => c.constraintId !== id));
    }
  };

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 flex flex-col gap-4 text-slate-100 shadow-xl">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Sliders className="w-5 h-5 text-indigo-400" />
          <h3 className="text-sm font-bold text-slate-100 uppercase font-mono tracking-wide">
            Design Constraints & Boundary Rules
          </h3>
        </div>
        <span className="text-[11px] font-mono text-slate-500">
          {constraints.length} Configured Limits
        </span>
      </div>

      {/* Add Constraint Row */}
      <div className="grid grid-cols-1 sm:grid-cols-6 gap-2 bg-slate-950 p-3 rounded-lg border border-slate-800">
        <div className="sm:col-span-2 space-y-1">
          <label className="text-[10px] font-mono text-slate-500 uppercase">Parameter</label>
          <input
            type="text"
            value={property}
            onChange={(e) => setProperty(e.target.value)}
            placeholder="e.g. output_voltage"
            className="w-full bg-slate-900 border border-slate-700 rounded p-1.5 text-xs text-slate-200 font-mono"
          />
        </div>

        <div className="space-y-1">
          <label className="text-[10px] font-mono text-slate-500 uppercase">Operator</label>
          <select
            value={operator}
            onChange={(e) => setOperator(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded p-1.5 text-xs text-indigo-300 font-mono font-bold"
          >
            <option value="=">=</option>
            <option value="!=">!=</option>
            <option value=">">&gt;</option>
            <option value=">=">&gt;=</option>
            <option value="<">&lt;</option>
            <option value="<=">&lt;=</option>
            <option value="RANGE">RANGE</option>
            <option value="IN">IN</option>
            <option value="NOT IN">NOT IN</option>
          </select>
        </div>

        <div className="space-y-1">
          <label className="text-[10px] font-mono text-slate-500 uppercase">Value</label>
          <input
            type="text"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            placeholder="e.g. 12"
            className="w-full bg-slate-900 border border-slate-700 rounded p-1.5 text-xs text-slate-200 font-mono"
          />
        </div>

        <div className="space-y-1">
          <label className="text-[10px] font-mono text-slate-500 uppercase">Unit</label>
          <input
            type="text"
            value={unit}
            onChange={(e) => setUnit(e.target.value)}
            placeholder="e.g. V, A, °C"
            className="w-full bg-slate-900 border border-slate-700 rounded p-1.5 text-xs text-slate-200 font-mono"
          />
        </div>

        <div className="flex items-end">
          <button
            onClick={handleAdd}
            className="w-full flex items-center justify-center gap-1 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-xs font-semibold py-1.5 transition cursor-pointer shadow"
          >
            <Plus className="w-4 h-4" />
            <span>Add</span>
          </button>
        </div>
      </div>

      {/* Constraints List */}
      {constraints.length === 0 ? (
        <div className="py-6 text-center text-xs text-slate-500 font-mono">
          No design constraints configured. Add parameter boundaries above to constrain the engineering search space.
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          {constraints.map((c) => (
            <div
              key={c.constraintId}
              className="flex items-center justify-between p-3 bg-slate-950/80 border border-slate-800 rounded-lg text-xs font-mono hover:border-slate-700 transition"
            >
              <div className="flex items-center gap-3 flex-wrap">
                <span className="font-bold text-slate-200">{c.property}</span>
                <span className="text-indigo-400 font-bold px-1.5 py-0.5 bg-indigo-950/80 rounded border border-indigo-800/40">
                  {c.operator}
                </span>
                <span className="text-emerald-400 font-bold">
                  {c.requiredValue} {c.unit || ""}
                </span>
                {c.requirementId && (
                  <span className="text-[10px] text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                    Linked: {c.requirementId}
                  </span>
                )}
                {c.severity && (
                  <span
                    className={`text-[9px] px-1.5 py-0.5 rounded border font-bold ${
                      c.severity === "CRITICAL"
                        ? "bg-rose-950/60 text-rose-300 border-rose-800/50"
                        : "bg-amber-950/60 text-amber-300 border-amber-800/50"
                    }`}
                  >
                    {c.severity}
                  </span>
                )}
              </div>
              <button
                onClick={() => handleRemove(c.constraintId)}
                className="text-slate-500 hover:text-rose-400 p-1 cursor-pointer transition"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
