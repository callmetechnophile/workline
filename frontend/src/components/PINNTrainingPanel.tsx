"use client";

import React from "react";
import { Brain, Play, CheckCircle2, TrendingDown, Layers, Activity } from "lucide-react";

export interface PINNMetricsData {
  mae_celsius: number;
  rmse_celsius: number;
  max_absolute_error_celsius: number;
  relative_l2_error_pct: number;
}

export interface TrainingResultData {
  model_id: string;
  epochs_completed: number;
  final_train_loss: number;
  validation_metrics: PINNMetricsData;
}

interface PINNTrainingPanelProps {
  trainingResult?: TrainingResultData | null;
  onTrainPINN: (epochs: number) => Promise<void>;
  isTraining?: boolean;
}

export const PINNTrainingPanel: React.FC<PINNTrainingPanelProps> = ({
  trainingResult,
  onTrainPINN,
  isTraining = false,
}) => {
  const m = trainingResult?.validation_metrics;

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-2xl backdrop-blur-md space-y-4">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-emerald-500/10 border border-emerald-500/20 rounded-lg text-emerald-400">
            <Brain className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
              PHYSICS-INFORMED NEURAL NETWORK (PINN)
            </h3>
            <p className="text-xs text-slate-400">Steady-State Thermal Diffusion PDE solver</p>
          </div>
        </div>

        <button
          onClick={() => onTrainPINN(50)}
          disabled={isTraining}
          className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold flex items-center gap-1.5 transition-all shadow-lg shadow-emerald-950/30 disabled:opacity-50"
        >
          {isTraining ? <Activity className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
          {isTraining ? "Training PINN..." : "Train Thermal PINN (50 Epochs)"}
        </button>
      </div>

      {trainingResult && m ? (
        <div className="space-y-4">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="bg-slate-950/60 p-3.5 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Validation MAE:</span>
              <div className="font-mono text-lg font-bold text-emerald-400 mt-0.5">
                {m.mae_celsius.toFixed(2)} °C
              </div>
            </div>
            <div className="bg-slate-950/60 p-3.5 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Validation RMSE:</span>
              <div className="font-mono text-lg font-bold text-cyan-400 mt-0.5">
                {m.rmse_celsius.toFixed(2)} °C
              </div>
            </div>
            <div className="bg-slate-950/60 p-3.5 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Max Discrepancy:</span>
              <div className="font-mono text-lg font-bold text-amber-400 mt-0.5">
                {m.max_absolute_error_celsius.toFixed(2)} °C
              </div>
            </div>
            <div className="bg-slate-950/60 p-3.5 rounded-lg border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Relative L2 Error:</span>
              <div className="font-mono text-lg font-bold text-purple-400 mt-0.5">
                {m.relative_l2_error_pct.toFixed(1)} %
              </div>
            </div>
          </div>

          <div className="p-3 bg-slate-950/40 border border-slate-800 rounded-lg text-xs text-slate-400 flex items-center justify-between font-mono">
            <span>Model ID: <strong className="text-slate-200">{trainingResult.model_id}</strong></span>
            <span>Final Loss: <strong className="text-emerald-400">{trainingResult.final_train_loss.toFixed(6)}</strong></span>
          </div>
        </div>
      ) : (
        <div className="bg-slate-950/40 border border-slate-800 rounded-xl p-6 text-center text-xs text-slate-500">
          No trained PINN model found for this project. Click <strong>"Train Thermal PINN"</strong> to generate dataset and train the physics network.
        </div>
      )}
    </div>
  );
};

export default PINNTrainingPanel;
