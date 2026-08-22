'use client';

import React, { useState, useEffect, useRef } from 'react';
import { SignInButton, SignUpButton, UserButton, useAuth } from '@clerk/nextjs';
import { Search, Mic, Sparkles, Download, ShieldCheck, RefreshCw, Layers, GitBranch, BookOpen, Calendar, Key, AlertTriangle, FileText, Check, Moon, Sun, Presentation, X, Zap, Share2, Wifi, BarChart2, FlaskConical, Thermometer, ShoppingCart, Network, Users, History, MessageCircle, FolderOpen, Shield, Receipt, XCircle } from 'lucide-react';

// Components
import AgentPipeline from '@/components/AgentPipeline';
import AuditTrail from '@/components/AuditTrail';
import ScopeViolation from '@/components/ScopeViolation';
import ExecutionReadiness from '@/components/ExecutionReadiness';
import ComponentTable from '@/components/ComponentTable';
import DecisionTrace from '@/components/DecisionTrace';
import ResearchPapers from '@/components/ResearchPapers';
import GanttRoadmap from '@/components/GanttRoadmap';

// Production Tier 1 Components
import DelegationScopeViewer from '@/components/DelegationScopeViewer';
import ReceiptExplorer from '@/components/ReceiptExplorer';
import ScopeViolationSimulator from '@/components/ScopeViolationSimulator';
import CostBreakdown from '@/components/CostBreakdown';
import AlternativeComponents from '@/components/AlternativeComponents';
import VoltageRiskTable from '@/components/VoltageRiskTable';
import PinMappingTable from '@/components/PinMappingTable';
import BOMExportPanel from '@/components/BOMExportPanel';

// Tier 2 Components
import PowerAnalysis from '@/components/PowerAnalysis';
import DependencyGraph from '@/components/DependencyGraph';
import WiringDiagram from '@/components/WiringDiagram';
import DatasheetPanel from '@/components/DatasheetPanel';
import ConnectionChatbot from '@/components/ConnectionChatbot';
import WorkspaceDashboard from '@/components/WorkspaceDashboard';

// Tier 3 Components
import TeamWorkspace from '@/components/TeamWorkspace';
import VersionHistory from '@/components/VersionHistory';
import ContradictionViewer from '@/components/ContradictionViewer';
import ThermalRiskPanel from '@/components/ThermalRiskPanel';
import ProcurementHeatmap from '@/components/ProcurementHeatmap';
import GraphExplorer from '@/components/GraphExplorer';

const DASHBOARD_TABS = [
  { id: "bom",            label: "BOM",                  icon: Layers },
  { id: "power",          label: "Power Analysis",        icon: Zap },
  { id: "dependency",     label: "Dependency Graph",      icon: Share2 },
  { id: "wiring",         label: "Wiring Diagram",        icon: Wifi },
  { id: "datasheets",     label: "Datasheets",            icon: FileText },
  { id: "papers",         label: "Research Papers",       icon: BookOpen },
  { id: "contradictions", label: "Research Conflicts",    icon: AlertTriangle },
  { id: "thermal",        label: "Thermal Analysis",      icon: Thermometer },
  { id: "heatmap",        label: "Procurement Heatmap",   icon: ShoppingCart },
  { id: "knowledge_graph",label: "Knowledge Graph",       icon: Network },
  { id: "team_workspace", label: "Team Workspace",        icon: Users },
  { id: "version_history",label: "Version History",       icon: History },
  { id: "assistant",      label: "Connection Assistant",  icon: MessageCircle },
  { id: "workspace",      label: "Saved Workspace",       icon: FolderOpen },
  { id: "delegation",     label: "Delegation Scope",      icon: Shield },
  { id: "receipts",       label: "Receipts",              icon: Receipt },
  { id: "violations",     label: "Violations",            icon: XCircle }
];

const SUGGESTIONS_POOL = [
  "Voice controlled lights",
  "Solar tracker",
  "Smart greenhouse",
  "Bionic robotic hand",
  "Automated hydroponic farm",
  "Autonomous delivery drone",
  "Self-balancing robot",
  "Smart weather station",
  "Laser security system",
  "Gesture controlled mouse",
  "Solar powered vacuum",
  "Smart irrigation system",
  "IoT smart home lock",
  "Wearable health tracker",
  "CNC engraving machine",
  "Autonomous lawn mower",
  "RFID sorting conveyor"
];

