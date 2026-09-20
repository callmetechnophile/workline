'use client';

import React, { useState } from 'react';
import { X, Sparkles, Calendar, Layers, ArrowRight, Lightbulb, Loader2 } from 'lucide-react';

interface NewProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (projectName: string, systemSpecification: string, targetDays: number, template?: string) => void;
  isProcessing: boolean;
  errorMessage?: string | null;
  apiBase?: string;
}

const TEMPLATE_SUGGESTIONS = [
  "High-efficiency 48V to 12V 20A Synchronous Buck Converter with telemetry",
  "Autonomous Delivery Drone Power Distribution & ESC Architecture",
  "Ultra-low-power BLE sensor node with energy harvesting (solar + supercap)",
  "Industrial Modbus RTU & CAN Bus Gateway with opto-isolation",
  "High-speed USB 3.2 Gen 2 Type-C Hub Controller with Power Delivery",
  "Smart Battery Management System (BMS) for 4S LiFePO4 pack with SMBus",
];

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

export default function NewProjectModal({
  isOpen,
  onClose,
  onSubmit,
  isProcessing,
  errorMessage,
  apiBase,
}: NewProjectModalProps) {
  const [projectName, setProjectName] = useState('');
  const [systemSpecification, setSystemSpecification] = useState('');
  const [targetDays, setTargetDays] = useState(30);
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');
  const [validationError, setValidationError] = useState<string | null>(null);
  const [isSynthesizing, setIsSynthesizing] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const cleanName = projectName.trim();
    const cleanSpec = systemSpecification.trim();

    if (!cleanName) {
      setValidationError('Project name is required and cannot be empty.');
      return;
    }
    if (!cleanSpec) {
      setValidationError('System specification & engineering goal is required.');
      return;
    }

    setValidationError(null);
    onSubmit(cleanName, cleanSpec, targetDays, selectedTemplate || undefined);
  };

  const handleSelectTemplate = (template: string) => {
    setSelectedTemplate(template);
    setSystemSpecification(template);
    // Do not overwrite projectName if user has already entered one
    if (!projectName.trim()) {
      setProjectName(template.slice(0, 45));
    }
  };

  const handleAutoSynthesize = async () => {
    const query = projectName.trim() || systemSpecification.trim() || selectedTemplate;
    if (!query) return;

    setIsSynthesizing(true);
    setValidationError(null);
    try {
      const baseUrl = apiBase || (typeof window !== 'undefined' && window.location.port === '3000' ? 'http://localhost:8000' : '');
      const res = await fetch(`${baseUrl}/api/requirements/synthesize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          idea: query,
          custom_specifications: systemSpecification.trim() || undefined,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        if (data.specification_text) {
          setSystemSpecification(data.specification_text);
          return;
        }
      }
      // Fallback synthesis if endpoint is unavailable on current gateway instance
      const fallbackSpecs = [
        `• Architecture: High-Reliability Embedded Controller for ${query}`,
        `• Power Budget: Nominal 5V/12V DC input, multi-rail buck regulation (< 35W TDP)`,
        `• Operating Limits: -40°C to +85°C Industrial Range with passive thermal dissipation`,
        `• Interfaces: High-speed differential routing with ESD and reverse-polarity protection`,
        `• Compliance: RoHS, CE-RED, FCC Part 15 Class B emissions baseline`,
      ].join('\n');
      setSystemSpecification((prev) => prev ? `${prev}\n\n${fallbackSpecs}` : fallbackSpecs);
    } catch (err: any) {
      console.warn('Auto-synthesis network error, using fallback:', err);
      const fallbackSpecs = [
        `• Architecture: High-Reliability Embedded Controller for ${query}`,
        `• Power Budget: Nominal 5V/12V DC input, multi-rail buck regulation (< 35W TDP)`,
        `• Operating Limits: -40°C to +85°C Industrial Range with passive thermal dissipation`,
        `• Interfaces: High-speed differential routing with ESD and reverse-polarity protection`,
        `• Compliance: RoHS, CE-RED, FCC Part 15 Class B emissions baseline`,
      ].join('\n');
      setSystemSpecification((prev) => prev ? `${prev}\n\n${fallbackSpecs}` : fallbackSpecs);
    } finally {
      setIsSynthesizing(false);
    }
  };

  const handleAddSpecChip = (chipText: string) => {
    const cleanChip = chipText.replace(/^\+\s*/, '').trim();
    setSystemSpecification((prev) => {
      const trimmed = prev.trim();
      if (!trimmed) return `• ${cleanChip}`;
      return `${trimmed}\n• ${cleanChip}`;
    });
  };

  const activeError = validationError || errorMessage;

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
            disabled={isProcessing}
            className="p-1.5 rounded-md text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors cursor-pointer disabled:opacity-50"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Modal Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {activeError && (
            <div className="p-3 bg-red-950/40 border border-red-800/60 rounded-lg text-xs text-red-300 font-mono">
              {activeError}
            </div>
          )}

          {/* 1. PROJECT NAME (Primary Human-Readable Identifier) */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label className="block text-xs font-mono font-semibold text-slate-300 uppercase">
                Project Name <span className="text-red-400">*</span>
              </label>
              <span className="text-[10px] text-slate-500 font-mono">{projectName.length}/100</span>
            </div>
            <input
              type="text"
              required
              maxLength={100}
              placeholder="e.g. 48V to 12V High-Efficiency Buck Converter"
              value={projectName}
              onChange={(e) => {
                setProjectName(e.target.value);
                if (validationError) setValidationError(null);
              }}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 font-sans"
            />
            <p className="text-[11px] text-slate-500">
              Give your engineering project a clear, recognizable name.
            </p>
          </div>

          {/* 2. SYSTEM SPECIFICATION & ENGINEERING GOAL (Technical Requirement) */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label className="block text-xs font-mono font-semibold text-slate-300 uppercase">
                System Specification & Engineering Goal <span className="text-red-400">*</span>
              </label>
              <button
                type="button"
                onClick={handleAutoSynthesize}
                disabled={isSynthesizing || (!projectName.trim() && !systemSpecification.trim())}
                className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-indigo-950/90 border border-indigo-700/60 text-[11px] font-mono font-semibold text-indigo-300 hover:text-white hover:bg-indigo-900/80 transition disabled:opacity-40 cursor-pointer shadow-sm"
                title="Automatically generate full technical specifications from your project idea"
              >
                {isSynthesizing ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin text-indigo-400" />
                ) : (
                  <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                )}
                <span>{isSynthesizing ? 'Synthesizing...' : 'Auto-Generate Specs'}</span>
              </button>
            </div>
            <textarea
              rows={4}
              required
              placeholder="e.g. Design a 4-layer PCB buck converter with 95% efficiency, overvoltage protection, and automotive-grade component sourcing..."
              value={systemSpecification}
              onChange={(e) => {
                setSystemSpecification(e.target.value);
                if (validationError) setValidationError(null);
              }}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 font-sans leading-relaxed"
            />

            {/* Quick-Add Specification Chips */}
            <div className="space-y-1 pt-1">
              <div className="flex items-center justify-between text-[10px] font-mono text-slate-400">
                <span>Quick-Add Specifications (click to customize):</span>
              </div>
              <div className="flex flex-wrap gap-1.5 max-h-20 overflow-y-auto">
                {QUICK_SPEC_CHIPS.map((chip, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handleAddSpecChip(chip)}
                    className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-950/80 border border-slate-800 text-slate-400 hover:text-indigo-300 hover:border-indigo-700/50 transition cursor-pointer"
                  >
                    {chip}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* 3. Timeline Parameter */}
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

          {/* 4. Suggestion Templates */}
          <div className="space-y-2 pt-1">
            <div className="flex items-center gap-1.5 text-[10px] font-mono font-bold text-slate-500 uppercase">
              <Lightbulb className="w-3 h-3 text-amber-400" />
              <span>Engineering Template Examples</span>
            </div>
            <div className="space-y-1.5 max-h-32 overflow-y-auto pr-1">
              {TEMPLATE_SUGGESTIONS.map((item, idx) => (
                <button
                  type="button"
                  key={idx}
                  onClick={() => handleSelectTemplate(item)}
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
              disabled={isProcessing}
              className="px-4 py-2 rounded-md border border-slate-800 text-slate-300 hover:bg-slate-800 text-xs font-medium transition-colors cursor-pointer disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isProcessing || !projectName.trim() || !systemSpecification.trim()}
              className="px-5 py-2 rounded-md bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-bold shadow-md transition-all flex items-center gap-2 cursor-pointer"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>INITIALIZING PROJECT...</span>
                </>
              ) : (
                <>
                  <span>INITIALIZE PROJECT</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
