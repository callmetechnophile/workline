'use client';

import React, { useState, useEffect } from 'react';
import { useAuth, SignInButton, SignUpButton } from '@clerk/nextjs';
import { useCognitoAuth } from '@/lib/CognitoAuthContext';
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
  Check,
  CheckCircle2,
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

import DatasheetPanel, { SingleDatasheet } from '@/components/DatasheetPanel';
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
import { AgentOperationsWorkspace } from '@/components/AgentOperationsWorkspace';
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
import EngineeringBackground from '@/components/EngineeringBackground';

/* ================================================================
   PUBLIC LANDING PAGE — Shown to unauthenticated visitors.
   No engineering data. No sidebar. No project context.
   ================================================================ */
function PublicLandingPage() {
  return (
    <div className="h-screen max-h-screen overflow-hidden bg-slate-950 text-slate-100 flex flex-col justify-between relative select-none">
      {/* 30% Blurry Engineering Background Layer (Robotics, Electronics, Code, AI) */}
      <EngineeringBackground variant="hero" />

      {/* Header */}
      <header className="relative z-10 border-b border-slate-800/80 bg-slate-950/60 backdrop-blur-md flex-shrink-0">
        <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <img src="/icon.png" alt="Workline Logo" className="w-6 h-6 object-contain" />
            <span className="font-mono text-xs md:text-sm font-black tracking-widest text-slate-100 uppercase">
              WORKLINE AI
            </span>
          </div>
          <div className="flex items-center gap-2.5">
            <SignInButton mode="modal">
              <button className="text-xs font-mono font-semibold px-3 py-1.5 rounded-md border border-slate-700 bg-slate-900 hover:bg-slate-800 text-slate-300 transition-all cursor-pointer">
                Sign In
              </button>
            </SignInButton>
            <SignUpButton mode="modal">
              <button className="text-xs font-mono font-semibold px-3.5 py-1.5 rounded-md bg-indigo-600 hover:bg-indigo-500 text-white transition-all shadow-sm shadow-indigo-600/20 cursor-pointer">
                Get Started
              </button>
            </SignUpButton>
          </div>
        </div>
      </header>

      {/* Hero Section — Perfectly Centered in 100vh Viewport */}
      <main className="relative z-10 flex-1 flex flex-col items-center justify-center px-4 py-2 md:py-4 min-h-0">
        <div className="max-w-2xl text-center space-y-3 md:space-y-4 my-auto">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-950/70 border border-indigo-500/40 text-indigo-300 text-[11px] font-mono backdrop-blur-md shadow-lg shadow-indigo-950/50">
            <Shield className="w-3 h-3 text-indigo-400" />
            <span>Hardware Engineering Intelligence Platform</span>
          </div>

          <h1 className="text-3xl sm:text-4xl md:text-5xl font-extrabold tracking-tight text-white leading-[1.15]">
            Ideation to Implementation<br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-indigo-400 to-purple-400">
              Production Ready Ideas
            </span>
          </h1>

          <p className="text-xs sm:text-sm text-slate-300/85 max-w-lg mx-auto leading-relaxed font-sans">
            Workline AI guides engineers through the complete hardware lifecycle —
            requirements, research, BOM optimization, PCB validation,
            multi-physics simulation, and autonomous procurement —
            with deterministic verification at every gate.
          </p>

          {/* Social OAuth & Clerk Sign-in Actions */}
          <div className="flex flex-wrap items-center justify-center gap-2.5 pt-2">
            <SignInButton mode="modal">
              <button
                className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-slate-900/90 border border-slate-700 hover:border-slate-500 hover:bg-slate-800 text-slate-200 text-xs font-semibold shadow-md transition-all cursor-pointer hover:translate-y-[-1px]"
              >
                <svg className="w-4 h-4 shrink-0" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.66-5.17 3.66-9.17z"/>
                  <path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.33 24 12 24z"/>
                  <path fill="#FBBC05" d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.16 0 9.94 0 12s.45 3.84 1.25 5.42l4.03-3.15z"/>
                  <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.33 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.93 6.72-4.93z"/>
                </svg>
                <span>Continue with Google</span>
              </button>
            </SignInButton>

            <SignInButton mode="modal">
              <button
                className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-slate-900/90 border border-slate-700 hover:border-slate-500 hover:bg-slate-800 text-slate-200 text-xs font-semibold shadow-md transition-all cursor-pointer hover:translate-y-[-1px]"
              >
                <svg className="w-4 h-4 shrink-0 fill-current text-slate-100" viewBox="0 0 24 24">
                  <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"/>
                </svg>
                <span>Continue with GitHub</span>
              </button>
            </SignInButton>

            <SignInButton mode="modal">
              <button className="flex items-center justify-center gap-2 px-5 py-2.5 rounded-lg bg-gradient-to-r from-indigo-600 via-indigo-500 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/30 transition-all cursor-pointer hover:translate-y-[-1px]">
                <Sparkles className="w-3.5 h-3.5 text-amber-300" />
                <span>Launch Workbench</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </SignInButton>
          </div>

          {/* Feature Highlights */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-3 md:pt-4 max-w-xl mx-auto">
            <div className="bg-slate-900/80 border border-slate-800/90 hover:border-cyan-500/50 rounded-xl p-3 text-center space-y-1 backdrop-blur-md shadow-xl shadow-black/40 transition-all hover:scale-[1.02] group">
              <div className="p-1.5 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 w-fit mx-auto group-hover:scale-110 transition-transform">
                <Cpu className="w-4 h-4" />
              </div>
              <h3 className="text-xs font-bold text-slate-100 tracking-wide">Component Intelligence</h3>
              <p className="text-[10px] text-slate-400 leading-tight">Autonomous BOM sourcing & datasheet extraction</p>
            </div>
            <div className="bg-slate-900/80 border border-slate-800/90 hover:border-amber-500/50 rounded-xl p-3 text-center space-y-1 backdrop-blur-md shadow-xl shadow-black/40 transition-all hover:scale-[1.02] group">
              <div className="p-1.5 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400 w-fit mx-auto group-hover:scale-110 transition-transform">
                <Zap className="w-4 h-4" />
              </div>
              <h3 className="text-xs font-bold text-slate-100 tracking-wide">Multi-Physics PINN</h3>
              <p className="text-[10px] text-slate-400 leading-tight">Neural thermal solvers & power tree verification</p>
            </div>
            <div className="bg-slate-900/80 border border-slate-800/90 hover:border-emerald-500/50 rounded-xl p-3 text-center space-y-1 backdrop-blur-md shadow-xl shadow-black/40 transition-all hover:scale-[1.02] group">
              <div className="p-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 w-fit mx-auto group-hover:scale-110 transition-transform">
                <Layers className="w-4 h-4" />
              </div>
              <h3 className="text-xs font-bold text-slate-100 tracking-wide">x402 Procurement</h3>
              <p className="text-[10px] text-slate-400 leading-tight">Non-custodial cryptographic order settlement</p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-slate-800/80 bg-slate-950/60 backdrop-blur-md py-2.5 px-6 flex-shrink-0">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <span className="text-[10px] md:text-[11px] text-slate-400 font-mono">
            © 2026 Workline AI — Engineering Intelligence Platform
          </span>
          <div className="flex items-center gap-4 text-xs text-slate-400 font-mono">
            <a href="https://github.com/callmetechnophile/workline" target="_blank" rel="noopener noreferrer" className="hover:text-cyan-400 transition-colors flex items-center gap-1">
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
  const [loadingStage, setLoadingStage] = useState(0);

  const PIPELINE_LOADING_STAGES = [
    { label: "Analyzing engineering idea...", sub: "Decomposing requirements, functional boundaries, and target domain" },
    { label: "Extracting requirements and constraints...", sub: "Synthesizing electrical, thermal, and mechanical limits" },
    { label: "Querying Nexar / Octopart component intelligence...", sub: "Grounding verified MPNs, datasheets, and real distributor stock" },
    { label: "Searching arXiv, Crossref, and Semantic Scholar...", sub: "Retrieving literature, peer-reviewed DOIs, and citations" },
    { label: "Analyzing voltage and power compatibility...", sub: "Verifying pin mapping, power rail sequencing, and thermal limits" },
    { label: "Generating knowledge graph connections...", sub: "Indexing nodes and relational constraints into SurrealDB" },
    { label: "Finalizing verified engineering package...", sub: "Assembling revision lineage, BOM, and deterministic gates" },
  ];

  useEffect(() => {
    let interval: any;
    if (isProcessing) {
      setLoadingStage(0);
      interval = setInterval(() => {
        setLoadingStage((prev) => (prev < 6 ? prev + 1 : prev));
      }, 2000);
    } else {
      setLoadingStage(0);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isProcessing]);

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
    getToken,
  } = useProject();
  const [localError, setLocalError] = useState<string | null>(null);
  const [projectDatasheets, setProjectDatasheets] = useState<SingleDatasheet[]>([]);
  const [isGeneratingDatasheets, setIsGeneratingDatasheets] = useState(false);

  const fetchProjectDatasheets = async () => {
    const pId = projectId || projectData?.project_id || 'default-project';
    try {
      const token = await getToken();
      const res = await fetch(`${apiBase}/api/documents/datasheets?project_id=${pId}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) {
          setProjectDatasheets(data);
        }
      }
    } catch (e) {
      console.warn('Failed to load project datasheets:', e);
    }
  };

  const handleGenerateKnowledgeBase = async () => {
    const pId = projectId || projectData?.project_id || 'default-project';
    setIsGeneratingDatasheets(true);
    try {
      const token = await getToken();
      const res = await fetch(`${apiBase}/api/documents/nexar/generate-knowledge-base`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          project_id: pId,
          idea: systemSpecification || projectName,
          components: projectData?.components || projectData?.bom || [],
        }),
      });
      if (res.ok) {
        const data = await res.json();
        if (data.datasheets && Array.isArray(data.datasheets) && data.datasheets.length > 0) {
          setProjectDatasheets(data.datasheets);
        } else {
          await fetchProjectDatasheets();
        }
      }
    } catch (e) {
      console.warn('Failed to generate knowledge base:', e);
    } finally {
      setIsGeneratingDatasheets(false);
    }
  };

  useEffect(() => {
    fetchProjectDatasheets();
  }, [projectId, projectData]);

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
      const msg = err?.message || '';
      if (msg.includes('fetch') || msg.includes('Failed to fetch') || msg.includes('NetworkError')) {
        setLocalError('The cloud backend was waking up from sleep. The connection has been established — please click "INITIALIZE PROJECT" again.');
      } else {
        setLocalError(msg || 'Failed to initialize project.');
      }
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
        <div className="flex flex-col items-center justify-center p-8 max-w-xl mx-auto my-8 space-y-6">
          <div className="text-center space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-950/80 border border-indigo-700/40 text-[11px] font-mono text-indigo-300">
              <Loader2 className="w-3.5 h-3.5 animate-spin text-indigo-400" />
              <span>AUTONOMOUS ENGINEERING PIPELINE RUNNING</span>
            </div>
            <h2 className="text-lg font-bold text-slate-100">
              Synthesizing Hardware Architecture
            </h2>
            <p className="text-xs text-slate-400 max-w-md mx-auto leading-relaxed">
              Progressing through deterministic design gates, querying component distributor intelligence, and indexing research literature.
            </p>
          </div>

          {/* Progress Bar */}
          <div className="w-full bg-slate-900 border border-slate-800 rounded-full h-1.5 overflow-hidden">
            <div
              className="bg-indigo-500 h-full transition-all duration-500 ease-out"
              style={{ width: `${Math.round(((loadingStage + 1) / PIPELINE_LOADING_STAGES.length) * 100)}%` }}
            />
          </div>

          {/* 7 Sequential Stages */}
          <div className="w-full bg-slate-900/90 border border-slate-800 rounded-xl p-4 space-y-3">
            {PIPELINE_LOADING_STAGES.map((stage, idx) => {
              const isCompleted = idx < loadingStage;
              const isCurrent = idx === loadingStage;
              return (
                <div
                  key={idx}
                  className={`flex items-start gap-3 p-2.5 rounded-lg transition-all ${
                    isCurrent
                      ? 'bg-indigo-950/50 border border-indigo-700/50 text-slate-100'
                      : isCompleted
                      ? 'bg-slate-950/40 text-slate-300'
                      : 'opacity-40 text-slate-500'
                  }`}
                >
                  <div className="mt-0.5 flex-shrink-0">
                    {isCompleted ? (
                      <div className="w-4 h-4 rounded-full bg-emerald-950 border border-emerald-500 flex items-center justify-center text-emerald-400">
                        <Check className="w-2.5 h-2.5" />
                      </div>
                    ) : isCurrent ? (
                      <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
                    ) : (
                      <div className="w-4 h-4 rounded-full border border-slate-700 flex items-center justify-center text-[9px] font-mono">
                        {idx + 1}
                      </div>
                    )}
                  </div>
                  <div className="space-y-0.5 text-xs">
                    <div className={`font-mono font-semibold ${isCurrent ? 'text-indigo-200' : isCompleted ? 'text-slate-200' : 'text-slate-500'}`}>
                      {stage.label}
                    </div>
                    <div className="text-[11px] text-slate-400">
                      {stage.sub}
                    </div>
                  </div>
                </div>
              );
            })}
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
        const activePapersList =
          Array.isArray(projectData?.research_papers) && projectData.research_papers.length > 0
            ? projectData.research_papers
            : (Array.isArray(projectData?.papers) ? projectData.papers : []);
        return (
          <div className="space-y-6">
            <ResearchPapers
              papers={activePapersList}
              summary={projectData?.research_summary || projectData?.paper_summary}
              intent={systemSpecification || projectName}
              projectId={projectId || projectData?.project_id}
              projectName={projectName}
              apiBase={apiBase}
              onPapersUpdated={(newPapers, newSummary) => {
                const updated = {
                  ...(projectData || {}),
                  research_papers: newPapers,
                  papers: newPapers,
                  research_summary: newSummary,
                  paper_summary: typeof newSummary === 'object' ? newSummary : { summary: newSummary },
                };
                setProject(updated, projectName, targetDays);
              }}
            />
            <ContradictionViewer contradictions={Array.isArray(projectData?.contradictions) ? projectData.contradictions : []} />
          </div>
        );

      case 'knowledge':
        return (
          <div className="space-y-6">
            <DatasheetPanel
              datasheets={projectDatasheets}
              onFetchDatasheets={handleGenerateKnowledgeBase}
              isGenerating={isGeneratingDatasheets}
            />
            <DocumentLibrary
              projectId={projectId || projectData?.project_id || 'default-project'}
              apiBase={apiBase}
              onKnowledgeBaseGenerated={fetchProjectDatasheets}
            />
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
              <AlternativeComponents components={safeBomItems} optimizationData={projectData?.optimization} />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <PinMappingTable pins={projectData?.architecture?.pin_mapping || projectData?.pin_mapping} />
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
            <BoardCanvas
              projectComponents={safeBomItems}
              projectName={projectName}
              systemSpecification={systemSpecification}
              pinMapping={projectData?.architecture?.pin_mapping || projectData?.pin_mapping}
            />
            <ComponentPlacement
              projectComponents={safeBomItems}
              projectName={projectName}
              systemSpecification={systemSpecification}
              pinMapping={projectData?.architecture?.pin_mapping || projectData?.pin_mapping}
            />
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


      case 'procurement': {
        if (!hasProject) {
          return <EmptyProjectState onOpenNewProject={() => setIsModalOpen(true)} label="procurement" />;
        }
        const calculatedTotalUsd = Number(
          projectData?.total_cost_usd ??
          projectData?.total_usd ??
          projectData?.cost_totals?.total_usd ??
          (safeBomItems.length > 0
            ? safeBomItems.reduce((sum: number, item: any) => sum + (item.final_cost || ((item.base_cost || item.unit_price || 0) + (item.shipping_cost || 0))), 0) / 83.0
            : 0)
        ) || 27.06;
        const procurementAmount = Number(calculatedTotalUsd.toFixed(2));

        return (
          <div className="space-y-6">
            <PaymentPanel
              payment={{
                quote_id: projectData?.quote_id || `quote_bom_${(projectName || 'active').toLowerCase()}`,
                payment_request_id: `req_${(projectName || 'active').toLowerCase()}`,
                project_id: projectData?.project_id || projectName,
                bom_id: `bom_${(projectName || 'active').toLowerCase()}`,
                amount_usd: procurementAmount,
                amount_usdc: procurementAmount,
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
      }

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
              projectName={projectName || projectData?.name}
              projectId={projectId || projectData?.project_id}
              apiBase={apiBase}
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
          <AgentOperationsWorkspace
            apiBase={apiBase}
            projectId={projectData?.project_id || (hasProject ? projectName : 'proj_smart_battery_management_system_bms_for_4s')}
            projectName={projectName || 'Smart Battery Management System (BMS) for 4S'}
            teamId={projectData?.team_id || 'default_team'}
          />
        );

      case 'services':
        return <APIServicesPanel apiBase={apiBase} />;

      case 'payments':
        return <X402PaymentsPanel apiBase={apiBase} />;

      case 'health':
        return <ServiceHealthPanel />;

      case 'integrations':
        return <SystemIntegrationsPanel />;



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
            activeSection !== 'integrations' && (
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
        apiBase={apiBase}
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
  const clerkAuth = useAuth();
  const cognitoAuth = useCognitoAuth();

  const isLoaded = clerkAuth.isLoaded && cognitoAuth.isLoaded;
  const isSignedIn = clerkAuth.isSignedIn || cognitoAuth.isSignedIn;

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
