"use client";

import React, { useState, useEffect } from "react";
import {
  CheckSquare,
  Sliders,
  ShieldCheck,
  AlertTriangle,
  Plus,
  Trash2,
  FileText,
  Activity,
  Layers,
  Sparkles,
  ArrowRight,
  FolderPlus,
  RefreshCw,
  ExternalLink,
  Info,
  X,
  Loader2,
  Check,
} from "lucide-react";
import { ConstraintEditor, ConstraintItem } from "./ConstraintEditor";
import { ConstraintPanel } from "./ConstraintPanel";
import { EngineeringStatusBadge } from "./EngineeringStatusBadge";
import { useProject } from "@/lib/ProjectContext";

const QUICK_SPEC_CHIPS = [
  "+ 12V / 24V DC Rail",
  "+ 4S LiFePO4 (12.8V)",
  "+ 30A Continuous / 60A Peak",
  "+ Active Cell Balancing",
  "+ I2C / SMBus Telemetry",
  "+ CAN 2.0B Bus",
  "+ -40°C to +85°C Operating Temp",
  "+ Hardware Overcurrent Protection",
  "+ Reverse Polarity Protection",
  "+ IP65 / IP67 Enclosure",
];

export interface RequirementRecord {
  requirement_id: string;
  project_id: string;
  title: string;
  description: string;
  category:
    | "SYSTEM"
    | "FUNCTIONAL"
    | "PERFORMANCE"
    | "ELECTRICAL"
    | "MECHANICAL"
    | "THERMAL"
    | "ENVIRONMENTAL"
    | "INTERFACE"
    | "COMPLIANCE"
    | "COST"
    | "SCHEDULE"
    | "RELIABILITY"
    | "POWER"
    | "OTHER";
  parameter?: string;
  target_value?: string;
  unit?: string;
  priority: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  verification_method: "Simulation" | "Datasheet" | "Analysis" | "Test" | "Inspection";
  source?: string;
  status: "DRAFT" | "ACTIVE" | "VERIFIED" | "FAILED" | "WAIVED";
  created_at?: number;
  updated_at?: number;
}

export interface ValidationMatrixRow {
  requirement_id: string;
  title: string;
  target: string;
  actual: string;
  status: "PASS" | "FAIL" | "WARNING" | "PENDING";
  evidence: string;
  timestamp: string;
}

interface RequirementsWorkspaceProps {
  projectId?: string;
  projectName?: string;
  projectData?: any;
  apiBase?: string;
  onOpenNewProject?: () => void;
  onSelectProject?: () => void;
}

