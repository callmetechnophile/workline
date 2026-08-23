'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '@clerk/nextjs';
import { 
  FolderKanban, 
  Plus, 
  Layers, 
  Sparkles, 
  X, 
  AlertCircle, 
  Loader2,
  Cpu,
  Zap,
  CircuitBoard,
  ShoppingCart,
  PackageCheck,
  CheckSquare,
  BookOpen,
  Database,
  Network
} from 'lucide-react';

// Layout Primitives
import Sidebar, { NavSection } from '@/components/layout/Sidebar';
import Topbar from '@/components/layout/Topbar';
import ProjectHeader from '@/components/layout/ProjectHeader';
import NewProjectModal from '@/components/layout/NewProjectModal';

// Workspace & Engineering Panels
import ProjectOverview from '@/components/ProjectOverview';
import ServiceHealthPanel from '@/components/ServiceHealthPanel';
import SystemIntegrationsPanel from '@/components/SystemIntegrationsPanel';
import ConversationsWorkspace from '@/components/ConversationsWorkspace';

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

import { BoardCanvas } from '@/components/BoardCanvas';
import { ComponentPlacement } from '@/components/ComponentPlacement';

import { ConstraintPanel } from '@/components/ConstraintPanel';
import { ConstraintEditor } from '@/components/ConstraintEditor';

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

// Contextual Copilot
import ConnectionChatbot from '@/components/ConnectionChatbot';

