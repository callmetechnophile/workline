"use client";

import React, { useState } from "react";
import {
  Layers,
  ShieldCheck,
  Flame,
  Brain,
  Sliders,
  Ruler,
  Cpu,
  Activity,
  PlusCircle,
  RefreshCw,
} from "lucide-react";
import PCBBoardView, { ComponentItem, BoardDetails } from "./PCBBoardView";
import PCBComponentPanel from "./PCBComponentPanel";
import PCBConstraintPanel, { ConstraintItemData } from "./PCBConstraintPanel";
import PCBValidationPanel, { ValidationReportData } from "./PCBValidationPanel";
import PCBPhysicsPanel, { FeaturePointData } from "./PCBPhysicsPanel";
import ThermalAnalysisPanel, { ThermalAnalysisData } from "./ThermalAnalysisPanel";
import PINNTrainingPanel, { TrainingResultData } from "./PINNTrainingPanel";
import PCBOptimizationPanel, { OptimizationData } from "./PCBOptimizationPanel";

interface PCBWorkspaceProps {
  projectId: string;
}

export const PCBWorkspace: React.FC<PCBWorkspaceProps> = ({ projectId }) => {
  const [activeTab, setActiveTab] = useState<"layout" | "drc" | "thermal" | "pinn" | "optimize" | "constraints">("layout");
  const [loading, setLoading] = useState(false);

  // Mock initial state for visualization
  const [board, setBoard] = useState<BoardDetails>({
    width: 80.0,
    height: 60.0,
    thickness: 1.6,
    layer_count: 4,
  });

  const [components, setComponents] = useState<ComponentItem[]>([
    { id: "comp_1", reference_designator: "U1", value: "ESP32-S3-WROOM-1", footprint_id: "FP_MODULE_ESP32", x: 25.0, y: 30.0, rotation: 0, layer: "TOP", locked: false },
    { id: "comp_2", reference_designator: "U2", value: "LM2596S-3.3", footprint_id: "FP_SOT223", x: 60.0, y: 20.0, rotation: 0, layer: "TOP", locked: false },
    { id: "comp_3", reference_designator: "U3", value: "BME280", footprint_id: "FP_SOIC8", x: 60.0, y: 45.0, rotation: 0, layer: "TOP", locked: false },
    { id: "comp_4", reference_designator: "J1", value: "Pin Header 1x4", footprint_id: "FP_HDR_1X4", x: 10.0, y: 10.0, rotation: 0, layer: "TOP", locked: true },
  ]);

  const [validationReport, setValidationReport] = useState<ValidationReportData>({
    status: "PASS",
    passed: true,
    summary: "PCB Validation PASS: 0 Errors, 0 Warnings across 12 rule categories.",
    error_count: 0,
    warning_count: 0,
    violations: [],
  });

  const [thermalData, setThermalData] = useState<ThermalAnalysisData>({
    ambient_temperature: 25.0,
    predicted_peak_temperature: 58.4,
    predicted_min_temperature: 26.2,
    predicted_avg_temperature: 32.1,
    hotspots: [
      { component: "U2 (LM2596S)", x: 60.0, y: 20.0, predicted_temp: 58.4 },
      { component: "U1 (ESP32-S3)", x: 25.0, y: 30.0, predicted_temp: 42.1 },
    ],
  });

  const [trainingResult, setTrainingResult] = useState<TrainingResultData | null>({
    model_id: "pinn_thm_8f2910c2",
    epochs_completed: 50,
    final_train_loss: 0.000312,
    validation_metrics: {
      mae_celsius: 0.38,
      rmse_celsius: 0.54,
      max_absolute_error_celsius: 1.12,
      relative_l2_error_pct: 1.4,
    },
  });

  const [optimizationResult, setOptimizationResult] = useState<OptimizationData | null>({
    initial_peak_temperature: 58.4,
    optimized_peak_temperature: 46.2,
    temperature_reduction_celsius: 12.2,
    iterations_evaluated: 50,
    accepted_moves_count: 4,
    history: [
      { iteration: 3, component_moved: "U2", previous_position: [60.0, 20.0], new_position: [68.0, 20.0], peak_temperature: 54.1, temperature_reduction: 4.3 },
      { iteration: 12, component_moved: "U2", previous_position: [68.0, 20.0], new_position: [68.0, 15.0], peak_temperature: 49.8, temperature_reduction: 4.3 },
      { iteration: 28, component_moved: "U1", previous_position: [25.0, 30.0], new_position: [20.0, 35.0], peak_temperature: 46.2, temperature_reduction: 3.6 },
    ],
  });

  const constraints: ConstraintItemData[] = [
    { name: "minimum_trace_width", value: 0.15, unit: "mm", source: "MANUFACTURING_RULE", source_reference: "Standard 6-mil DFM Limit" },
    { name: "minimum_clearance", value: 0.15, unit: "mm", source: "MANUFACTURING_RULE", source_reference: "Standard 6-mil DFM Spacing" },
    { name: "minimum_via_drill", value: 0.30, unit: "mm", source: "MANUFACTURING_RULE", source_reference: "Standard Mechanical Drill" },
    { name: "maximum_temperature", value: 85.0, unit: "°C", source: "DATASHEET", source_reference: "Industrial Silicon Junction Rating" },
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <Layers className="w-5 h-5 text-cyan-400" />
            PCB Engineering Unit & PINN Physics Engine
          </h2>
          <p className="text-xs text-slate-400">
            Physical Representation • 12-Check DRC • Physics-Informed Thermal Modeling • Placement Optimization
          </p>
        </div>
      </div>

      {/* Workspace Tabs */}
      <div className="flex gap-2 border-b border-slate-800 pb-2 overflow-x-auto">
        <button
          onClick={() => setActiveTab("layout")}
          className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all ${
            activeTab === "layout" ? "bg-cyan-600 text-white shadow-md shadow-cyan-950/40" : "bg-slate-800 text-slate-400 hover:text-slate-200"
          }`}
        >
          <Layers className="w-3.5 h-3.5" /> 2D Board Layout
        </button>
        <button
          onClick={() => setActiveTab("drc")}
          className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all ${
            activeTab === "drc" ? "bg-cyan-600 text-white shadow-md shadow-cyan-950/40" : "bg-slate-800 text-slate-400 hover:text-slate-200"
          }`}
        >
          <ShieldCheck className="w-3.5 h-3.5" /> 12-Check DRC
        </button>
        <button
          onClick={() => setActiveTab("thermal")}
          className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all ${
            activeTab === "thermal" ? "bg-cyan-600 text-white shadow-md shadow-cyan-950/40" : "bg-slate-800 text-slate-400 hover:text-slate-200"
          }`}
        >
          <Flame className="w-3.5 h-3.5" /> Thermal Analysis
        </button>
        <button
          onClick={() => setActiveTab("pinn")}
          className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all ${
            activeTab === "pinn" ? "bg-cyan-600 text-white shadow-md shadow-cyan-950/40" : "bg-slate-800 text-slate-400 hover:text-slate-200"
          }`}
        >
          <Brain className="w-3.5 h-3.5" /> PINN Neural Network
        </button>
        <button
          onClick={() => setActiveTab("optimize")}
          className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all ${
            activeTab === "optimize" ? "bg-cyan-600 text-white shadow-md shadow-cyan-950/40" : "bg-slate-800 text-slate-400 hover:text-slate-200"
          }`}
        >
          <Sliders className="w-3.5 h-3.5" /> Placement Optimizer
        </button>
        <button
          onClick={() => setActiveTab("constraints")}
          className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all ${
            activeTab === "constraints" ? "bg-cyan-600 text-white shadow-md shadow-cyan-950/40" : "bg-slate-800 text-slate-400 hover:text-slate-200"
          }`}
        >
          <Ruler className="w-3.5 h-3.5" /> Design Constraints
        </button>
      </div>

      {/* Active Tab Panel Content */}
      <div className="space-y-6">
        {activeTab === "layout" && (
          <div className="space-y-6">
            <PCBBoardView board={board} components={components} hotspots={thermalData.hotspots} />
            <PCBComponentPanel components={components} />
          </div>
        )}

        {activeTab === "drc" && (
          <PCBValidationPanel report={validationReport} onRevalidate={async () => {}} />
        )}

        {activeTab === "thermal" && (
          <ThermalAnalysisPanel thermalData={thermalData} onRunInference={async () => {}} />
        )}

        {activeTab === "pinn" && (
          <PINNTrainingPanel trainingResult={trainingResult} onTrainPINN={async () => {}} />
        )}

        {activeTab === "optimize" && (
          <PCBOptimizationPanel optimizationResult={optimizationResult} onRunOptimization={async () => {}} />
        )}

        {activeTab === "constraints" && (
          <PCBConstraintPanel constraints={constraints} />
        )}
      </div>
    </div>
  );
};

export default PCBWorkspace;
