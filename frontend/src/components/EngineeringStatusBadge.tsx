"use client";

import React from "react";
import {
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Loader2,
  Clock,
  Ban,
  HelpCircle,
  ShieldAlert,
  AlertOctagon,
} from "lucide-react";

export type EngineeringStatus =
  | "PASS"
  | "FAIL"
  | "WARNING"
  | "RUNNING"
  | "PENDING"
  | "BLOCKED"
  | "UNKNOWN"
  | "MOCKED"
  | "NOT_CONFIGURED"
  | "RESOLVED"
  | "UNRESOLVED"
  | "CONFLICT";

interface EngineeringStatusBadgeProps {
  status: EngineeringStatus | string;
  label?: string;
  size?: "sm" | "md" | "lg";
  className?: string;
}

export const EngineeringStatusBadge: React.FC<EngineeringStatusBadgeProps> = ({
  status,
  label,
  size = "md",
  className = "",
}) => {
  const normStatus = (status || "UNKNOWN").toUpperCase();

  let statusClass = "status-unknown";
  let Icon = HelpCircle;
  let defaultLabel = normStatus;

  switch (normStatus) {
    case "PASS":
    case "RESOLVED":
    case "VERIFIED":
      statusClass = "status-pass";
      Icon = CheckCircle2;
      defaultLabel = "PASS";
      break;
    case "FAIL":
    case "ERROR":
    case "VIOLATION":
      statusClass = "status-fail";
      Icon = XCircle;
      defaultLabel = "FAIL";
      break;
    case "WARNING":
    case "DERATED":
    case "CONFLICT":
      statusClass = "status-warning";
      Icon = AlertTriangle;
      defaultLabel = "WARNING";
      break;
    case "RUNNING":
    case "EXECUTING":
    case "SOLVING":
      statusClass = "status-running";
      Icon = Loader2;
      defaultLabel = "RUNNING";
      break;
    case "PENDING":
    case "QUEUED":
      statusClass = "status-pending";
      Icon = Clock;
      defaultLabel = "PENDING";
      break;
    case "BLOCKED":
    case "HALTED":
      statusClass = "status-blocked";
      Icon = Ban;
      defaultLabel = "BLOCKED";
      break;
    case "MOCKED":
    case "SYNTHETIC":
      statusClass = "status-mocked";
      Icon = ShieldAlert;
      defaultLabel = "MOCKED";
      break;
    case "NOT_CONFIGURED":
    case "UNCONFIGURED":
      statusClass = "status-not-configured";
      Icon = AlertOctagon;
      defaultLabel = "NOT_CONFIGURED";
      break;
    default:
      statusClass = "status-unknown";
      Icon = HelpCircle;
      defaultLabel = normStatus;
  }

  const iconSizes = {
    sm: "w-3 h-3",
    md: "w-3.5 h-3.5",
    lg: "w-4 h-4",
  };

  const textSizes = {
    sm: "text-[10px] px-1.5 py-0.5",
    md: "text-[11px] px-2 py-0.5",
    lg: "text-xs px-2.5 py-1",
  };

  return (
    <span
      className={`status-badge ${statusClass} ${textSizes[size]} font-mono inline-flex items-center gap-1.5 rounded-md font-semibold tracking-wider ${className}`}
      role="status"
      aria-label={`Status: ${label || defaultLabel}`}
    >
      <Icon className={`${iconSizes[size]} ${normStatus === "RUNNING" ? "animate-spin" : ""}`} aria-hidden="true" />
      <span>{label || defaultLabel}</span>
    </span>
  );
};

export default EngineeringStatusBadge;