export const RequirementsWorkspace: React.FC<RequirementsWorkspaceProps> = ({
  projectId,
  projectName,
  projectData,
  apiBase = "",
  onOpenNewProject,
  onSelectProject,
}) => {
  const projectContext = useProject();
  const [activeTab, setActiveTab] = useState<"overview" | "requirements" | "constraints" | "validation">("overview");
  const [requirements, setRequirements] = useState<RequirementRecord[]>([]);
  const [constraints, setConstraints] = useState<ConstraintItem[]>([]);
  const [validationRows, setValidationRows] = useState<ValidationMatrixRow[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [isSynthesizing, setIsSynthesizing] = useState<boolean>(false);
  const [isCustomSpecModalOpen, setIsCustomSpecModalOpen] = useState<boolean>(false);
  const [customSpecText, setCustomSpecText] = useState<string>("");
  const [mergeMode, setMergeMode] = useState<"replace" | "append">("append");
  const [feedbackMessage, setFeedbackMessage] = useState<string | null>(null);

  // Form State for Add Requirement
  const [formTitle, setFormTitle] = useState("");
  const [formDesc, setFormDesc] = useState("");
  const [formCategory, setFormCategory] = useState<RequirementRecord["category"]>("ELECTRICAL");
  const [formParam, setFormParam] = useState("");
  const [formTarget, setFormTarget] = useState("");
  const [formUnit, setFormUnit] = useState("");
  const [formPriority, setFormPriority] = useState<RequirementRecord["priority"]>("HIGH");
  const [formVerification, setFormVerification] = useState<RequirementRecord["verification_method"]>("Simulation");
  const [formSource, setFormSource] = useState("System Architecture Spec");

  // Load requirements & constraints from projectData or API
  useEffect(() => {
    if (!projectId) {
      setRequirements([]);
      setConstraints([]);
      setValidationRows([]);
      return;
    }

    // Initialize from projectData if available
    const initialReqs: RequirementRecord[] = [];
    if (projectData?.requirements && Array.isArray(projectData.requirements)) {
      projectData.requirements.forEach((r: any, idx: number) => {
        initialReqs.push({
          requirement_id: r.requirement_id || r.requirementId || `REQ-${String(idx + 1).padStart(3, "0")}`,
          project_id: projectId,
          title: r.title || r.parameter || r.description?.slice(0, 35) || `Requirement ${idx + 1}`,
          description: r.description || r.title || "",
          category: (r.category?.toUpperCase() || "ELECTRICAL") as any,
          parameter: r.parameter || r.property,
          target_value: r.target_value || r.required_value || r.targetValue,
          unit: r.unit || r.required_unit,
          priority: (r.priority?.toUpperCase() || "HIGH") as any,
          verification_method: (r.verification_method || "Simulation") as any,
          source: r.source || "Project Specification",
          status: (r.status?.toUpperCase() || "ACTIVE") as any,
        });
      });
    }

    const initialCons: ConstraintItem[] = [];
    if (projectData?.constraints && Array.isArray(projectData.constraints)) {
      projectData.constraints.forEach((c: any, idx: number) => {
        initialCons.push({
          constraintId: c.constraint_id || c.constraintId || `CON-${String(idx + 1).padStart(3, "0")}`,
          property: c.property || c.parameter || "voltage",
          operator: c.operator || "=",
          requiredValue: c.required_value || c.requiredValue || c.value || "",
          unit: c.required_unit || c.unit,
          severity: c.severity || "CRITICAL",
          requirementId: c.requirement_id || c.requirementId,
        });
      });
    }

    const initialValidation: ValidationMatrixRow[] = [];
    if (projectData?.validation_results && Array.isArray(projectData.validation_results)) {
      projectData.validation_results.forEach((v: any) => {
        initialValidation.push({
          requirement_id: v.requirement_id || "REQ-001",
          title: v.property || v.title || "Parameter Target",
          target: v.required_value || v.target || "—",
          actual: v.actual_value || v.actual || "—",
          status: (v.status || v.overall_status || "PENDING") as any,
          evidence: v.reason || v.source_document || "Datasheet / Simulation Model",
          timestamp: v.timestamp || new Date().toLocaleTimeString(),
        });
      });
    }

    setRequirements(initialReqs);
    setConstraints(initialCons);
    setValidationRows(initialValidation);

    // If requirements are empty, attempt to fetch from backend storage
    const baseUrl = apiBase || (typeof window !== "undefined" && window.location.port === "3000" ? "http://localhost:8000" : "");
    if (initialReqs.length === 0 && baseUrl && projectId) {
      fetch(`${baseUrl}/api/requirements?project_id=${projectId}`)
        .then((res) => (res.ok ? res.json() : []))
        .then((backendReqs) => {
          if (Array.isArray(backendReqs) && backendReqs.length > 0) {
            const mapped: RequirementRecord[] = backendReqs.map((r: any, idx: number) => ({
              requirement_id: r.requirement_id || `REQ-${String(idx + 1).padStart(3, "0")}`,
              project_id: projectId,
              title: r.title || r.parameter || `Requirement ${idx + 1}`,
              description: r.description || r.title || "",
              category: (r.category?.toUpperCase() || "ELECTRICAL") as any,
              parameter: r.parameter,
              target_value: r.target_value ? String(r.target_value) : undefined,
              unit: r.unit,
              priority: (r.priority?.toUpperCase() || "HIGH") as any,
              verification_method: (r.verification_method || "Simulation") as any,
              source: r.source || "Backend Store",
              status: (r.status?.toUpperCase() || "ACTIVE") as any,
            }));
            setRequirements(mapped);
          }
        })
        .catch(() => {});
    }

    if (initialCons.length === 0 && baseUrl && projectId) {
      fetch(`${baseUrl}/api/constraints?project_id=${projectId}`)
        .then((res) => (res.ok ? res.json() : []))
        .then((backendCons) => {
          if (Array.isArray(backendCons) && backendCons.length > 0) {
            const mapped: ConstraintItem[] = backendCons.map((c: any, idx: number) => ({
              constraintId: c.constraint_id || `CON-${String(idx + 1).padStart(3, "0")}`,
              property: c.property || c.property_name || "limit",
              operator: c.operator || "<=",
              requiredValue: String(c.required_value !== undefined ? c.required_value : c.value || ""),
              unit: c.required_unit || c.unit || "",
              severity: (c.severity?.toUpperCase() || "CRITICAL") as any,
              requirementId: c.requirement_id,
            }));
            setConstraints(mapped);
          }
        })
        .catch(() => {});
    }
  }, [projectId, projectData, apiBase]);

  // Handle auto-synthesis of requirements from project idea and/or custom specifications
  const handleAutoSynthesize = async (customSpecs?: string) => {
    const activeIdea =
      projectData?.system_specification ||
      projectData?.intent ||
      projectName ||
      projectId ||
      "Embedded Electronic Hardware System";

    setIsSynthesizing(true);
    setFeedbackMessage(null);
    try {
      const baseUrl = apiBase || (typeof window !== "undefined" && window.location.port === "3000" ? "http://localhost:8000" : "");
      const res = await fetch(`${baseUrl}/api/requirements/synthesize`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project_id: projectId,
          idea: activeIdea,
          custom_specifications: customSpecs || undefined,
        }),
      });

      if (!res.ok) {
        throw new Error(`Synthesis failed with HTTP ${res.status}`);
      }

      const data = await res.json();
      const generatedReqs: RequirementRecord[] = (data.requirements || []).map((r: any, idx: number) => ({
        requirement_id: r.requirement_id || r.id || `REQ-${String(idx + 1).padStart(3, "0")}`,
        project_id: projectId || "current_project",
        title: r.title || r.parameter || r.description?.slice(0, 35) || `Requirement ${idx + 1}`,
        description: r.description || r.title || "",
        category: (r.category?.toUpperCase() || "ELECTRICAL") as any,
        parameter: r.parameter || r.property,
        target_value: r.target_value !== undefined ? String(r.target_value) : undefined,
        unit: r.unit || undefined,
        priority: (r.priority?.toUpperCase() || "HIGH") as any,
        verification_method: (r.verification_method || "Simulation") as any,
        source: r.source || (customSpecs ? "USER_CUSTOM_SPEC" : "Idea Decomposition"),
        status: (r.status?.toUpperCase() || "ACTIVE") as any,
      }));

      const generatedCons: ConstraintItem[] = (data.constraints || []).map((c: any, idx: number) => ({
        constraintId: c.constraint_id || c.id || `CON-${String(idx + 1).padStart(3, "0")}`,
        property: c.property || c.parameter || "limit",
        operator: c.operator || "<=",
        requiredValue: String(c.required_value !== undefined ? c.required_value : c.value || ""),
        unit: c.unit || c.required_unit || "",
        severity: (c.severity?.toUpperCase() || "CRITICAL") as any,
        requirementId: c.requirement_id || undefined,
      }));

      let finalReqs: RequirementRecord[];
      let finalCons: ConstraintItem[];

      if (customSpecs && mergeMode === "append") {
        const existingTitles = new Set(requirements.map((r) => r.title.toLowerCase()));
        const uniqueNewReqs = generatedReqs.filter((r) => !existingTitles.has(r.title.toLowerCase()));
        finalReqs = [...uniqueNewReqs, ...requirements];

        const existingConProps = new Set(constraints.map((c) => `${c.property}:${c.requiredValue}`));
        const uniqueNewCons = generatedCons.filter((c) => !existingConProps.has(`${c.property}:${c.requiredValue}`));
        finalCons = [...uniqueNewCons, ...constraints];
      } else {
        finalReqs = generatedReqs;
        finalCons = generatedCons;
      }

      setRequirements(finalReqs);
      setConstraints(finalCons);

      // Synchronize back to ProjectContext
      if (projectContext?.setProject) {
        const updatedProjectData = {
          ...(projectData || {}),
          requirements: finalReqs,
          constraints: finalCons,
          structured_requirements: data.requirements,
          structured_constraints: data.constraints,
          understanding: data.understanding || projectData?.understanding,
          system_specification: data.specification_text || projectData?.system_specification,
        };
        projectContext.setProject(
          updatedProjectData,
          projectName || projectContext.projectName,
          projectContext.targetDays,
          {
            projectId: projectId || projectContext.projectId,
            systemSpecification: data.specification_text || projectData?.system_specification || projectContext.systemSpecification,
          }
        );
      }

      // Batch persist to backend
      if (baseUrl) {
        fetch(`${baseUrl}/api/requirements/batch`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            project_id: projectId,
            requirements: finalReqs,
            constraints: finalCons,
          }),
        }).catch(() => {});
      }

      setFeedbackMessage(`Generated ${finalReqs.length} requirements and ${finalCons.length} design constraints.`);
      setIsCustomSpecModalOpen(false);
      setCustomSpecText("");
    } catch (err: any) {
      console.error("Auto-synthesize failed:", err);
      setFeedbackMessage("Failed to synthesize requirements. Please try again.");
    } finally {
      setIsSynthesizing(false);
      setTimeout(() => setFeedbackMessage(null), 5000);
    }
  };

  // Derived Overview Metrics (100% computed from actual data, zero mock)
  const reqCount = requirements.length;
  const conCount = constraints.length;
  const verifiedCount = requirements.filter((r) => r.status === "VERIFIED").length;
  const pendingCount = requirements.filter((r) => r.status === "ACTIVE" || r.status === "DRAFT").length;
  const violationCount =
    requirements.filter((r) => r.status === "FAILED").length +
    validationRows.filter((v) => v.status === "FAIL").length;

  let overallStatus: "PASS" | "WARNING" | "FAIL" | "PENDING" = "PENDING";
  if (reqCount === 0 && conCount === 0) {
    overallStatus = "PENDING";
  } else if (violationCount > 0) {
    overallStatus = "FAIL";
  } else if (pendingCount > 0) {
    overallStatus = verifiedCount > 0 ? "WARNING" : "PENDING";
  } else {
    overallStatus = "PASS";
  }

  // Handle Add Requirement
  const handleSaveRequirement = async () => {
    if (!formTitle.trim() && !formDesc.trim()) return;

    const newReqId = `REQ-${String(requirements.length + 1).padStart(3, "0")}`;
    const newReq: RequirementRecord = {
      requirement_id: newReqId,
      project_id: projectId || "current_project",
      title: formTitle || formDesc.slice(0, 30),
      description: formDesc || formTitle,
      category: formCategory,
      parameter: formParam || undefined,
      target_value: formTarget || undefined,
      unit: formUnit || undefined,
      priority: formPriority,
      verification_method: formVerification,
      source: formSource || "Manual Entry",
      status: "ACTIVE",
      created_at: Date.now() / 1000,
      updated_at: Date.now() / 1000,
    };

    setRequirements((prev) => [...prev, newReq]);

    // Async save to backend if API is configured
    try {
      if (apiBase) {
        await fetch(`${apiBase}/api/requirements`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            requirement_id: newReq.requirement_id,
            project_id: newReq.project_id,
            title: newReq.title,
            description: newReq.description,
            category: newReq.category,
            parameter: newReq.parameter,
            target_value: newReq.target_value,
            unit: newReq.unit,
            priority: newReq.priority,
            verification_method: newReq.verification_method,
            source: newReq.source,
          }),
        });
      }
    } catch {
      // Retain in memory
    }

    setIsModalOpen(false);
    setFormTitle("");
    setFormDesc("");
    setFormParam("");
    setFormTarget("");
    setFormUnit("");
  };

  const handleDeleteRequirement = (reqId: string) => {
    setRequirements((prev) => prev.filter((r) => r.requirement_id !== reqId));
    setConstraints((prev) => prev.filter((c) => c.requirementId !== reqId));
    if (apiBase) {
      fetch(`${apiBase}/api/requirements/${reqId}`, { method: "DELETE" }).catch(() => {});
    }
  };

  // If no project selected, display clear No Project State
  if (!projectId) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center bg-slate-900/40 border border-slate-800 rounded-xl space-y-4">
        <div className="w-12 h-12 rounded-full bg-slate-800/80 border border-slate-700 flex items-center justify-center text-slate-400">
          <CheckSquare className="w-6 h-6" />
        </div>
        <div className="space-y-1">
          <h2 className="text-base font-bold text-slate-100">No Active Engineering Project</h2>
          <p className="text-xs text-slate-400 max-w-md">
            Create or select an engineering project to define system objectives, parameters, design constraints, and verification matrices.
          </p>
        </div>
        <div className="flex items-center gap-3 pt-2">
          {onOpenNewProject && (
            <button
              onClick={onOpenNewProject}
              className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold shadow-lg shadow-indigo-600/20 transition cursor-pointer"
            >
              <FolderPlus className="w-4 h-4" />
              Create Project
            </button>
          )}
          {onSelectProject && (
            <button
              onClick={onSelectProject}
              className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg text-xs font-semibold transition cursor-pointer"
            >
              Select Project
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Workspace Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-xl">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <CheckSquare className="w-5 h-5 text-indigo-400" />
            <h1 className="text-base font-bold text-slate-100 tracking-wide font-mono uppercase">
              Requirements & Specification
            </h1>
          </div>
          <p className="text-xs text-slate-400">
            Define system objectives, engineering requirements, design constraints, and verification criteria.
          </p>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <button
            onClick={() => handleAutoSynthesize()}
            disabled={isSynthesizing}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 disabled:opacity-50 text-white rounded-lg text-xs font-semibold transition shadow cursor-pointer"
            title="Auto-extract engineering requirements and constraints from project idea"
          >
            {isSynthesizing ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
            <span>Auto-Generate (AI)</span>
          </button>
          <button
            onClick={() => setIsCustomSpecModalOpen(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg text-xs font-semibold transition cursor-pointer"
            title="Enter and synthesize user custom specifications and operating thresholds"
          >
            <Sliders className="w-3.5 h-3.5 text-indigo-400" />
            <span>Custom Specifications</span>
          </button>
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg text-xs font-semibold transition shadow cursor-pointer"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Add Requirement</span>
          </button>
        </div>
      </div>

      {/* Feedback Banner */}
      {feedbackMessage && (
        <div className="flex items-center justify-between p-3 bg-indigo-950/70 border border-indigo-700/60 rounded-xl text-xs text-indigo-200 animate-in fade-in duration-200">
          <div className="flex items-center gap-2">
            <Check className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>{feedbackMessage}</span>
          </div>
          <button
            onClick={() => setFeedbackMessage(null)}
            className="text-slate-400 hover:text-slate-200 p-1"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* Tabs Navigation */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setActiveTab("overview")}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-medium transition cursor-pointer ${
            activeTab === "overview"
              ? "bg-indigo-950/80 text-indigo-300 border border-indigo-800/60 font-semibold"
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/60"
          }`}
        >
          <Activity className="w-3.5 h-3.5" />
          <span>Overview</span>
        </button>

        <button
          onClick={() => setActiveTab("requirements")}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-medium transition cursor-pointer ${
            activeTab === "requirements"
              ? "bg-indigo-950/80 text-indigo-300 border border-indigo-800/60 font-semibold"
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/60"
          }`}
        >
          <CheckSquare className="w-3.5 h-3.5" />
          <span>Requirements ({reqCount})</span>
        </button>

        <button
          onClick={() => setActiveTab("constraints")}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-medium transition cursor-pointer ${
            activeTab === "constraints"
              ? "bg-indigo-950/80 text-indigo-300 border border-indigo-800/60 font-semibold"
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/60"
          }`}
        >
          <Sliders className="w-3.5 h-3.5" />
          <span>Constraints ({conCount})</span>
        </button>

        <button
          onClick={() => setActiveTab("validation")}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-medium transition cursor-pointer ${
            activeTab === "validation"
              ? "bg-indigo-950/80 text-indigo-300 border border-indigo-800/60 font-semibold"
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/60"
          }`}
        >
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Validation ({validationRows.length})</span>
        </button>
      </div>

      {/* ==================== TAB 1: OVERVIEW ==================== */}
      {activeTab === "overview" && (
        <div className="space-y-6">
          {/* Summary Metric Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            <div className="p-4 bg-slate-900/70 border border-slate-800 rounded-xl flex flex-col gap-1">
              <span className="text-[11px] font-mono text-slate-500 uppercase">Requirements</span>
              <span className="text-xl font-bold font-mono text-slate-100">{reqCount}</span>
            </div>

            <div className="p-4 bg-slate-900/70 border border-slate-800 rounded-xl flex flex-col gap-1">
              <span className="text-[11px] font-mono text-slate-500 uppercase">Constraints</span>
              <span className="text-xl font-bold font-mono text-indigo-300">{conCount}</span>
            </div>

            <div className="p-4 bg-slate-900/70 border border-slate-800 rounded-xl flex flex-col gap-1">
              <span className="text-[11px] font-mono text-slate-500 uppercase">Validated</span>
              <span className="text-xl font-bold font-mono text-emerald-400">{verifiedCount}</span>
            </div>

            <div className="p-4 bg-slate-900/70 border border-slate-800 rounded-xl flex flex-col gap-1">
              <span className="text-[11px] font-mono text-slate-500 uppercase">Pending</span>
              <span className="text-xl font-bold font-mono text-amber-400">{pendingCount}</span>
            </div>

            <div className="p-4 bg-slate-900/70 border border-slate-800 rounded-xl flex flex-col gap-1">
              <span className="text-[11px] font-mono text-slate-500 uppercase">Violations</span>
              <span className={`text-xl font-bold font-mono ${violationCount > 0 ? "text-rose-400" : "text-slate-400"}`}>
                {violationCount}
              </span>
            </div>

            <div className="p-4 bg-slate-900/70 border border-slate-800 rounded-xl flex flex-col gap-1">
              <span className="text-[11px] font-mono text-slate-500 uppercase">Overall Status</span>
              <div>
                <EngineeringStatusBadge status={overallStatus} size="sm" />
              </div>
            </div>
          </div>

          {/* Project Details Box */}
          <div className="p-5 bg-slate-900/50 border border-slate-800 rounded-xl space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 font-mono text-xs text-slate-300">
                <FileText className="w-4 h-4 text-indigo-400" />
                <span>Project: <strong>{projectName || projectId}</strong></span>
              </div>
              <span className="text-[10px] font-mono text-slate-500">ID: {projectId}</span>
            </div>

            {reqCount === 0 && conCount === 0 ? (
              <div className="py-8 px-4 text-center space-y-4 bg-slate-950/60 border border-dashed border-slate-800 rounded-xl my-2">
                <div className="space-y-1">
                  <p className="text-sm font-semibold text-slate-200">No requirements or design constraints defined yet.</p>
                  <p className="text-xs text-slate-400 max-w-lg mx-auto">
                    Generate structured engineering requirements automatically from the project concept, or provide your custom operating voltages, currents, and communication limits.
                  </p>
                </div>
                <div className="flex flex-wrap items-center justify-center gap-2.5 pt-1">
                  <button
                    onClick={() => handleAutoSynthesize()}
                    disabled={isSynthesizing}
                    className="inline-flex items-center gap-1.5 px-4 py-2 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 disabled:opacity-50 text-white rounded-lg text-xs font-semibold transition shadow-lg shadow-indigo-600/20 cursor-pointer"
                  >
                    {isSynthesizing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                    <span>Auto-Generate Requirements from Idea</span>
                  </button>
                  <button
                    onClick={() => setIsCustomSpecModalOpen(true)}
                    className="inline-flex items-center gap-1.5 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg text-xs font-semibold transition cursor-pointer"
                  >
                    <Sliders className="w-4 h-4 text-indigo-400" />
                    <span>Enter Custom Specifications</span>
                  </button>
                  <button
                    onClick={() => setIsModalOpen(true)}
                    className="inline-flex items-center gap-1.5 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 rounded-lg text-xs font-semibold transition cursor-pointer"
                  >
                    <Plus className="w-4 h-4" />
                    <span>+ Manual Entry</span>
                  </button>
                </div>
              </div>
            ) : (
              <div className="space-y-2 pt-2">
                <h4 className="text-xs font-bold font-mono text-slate-300 uppercase">Quick Specification Highlights</h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {requirements.slice(0, 4).map((r) => (
                    <div key={r.requirement_id} className="p-2.5 bg-slate-950 border border-slate-800 rounded-lg text-xs">
                      <div className="flex items-center justify-between text-slate-300 font-mono font-bold">
                        <span>{r.requirement_id}</span>
                        <span className="text-[10px] text-indigo-400">{r.category}</span>
                      </div>
                      <p className="text-slate-400 text-[11px] truncate mt-0.5">{r.title}</p>
                      {r.target_value && (
                        <div className="text-[10px] text-emerald-400 font-mono mt-1">
                          Target: {r.target_value} {r.unit || ""}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ==================== TAB 2: REQUIREMENTS ==================== */}
      {activeTab === "requirements" && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-100 font-mono uppercase">
              System & Engineering Requirements
            </h3>
            <button
              onClick={() => setIsModalOpen(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-xs font-semibold transition cursor-pointer"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add Requirement</span>
            </button>
          </div>

          {requirements.length === 0 ? (
            <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-10 text-center space-y-4">
              <CheckSquare className="w-8 h-8 text-slate-600 mx-auto" />
              <div className="space-y-1">
                <h4 className="text-sm font-bold text-slate-200">No requirements defined.</h4>
                <p className="text-xs text-slate-400 max-w-md mx-auto">
                  Automatically synthesize verified engineering requirements and constraints from your project idea, or supply your own custom operational specifications.
                </p>
              </div>
              <div className="flex flex-wrap items-center justify-center gap-2.5 pt-1">
                <button
                  onClick={() => handleAutoSynthesize()}
                  disabled={isSynthesizing}
                  className="inline-flex items-center gap-1.5 px-4 py-2 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 disabled:opacity-50 text-white rounded-lg text-xs font-semibold transition shadow cursor-pointer"
                >
                  {isSynthesizing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                  <span>Auto-Generate from Idea</span>
                </button>
                <button
                  onClick={() => setIsCustomSpecModalOpen(true)}
                  className="inline-flex items-center gap-1.5 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg text-xs font-semibold transition cursor-pointer"
                >
                  <Sliders className="w-4 h-4 text-indigo-400" />
                  <span>Enter Custom Specifications</span>
                </button>
                <button
                  onClick={() => setIsModalOpen(true)}
                  className="inline-flex items-center gap-1.5 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 rounded-lg text-xs font-semibold transition cursor-pointer"
                >
                  <Plus className="w-4 h-4" />
                  <span>+ Manual Entry</span>
                </button>
              </div>
            </div>
          ) : (
            <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs font-mono">
                  <thead className="bg-slate-950/80 border-b border-slate-800 text-slate-400 uppercase text-[10px]">
                    <tr>
                      <th className="py-3 px-4">ID</th>
                      <th className="py-3 px-4">Requirement / Objective</th>
                      <th className="py-3 px-4">Category</th>
                      <th className="py-3 px-4">Target Spec</th>
                      <th className="py-3 px-4">Priority</th>
                      <th className="py-3 px-4">Verification</th>
                      <th className="py-3 px-4">Status</th>
                      <th className="py-3 px-4 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800 text-slate-300">
                    {requirements.map((r) => (
                      <tr key={r.requirement_id} className="hover:bg-slate-800/40 transition">
                        <td className="py-3 px-4 font-bold text-slate-100 whitespace-nowrap">
                          {r.requirement_id}
                        </td>
                        <td className="py-3 px-4 max-w-xs">
                          <div className="font-sans font-medium text-slate-200">{r.title}</div>
                          {r.description !== r.title && (
                            <div className="text-[11px] text-slate-400 font-sans truncate">{r.description}</div>
                          )}
                        </td>
                        <td className="py-3 px-4 whitespace-nowrap">
                          <span className="px-2 py-0.5 rounded text-[10px] bg-slate-950 text-indigo-300 border border-slate-800">
                            {r.category}
                          </span>
                        </td>
                        <td className="py-3 px-4 whitespace-nowrap">
                          {r.target_value ? (
                            <span className="text-emerald-400 font-bold">
                              {r.parameter ? `${r.parameter} = ` : ""}
                              {r.target_value} {r.unit || ""}
                            </span>
                          ) : (
                            <span className="text-slate-500">—</span>
                          )}
                        </td>
                        <td className="py-3 px-4 whitespace-nowrap">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] border font-bold ${
                              r.priority === "CRITICAL"
                                ? "bg-rose-950/60 text-rose-300 border-rose-800/50"
                                : r.priority === "HIGH"
                                ? "bg-amber-950/60 text-amber-300 border-amber-800/50"
                                : "bg-slate-800 text-slate-300 border-slate-700"
                            }`}
                          >
                            {r.priority}
                          </span>
                        </td>
                        <td className="py-3 px-4 whitespace-nowrap text-slate-400">
                          {r.verification_method}
                        </td>
                        <td className="py-3 px-4 whitespace-nowrap">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] border font-bold ${
                              r.status === "VERIFIED"
                                ? "bg-emerald-950/60 text-emerald-300 border-emerald-800/50"
                                : r.status === "FAILED"
                                ? "bg-rose-950/60 text-rose-300 border-rose-800/50"
                                : "bg-slate-800 text-slate-400 border-slate-700"
                            }`}
                          >
                            {r.status}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-right whitespace-nowrap">
                          <button
                            onClick={() => handleDeleteRequirement(r.requirement_id)}
                            className="p-1 text-slate-500 hover:text-rose-400 transition cursor-pointer"
                            title="Delete Requirement"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ==================== TAB 3: CONSTRAINTS ==================== */}
      {activeTab === "constraints" && (
        <div className="space-y-6">
          <ConstraintEditor
            constraints={constraints}
            onChangeConstraints={(updated) => setConstraints(updated)}
            availableRequirementIds={requirements.map((r) => r.requirement_id)}
          />

          <ConstraintPanel
            minTraceWidthMm={projectData?.board_constraints?.min_trace_width_mm}
            minClearanceMm={projectData?.board_constraints?.min_clearance_mm}
            maxBoardTempC={projectData?.board_constraints?.max_board_temp_c}
            targetDiffImpedanceOhm={projectData?.board_constraints?.target_diff_impedance_ohm}
          />
        </div>
      )}

      {/* ==================== TAB 4: VALIDATION ==================== */}
      {activeTab === "validation" && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-100 font-mono uppercase">
              Verification & Validation Matrix
            </h3>
            <span className="text-xs font-mono text-slate-500">Deterministic Engine v1.0</span>
          </div>

          {validationRows.length === 0 ? (
            <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-12 text-center space-y-3">
              <ShieldCheck className="w-8 h-8 text-slate-600 mx-auto" />
              <div className="space-y-1">
                <h4 className="text-sm font-bold text-slate-200">No validation results available.</h4>
                <p className="text-xs text-slate-500 max-w-sm mx-auto">
                  Run validation after requirements, design constraints, and engineering simulation models are available.
                </p>
              </div>
            </div>
          ) : (
            <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs font-mono">
                  <thead className="bg-slate-950/80 border-b border-slate-800 text-slate-400 uppercase text-[10px]">
                    <tr>
                      <th className="py-3 px-4">Requirement</th>
                      <th className="py-3 px-4">Target Spec</th>
                      <th className="py-3 px-4">Actual Measured / Simulated</th>
                      <th className="py-3 px-4">Result</th>
                      <th className="py-3 px-4">Evidence / Source</th>
                      <th className="py-3 px-4">Timestamp</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800 text-slate-300">
                    {validationRows.map((row, idx) => (
                      <tr key={idx} className="hover:bg-slate-800/40 transition">
                        <td className="py-3 px-4 font-bold text-slate-100">
                          <div>{row.requirement_id}</div>
                          <span className="text-[10px] text-slate-400 font-sans font-normal">{row.title}</span>
                        </td>
                        <td className="py-3 px-4 text-emerald-400 font-bold">{row.target}</td>
                        <td className="py-3 px-4 text-slate-200 font-bold">{row.actual}</td>
                        <td className="py-3 px-4">
                          <EngineeringStatusBadge status={row.status} size="sm" />
                        </td>
                        <td className="py-3 px-4 text-slate-400 text-[11px] max-w-xs truncate">{row.evidence}</td>
                        <td className="py-3 px-4 text-slate-500 text-[10px]">{row.timestamp}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ==================== ADD REQUIREMENT MODAL ==================== */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-lg w-full p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <Plus className="w-5 h-5 text-indigo-400" />
                <h3 className="text-sm font-bold text-slate-100 uppercase font-mono">
                  Define Engineering Requirement
                </h3>
              </div>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-slate-500 hover:text-slate-300 p-1 cursor-pointer transition"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3 text-xs font-mono">
              <div className="space-y-1">
                <label className="text-slate-400">Title / Short Name *</label>
                <input
                  type="text"
                  value={formTitle}
                  onChange={(e) => setFormTitle(e.target.value)}
                  placeholder="e.g. Regulated 12V Rail Output"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200"
                />
              </div>

              <div className="space-y-1">
                <label className="text-slate-400">Description</label>
                <textarea
                  rows={2}
                  value={formDesc}
                  onChange={(e) => setFormDesc(e.target.value)}
                  placeholder="Detailed functional and operational objective..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 resize-none font-sans"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-slate-400">Category</label>
                  <select
                    value={formCategory}
                    onChange={(e) => setFormCategory(e.target.value as any)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-200"
                  >
                    <option value="SYSTEM">SYSTEM</option>
                    <option value="FUNCTIONAL">FUNCTIONAL</option>
                    <option value="PERFORMANCE">PERFORMANCE</option>
                    <option value="ELECTRICAL">ELECTRICAL</option>
                    <option value="MECHANICAL">MECHANICAL</option>
                    <option value="THERMAL">THERMAL</option>
                    <option value="ENVIRONMENTAL">ENVIRONMENTAL</option>
                    <option value="INTERFACE">INTERFACE</option>
                    <option value="COMPLIANCE">COMPLIANCE</option>
                    <option value="COST">COST</option>
                    <option value="SCHEDULE">SCHEDULE</option>
                    <option value="RELIABILITY">RELIABILITY</option>
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="text-slate-400">Priority</label>
                  <select
                    value={formPriority}
                    onChange={(e) => setFormPriority(e.target.value as any)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-200"
                  >
                    <option value="CRITICAL">CRITICAL</option>
                    <option value="HIGH">HIGH</option>
                    <option value="MEDIUM">MEDIUM</option>
                    <option value="LOW">LOW</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-2">
                <div className="space-y-1">
                  <label className="text-slate-400">Parameter</label>
                  <input
                    type="text"
                    value={formParam}
                    onChange={(e) => setFormParam(e.target.value)}
                    placeholder="e.g. output_voltage"
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-200"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-slate-400">Target Value</label>
                  <input
                    type="text"
                    value={formTarget}
                    onChange={(e) => setFormTarget(e.target.value)}
                    placeholder="e.g. 12"
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-200"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-slate-400">Unit</label>
                  <input
                    type="text"
                    value={formUnit}
                    onChange={(e) => setFormUnit(e.target.value)}
                    placeholder="e.g. V"
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-200"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-slate-400">Verification Method</label>
                  <select
                    value={formVerification}
                    onChange={(e) => setFormVerification(e.target.value as any)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-200"
                  >
                    <option value="Simulation">Simulation</option>
                    <option value="Datasheet">Datasheet</option>
                    <option value="Analysis">Analysis</option>
                    <option value="Test">Test</option>
                    <option value="Inspection">Inspection</option>
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="text-slate-400">Source Spec</label>
                  <input
                    type="text"
                    value={formSource}
                    onChange={(e) => setFormSource(e.target.value)}
                    placeholder="e.g. Architecture Document"
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-200"
                  />
                </div>
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
              <button
                onClick={() => setIsModalOpen(false)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-semibold transition cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveRequirement}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold transition shadow cursor-pointer"
              >
                Save Requirement
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Custom Specifications Modal */}
      {isCustomSpecModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-2xl w-full p-6 space-y-4 shadow-2xl text-xs max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <Sliders className="w-4 h-4 text-indigo-400" />
                  <h3 className="text-sm font-bold text-slate-100 font-mono uppercase">
                    Custom Engineering Specifications
                  </h3>
                </div>
                <p className="text-slate-400 text-[11px]">
                  Provide your own technical specifications, operating limits, communication buses, or safety cutoffs. The engine will extract structured requirements & design constraints.
                </p>
              </div>
              <button
                onClick={() => setIsCustomSpecModalOpen(false)}
                className="text-slate-400 hover:text-slate-200 p-1 cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Quick Chips */}
            <div className="space-y-1.5">
              <label className="text-slate-400 font-medium">Quick Preset Parameters (click to append):</label>
              <div className="flex flex-wrap gap-1.5">
                {QUICK_SPEC_CHIPS.map((chip) => (
                  <button
                    key={chip}
                    type="button"
                    onClick={() => {
                      setCustomSpecText((prev) =>
                        prev ? `${prev.trim()}, ${chip.replace(/^\+\s*/, "")}` : chip.replace(/^\+\s*/, "")
                      );
                    }}
                    className="px-2.5 py-1 bg-slate-950 hover:bg-slate-800 border border-slate-800 hover:border-indigo-600/50 rounded-md text-[11px] text-slate-300 font-mono transition cursor-pointer"
                  >
                    {chip}
                  </button>
                ))}
              </div>
            </div>

            {/* Custom Specs Textarea */}
            <div className="space-y-1.5">
              <label className="text-slate-300 font-medium">
                Specifications, Interfaces & Parameters:
              </label>
              <textarea
                rows={5}
                value={customSpecText}
                onChange={(e) => setCustomSpecText(e.target.value)}
                placeholder="e.g. 4S LiFePO4 battery pack, 12.8V nominal, 14.6V charge cutoff, continuous discharge current 30A, peak 60A for 10s, CAN bus 250kbps telemetry, cell overvoltage 3.65V, undervoltage 2.50V, operating temp -20°C to 60°C..."
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-slate-200 font-mono text-xs focus:border-indigo-500 focus:outline-none"
              />
            </div>

            {/* Synthesis Mode */}
            <div className="flex items-center justify-between p-3 bg-slate-950/60 border border-slate-800 rounded-lg">
              <span className="text-slate-400">Merge with existing requirements:</span>
              <div className="flex items-center gap-3">
                <label className="flex items-center gap-1.5 text-slate-300 cursor-pointer text-xs">
                  <input
                    type="radio"
                    name="mergeMode"
                    value="append"
                    checked={mergeMode === "append"}
                    onChange={() => setMergeMode("append")}
                    className="text-indigo-600"
                  />
                  <span>Append & Update</span>
                </label>
                <label className="flex items-center gap-1.5 text-slate-300 cursor-pointer text-xs">
                  <input
                    type="radio"
                    name="mergeMode"
                    value="replace"
                    checked={mergeMode === "replace"}
                    onChange={() => setMergeMode("replace")}
                    className="text-indigo-600"
                  />
                  <span>Replace All</span>
                </label>
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center justify-between pt-3 border-t border-slate-800">
              <button
                type="button"
                onClick={() => setCustomSpecText("")}
                disabled={!customSpecText}
                className="text-xs text-slate-500 hover:text-slate-400 disabled:opacity-30 cursor-pointer"
              >
                Clear Text
              </button>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => setIsCustomSpecModalOpen(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-semibold transition cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={async () => {
                    await handleAutoSynthesize(customSpecText);
                    setIsCustomSpecModalOpen(false);
                  }}
                  disabled={isSynthesizing}
                  className="inline-flex items-center gap-1.5 px-4 py-2 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 disabled:opacity-50 text-white rounded-lg text-xs font-semibold transition shadow cursor-pointer"
                >
                  {isSynthesizing ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
                  <span>Synthesize Requirements</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