export default function Home() {
  const [intent, setIntent] = useState('');
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [activeAgent, setActiveAgent] = useState<string | null>(null);
  const [currentStepIndex, setCurrentStepIndex] = useState(-1);
  const [pipelineData, setPipelineData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [recentSearches, setRecentSearches] = useState<string[]>([]);
  const { getToken, userId, isSignedIn } = useAuth();
  const [savedHistory, setSavedHistory] = useState<any[]>([]);
  const [isSaving, setIsSaving] = useState(false);
  const [isLightMode, setIsLightMode] = useState(false);
  const [usageCount, setUsageCount] = useState(0);
  const [pptModalOpen, setPptModalOpen] = useState(false);
  const [pptPrompt, setPptPrompt] = useState('');
  const [activeDashboardTab, setActiveDashboardTab] = useState('bom');
  const [targetDays, setTargetDays] = useState(0);
  const [receiptRefreshTrigger, setReceiptRefreshTrigger] = useState(0);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const isTestingEnv = typeof window !== 'undefined' && 
    (window.location.hostname === 'localhost' || 
     window.location.hostname === '127.0.0.1' || 
     process.env.NODE_ENV === 'development');

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const count = parseInt(localStorage.getItem('workline_guest_usage') || '0', 10);
      setUsageCount(count);
    }
    // Shuffle pool and select 4 suggestions on mount
    const shuffled = [...SUGGESTIONS_POOL].sort(() => 0.5 - Math.random());
    setSuggestions(shuffled.slice(0, 4));
  }, []);

  const incrementUsage = () => {
    const newCount = usageCount + 1;
    setUsageCount(newCount);
    if (typeof window !== 'undefined') {
      localStorage.setItem('workline_guest_usage', newCount.toString());
    }
  };
  
  // Audio wave fluctuation simulation
  const [waveHeights, setWaveHeights] = useState<number[]>([15, 30, 20, 40, 10, 30]);
  const [apiBase, setApiBase] = useState('');
  const [recognition, setRecognition] = useState<any>(null);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        const rec = new SpeechRecognition();
        rec.continuous = true;
        rec.interimResults = true;
        rec.lang = 'en-US';
        
        rec.onresult = (event: any) => {
          let interimTranscript = '';
          let finalTranscript = '';
          for (let i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
              finalTranscript += event.results[i][0].transcript;
            } else {
              interimTranscript += event.results[i][0].transcript;
            }
          }
          const text = finalTranscript || interimTranscript;
          if (text) {
            setIntent(text);
          }
        };
        
        rec.onerror = (err: any) => {
          console.error("Speech recognition error:", err);
          setIsRecording(false);
        };
        
        rec.onend = () => {
          setIsRecording(false);
        };
        
        setRecognition(rec);
      }
    }
  }, []);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      if (process.env.NEXT_PUBLIC_API_URL) {
        setApiBase(process.env.NEXT_PUBLIC_API_URL);
      } else if (window.location.port === '3000') {
        setApiBase('http://localhost:8000');
      } else {
        setApiBase('');
      }
    }
  }, []);

  useEffect(() => {
    if (typeof document !== 'undefined') {
      if (isLightMode) {
        document.body.classList.add('light-mode');
      } else {
        document.body.classList.remove('light-mode');
      }
    }
  }, [isLightMode]);

  useEffect(() => {
    if (targetDays > 0 && pipelineData && pipelineData.roadmap && pipelineData.gantt) {
      const originalDays = [5, 7, 6, 4];
      const scale = targetDays / 22;
      
      const scaledDays: number[] = [];
      for (let i = 0; i < originalDays.length - 1; i++) {
        scaledDays.push(Math.max(1, Math.round(originalDays[i] * scale)));
      }
      const lastVal = targetDays - scaledDays.reduce((sum, d) => sum + d, 0);
      scaledDays.push(Math.max(1, lastVal));

      const updatedRoadmap = pipelineData.roadmap.map((phase: any, index: number) => ({
        ...phase,
        duration_days: scaledDays[index] || 1
      }));

      let currentDate = new Date();
      const updatedGantt = pipelineData.gantt.map((task: any, index: number) => {
        const duration = scaledDays[index] || 1;
        const start = currentDate.toISOString().split('T')[0];
        currentDate.setDate(currentDate.getDate() + duration);
        const end = currentDate.toISOString().split('T')[0];
        return {
          ...task,
          start,
          end
        };
      });

      const currentRoadmapDurations = pipelineData.roadmap.map((p: any) => p.duration_days).join(',');
      const newRoadmapDurations = scaledDays.join(',');
      if (currentRoadmapDurations !== newRoadmapDurations) {
        setPipelineData((prev: any) => ({
          ...prev,
          roadmap: updatedRoadmap,
          gantt: updatedGantt
        }));
      }
    }
  }, [targetDays, pipelineData]);

  useEffect(() => {
    async function fetchHistory() {
      if (!userId || !apiBase) return;
      try {
        const token = await getToken();
        const response = await fetch(`${apiBase}/api/packages/history`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        if (response.ok) {
          const data = await response.json();
          setSavedHistory(data);
        }
      } catch (err) {
        console.error("Failed to fetch history:", err);
      }
    }
    fetchHistory();
  }, [userId, apiBase, getToken]);

  const handleSavePackage = async () => {
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
          intent: pipelineData.intent,
          readiness_score: pipelineData.validation?.readiness_score || 80,
          risk_score: pipelineData.validation?.risk_score || 30,
          optimization_score: pipelineData.optimization?.optimization_score || 90,
          data: pipelineData
        })
      });
      if (response.ok) {
        const updatedResponse = await fetch(`${apiBase}/api/packages/history`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (updatedResponse.ok) {
          const data = await updatedResponse.json();
          setSavedHistory(data);
        }
        alert("Specification package saved successfully to your profile!");
      } else {
        alert("Failed to save package.");
      }
    } catch (err) {
      console.error(err);
      alert("Error saving package.");
    } finally {
      setIsSaving(false);
    }
  };

  const handleLoadHistory = (item: any) => {
    setPipelineData(item.data);
    setIntent(item.intent);
  };

  const handleHomeClick = () => {
    setPipelineData(null);
    setIntent('');
    setError(null);
  };

  const handleGeneratePPT = () => {
    if (!pipelineData) return;
    
    const projectName = (pipelineData.intent || intent || "WORKLINE AI").toUpperCase();
    const coreVibe = "Cyberpunk dark-mode blueprint tech console, glowing cyan and electric blue accents, neon red alerts";
    const targetAudience = "Investors, Product Managers, Engineers, Security Auditors";
    
    const rawBackground = `
- Intent: ${pipelineData.intent}
- Core Concept: Autonomous Multi-Agent engineering pipeline for hardware prototyping.
- Built Deliverables & Capabilities:
  1. AI-Agent Sequenced Planner: Sequential execution logs across 8 agents (Planner, Retrieval, Extraction, Research, Validation, Optimization, Planning, Export).
  2. ArmorIQ Safety Enforcer: Runtime tool authorization checker with visual 'Blocked Info' logs intercepting unauthorized scopes (e.g. preventing the Research Agent from calling export_pdf).
  3. Real-time User Interface: Browser Web Speech API for voice-to-text inputs, Clerk authentication profiles, and a 2-generation guest usage blocker.
  4. Design Traceability & BOM Sourcing: Interactive Bill of Materials (BOM) showing component specs and optimized cost-effective alternatives, backed by a Decision Trace transparent log.
  5. Literature Integration & AI Advisor: Retrieved Reference cards displaying at least 4 research papers with metadata linking to source URLs, complete with an interactive 'AI Integration Advisor' chatbot drawer to discuss custom architecture integrations.
  6. Execution Readiness circular score dials (Readiness, Risk, and Optimization scores) and sequential Gantt Roadmap assembly timeline schedules.
`;

    const promptText = `Act as a premium presentation architect specializing in Gamma's specific layout engine. 

I am going to provide you with raw data from a completed project. Your goal is to transform this data into a highly structured, markdown-formatted presentation that Gamma can automatically parse into visually striking, multi-column, and high-motion interactive cards.

### 1. PROJECT DATA & CONTEXT
*   **Project Name:** ${projectName}
*   **Core Vibe:** ${coreVibe}
*   **Target Audience:** ${targetAudience}

---
### RAW PROJECT BACKGROUND (DO NOT COPY WORD-FOR-WORD)
${rawBackground.trim()}
---

### 2. EXECUTION RULES FOR GAMMA GENERATION
*   **Use Multi-Column Layouts:** For features, comparisons, or steps, split the text into 2 or 3 columns to mimic interactive UI dashboards.
*   **Keep Text Punchy:** Use short, high-impact headers and minimal body text.
*   **Add Visual Notes:** At the end of every card, include an italicized "Visual & Motion Note" to guide image placement and slide transitions (e.g., Morph transitions, zoom effects).

### 3. THE OUTLINE FOR GENERATION

---
## Card 1: Title Slide
### ${projectName}
#### IDEA -> RESEARCH -> OPTIMIZE -> EXECUTE: Accelerating hardware prototyping via secure, autonomous multi-agent pipelines.

*Visual Note: Use a full-bleed, high-contrast tech background. Set transition to smooth morph.*

---
## Card 2: The Problem & Opportunity
### Why We Built This

[Column 1]
**The Core Pain Point**
* Prototyping hardware is bottlenecked by complex component sourcing, lack of automated cost optimization, and security compliance risks during autonomous research.

[Column 2]
**The Opportunity**
* WORKLINE AI leverages 8 sequenced agents to automate research, optimize component sourcing, enforce runtime safety policies, and provide live design guidance.

*Visual Note: Use a split screen layout. High-contrast colors to separate the problem from the solution.*

---
## Card 3: Project Architecture & Flow
### How the Interactive Motion System Works

* **Step 1: Core Engine** -> Natural language intents processed via sequential multi-agent pipeline (Planner, Retrieval, Extraction, Research).
* **Step 2: Interactive Middleware** -> Validation & Optimization agents calculate scores, compile optimal BOM components, and enforce zero-trust policies.
* **Step 3: Motion Delivery** -> Live Gantt Roadmaps, clickable research references, interactive chatbot advisor drawer, and specification package exports.

*Visual Note: Format this as a horizontal timeline or sequential cards. Design for a linear, flowing motion path.*

---
## Card 4: Key Features & Capabilities
### The Core Built Deliverables

[Column 1]
⚡ **ArmorIQ Enforcer**
* Zero-trust security checker. Intercepts and blocks out-of-scope tools (e.g. blocking Research Agent from PDF exporting) and posts transparent 'Blocked Info' logs.

[Column 2]
🎨 **Intelligent Console UI**
* Dynamic landing page with real-time browser Web Speech API voice-to-text typing, Clerk profiles, and a 2-generation guest usage screen blocker.

[Column 3]
⚙️ **AI Advisor Chatbot**
* Interactive sliding chat drawer connected to a custom backend /chat advisor API to discuss architectural integrations on-the-fly.

*Visual Note: Use a 3-column card grid to mimic an interactive software dashboard feature list.*

---
## Card 5: Real-World Impact & Metrics
### What the Complete Build Achieves

> **Key Milestone:** Accelerates mechanical and hardware prototyping speeds by up to 80% while guaranteeing 100% policy compliance.

* **Performance:** High-reliability API builds serving optimized BOM component options and detailed Gantt roadmap assembly schedules.
* **User Experience:** Seamless glass-morphism panels, circular execution readiness dials, and interactive links to real academic publications.

*Visual Note: Use a large callout block or stat callout layout for the key milestone to make it pop instantly.*

---
## Card 6: Next Steps & Future Scale
### Where the Project Goes Next

* **Phase 1:** Expand the Optimization Agent to integrate live real-time API pricing from hardware distributors.
* **Phase 2:** Scale the AI Advisor to support multi-user team workspaces with synchronized chat logs.

*Visual Note: Clean, minimalist closing slide with a clear focal point on the next milestones.*`;

    if (typeof navigator !== 'undefined' && navigator.clipboard) {
      navigator.clipboard.writeText(promptText).then(() => {
        alert("Gamma prompt copied to clipboard! Opening Gamma... Press Ctrl+V (or Cmd+V) to paste the prompt in the text box.");
        window.open("https://gamma.app/create/paste", "_blank");
      }).catch(err => {
        console.error("Clipboard copy failed:", err);
        window.open("https://gamma.app/create/paste", "_blank");
      });
    } else {
      window.open("https://gamma.app/create/paste", "_blank");
    }
  };

  useEffect(() => {
    let interval: any;
    if (isRecording) {
      interval = setInterval(() => {
        setWaveHeights(Array.from({ length: 10 }, () => Math.floor(Math.random() * 35) + 5));
      }, 150);
    } else {
      setWaveHeights([15, 25, 10, 20, 8]);
    }
    return () => clearInterval(interval);
  }, [isRecording]);

  const handleVoiceInput = async () => {
    if (isRecording) {
      // Stop recording
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop();
      }
      setIsRecording(false);
    } else {
      // Start recording
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const recorder = new MediaRecorder(stream);
        chunksRef.current = [];
        
        recorder.ondataavailable = (e) => {
          if (e.data && e.data.size > 0) {
            chunksRef.current.push(e.data);
          }
        };
        
        recorder.onstop = async () => {
          const audioBlob = new Blob(chunksRef.current, { type: 'audio/wav' });
          const formData = new FormData();
          formData.append('file', audioBlob, 'audio.wav');
          
          try {
            setIntent("Transcribing voice input...");
            const res = await fetch(`${apiBase || 'http://localhost:8000'}/api/speech/stt`, {
              method: 'POST',
              body: formData
            });
            if (res.ok) {
              const data = await res.json();
              setIntent(data.text || "");
            } else {
              setIntent("Error in transcription.");
            }
          } catch (err) {
            console.error("Transcription upload failed:", err);
            setIntent("Transcription failed.");
          }
          
          // Stop stream tracks
          stream.getTracks().forEach(track => track.stop());
        };
        
        mediaRecorderRef.current = recorder;
        recorder.start();
        setIsRecording(true);
        setIntent("Listening (Click Mic to Stop)...");
      } catch (err) {
        console.error("Failed to start recording:", err);
        // Sandbox fallback if mic is blocked/unsupported
        setIsRecording(true);
        setIntent("Listening...");
        setTimeout(() => {
          setIntent("I want to build a solar powered vacuum cleaner");
          setIsRecording(false);
        }, 3000);
      }
    }
  };

  const handleSearchSubmit = async (searchIntent = intent) => {
    if (isRecording) {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop();
      }
      setIsRecording(false);
    }
    
    // Check guest usage limit
    if (!isTestingEnv && !userId && usageCount >= 2) {
      return;
    }
    
    if (!searchIntent.trim() || searchIntent === "Listening...") return;

    if (!targetDays || targetDays <= 0) {
      setError("Please specify a target timeline (greater than 0 days) before proceeding.");
      return;
    }
    
    setError(null);
    setPipelineData(null);
    setIsProcessing(true);
    setCurrentStepIndex(0);
    setActiveAgent("Planner Agent");

    try {
      // Fetch details from FastAPI backend
      const response = await fetch(`${apiBase}/api/research`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ intent: searchIntent, target_days: targetDays })
      });

      if (!response.ok) {
        throw new Error("Failed to generate engineering package. Ensure the FastAPI backend is running.");
      }

      const backendResult = await response.json();

      // Update recent searches
      if (!recentSearches.includes(searchIntent.toUpperCase())) {
        setRecentSearches([searchIntent.toUpperCase(), ...recentSearches.slice(0, 2)]);
      }

      // Step-by-step pipeline visualization
      const pipelineSteps = [
        "Planner Agent",
        "Retrieval Agent",
        "Extraction Agent",
        "BOM Optimization Engine",
        "Research Agent",
        "Validation Agent",
        "Optimization Agent",
        "Planning Agent",
        "Export Agent"
      ];

      for (let i = 0; i < pipelineSteps.length; i++) {
        setActiveAgent(pipelineSteps[i]);
        setCurrentStepIndex(i);
        await new Promise((resolve) => setTimeout(resolve, 850));
      }

      setPipelineData(backendResult);
      setActiveAgent(null);
      setCurrentStepIndex(-1);
      setIsProcessing(false);
      setReceiptRefreshTrigger(prev => prev + 1);
      
      // Increment guest usage count
      if (!userId) {
        incrementUsage();
      }

    } catch (err: any) {
      setError(err.message || "An unexpected error occurred.");
      setIsProcessing(false);
      setActiveAgent(null);
      setCurrentStepIndex(-1);
    }
  };

  const showResults = pipelineData && !isProcessing;

  return (
    <div 
      className={`min-h-screen flex flex-col relative overflow-x-hidden transition-colors duration-300 scanline ${
        isLightMode ? "text-slate-900 bg-slate-50/90" : "text-slate-100 bg-slate-950/65"
      }`}
      style={{
        backgroundImage: isLightMode 
          ? "linear-gradient(rgba(248, 250, 252, 0.88), rgba(248, 250, 252, 0.88)), url('/bg.png')" 
          : "linear-gradient(rgba(3, 7, 18, 0.72), rgba(3, 7, 18, 0.72)), url('/bg.png')",
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundAttachment: 'fixed'
      }}
    >
      {/* Top Navbar */}
      <header className="px-6 py-4 flex justify-between items-center z-10">
        {/* Top Left: Cyborg Icon (Click returns to Home) */}
        <button 
          onClick={handleHomeClick}
          className="flex items-center gap-1 cursor-pointer hover:opacity-85 transition-all focus:outline-none"
          title="Return to Home Console"
        >
          <svg className={`w-8 h-8 transition-colors ${isLightMode ? "text-slate-800" : "text-slate-200"}`} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 17.25v1.007a3 3 0 01-.879 2.122L7.5 21h9l-.621-.621A3 3 0 0115 18.257V17.25m6-12V15a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 15V5.25m18 0A2.25 2.25 0 0018.75 3H5.25A2.25 2.25 0 003 5.25m18 0V12a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 12V5.25" />
            <circle cx="9" cy="9" r="1.5" />
            <circle cx="15" cy="9" r="1.5" />
            <path strokeLinecap="round" d="M12 12v2" />
          </svg>
        </button>

        {/* Top Right Controls: Auth & Toggle */}
        <div className="flex items-center gap-3">
          {!isSignedIn && (
            <div className="flex items-center gap-2">
              <SignInButton mode="modal">
                <button className="text-xs font-mono font-bold px-3.5 py-1.5 rounded border border-zinc-800 bg-zinc-950/40 hover:bg-zinc-900 text-slate-300 hover:text-white transition-all cursor-pointer">
                  Sign In
                </button>
              </SignInButton>
              <SignUpButton mode="modal">
                <button className="text-xs font-mono font-bold px-3.5 py-1.5 rounded bg-indigo-600 hover:bg-indigo-500 text-white transition-all cursor-pointer">
                  Sign Up
                </button>
              </SignUpButton>
            </div>
          )}
          {isSignedIn && (
            <div className="flex items-center gap-2">
              <UserButton />
            </div>
          )}
          <button 
            onClick={() => setIsLightMode(!isLightMode)}
            className="p-2 rounded-full border border-zinc-800 bg-zinc-950/40 text-slate-300 hover:text-white hover:border-zinc-700 transition-all cursor-pointer"
            title={isLightMode ? "Switch to Dark Mode" : "Switch to Light Mode"}
          >
            {isLightMode ? <Sun className="w-4 h-4 text-amber-500" /> : <Moon className="w-4 h-4" />}
          </button>
        </div>
      </header>

      {/* Landing Layout Container */}
      {!showResults ? (
        <div className="flex-1 flex flex-col justify-center items-center px-4 max-w-4xl mx-auto w-full z-10 pb-20 mt-4 text-center">
          {/* Brand Logo Icon */}
          <img 
            src="/icon.png" 
            alt="Workline AI Logo" 
            className="w-20 h-20 md:w-24 md:h-24 mb-3 object-contain" 
          />

          {/* Header Title Block */}
          <h1 className={`font-mono tracking-[0.25em] text-4xl md:text-6xl font-black uppercase transition-colors duration-300 ${
            isLightMode ? "text-slate-900" : "text-slate-100"
          }`}>
            WORKLINE AI
          </h1>

          {/* Subtitle */}
          <h2 className="text-xs md:text-sm text-slate-200 tracking-[0.3em] font-extrabold mt-6 mb-2 uppercase">
            IDEA -&gt; RESEARCH -&gt; OPTIMIZE -&gt; EXECUTE
          </h2>

          {/* Description */}
          <p className="text-xs text-slate-400 italic mb-8">
            Hey Builder, What new ideas are running over your mind
          </p>

          {/* Search Pill Input */}
          <div className="bg-zinc-950/70 border border-zinc-850 rounded-full py-1.5 pl-6 pr-2.5 max-w-2xl w-full flex items-center justify-between shadow-2xl backdrop-blur-md mb-6 hover:border-zinc-700 transition-all duration-300">
            <input
              type="text"
              placeholder="I want to build a remote control car..."
              value={intent}
              onChange={(e) => setIntent(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearchSubmit()}
              disabled={isProcessing}
              className="w-full bg-transparent border-0 outline-none text-slate-100 placeholder-slate-500 text-xs py-1.5 disabled:opacity-50"
            />
            
            <div className="flex items-center gap-3.5 flex-shrink-0">
              {isRecording && (
                <div className="flex items-end gap-0.5 h-6 px-1 bg-red-950/30 border border-red-500/20 rounded">
                  {waveHeights.map((h, i) => (
                    <div 
                      key={i} 
                      className="w-0.5 bg-red-500 rounded-t" 
                      style={{ height: `${h}%` }} 
                    />
                  ))}
                </div>
              )}
              
              <button
                onClick={handleVoiceInput}
                disabled={isProcessing}
                className={`p-2 rounded-full border transition-all ${
                  isRecording 
                    ? "bg-red-500 border-red-500 text-slate-950" 
                    : "bg-transparent border-transparent text-slate-400 hover:text-white"
                }`}
                title={isRecording ? "Stop Recording" : "Voice Input"}
              >
                <Mic className="w-4 h-4" />
              </button>

              <button
                onClick={() => handleSearchSubmit()}
                disabled={isProcessing || !intent.trim()}
                className="bg-zinc-900 hover:bg-zinc-850 text-slate-300 hover:text-white p-2.5 rounded-full border border-zinc-800 hover:border-zinc-700 transition-all disabled:opacity-40"
              >
                {isProcessing ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <Search className="w-4 h-4" />
                )}
              </button>
            </div>
          </div>

          <div className="flex items-center gap-3 text-xs font-mono mb-8 bg-zinc-950/40 border border-zinc-850/60 p-2.5 px-5 rounded-full max-w-sm select-none">
            <span className="text-slate-400">Target Timeline:</span>
            <input 
              type="number" 
              value={targetDays} 
              onChange={(e) => setTargetDays(Math.max(0, parseInt(e.target.value) || 0))}
              className={`w-16 bg-zinc-900 border rounded px-2.5 py-1 text-center font-bold focus:outline-none transition-all ${
                targetDays === 0
                  ? "border-red-500/50 text-red-400 animate-pulse"
                  : "border-zinc-800 text-cyan-400 focus:border-cyan-500"
              }`} 
            />
            <span className="text-slate-500">Days</span>
          </div>

          {/* Suggestions List */}
          <div className="space-y-3 mb-6">
            <span className="text-[10px] text-slate-500 font-mono tracking-widest uppercase block">SUGGESTIONS</span>
            <div className="flex flex-wrap justify-center gap-2 max-w-xl">
              {suggestions.map((item, i) => (
                <button
                  key={i}
                  onClick={() => {
                    setIntent(item);
                    handleSearchSubmit(item);
                  }}
                  disabled={isProcessing}
                  className="bg-zinc-950/70 border border-zinc-850 hover:border-zinc-700 text-slate-300 hover:text-white text-[11px] px-4 py-1.5 rounded-full transition-all disabled:opacity-50"
                >
                  {item}
                </button>
              ))}
            </div>
          </div>

          {/* Saved Specifications List (Signed In Only) */}
          {isSignedIn && savedHistory.length > 0 && (
            <div className="space-y-3 mb-6">
              <span className="text-[10px] text-cyan-400 font-mono tracking-widest uppercase block">
                SAVED SPECIFICATIONS
              </span>
              <div className="flex flex-wrap justify-center gap-2 max-w-xl">
                {savedHistory.map((item, i) => (
                  <button
                    key={i}
                    onClick={() => handleLoadHistory(item)}
                    disabled={isProcessing}
                    className="bg-zinc-950/90 border border-zinc-850 hover:border-cyan-900/50 text-slate-300 hover:text-white text-[10px] font-bold px-4 py-1.5 rounded-full transition-all tracking-wide flex items-center gap-1.5 cursor-pointer"
                  >
                    <Layers className="w-3 h-3 text-cyan-400" />
                    {item.intent.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Recent Searches */}
          {recentSearches.length > 0 && (
            <div className="space-y-3 mb-6">
              <span className="text-[10px] text-slate-500 font-mono tracking-widest uppercase block">
                RECENT SEARCHES
              </span>
              <div className="flex justify-center">
                {recentSearches.map((item, i) => (
                  <button
                    key={i}
                    onClick={() => {
                      setIntent(item);
                      handleSearchSubmit(item);
                    }}
                    disabled={isProcessing}
                    className="bg-zinc-950/90 border border-zinc-850 hover:border-zinc-700 text-slate-300 hover:text-white text-[10px] font-bold px-4 py-1 rounded-full transition-all tracking-wide"
                  >
                    {item}
                  </button>
                ))}
              </div>
            </div>
          )}

          {error && (
            <div className="mt-4 bg-red-950/20 border border-red-500/30 rounded p-3 text-xs text-red-400 flex items-center gap-2 max-w-md">
              <AlertTriangle className="w-4 h-4 flex-shrink-0" />
              {error}
            </div>
          )}

          {/* Pipeline Active Loader */}
          {isProcessing && (
            <div className="mt-8 w-full max-w-4xl">
              <AgentPipeline 
                logs={pipelineData ? pipelineData.audit_trail : []} 
                activeAgent={activeAgent} 
                isProcessing={isProcessing} 
              />
            </div>
          )}

          {/* Bottom Branding Center */}
          <div className="absolute bottom-6 left-0 right-0 text-center space-y-1 select-none pointer-events-none">
            <div className="text-[11px] font-black uppercase tracking-[0.2em] bg-gradient-to-r from-pink-500 to-indigo-400 bg-clip-text text-transparent">
              MULTI-MODEL WEB AGENT
            </div>
            <div className="text-[9px] text-slate-500 font-mono tracking-wider uppercase">
              ORGANISED COLLECTION OF IDEAS
            </div>
          </div>

          {/* Bottom Left Social Links Group: GitHub, LinkedIn, Instagram */}
          <div className="absolute bottom-6 left-6 flex items-center gap-2.5 z-20">
            <a 
              href="https://github.com/callmetechnophile/workline" 
              target="_blank" 
              rel="noreferrer"
              aria-label="GitHub"
              className="p-2 rounded-full border border-zinc-800 bg-zinc-950/40 text-slate-400 hover:text-white hover:border-zinc-700 transition-all cursor-pointer"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"></path>
                <path d="M9 18c-4.51 2-5-2-7-2"></path>
              </svg>
            </a>
            <a 
              href="https://www.linkedin.com/in/callmetechnophile" 
              target="_blank" 
              rel="noreferrer"
              aria-label="LinkedIn"
              className="p-2 rounded-full border border-zinc-800 bg-zinc-950/40 text-slate-400 hover:text-white hover:border-zinc-700 transition-all cursor-pointer"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path>
                <rect x="2" y="9" width="4" height="12"></rect>
                <circle cx="4" cy="4" r="2"></circle>
              </svg>
            </a>
            <a 
              href="https://www.instagram.com/mr.devgenius" 
              target="_blank" 
              rel="noreferrer"
              aria-label="Instagram"
              className="p-2 rounded-full border border-zinc-800 bg-zinc-950/40 text-slate-400 hover:text-white hover:border-zinc-700 transition-all cursor-pointer"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect>
                <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path>
                <line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line>
              </svg>
            </a>
          </div>

          {/* Bottom Right: Powered by Workline */}
          <div className="absolute bottom-6 right-6 text-xs text-slate-500 font-mono z-20 select-none">
            Powered by <span className="text-slate-300 font-bold">Workline</span>
          </div>
        </div>
      ) : (
        /* Results Dashboard view */
        <div className="max-w-7xl mx-auto px-4 mt-4 space-y-8 pb-16 z-10 w-full">
          {/* Header Title block in small format */}
          <div className="flex flex-col md:flex-row justify-between items-center gap-4 bg-zinc-950/80 border border-zinc-850 p-4 rounded-lg backdrop-blur-md">
            <div>
              <div className="text-xs font-mono tracking-widest text-cyan-400 font-extrabold uppercase">
                Workline AI
              </div>
              <h2 className="text-sm font-bold text-slate-100 mt-1">
                Engineering Spec: <span className="text-slate-300 italic">"{pipelineData.intent}"</span>
              </h2>
            </div>

            {/* Micro input bar for search from results dashboard */}
            <div className="flex items-center gap-2 max-w-md w-full">
              <input
                type="text"
                value={intent}
                onChange={(e) => setIntent(e.target.value)}
                placeholder="Submit new design target..."
                onKeyDown={(e) => e.key === 'Enter' && handleSearchSubmit()}
                className="bg-slate-900 border border-slate-800 rounded px-3 py-1.5 text-xs w-full text-slate-100 placeholder-slate-500 outline-none"
              />
              <div className="flex items-center gap-1 text-[10px] font-mono text-slate-400 bg-slate-900 border border-slate-800 px-2.5 py-1 rounded flex-shrink-0 select-none">
                <span>Days:</span>
                <input 
                  type="number" 
                  value={targetDays} 
                  onChange={(e) => setTargetDays(Math.max(0, parseInt(e.target.value) || 0))}
                  className={`w-10 bg-transparent border-0 text-center font-bold focus:outline-none transition-all ${
                    targetDays === 0 ? "text-red-400 animate-pulse" : "text-cyan-400"
                  }`} 
                />
              </div>
              <button
                onClick={() => handleSearchSubmit()}
                className="bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs px-3 py-1.5 rounded transition-all flex items-center gap-1.5 flex-shrink-0"
              >
                <RefreshCw className="w-3 h-3" />
                Query
              </button>
            </div>
          </div>

          {/* Active Logs Pipeline overview */}
          <AgentPipeline 
            logs={pipelineData.audit_trail} 
            activeAgent={null} 
            isProcessing={false} 
          />

          {/* Execution Readiness circular dials */}
          <ExecutionReadiness 
            readiness={pipelineData.validation?.readiness_score || 80}
            risk={pipelineData.validation?.risk_score || 30}
            optimization={pipelineData.optimization?.optimization_score || 90}
          />

          {/* Scope Violation Enforcer block display */}
          <ScopeViolation logs={pipelineData.audit_trail} />

          {/* Tier 1 & Tier 2 Feature Tabbed Dashboard */}
          <div className="glass-panel p-6 border border-slate-800 bg-slate-950/40 space-y-6">
            <div className="flex flex-wrap border-b border-slate-800/60">
              {DASHBOARD_TABS.map((tab) => {
                const Icon = tab.icon;
                const isActive = activeDashboardTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveDashboardTab(tab.id)}
                    className={`flex items-center gap-1.5 py-2.5 px-3.5 text-[10px] font-mono font-bold tracking-widest uppercase border-b-2 transition-all cursor-pointer whitespace-nowrap ${
                      isActive
                        ? "border-cyan-500 text-cyan-400"
                        : "border-transparent text-slate-500 hover:text-slate-200 hover:border-slate-600"
                    }`}
                  >
                    <Icon className={`w-3 h-3 flex-shrink-0 ${isActive ? 'text-cyan-400' : 'text-slate-600'}`} />
                    {tab.label}
                  </button>
                );
              })}
            </div>

            <div className="transition-all duration-300">
              {activeDashboardTab === 'bom' && (
                <div className="space-y-6">
                  <ComponentTable components={pipelineData.components} />
                  <CostBreakdown components={pipelineData.components} costSummary={pipelineData.cost_summary} />
                  <AlternativeComponents components={pipelineData.components} />
                  <VoltageRiskTable risks={pipelineData.voltage_risks} />
                  <PinMappingTable pins={pipelineData.pin_mapping} />
                  <BOMExportPanel apiBase={apiBase} exports={pipelineData.bom_exports} />
                  <DecisionTrace decisions={pipelineData.decision_trace} />
                  <GanttRoadmap 
                    roadmap={pipelineData.roadmap} 
                    gantt={pipelineData.gantt} 
                    projectId={pipelineData.version_history?.project_id || 1}
                    projectName={pipelineData.intent || "WorkflowGuide Project"}
                  />
                </div>
              )}
              {activeDashboardTab === 'power' && (
                <PowerAnalysis data={pipelineData.power_analysis} />
              )}
              {activeDashboardTab === 'dependency' && (
                <DependencyGraph data={pipelineData.dependency_graph} />
              )}
              {activeDashboardTab === 'wiring' && (
                <WiringDiagram data={pipelineData.wiring_diagram} />
              )}
              {activeDashboardTab === 'datasheets' && (
                <DatasheetPanel datasheets={pipelineData.datasheets} />
              )}
              {activeDashboardTab === 'papers' && (
                <ResearchPapers 
                  papers={pipelineData.papers} 
                  summary={pipelineData.paper_summary} 
                  intent={intent || pipelineData.intent}
                  apiBase={apiBase}
                />
              )}
              {activeDashboardTab === 'contradictions' && (
                <ContradictionViewer contradictions={pipelineData.contradictions} />
              )}
              {activeDashboardTab === 'thermal' && (
                <ThermalRiskPanel thermalReports={pipelineData.thermal_analysis} />
              )}
              {activeDashboardTab === 'heatmap' && (
                <ProcurementHeatmap components={pipelineData.components} />
              )}
              {activeDashboardTab === 'knowledge_graph' && (
                <GraphExplorer 
                  projectName={pipelineData.version_history?.project_id || pipelineData.intent} 
                  apiBase={apiBase}
                />
              )}
              {activeDashboardTab === 'team_workspace' && (
                <TeamWorkspace 
                  teamData={pipelineData.team_workspace} 
                  projectId={pipelineData.version_history?.project_id} 
                  apiBase={apiBase} 
                />
              )}
              {activeDashboardTab === 'version_history' && (
                <VersionHistory 
                  versionData={pipelineData.version_history} 
                  apiBase={apiBase}
                  onRefresh={async () => {
                    try {
                      const res = await fetch(`${apiBase}/api/versioning/versions/${pipelineData.version_history.project_id}`);
                      if (res.ok) {
                        const list = await res.json();
                        setPipelineData({
                          ...pipelineData,
                          version_history: {
                            ...pipelineData.version_history,
                            versions: list
                          }
                        });
                      }
                    } catch (err) {
                      console.error(err);
                    }
                  }}
                />
              )}
              {activeDashboardTab === 'assistant' && (
                <ConnectionChatbot 
                  projectContext={{
                    bom: pipelineData.components,
                    wiring: pipelineData.wiring_diagram,
                    power: pipelineData.power_analysis,
                    datasheets: pipelineData.datasheets
                  }}
                />
              )}
              {activeDashboardTab === 'workspace' && (
                <WorkspaceDashboard 
                  activeProjectName={pipelineData.intent || ""}
                  currentData={pipelineData}
                  apiBase={apiBase}
                  onLoadProject={(data) => {
                    setPipelineData(data);
                    setIntent(data.name || data.intent);
                  }}
                  onSaveTrigger={async (name) => {}}
                />
              )}
              {activeDashboardTab === 'delegation' && (
                <DelegationScopeViewer logs={pipelineData.audit_trail} />
              )}
              {activeDashboardTab === 'receipts' && (
                <ReceiptExplorer apiBase={apiBase} refreshTrigger={receiptRefreshTrigger} />
              )}
              {activeDashboardTab === 'violations' && (
                <ScopeViolationSimulator 
                  apiBase={apiBase} 
                  onViolationTriggered={() => setReceiptRefreshTrigger(prev => prev + 1)} 
                />
              )}
            </div>
          </div>

          {/* Export spec buttons panel */}
          <div className="glass-panel p-6 border border-blue-500/20 bg-slate-900/10 flex flex-col md:flex-row justify-between items-center gap-4">
            <div>
              <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-1.5 mb-1 font-mono">
                <FileText className="w-4 h-4 text-cyan-400" />
                Download Info
              </h3>
              <p className="text-xs text-slate-400">
                Export complete engineering specifications, BOM quotes, and Gantt roadmap timeline.
              </p>
            </div>
            
            <div className="flex flex-wrap gap-3">
              {isSignedIn && (
                <button
                  onClick={handleSavePackage}
                  disabled={isSaving}
                  className="bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold px-4 py-2.5 rounded transition-all flex items-center gap-1.5 shadow-lg shadow-cyan-500/10 cursor-pointer disabled:opacity-50"
                >
                  <Check className="w-3.5 h-3.5" />
                  {isSaving ? "Saving..." : "Save Spec"}
                </button>
              )}
              <button
                onClick={handleGeneratePPT}
                className="bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold px-4 py-2.5 rounded transition-all flex items-center gap-1.5 shadow-lg shadow-purple-500/10 cursor-pointer"
              >
                <Presentation className="w-3.5 h-3.5" />
                Presentation
              </button>
              <a
                href={`${apiBase}${pipelineData.exports?.pdf?.url}`}
                download
                className="bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold px-4 py-2.5 rounded transition-all flex items-center gap-1.5 shadow-lg shadow-blue-500/10"
              >
                <Download className="w-3.5 h-3.5" />
                Export PDF
              </a>
              <a
                href={`${apiBase}${pipelineData.exports?.csv?.url}`}
                download
                className="bg-slate-900 hover:bg-slate-800 border border-slate-850 text-slate-300 text-xs font-bold px-4 py-2.5 rounded transition-all flex items-center gap-1.5"
              >
                <Download className="w-3.5 h-3.5" />
                Export CSV
              </a>
              <a
                href={`${apiBase}${pipelineData.exports?.markdown?.url}`}
                download
                className="bg-slate-900 hover:bg-slate-800 border border-slate-850 text-slate-300 text-xs font-bold px-4 py-2.5 rounded transition-all flex items-center gap-1.5"
              >
                <Download className="w-3.5 h-3.5" />
                Export Markdown
              </a>
              <a
                href={`${apiBase}${pipelineData.exports?.docx?.url}`}
                download
                className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold px-4 py-2.5 rounded transition-all flex items-center gap-1.5 shadow-lg shadow-indigo-500/10"
              >
                <Download className="w-3.5 h-3.5" />
                Export DOCX
              </a>
            </div>
          </div>

          {/* Audit Verification Log panel */}
          <AuditTrail logs={pipelineData.audit_trail} />
        </div>
      )}


      {/* Blocker Overlay for Guests exceeding limit */}
      {!isTestingEnv && !userId && usageCount >= 2 && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/75 backdrop-blur-xl px-4 animate-fade-in">
          <div className="glass-panel p-8 max-w-md w-full border border-blue-500/30 bg-zinc-950/90 text-center shadow-2xl space-y-6">
            <img 
              src="/icon.png" 
              alt="Armourline AI Logo" 
              className="w-16 h-16 mx-auto object-contain animate-pulse" 
            />
            <div className="space-y-2">
              <h2 className="text-xl font-mono font-black tracking-widest text-slate-100 uppercase">
                LIMIT REACHED
              </h2>
              <p className="text-xs text-slate-400 leading-relaxed">
                You have used your 2 free search generations. Please Sign In or Sign Up below to unlock unlimited cryptographic research packages.
              </p>
            </div>
            
            <div className="flex flex-col gap-3 pt-2">
              <SignInButton mode="modal">
                <button className="w-full text-xs font-mono font-bold py-3 rounded border border-zinc-800 bg-zinc-950 hover:bg-zinc-900 text-slate-200 hover:text-white transition-all cursor-pointer">
                  Sign In
                </button>
              </SignInButton>
              <SignUpButton mode="modal">
                <button className="w-full text-xs font-mono font-bold py-3 rounded bg-indigo-600 hover:bg-indigo-500 text-white transition-all cursor-pointer shadow-lg shadow-indigo-600/20">
                  Create Free Account
                </button>
              </SignUpButton>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