export default function Home() {
  const [activeSection, setActiveSection] = useState<NavSection>('overview');
  const [isLightMode, setIsLightMode] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isCopilotOpen, setIsCopilotOpen] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [pipelineData, setPipelineData] = useState<any>(null);
  const [currentProjectName, setCurrentProjectName] = useState<string>('');
  const [targetDays, setTargetDays] = useState<number>(30);
  const [savedHistory, setSavedHistory] = useState<any[]>([]);
  const [isSaving, setIsSaving] = useState(false);

  const { getToken, userId } = useAuth();
  const [apiBase, setApiBase] = useState('');

  useEffect(() => {
    if (typeof window !== 'undefined') {
      if (process.env.NEXT_PUBLIC_API_URL) {
        setApiBase(process.env.NEXT_PUBLIC_API_URL);
      } else if (window.location.port === '3000') {
        setApiBase('http://localhost:8000');
      } else {
        setApiBase('https://workline-core-gateway.onrender.com');
      }

      // Load cached project if present
      const cached = localStorage.getItem('workline_active_project');
      if (cached) {
        try {
          const parsed = JSON.parse(cached);
          setPipelineData(parsed.data);
          setCurrentProjectName(parsed.name || 'Synchronous Buck Converter');
          setTargetDays(parsed.days || 30);
        } catch (e) {
          console.error(e);
        }
      }
    }
  }, []);

  // Fetch session history
  useEffect(() => {
    async function fetchHistory() {
      if (!userId || !apiBase) return;
      try {
        const token = await getToken();
        const res = await fetch(`${apiBase}/api/packages/history`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          setSavedHistory(data);
        }
      } catch (err) {
        console.error("Failed to fetch session history:", err);
      }
    }
    fetchHistory();
  }, [userId, apiBase, getToken]);

  const handleCreateProject = async (intent: string, days: number) => {
    setIsProcessing(true);
    setError(null);
    try {
      const response = await fetch(`${apiBase}/api/research`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ intent, target_days: days })
      });

      if (!response.ok) {
        throw new Error(`Engineering analysis failed (HTTP ${response.status}). Ensure R1 Core Gateway is reachable.`);
      }

      const result = await response.json();
      setPipelineData(result);
      setCurrentProjectName(intent);
      setTargetDays(days);
      setIsModalOpen(false);
      setActiveSection('overview');

      if (typeof window !== 'undefined') {
        localStorage.setItem('workline_active_project', JSON.stringify({
          name: intent,
          days,
          data: result
        }));
      }
    } catch (err: any) {
      setError(err?.message || "Failed to initialize project.");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSaveSpec = async () => {
    if (!pipelineData) return;
    setIsSaving(true);
    try {
      const token = await getToken();
      const response = await fetch(`${apiBase}/api/packages/save`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          intent: currentProjectName || pipelineData.intent,
          readiness_score: pipelineData.validation?.readiness_score || 85,
          risk_score: pipelineData.validation?.risk_score || 25,
          optimization_score: pipelineData.optimization?.optimization_score || 90,
          data: pipelineData
        })
      });

      if (response.ok) {
        const updated = await fetch(`${apiBase}/api/packages/history`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (updated.ok) {
          const list = await updated.json();
          setSavedHistory(list);
        }
        alert("Engineering specification package saved to your profile.");
      } else {
        alert("Failed to save specification.");
      }
    } catch (err) {
      console.error(err);
      alert("Error connecting to Workline API.");
    } finally {
      setIsSaving(false);
    }
  };

  const handleLoadHistory = (item: any) => {
    setPipelineData(item.data);
    setCurrentProjectName(item.intent || 'Loaded Project');
    setActiveSection('overview');
  };

  const renderActiveWorkspace = () => {
    if (isProcessing) {
      return (
        <div className="flex flex-col items-center justify-center p-16 space-y-4 text-center">
          <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
          <div className="space-y-1">
            <h2 className="text-sm font-bold text-slate-100">Running Autonomous Engineering Analysis</h2>
            <p className="text-xs text-slate-400 max-w-sm">
              Synthesizing requirements, querying literature vectors, calculating BOM costs, and solving thermal PINN models...
            </p>
          </div>
        </div>
      );
    }

    switch (activeSection) {
      case 'overview':
      case 'projects':
        return (
          <ProjectOverview
            projectData={pipelineData}
            onNavigate={(sec) => setActiveSection(sec)}
            onOpenNewProject={() => setIsModalOpen(true)}
          />
        );

      case 'requirements':
        return (
          <div className="space-y-6">
            <ConstraintEditor />
            <ConstraintPanel />
          </div>
        );

      case 'research':
        return (
          <div className="space-y-6">
            <ResearchPapers 
              papers={pipelineData?.research_papers || []} 
              summary={pipelineData?.research_summary || {
                paper_id: 'lit_01',
                title: 'Literature Overview',
                summary: 'Academic synthesis for hardware component topology and constraints.',
                conclusions: ['Validated topology', 'Meets thermal specs'],
                recommendations: 'Proceed with selected architecture.'
              }}
            />
            <ContradictionViewer contradictions={pipelineData?.contradictions || []} />
          </div>
        );

      case 'knowledge':
        return (
          <div className="space-y-6">
            <DatasheetPanel />
            <DocumentLibrary />
            <GraphExplorer 
              projectName={currentProjectName || 'Active Engineering Project'} 
              apiBase={apiBase} 
            />
          </div>
        );

      case 'architecture':
        return (
          <div className="space-y-6">
            <DependencyGraph data={pipelineData?.dependency_graph || { nodes: [], edges: [] }} />
            <WiringDiagram data={pipelineData?.wiring_diagram || { connections: [] }} />
          </div>
        );

      case 'components':
        return (
          <div className="space-y-6">
            <ComponentTable components={pipelineData?.bom || []} />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <CandidateComparison />
              <AlternativeComponents components={pipelineData?.bom || []} />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <PinMappingTable />
              <VoltageRiskTable />
            </div>
          </div>
        );

      case 'bom':
        return (
          <div className="space-y-6">
            <BOMTable />
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <CostBreakdown components={pipelineData?.bom || []} />
              </div>
              <div>
                <BOMExportPanel apiBase={apiBase} exports={pipelineData?.exports} />
              </div>
            </div>
          </div>
        );

      case 'pcb':
        return (
          <div className="space-y-6">
            <BoardCanvas />
            <ComponentPlacement />
          </div>
        );

      case 'simulation':
        return (
          <div className="space-y-6">
            <ThermalRiskPanel />
            <PowerAnalysis data={pipelineData?.power_analysis || { 
              power_items: [], 
              summary: { 
                total_power_load_w: 12.5, 
                peak_current_a: 2.1, 
                peak_power_load_w: 24.0, 
                standby_load_ma: 15, 
                battery_voltage_v: 12, 
                battery_capacity_ah: 5, 
                estimated_runtime_hours: 4.8, 
                voltage_domains_count: 3 
              }, 
              warnings: [] 
            }} />
          </div>
        );

      case 'procurement':
        return (
          <div className="space-y-6">
            <ProcurementHeatmap />
            <ReceiptExplorer apiBase={apiBase} />
          </div>
        );

      case 'release':
        return (
          <div className="space-y-6">
            <ExecutionReadiness 
              readiness={pipelineData?.validation?.readiness_score || 85}
              risk={pipelineData?.validation?.risk_score || 25}
              optimization={pipelineData?.optimization?.optimization_score || 90}
            />
            <GanttRoadmap 
              roadmap={pipelineData?.roadmap || []}
              gantt={pipelineData?.gantt || []}
              projectName={currentProjectName}
            />
            <AuditTrail logs={pipelineData?.audit_trail || []} />
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

      case 'agents': {
        const sampleAgent = {
          agent_id: "agent_r2_research",
          name: "R2 Research & Sourcing Agent",
          description: "Datasheet extraction, constraint resolution, and component discovery.",
          provider: "Workline AI Cluster",
          protocol: "WORKLINE_IPC",
          version: "1.0.0-rc1",
          status: "AVAILABLE" as const,
          capabilities: [
            {
              capability_id: "cap_research",
              name: "Autonomous Datasheet Synthesis",
              description: "Extracts electrical tolerances and pin constraints.",
              capability_type: "RESEARCH",
              estimated_cost: 0.05,
              risk_level: "LOW" as const,
              availability: true,
              version: "1.0.0"
            }
          ]
        };

        return (
          <div className="space-y-6">
            <AgentRegistry agents={[sampleAgent]} />
            <AgentCapabilityPanel agent={sampleAgent} />
            <AgentTaskPanel tasks={[]} />
            <AgentExecutionTimeline externalTasks={[]} />
          </div>
        );
      }

      case 'health':
        return <ServiceHealthPanel />;

      case 'integrations':
        return <SystemIntegrationsPanel />;

      case 'settings':
        return (
          <div className="bg-slate-900/80 border border-slate-800 rounded-lg p-6 space-y-4 max-w-2xl">
            <h2 className="text-sm font-bold text-slate-100 uppercase font-mono">Workspace Settings</h2>
            <div className="space-y-3 text-xs text-slate-300">
              <div>
                <label className="block text-slate-500 font-mono mb-1">R1 CORE GATEWAY URL</label>
                <input
                  type="text"
                  disabled
                  value={apiBase}
                  className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-slate-300 font-mono"
                />
              </div>
              <div>
                <label className="block text-slate-500 font-mono mb-1">PAYMENT PROTOCOL NETWORK</label>
                <input
                  type="text"
                  disabled
                  value="Base Sepolia (x402 Testnet USDC)"
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
        projectName={currentProjectName}
        hasProject={Boolean(pipelineData)}
      />

      {/* Main Execution Workspace Shell */}
      <div className="flex-1 flex flex-col min-w-0 h-screen overflow-y-auto">
        <Topbar
          isLightMode={isLightMode}
          onToggleTheme={() => setIsLightMode(!isLightMode)}
          projectName={currentProjectName}
          onOpenNewProject={() => setIsModalOpen(true)}
          onOpenCopilot={() => setIsCopilotOpen(true)}
        />

        <main className="flex-1 p-6 max-w-7xl w-full mx-auto space-y-6">
          {error && (
            <div className="bg-red-950/30 border border-red-500/40 rounded-lg p-4 text-xs text-red-300 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0 text-red-400" />
                <span>{error}</span>
              </div>
              <button
                onClick={() => setError(null)}
                className="text-red-400 hover:text-red-200 text-xs font-mono"
              >
                Dismiss
              </button>
            </div>
          )}

          {/* Project Context Header (Rendered on engineering modules if project active) */}
          {pipelineData && activeSection !== 'conversations' && activeSection !== 'health' && activeSection !== 'integrations' && activeSection !== 'settings' && (
            <ProjectHeader
              projectName={currentProjectName || 'Autonomous Engineering Project'}
              targetDays={targetDays}
              onSave={handleSaveSpec}
              isSaving={isSaving}
              onRefresh={() => handleCreateProject(currentProjectName, targetDays)}
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
              <span className="text-xs font-bold text-slate-100 uppercase font-mono">Workline Copilot</span>
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
                bom: pipelineData?.bom || [],
                wiring: pipelineData?.wiring_diagram || {},
                power: pipelineData?.power_analysis || {},
                datasheets: pipelineData?.datasheets || []
              }}
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
      />
    </div>
  );
}
