'use client';

import React, { useState } from 'react';
import { X, Sparkles, Calendar, Layers, ArrowRight, Lightbulb, Mic } from 'lucide-react';

interface NewProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (intent: string, targetDays: number) => void;
  isProcessing: boolean;
}

const TEMPLATE_SUGGESTIONS = [
  "High-efficiency 48V to 12V 20A Synchronous Buck Converter with telemetry",
  "Autonomous Delivery Drone Power Distribution & ESC Architecture",
  "Ultra-low-power BLE sensor node with energy harvesting (solar + supercap)",
  "Industrial Modbus RTU & CAN Bus Gateway with opto-isolation",
  "High-speed USB 3.2 Gen 2 Type-C Hub Controller with Power Delivery",
  "Smart Battery Management System (BMS) for 4S LiFePO4 pack with SMBus",
];

export default function NewProjectModal({
  isOpen,
  onClose,
  onSubmit,
  isProcessing,
}: NewProjectModalProps) {
  const [intent, setIntent] = useState('');
  const [targetDays, setTargetDays] = useState(30);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!intent.trim()) return;
    onSubmit(intent, targetDays);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-md px-4 animate-in fade-in duration-200">
      <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-xl w-full shadow-2xl overflow-hidden">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 rounded-md bg-indigo-950 border border-indigo-700/50 text-indigo-400">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-slate-100">Create Engineering Project</h2>
              <p className="text-[11px] text-slate-400">Specify requirements to run autonomous analysis</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-md text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Modal Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          {/* Engineering Intent Input */}
          <div className="space-y-1.5">
            <label className="block text-xs font-mono font-semibold text-slate-300 uppercase">
              System Specification & Engineering Goal <span className="text-red-400">*</span>
            </label>
            <textarea
              rows={3}
              required
              placeholder="e.g. Design a 4-layer PCB buck converter with 95% efficiency, overvoltage protection, and automotive-grade component sourcing..."
              value={intent}
              onChange={(e) => setIntent(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 font-sans"
            />
          </div>

          {/* Timeline Parameter */}
          <div className="space-y-1.5">
            <label className="block text-xs font-mono font-semibold text-slate-300 uppercase">
              Target Execution Timeline (Days) <span className="text-red-400">*</span>
            </label>
            <div className="flex items-center gap-3">
              <input
                type="number"
                min={1}
                max={365}
                required
                value={targetDays}
                onChange={(e) => setTargetDays(parseInt(e.target.value) || 1)}
                className="w-28 bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs font-mono font-bold text-slate-100 focus:outline-none focus:border-indigo-500"
              />
              <span className="text-xs text-slate-400">
                Determines procurement lead-time filters and critical path roadmap.
              </span>
            </div>
          </div>

          {/* Suggestion Templates */}
          <div className="space-y-2 pt-1">
            <div className="flex items-center gap-1.5 text-[10px] font-mono font-bold text-slate-500 uppercase">
              <Lightbulb className="w-3 h-3 text-amber-400" />
              <span>Engineering Template Examples</span>
            </div>
            <div className="space-y-1.5 max-h-36 overflow-y-auto pr-1">
              {TEMPLATE_SUGGESTIONS.map((item, idx) => (
                <button
                  type="button"
                  key={idx}
                  onClick={() => setIntent(item)}
                  className="w-full text-left p-2 rounded-md bg-slate-950/60 border border-slate-850 hover:border-indigo-500/40 text-[11px] text-slate-300 hover:text-white transition-all cursor-pointer truncate block"
                >
                  {item}
                </button>
              ))}
            </div>
          </div>

          {/* Modal Footer */}
          <div className="pt-3 border-t border-slate-850 flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-md border border-slate-800 text-slate-300 hover:bg-slate-800 text-xs font-medium transition-colors cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isProcessing || !intent.trim()}
              className="px-5 py-2 rounded-md bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-bold shadow-md transition-all flex items-center gap-2 cursor-pointer"
            >
              <span>{isProcessing ? 'Synthesizing...' : 'Initialize Project'}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
