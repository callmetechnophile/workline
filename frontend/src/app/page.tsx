'use client';

import React, { useState } from 'react';
import { useAuth } from '@clerk/nextjs';
import { SignInButton, SignUpButton } from '@clerk/nextjs';
import {
  Sparkles,
  X,
  AlertCircle,
  Loader2,
  ExternalLink,
  ArrowRight,
  Shield,
  Cpu,
  Layers,
  Zap,
} from 'lucide-react';

// Layout Primitives
import Sidebar, { NavSection } from '@/components/layout/Sidebar';
import Topbar from '@/components/layout/Topbar';
import ProjectHeader from '@/components/layout/ProjectHeader';
import NewProjectModal from '@/components/layout/NewProjectModal';

// Project Context
import { ProjectProvider, useProject } from '@/lib/ProjectContext';

// Workspace & Engineering Panels
import ProjectOverview from '@/components/ProjectOverview';
import ServiceHealthPanel from '@/components/ServiceHealthPanel';
import SystemIntegrationsPanel from '@/components/SystemIntegrationsPanel';
import ConversationsWorkspace from '@/components/ConversationsWorkspace';
import APIServicesPanel from '@/components/APIServicesPanel';
import X402PaymentsPanel from '@/components/X402PaymentsPanel';

// Engineering Modules
import { BOMTable } from '@/components/BOMTable';
import BOMExportPanel from '@/components/BOMExportPanel';
import CostBreakdown from '@/components/CostBreakdown';
import ComponentTable from '@/components/ComponentTable';
import { CandidateComparison } from '@/components/CandidateComparison';
import AlternativeComponents from '@/components/AlternativeComponents';
import PinMappingTable from '@/components/PinMappingTable';
import VoltageRiskTable from '@/components/VoltageRiskTable';

import PowerAnalysis from '@/components/PowerAnalysis';
import ThermalRiskPanel from '@/components/ThermalRiskPanel';
import { PCBLayoutVisualization } from '@/components/PCBLayoutVisualization';

import { BoardCanvas } from '@/components/BoardCanvas';
import { ComponentPlacement } from '@/components/ComponentPlacement';


import { ConstraintPanel } from '@/components/ConstraintPanel';
import { ConstraintEditor } from '@/components/ConstraintEditor';
import { RequirementsWorkspace } from '@/components/RequirementsWorkspace';

import ResearchPapers from '@/components/ResearchPapers';
import ContradictionViewer from '@/components/ContradictionViewer';

import DatasheetPanel from '@/components/DatasheetPanel';
import { DocumentLibrary } from '@/components/DocumentLibrary';
import GraphExplorer from '@/components/GraphExplorer';

import DependencyGraph from '@/components/DependencyGraph';
import WiringDiagram from '@/components/WiringDiagram';

import ProcurementHeatmap from '@/components/ProcurementHeatmap';
import ReceiptExplorer from '@/components/ReceiptExplorer';

import ExecutionReadiness from '@/components/ExecutionReadiness';
import GanttRoadmap from '@/components/GanttRoadmap';
import AuditTrail from '@/components/AuditTrail';

// System & Agent Operations
import { AgentRegistry } from '@/components/AgentRegistry';
import { AgentCapabilityPanel } from '@/components/AgentCapabilityPanel';
import { AgentTaskPanel } from '@/components/AgentTaskPanel';
import { AgentExecutionTimeline } from '@/components/AgentExecutionTimeline';

// Team & Collaboration
import TeamWorkspace from '@/components/TeamWorkspace';

// Payment & Image Generation
import { PaymentPanel, PaymentDetails } from '@/components/PaymentPanel';
import ImageGenerationPanel from '@/components/ImageGenerationPanel';

// Contextual Copilot
import ConnectionChatbot from '@/components/ConnectionChatbot';

/* ================================================================
   PUBLIC LANDING PAGE — Shown to unauthenticated visitors.
   No engineering data. No sidebar. No project context.
   ================================================================ */
function PublicLandingPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-md">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <img src="/icon.png" alt="Workline Logo" className="w-7 h-7 object-contain" />
            <span className="font-mono text-sm font-black tracking-widest text-slate-100 uppercase">
              WORKLINE AI
            </span>
          </div>
          <div className="flex items-center gap-3">
            <SignInButton mode="modal">
              <button className="text-xs font-mono font-semibold px-4 py-2 rounded border border-slate-700 bg-slate-900 hover:bg-slate-800 text-slate-200 transition-all cursor-pointer">
                Sign In
              </button>
            </SignInButton>
            <SignUpButton mode="modal">
              <button className="text-xs font-mono font-semibold px-4 py-2 rounded bg-indigo-600 hover:bg-indigo-500 text-white transition-all cursor-pointer">
                Get Started
              </button>
            </SignUpButton>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1 flex flex-col items-center justify-center px-6 py-20">
        <div className="max-w-2xl text-center space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-950/60 border border-indigo-700/40 text-indigo-300 text-xs font-mono">
            <Shield className="w-3.5 h-3.5" />
            <span>Hardware Engineering Intelligence Platform</span>
          </div>

          <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-white leading-tight">
            From Idea to<br />
            <span className="text-indigo-400">Production-Ready Hardware</span>
          </h1>

          <p className="text-sm text-slate-400 max-w-lg mx-auto leading-relaxed">
            Workline AI guides engineers through the complete hardware lifecycle —
            requirements, research, BOM optimization, PCB validation,
            multi-physics simulation, and autonomous procurement —
            with deterministic verification at every gate.
          </p>

          <div className="flex items-center justify-center gap-4 pt-4">
            <SignUpButton mode="modal">
              <button className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-semibold shadow-lg transition-all cursor-pointer flex items-center gap-2">
                <span>Start Engineering</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </SignUpButton>
            <SignInButton mode="modal">
              <button className="px-6 py-2.5 border border-slate-700 bg-slate-900 hover:bg-slate-800 text-slate-200 rounded-lg text-sm font-medium transition-all cursor-pointer">
                Sign In
              </button>
            </SignInButton>
          </div>

          {/* Feature Highlights */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-12 max-w-xl mx-auto">
            <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-4 text-center space-y-2">
              <Cpu className="w-5 h-5 text-indigo-400 mx-auto" />
              <h3 className="text-xs font-bold text-slate-200">Component Intelligence</h3>
              <p className="text-[11px] text-slate-400">Autonomous BOM sourcing & datasheet extraction</p>
            </div>
            <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-4 text-center space-y-2">
              <Zap className="w-5 h-5 text-amber-400 mx-auto" />
              <h3 className="text-xs font-bold text-slate-200">Multi-Physics PINN</h3>
              <p className="text-[11px] text-slate-400">Neural thermal solvers & power tree verification</p>
            </div>
            <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-4 text-center space-y-2">
              <Layers className="w-5 h-5 text-emerald-400 mx-auto" />
              <h3 className="text-xs font-bold text-slate-200">x402 Procurement</h3>
              <p className="text-[11px] text-slate-400">Non-custodial cryptographic order settlement</p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-6">
        <div className="max-w-6xl mx-auto px-6 flex items-center justify-between">
          <span className="text-[11px] text-slate-500 font-mono">
            © 2026 Workline AI — Engineering Intelligence Platform
          </span>
          <div className="flex items-center gap-4 text-xs text-slate-500 font-mono">
            <a href="https://github.com/callmetechnophile/workline" target="_blank" rel="noopener noreferrer" className="hover:text-slate-300 transition-colors flex items-center gap-1">
              <span>GitHub</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}

/* ================================================================
   AUTHENTICATED ENGINEERING WORKBENCH — Shown after Clerk sign-in.
   All data comes from ProjectContext. No inline mock data.
   ================================================================ */
