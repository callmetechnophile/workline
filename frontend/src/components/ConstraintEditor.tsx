"use client";

import React, { useState } from "react";
import { Sliders, Plus, Trash2 } from "lucide-react";
import { ConstraintItem } from "./RequirementPanel";

interface ConstraintEditorProps {
  constraints?: ConstraintItem[];
  onChangeConstraints?: (updated: ConstraintItem[]) => void;
}

export const ConstraintEditor: React.FC<ConstraintEditorProps> = ({
  constraints = [],
  onChangeConstraints,
}) => {
  const [property, setProperty] = useState("");
  const [operator, setOperator] = useState("");
  const [value, setValue] = useState("");

  const handleAdd = () => {
    if (!value.trim()) return;
    const newConstraint: ConstraintItem = {
      constraintId: `c_${Date.now()}`,
      property,
      operator,
      requiredValue: value,
      dimension: property.includes("current") ? "CURRENT" : "VOLTAGE",
    };
    if (onChangeConstraints) {
      onChangeConstraints([...constraints, newConstraint]);
    }
  };

  const handleRemove = (id: string) => {
    if (onChangeConstraints) {
      onChangeConstraints(constraints.filter((c) => c.constraintId !== id));
    }
  };

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4 text-zinc-100">
      <div className="flex items-center gap-2 pb-2 border-b border-zinc-800">
        <Sliders className="w-5 h-5 text-indigo-400" />
        <h3 className="text-base font-bold text-zinc-100">Constraint Editor</h3>
      </div>

      <div className="grid grid-cols-4 gap-2">
        <select
          value={property}
          onChange={(e) => setProperty(e.target.value)}
          className="bg-zinc-950 border border-zinc-800 rounded p-2 text-xs text-zinc-200"
        >
          <option value="output_voltage">output_voltage</option>
          <option value="input_voltage">input_voltage</option>
          <option value="output_current">output_current</option>
          <option value="operating_temp">operating_temp</option>
          <option value="efficiency">efficiency</option>
        </select>

        <select
          value={operator}
          onChange={(e) => setOperator(e.target.value)}
          className="bg-zinc-950 border border-zinc-800 rounded p-2 text-xs text-zinc-200 font-mono"
        >
          <option value="=">=</option>
          <option value=">=">&gt;=</option>
          <option value="<=">&lt;=</option>
          <option value=">">&gt;</option>
          <option value="<">&lt;</option>
          <option value="!=">!=</option>
        </select>

        <input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="e.g. 3.3V, 2A"
          className="bg-zinc-950 border border-zinc-800 rounded p-2 text-xs text-zinc-200"
        />

        <button
          onClick={handleAdd}
          className="flex items-center justify-center gap-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-xs font-semibold py-2 transition"
        >
          <Plus className="w-4 h-4" />
          Add
        </button>
      </div>

      <div className="flex flex-col gap-2 pt-2">
        {constraints.map((c) => (
          <div
            key={c.constraintId}
            className="flex items-center justify-between p-2.5 bg-zinc-950 border border-zinc-800 rounded text-xs font-mono"
          >
            <div className="flex items-center gap-2">
              <span className="font-bold text-zinc-200">{c.property}</span>
              <span className="text-indigo-400 font-bold">{c.operator}</span>
              <span className="text-emerald-400 font-bold">{c.requiredValue}</span>
              <span className="text-[10px] text-zinc-500">({c.dimension})</span>
            </div>
            <button
              onClick={() => handleRemove(c.constraintId)}
              className="text-rose-400 hover:text-rose-200 p-1"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};
