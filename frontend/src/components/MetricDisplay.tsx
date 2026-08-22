"use client";

import React from "react";

interface MetricDisplayProps {
  label: string;
  value: string | number;
  unit?: string;
  subtext?: string;
  status?: "default" | "success" | "warning" | "error" | "info";
  className?: string;
}

export const MetricDisplay: React.FC<MetricDisplayProps> = ({
  label,
  value,
  unit,
  subtext,
  status = "default",
  className = "",
}) => {
  const statusColors = {
    default: "text-foreground",
    success: "text-emerald-400",
    warning: "text-amber-400",
    error: "text-rose-400",
    info: "text-cyan-400",
  };

  return (
    <div className={`flex flex-col p-3 rounded-lg bg-surface border border-border ${className}`}>
      <span className="text-[11px] font-medium uppercase tracking-wider text-muted-foreground">
        {label}
      </span>
      <div className="flex items-baseline gap-1 mt-1">
        <span className={`text-lg font-bold font-mono font-tabular ${statusColors[status]}`}>
          {value}
        </span>
        {unit && (
          <span className="text-xs font-mono font-medium text-muted-foreground">
            {unit}
          </span>
        )}
      </div>
      {subtext && (
        <span className="text-[10px] text-muted-foreground mt-0.5 font-mono">
          {subtext}
        </span>
      )}
    </div>
  );
};

export default MetricDisplay;