function AuthenticatedWorkbench() {
  const [activeSection, setActiveSection] = useState<NavSection>('overview');
  const [isLightMode, setIsLightMode] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isCopilotOpen, setIsCopilotOpen] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  const {
    projectData,
    projectId,
    projectName,
    systemSpecification,
    targetDays,
    teamName,
    status,
    hasProject,
    error,
    apiBase,
    setProject,
    savedHistory,
    isSaving,
    saveSpec,
  } = useProject();

  const { getToken } = useAuth();
  const [localError, setLocalError] = useState<string | null>(null);

  const handleCreateProject = async (
    name: string,
    specification: string,
    days: number,
    template?: string
  ) => {
    setIsProcessing(true);
    setLocalError(null);
    try {
      const token = await getToken();
      const response = await fetch(`${apiBase}/api/research`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          project_name: name.trim(),
          system_specification: specification.trim(),
          intent: specification.trim(),
          target_days: days,
          engineering_template: template,
        }),
      });

      if (!response.ok) {
        const errJson = await response.json().catch(() => null);
        throw new Error(
          errJson?.detail ||
            `Engineering analysis failed (HTTP ${response.status}). Ensure R1 Core Gateway is reachable.`
        );
      }

      const result = await response.json();
      setProject(result, result.project_name || name, days, {
        projectId: result.project_id,
        systemSpecification: specification,
        engineeringTemplate: template,
      });
      setIsModalOpen(false);
      setActiveSection('overview');
    } catch (err: any) {
      setLocalError(err?.message || 'Failed to initialize project.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleLoadHistory = (item: any) => {
    const loadedName = item.project_name || item.intent || 'Loaded Project';
    const loadedSpec = item.system_specification || item.intent || '';
    const loadedId = item.project_id || `PROJ-${loadedName.slice(0, 4).toUpperCase()}`;
    const loadedDays = item.target_days || 30;
    setProject(item.data, loadedName, loadedDays, {
      projectId: loadedId,
      systemSpecification: loadedSpec,
      engineeringTemplate: item.engineering_template,
      teamName: item.team_id || 'Hardware Engineering',
      status: item.status || 'active',
    });
    setActiveSection('overview');
  };

  const displayError = localError || error;

  const renderActiveWorkspace = () => {
    if (isProcessing) {
      return (
        <div className="flex flex-col items-center justify-center p-16 space-y-4 text-center">
          <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
          <div className="space-y-1">
            <h2 className="text-sm font-bold text-slate-100">
              Running Autonomous Engineering Analysis
            </h2>
            <p className="text-xs text-slate-400 max-w-sm">
              Synthesizing requirements, querying literature vectors, calculating
              BOM costs, and solving thermal PINN models...
            </p>
          </div>
        </div>
      );
    }

    const safeBomItems = Array.isArray(projectData?.bom_items)
      ? projectData.bom_items
      : Array.isArray(projectData?.bom?.items)
      ? projectData.bom.items
      : Array.isArray(projectData?.bom)
      ? projectData.bom
      : [];

    switch (activeSection) {
      case 'overview':
      case 'projects':
        return (
          <ProjectOverview
            projectData={projectData}
            projectName={projectName}
            projectId={projectId}
            systemSpecification={systemSpecification}
            targetDays={targetDays}
            teamName={teamName}
            status={status}
            onNavigate={(sec) => setActiveSection(sec)}
            onOpenNewProject={() => setIsModalOpen(true)}
          />
        );

      case 'requirements':
        return (
          <RequirementsWorkspace
            projectId={projectData?.project_id || (hasProject ? projectName : undefined)}
            projectName={projectName}
            projectData={projectData}
            apiBase={apiBase}
            onOpenNewProject={() => setIsModalOpen(true)}
          />
        );

      case 'research':
        if (!hasProject) {
          return <EmptyProjectState onOpenNewProject={() => setIsModalOpen(true)} label="research" />;
        }
        return (
          <div className="space-y-6">
            <ResearchPapers
              papers={Array.isArray(projectData?.research_papers) ? projectData.research_papers : []}
              summary={projectData?.research_summary}
            />
            <ContradictionViewer contradictions={Array.isArray(projectData?.contradictions) ? projectData.contradictions : []} />
          </div>
        );

      case 'knowledge':
        return (
          <div className="space-y-6">
            <DatasheetPanel />
            <DocumentLibrary />
            <GraphExplorer
              projectName={projectName || 'Active Engineering Project'}
              apiBase={apiBase}
            />
          </div>
        );

      case 'architecture':
        if (!hasProject) {
          return <EmptyProjectState onOpenNewProject={() => setIsModalOpen(true)} label="architecture" />;
        }
        return (
          <div className="space-y-6">
            <DependencyGraph data={projectData?.dependency_graph || { nodes: [], edges: [] }} />
            <WiringDiagram data={projectData?.wiring_diagram || { connections: [] }} />

            <ImageGenerationPanel
              projectId={projectData?.project_id || (hasProject ? projectName : 'default_project')}
              onGenerateImage={async (params) => {
                const res = await fetch(`${apiBase}/api/generation/image`, {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify(params),
                });
                return await res.json();
              }}
            />
          </div>

        );

      case 'components':
        if (!hasProject) {
          return <EmptyProjectState onOpenNewProject={() => setIsModalOpen(true)} label="components" />;
        }
        return (
          <div className="space-y-6">
            <ComponentTable components={safeBomItems} />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <CandidateComparison />
              <AlternativeComponents components={safeBomItems} />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <PinMappingTable />
              <VoltageRiskTable />
            </div>
          </div>
        );

      case 'bom':
        if (!hasProject) {
          return <EmptyProjectState onOpenNewProject={() => setIsModalOpen(true)} label="BOM" />;
        }
        return (
          <div className="space-y-6">
            <BOMTable items={safeBomItems} />
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <CostBreakdown components={safeBomItems} />
              </div>
              <div>
                <BOMExportPanel apiBase={apiBase} exports={projectData?.exports} />
              </div>
            </div>
          </div>
        );

      case 'pcb':
        if (!hasProject) {
          return <EmptyProjectState onOpenNewProject={() => setIsModalOpen(true)} label="PCB layout" />;
        }
        return (
          <div className="space-y-6">
            <PCBLayoutVisualization
              projectId={projectData?.project_id || projectId || projectName}
              projectName={projectName}
              engineeringGoal={systemSpecification}
              components={safeBomItems}
              powerAnalysis={projectData?.power_analysis}
              thermalAnalysis={projectData?.thermal_reports}
              apiBase={apiBase}
            />
            <BoardCanvas />
            <ComponentPlacement />
          </div>
        );

      case 'simulation':
        if (!hasProject) {
          return <EmptyProjectState onOpenNewProject={() => setIsModalOpen(true)} label="thermal analysis" />;
        }
        return (
          <div className="space-y-6">
            <ThermalRiskPanel
              projectId={projectData?.project_id || projectId || projectName}
              components={safeBomItems}
              powerAnalysis={projectData?.power_analysis}
              thermalReports={projectData?.thermal_reports}
            />
            <PowerAnalysis data={projectData?.power_analysis} />
          </div>
        );


      case 'procurement':
        if (!hasProject) {
          return <EmptyProjectState onOpenNewProject={() => setIsModalOpen(true)} label="procurement" />;
        }
        return (
          <div className="space-y-6">
            <PaymentPanel
              payment={{
                quote_id: projectData?.quote_id || `quote_bom_${(projectName || 'active').toLowerCase()}`,
                payment_request_id: `req_${(projectName || 'active').toLowerCase()}`,
                project_id: projectData?.project_id || projectName,
                bom_id: `bom_${(projectName || 'active').toLowerCase()}`,
                amount_usd: 5.00,
                amount_usdc: 5.00,
                currency: 'USD',

                network: 'algorand-testnet',
                asset: 'USDC',
                asset_id: 10458941,
                recipient: '3DOOXTOUNS7G3R6T2B2ESQBKECUQ2VRSOFXSOV54TAZ43FMC36X7W6G7MY',
                expires_at: new Date(Date.now() + 86400000).toISOString(),
                status: 'REQUIRED',
              }}

              onAuthorizePayment={async (quoteId, proof) => {
                const res = await fetch(`${apiBase}/api/procurement/${quoteId}/pay`, {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({
                    payment_proof: proof.signature,
                    tx_hash: proof.tx_hash,
                    signed_txn: proof.signed_txn,
                  }),
                });
                if (!res.ok) {
                  const err = await res.json();
                  throw new Error(err.detail || 'Payment authorization failed');
                }
              }}
              onGenerateReport={async (quoteId) => {
                const res = await fetch(`${apiBase}/api/procurement/report/${quoteId}`);
                if (!res.ok) throw new Error('Report generation failed');
                return await res.json();
              }}
            />
            <ProcurementHeatmap />
            <ReceiptExplorer apiBase={apiBase} />
          </div>
        );

      case 'release':
        if (!hasProject) {
          return <EmptyProjectState onOpenNewProject={() => setIsModalOpen(true)} label="release readiness" />;
        }
        return (
          <div className="space-y-6">
            <ExecutionReadiness
              readiness={projectData?.validation?.readiness_score}
              risk={projectData?.validation?.risk_score}
              optimization={projectData?.optimization?.optimization_score}
            />
            <GanttRoadmap
              roadmap={projectData?.roadmap || []}
              gantt={projectData?.gantt || []}
              projectName={projectName}
            />
            <AuditTrail logs={projectData?.audit_trail || []} />
          </div>
        );

      case 'conversations':
        return (
          <ConversationsWorkspace
            savedHistory={savedHistory}
            onLoadHistory={handleLoadHistory}
            onOpenNewProject={() => setIsModalOpen(true)}
          />
        );

      case 'teams':
        return (
          <TeamWorkspace
            apiBase={apiBase}
            projectId={projectData?.project_id || (hasProject ? projectName : undefined)}
            currentUserRole="OWNER"
          />
        );

      case 'agents':
        return (
          <div className="space-y-6">
            <AgentRegistry agents={[]} />
            <AgentCapabilityPanel agent={null} />
            <AgentTaskPanel tasks={[]} />
            <AgentExecutionTimeline externalTasks={[]} />
          </div>
        );

      case 'services':
        return <APIServicesPanel apiBase={apiBase} />;

      case 'payments':
        return <X402PaymentsPanel apiBase={apiBase} />;

      case 'health':
        return <ServiceHealthPanel />;

      case 'integrations':
        return <SystemIntegrationsPanel />;

      case 'settings':
        return (
          <div className="bg-slate-900/80 border border-slate-800 rounded-lg p-6 space-y-5 max-w-3xl">
            <h2 className="text-sm font-bold text-slate-100 uppercase font-mono tracking-wider">
              Workspace & Infrastructure Settings
            </h2>
            <div className="space-y-4 text-xs text-slate-300">
              <div>
                <label className="block text-slate-500 font-mono mb-1">
                  R1 CORE GATEWAY URL
                </label>
                <input
                  type="text"
                  disabled
                  value={apiBase}
                  className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-slate-300 font-mono"
                />
              </div>

              <div>
                <label className="block text-slate-500 font-mono mb-1">
                  CENTRAL AI INFERENCE PROVIDER
                </label>
                <input
                  type="text"
                  disabled
                  value="Amazon Bedrock (R2 AI / Google ADK Runtime)"
                  className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-slate-300 font-mono"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
                <div className="bg-slate-950 p-3 rounded border border-slate-800 font-mono">
                  <div className="text-[10px] text-indigo-400 font-bold">Research & Literature Model</div>
                  <div className="text-slate-200 mt-1 font-semibold">DeepSeek V3 / R1</div>
                </div>
                <div className="bg-slate-950 p-3 rounded border border-slate-800 font-mono">
                  <div className="text-[10px] text-indigo-400 font-bold">Fast Code & Tools Model</div>
                  <div className="text-slate-200 mt-1 font-semibold">Claude 3.5 Haiku</div>
                </div>
                <div className="bg-slate-950 p-3 rounded border border-slate-800 font-mono">
                  <div className="text-[10px] text-indigo-400 font-bold">Multi-Physics & Reports Model</div>
                  <div className="text-slate-200 mt-1 font-semibold">Claude 3.5 / 3.7 Sonnet</div>
                </div>
                <div className="bg-slate-950 p-3 rounded border border-slate-800 font-mono">
                  <div className="text-[10px] text-indigo-400 font-bold">Visual Generation Engine</div>
                  <div className="text-slate-200 mt-1 font-semibold">Amazon Nova Canvas / Titan</div>
                </div>
              </div>

              <div>
                <label className="block text-slate-500 font-mono mb-1">
                  PAYMENT PROTOCOL & BLOCKCHAIN SETTLEMENT
                </label>
                <input
                  type="text"
                  disabled
                  value="Algorand Mainnet (USDC ASA #31566704) via GoPlausible x402"
                  className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-slate-300 font-mono"
                />
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className={`min-h-screen flex bg-slate-950 text-slate-100 ${isLightMode ? 'light' : 'dark'}`}>
      {/* Persistent Industrial Left Sidebar */}
      <Sidebar
        activeSection={activeSection}
        onSelectSection={(sec) => setActiveSection(sec)}
        onOpenNewProject={() => setIsModalOpen(true)}
        projectName={projectName}
        hasProject={hasProject}
      />

      {/* Main Execution Workspace Shell */}
      <div className="flex-1 flex flex-col min-w-0 h-screen overflow-y-auto">
        <Topbar
          isLightMode={isLightMode}
          onToggleTheme={() => setIsLightMode(!isLightMode)}
          projectName={projectName}
          onOpenNewProject={() => setIsModalOpen(true)}
          onOpenCopilot={() => setIsCopilotOpen(true)}
        />

        <main className="flex-1 p-6 max-w-7xl w-full mx-auto space-y-6">
          {displayError && (
            <div className="bg-red-950/30 border border-red-500/40 rounded-lg p-4 text-xs text-red-300 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0 text-red-400" />
                <span>{displayError}</span>
              </div>
              <button
                onClick={() => setLocalError(null)}
                className="text-red-400 hover:text-red-200 text-xs font-mono cursor-pointer"
              >
                Dismiss
              </button>
            </div>
          )}

          {/* Project Context Header */}
          {hasProject &&
            activeSection !== 'conversations' &&
            activeSection !== 'health' &&
            activeSection !== 'integrations' &&
            activeSection !== 'settings' && (
              <ProjectHeader
                projectName={projectName || 'Autonomous Engineering Project'}
                teamName={teamName}
                status={status as any}
                targetDays={targetDays}
                onSave={saveSpec}
                isSaving={isSaving}
                onRefresh={() => handleCreateProject(projectName, systemSpecification, targetDays)}
              />
            )}

          {/* Active Workspace View */}
          {renderActiveWorkspace()}
        </main>
      </div>

      {/* Contextual AI Copilot Drawer */}
      {isCopilotOpen && (
        <div className="fixed inset-y-0 right-0 w-96 bg-slate-900 border-l border-slate-800 shadow-2xl z-40 flex flex-col animate-in slide-in-from-right duration-200">
          <div className="h-14 px-4 border-b border-slate-800 flex items-center justify-between bg-slate-950">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-indigo-400" />
              <span className="text-xs font-bold text-slate-100 uppercase font-mono">
                Workline Copilot
              </span>
            </div>
            <button
              onClick={() => setIsCopilotOpen(false)}
              className="p-1 rounded text-slate-400 hover:text-white cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-4">
            <ConnectionChatbot
              projectContext={{
                bom: projectData?.bom || [],
                wiring: projectData?.wiring_diagram || {},
                power: projectData?.power_analysis || {},
                datasheets: projectData?.datasheets || [],
              }}
              apiBase={apiBase}
            />
          </div>
        </div>
      )}

      {/* New Project Creation Modal */}
      <NewProjectModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleCreateProject}
        isProcessing={isProcessing}
        errorMessage={localError}
      />
    </div>
  );
}

/* ================================================================
   EMPTY PROJECT STATE — Shown on engineering modules when no
   project is selected. Never renders fabricated data.
   ================================================================ */
function EmptyProjectState({
  onOpenNewProject,
  label,
}: {
  onOpenNewProject: () => void;
  label: string;
}) {
  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-12 text-center max-w-xl mx-auto my-8 space-y-4">
      <div className="w-10 h-10 rounded-full bg-slate-800 text-slate-500 flex items-center justify-center mx-auto">
        <Layers className="w-5 h-5" />
      </div>
      <div className="space-y-1">
        <h3 className="text-sm font-bold text-slate-200">No Project Selected</h3>
        <p className="text-xs text-slate-400">
          Create or select a project to view {label} data.
        </p>
      </div>
      <button
        onClick={onOpenNewProject}
        className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-md text-xs font-semibold shadow transition-all cursor-pointer inline-flex items-center gap-1.5"
      >
        <span>Create Project</span>
        <ArrowRight className="w-3.5 h-3.5" />
      </button>
    </div>
  );
}

/* ================================================================
   ROOT HOME COMPONENT — Auth gate.
   Unauthenticated → PublicLandingPage
   Authenticated   → ProjectProvider → AuthenticatedWorkbench
   ================================================================ */
export default function Home() {
  const { isSignedIn, isLoaded } = useAuth();

  if (!isLoaded) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <Loader2 className="w-6 h-6 text-indigo-400 animate-spin" />
      </div>
    );
  }

  if (!isSignedIn) {
    return <PublicLandingPage />;
  }

  return (
    <ProjectProvider>
      <AuthenticatedWorkbench />
    </ProjectProvider>
  );
}
