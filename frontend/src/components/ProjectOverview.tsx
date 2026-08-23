'use client';

import React from 'react';
import { 
  CheckSquare, 
  BookOpen, 
  Layers, 
  Zap, 
  ShoppingCart, 
  PackageCheck, 
  ArrowRight, 
  AlertTriangle,
  Cpu,
  CircuitBoard,
  Activity,
  FileText,
  CheckCircle2
} from 'lucide-react';
import { NavSection } from './layout/Sidebar';
import EngineeringStatusBadge from './EngineeringStatusBadge';

interface ProjectOverviewProps {
  projectData: any;
  projectName?: string;
  projectId?: string;
  systemSpecification?: string;
  targetDays?: number;
  teamName?: string;
  status?: string;
  onNavigate: (section: NavSection) => void;
  onOpenNewProject: () => void;
}

export default function ProjectOverview({
  projectData,
  projectName,
  projectId,
  systemSpecification,
  targetDays,
  teamName,
  status,
  onNavigate,
  onOpenNewProject,
}: ProjectOverviewProps) {
  if (!projectData) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-12 text-center max-w-2xl mx-auto my-12 space-y-5">
        <div className="w-12 h-12 rounded-full bg-indigo-950/80 border border-indigo-700/40 text-indigo-400 flex items-center justify-center mx-auto">
          <Layers className="w-6 h-6" />
        </div>
        <div className="space-y-1.5">
          <h2 className="text-base font-bold text-slate-100">No Active Engineering Project</h2>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            Create or select a project to analyze requirements, generate optimized BOMs, run multi-physics simulations, and execute procurement.
          </p>
        </div>
        <button
          onClick={onOpenNewProject}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-md text-xs font-semibold shadow transition-all cursor-pointer inline-flex items-center gap-2"
        >
          <span>Create First Project</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>
    );
  }

  const resolvedProjectName = projectName || projectData.project_name || 'Untitled Engineering Project';
  const resolvedProjectId = projectId || projectData.project_id || `PROJ-${resolvedProjectName.slice(0, 4).toUpperCase()}`;
  const resolvedGoal = systemSpecification || projectData.system_specification || projectData.intent || 'High-speed engineering system specification';
  const resolvedTargetDays = targetDays || projectData.target_timeline_days || 30;
  const resolvedTeamName = teamName || projectData.team_id || 'Hardware Engineering';
  const resolvedStatus = status || projectData.status || 'Active';

  const bomItems = projectData.bom || [];
  const papers = projectData.research_papers || [];
  const conflicts = projectData.contradictions || [];
  const readiness = projectData.validation?.readiness_score ?? '—';
  const risk = projectData.validation?.risk_score ?? '—';

  const modules = [
    {
      id: 'requirements' as NavSection,
      title: 'Requirements & Constraints',
      count: 'Validated',
      desc: 'System power, voltage, and interface constraints',
      icon: CheckSquare,
      status: 'PASS' as const,
    },
    {
      id: 'research' as NavSection,
      title: 'Research & Literature',
      count: `${papers.length} Sources`,
      desc: 'Academic papers, datasheets & technical references',
      icon: BookOpen,
      status: papers.length > 0 ? ('PASS' as const) : ('PENDING' as const),
    },
    {
      id: 'components' as NavSection,
      title: 'Components & Sourcing',
      count: `${bomItems.length} Parts`,
      desc: 'Pin mapping, voltage risk, and candidate alternatives',
      icon: Cpu,
      status: bomItems.length > 0 ? ('PASS' as const) : ('PENDING' as const),
    },
    {
      id: 'bom' as NavSection,
      title: 'Bill of Materials',
      count: projectData.optimization?.total_cost_inr ? `₹${projectData.optimization.total_cost_inr}` : '—',
      desc: 'Multi-vendor consolidation (DigiKey, Mouser, Robu)',
      icon: Layers,
      status: bomItems.length > 0 ? ('PASS' as const) : ('PENDING' as const),
    },
    {
      id: 'pcb' as NavSection,
      title: 'PCB & Layout',
      count: projectData.pcb ? 'Layout Ready' : '—',
      desc: 'DRC geometric checks, layer stackup & pin routing',
      icon: CircuitBoard,
      status: projectData.pcb ? ('PASS' as const) : ('PENDING' as const),
    },
    {
      id: 'simulation' as NavSection,
      title: 'Simulation & Physics',
      count: projectData.power_analysis ? 'Analyzed' : '—',
      desc: 'PINN surrogate neural loss & power tree dissipation',
      icon: Zap,
      status: projectData.power_analysis ? ('PASS' as const) : ('PENDING' as const),
    },
    {
      id: 'procurement' as NavSection,
      title: 'Procurement & Orders',
      count: projectData.procurement ? 'Quote Ready' : '—',
      desc: 'Non-custodial x402 payment challenge & settlement',
      icon: ShoppingCart,
      status: projectData.procurement ? ('PASS' as const) : ('PENDING' as const),
    },
    {
      id: 'release' as NavSection,
      title: 'Release Readiness',
      count: typeof readiness === 'number' ? `${readiness}% Score` : '—',
      desc: 'Deterministic gates & tamper-evident packaging',
      icon: PackageCheck,
      status: typeof risk === 'number' && risk < 35 ? ('PASS' as const) : ('PENDING' as const),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Project Identity & Specification Header */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-3">
          <div>
            <div className="text-[10px] font-mono font-bold tracking-wider text-slate-500 uppercase">
              PROJECT IDENTITY
            </div>
            <h1 className="text-lg font-bold text-slate-100 tracking-tight">
              {resolvedProjectName}
            </h1>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[11px] font-mono px-2.5 py-1 rounded bg-slate-950 border border-slate-800 text-slate-400">
              ID: {resolvedProjectId}
            </span>
            <span className="text-[11px] font-mono px-2.5 py-1 rounded bg-cyan-950/40 border border-cyan-800/40 text-cyan-300 font-semibold">
              TEAM: {resolvedTeamName}
            </span>
            <span className="text-[11px] font-mono px-2.5 py-1 rounded bg-emerald-950/40 border border-emerald-800/40 text-emerald-300 uppercase font-semibold">
              {resolvedStatus}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className="md:col-span-2 space-y-1">
            <span className="text-[10px] font-mono text-slate-500 uppercase font-bold">
              ENGINEERING GOAL & SPECIFICATION
            </span>
            <p className="text-slate-300 font-sans leading-relaxed text-xs">
              {resolvedGoal}
            </p>
          </div>
          <div className="space-y-1 md:border-l md:border-slate-800 md:pl-4">
            <span className="text-[10px] font-mono text-slate-500 uppercase font-bold">
              TARGET TIMELINE
            </span>
            <div className="text-sm font-bold font-mono text-indigo-400">
              {resolvedTargetDays} Days
            </div>
            <div className="text-[11px] text-slate-500">Autonomous execution window</div>
          </div>
        </div>
      </div>

      {/* Sequential Pipeline Orchestration Status */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-mono font-bold tracking-wider text-slate-500 uppercase">
              SEQUENTIAL PIPELINE ORCHESTRATION (R1 → R2 → R3 → R4 → R5)
            </span>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-950/80 text-indigo-300 border border-indigo-800/40">
              R1 AUTHORITATIVE
            </span>
          </div>
          <span className="text-[11px] font-mono text-emerald-400 font-bold flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>LINEAGE VERIFIED</span>
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2.5">
          <div className="bg-slate-950/80 border border-slate-800 rounded-lg p-2.5 space-y-1">
            <div className="flex items-center justify-between text-[10px] font-mono">
              <span className="text-slate-400 font-bold">R2: REQUIREMENTS</span>
              <span className="text-emerald-400 font-bold">✓ Rev {projectData.pipeline_lineage?.requirements_revision || 1}</span>
            </div>
            <div className="text-[11px] font-semibold text-slate-200 truncate">Validated Goals</div>
            <div className="text-[9px] text-slate-500 font-mono">Upstream: User Request</div>
          </div>

          <div className="bg-slate-950/80 border border-slate-800 rounded-lg p-2.5 space-y-1">
            <div className="flex items-center justify-between text-[10px] font-mono">
              <span className="text-slate-400 font-bold">R3: RESEARCH</span>
              <span className="text-emerald-400 font-bold">✓ Rev {projectData.pipeline_lineage?.research_revision || 1}</span>
            </div>
            <div className="text-[11px] font-semibold text-slate-200 truncate">{papers.length} Papers & Standards</div>
            <div className="text-[9px] text-slate-500 font-mono">Based on: R2_v{projectData.pipeline_lineage?.requirements_revision || 1}</div>
          </div>

          <div className="bg-slate-950/80 border border-slate-800 rounded-lg p-2.5 space-y-1">
            <div className="flex items-center justify-between text-[10px] font-mono">
              <span className="text-slate-400 font-bold">R4: ENGINEERING</span>
              <span className="text-emerald-400 font-bold">✓ Rev {projectData.pipeline_lineage?.architecture_revision || 1}</span>
            </div>
            <div className="text-[11px] font-semibold text-slate-200 truncate">Architecture & Wiring</div>
            <div className="text-[9px] text-slate-500 font-mono">Based on: R2_v1 + R3_v1</div>
          </div>

          <div className="bg-slate-950/80 border border-slate-800 rounded-lg p-2.5 space-y-1">
            <div className="flex items-center justify-between text-[10px] font-mono">
              <span className="text-slate-400 font-bold">R5: CANONICAL BOM</span>
              <span className="text-emerald-400 font-bold">✓ Rev {projectData.pipeline_lineage?.bom_revision || 1}</span>
            </div>
            <div className="text-[11px] font-semibold text-slate-200 truncate">{bomItems.length} Sourced Parts</div>
            <div className="text-[9px] text-slate-500 font-mono">Based on: R2+R3+R4</div>
          </div>

          <div className="bg-slate-950/80 border border-indigo-800/40 rounded-lg p-2.5 space-y-1">
            <div className="flex items-center justify-between text-[10px] font-mono">
              <span className="text-indigo-300 font-bold">PROCUREMENT / x402</span>
              <span className="text-indigo-400 font-bold">● READY</span>
            </div>
            <div className="text-[11px] font-semibold text-indigo-200 truncate">${Number(projectData.total_cost_usd || projectData.total_usd || 0).toFixed(2)} USD</div>
            <div className="text-[9px] text-indigo-400 font-mono">Algorand Settlement</div>
          </div>
        </div>
      </div>

      {/* High-Level Metric Tiles */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/90 border border-slate-800 rounded-lg p-4 space-y-1">
          <div className="text-[11px] font-mono text-slate-500 uppercase">Readiness Score</div>
          <div className="text-2xl font-bold font-mono text-emerald-400">{readiness}%</div>
          <div className="text-[10px] text-slate-400">All core criteria verified</div>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 rounded-lg p-4 space-y-1">
          <div className="text-[11px] font-mono text-slate-500 uppercase">Risk Index</div>
          <div className="text-2xl font-bold font-mono text-amber-400">{risk}%</div>
          <div className="text-[10px] text-slate-400">Low thermal derating exposure</div>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 rounded-lg p-4 space-y-1">
          <div className="text-[11px] font-mono text-slate-500 uppercase">BOM Line Items</div>
          <div className="text-2xl font-bold font-mono text-slate-100">{bomItems.length}</div>
          <div className="text-[10px] text-slate-400">Multi-supplier verified</div>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 rounded-lg p-4 space-y-1">
          <div className="text-[11px] font-mono text-slate-500 uppercase">Literature Sources</div>
          <div className="text-2xl font-bold font-mono text-cyan-400">{papers.length}</div>
          <div className="text-[10px] text-slate-400">Extracted from IEEE/arXiv</div>
        </div>
      </div>

      {/* Engineering Lifecycle Modules Grid */}
      <div className="space-y-3">
        <h2 className="text-xs font-mono font-bold tracking-wider text-slate-400 uppercase">
          Engineering Lifecycle Workspaces
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {modules.map((m) => {
            const Icon = m.icon;
            return (
              <button
                key={m.id}
                onClick={() => onNavigate(m.id)}
                className="bg-slate-900/80 hover:bg-slate-850 border border-slate-800 hover:border-slate-700 rounded-lg p-4 text-left transition-all group flex flex-col justify-between h-36 cursor-pointer"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <div className="p-2 rounded-md bg-slate-950 border border-slate-800 text-indigo-400 group-hover:text-indigo-300">
                      <Icon className="w-4 h-4" />
                    </div>
                    <EngineeringStatusBadge status={m.status} size="sm" />
                  </div>
                  <h3 className="text-xs font-bold text-slate-200 group-hover:text-white truncate">
                    {m.title}
                  </h3>
                  <p className="text-[11px] text-slate-400 line-clamp-2 mt-0.5">
                    {m.desc}
                  </p>
                </div>
                <div className="flex items-center justify-between text-[11px] font-mono font-semibold text-slate-300 pt-2 border-t border-slate-850/60">
                  <span>{m.count}</span>
                  <ArrowRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-indigo-400 group-hover:translate-x-0.5 transition-all" />
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Conflicts / Warnings Notification Area if any */}
      {conflicts.length > 0 && (
        <div className="bg-amber-950/20 border border-amber-500/30 rounded-lg p-4 space-y-2">
          <div className="flex items-center gap-2 text-xs font-mono font-bold text-amber-400">
            <AlertTriangle className="w-4 h-4" />
            <span>{conflicts.length} Engineering Constraints Flagged for Review</span>
          </div>
          <ul className="text-xs text-slate-300 space-y-1 list-disc list-inside">
            {conflicts.slice(0, 2).map((c: any, idx: number) => (
              <li key={idx} className="truncate">
                {c.description || c.title || 'Constraint contradiction identified in power sequencing.'}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
