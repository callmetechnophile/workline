# Workline Frontend Architecture & UX Redesign Audit

**Date**: 2026-08-23  
**Audit Scope**: Frontend UX, Shell Layout, Navigation, and Component Architecture  
**Target Brand**: **Workline AI** (Industrial Engineering Execution Platform)  

---

## 1. Executive Summary & Problem Statement

The previous frontend layout was structured around an **AI Agent Orchestration Landing Page** (hero title, suggestion pills, voice input button, and a step-by-step "Autonomous Multi-Agent Pipeline" execution view with Planner Agent, Retrieval Agent, Extraction Agent, etc.).

This mental model belongs to an agent framework (like ArmourFlow), **not** an engineering execution platform like Workline.

**Workline's Core Identity**:
An AI-powered hardware & systems engineering workstation guiding engineers and builders through:
$$\text{Idea} \longrightarrow \text{Requirements} \longrightarrow \text{Research} \longrightarrow \text{Knowledge} \longrightarrow \text{Architecture} \longrightarrow \text{Components} \longrightarrow \text{BOM} \longrightarrow \text{PCB} \longrightarrow \text{Simulation} \longrightarrow \text{Procurement} \longrightarrow \text{Release}$$

Backend microservices ($R_1, R_2, R_3, R_4, R_5$) and internal agent loops are **hidden implementation details**, never the primary UI focus.

---

## 2. Current Frontend State Audit

| Aspect | Current Implementation | Target Engineering Architecture | Action |
| :--- | :--- | :--- | :--- |
| **Primary Route (`/`)** | Monolithic hero landing with search pill and agent pipeline progress bar | Persistent `AppShell` with Sidebar, Topbar, Project Header, and Engineering Workspaces | **REBUILD** |
| **Navigation** | No persistent sidebar; horizontal tab bar shown only after research completion | Persistent Left Sidebar: Workspace (Projects, Conversations), Engineering (10 modules), System (Agents, Health, Integrations) | **CREATE** |
| **Project Model** | Ad-hoc transient `pipelineData` state in memory | First-class project context (`activeProject`, ID, name, status, timeline, persistence via `/api/packages`) | **REBUILD** |
| **Agent Visibility** | Central hero view showing 9 agent steps sequentially | Relocated to `System -> Agents` (`AgentRegistry.tsx`, `AgentCapabilityPanel.tsx`) | **RELOCATE** |
| **Service Status** | Hidden / unmonitored in UI | Explicit `System -> Service Health` monitoring $R_1, R_2, R_3, R_4, R_5$ | **CREATE** |
| **Conversations** | Transient voice input and saved history drawer | Dedicated `Conversations` workspace with contextual history | **REBUILD** |
| **Engineering Modules** | Hidden inside dashboard tabs under results | Direct first-class navigation items under `ENGINEERING` section | **INTEGRATE** |
| **Design Language** | Dark cyberpunk landing page with neon gradients and circuit background | Professional industrial dark-mode workstation (Stripe-grade precision, high data density, thin borders) | **MODERNIZE** |
| **Branding** | Legacy product artifacts | Pure Workline AI identity | **STANDARDIZE** |

---

## 3. Component Inventory & Migration Strategy

### 3.1 Components to Remove from Primary UI
- Monolithic landing hero in `page.tsx`
- Suggestion pill pool as the main UI interface
- Multi-agent step progression loader as the primary screen
- Bottom-left floating social icons rail

### 3.2 Existing Functional Components to Integrate into Engineering Shell
- **Requirements**: `ConstraintEditor.tsx`, `ConstraintPanel.tsx`
- **Research**: `ResearchPapers.tsx`, `ContradictionViewer.tsx`, `FindingPanel.tsx`
- **Knowledge**: `DatasheetPanel.tsx`, `DocumentLibrary.tsx`, `DocumentViewer.tsx`, `GraphExplorer.tsx`
- **Architecture**: `DependencyGraph.tsx`, `WiringDiagram.tsx`
- **Components**: `ComponentTable.tsx`, `ComponentComparison.tsx`, `AlternativeComponents.tsx`, `PinMappingTable.tsx`, `VoltageRiskTable.tsx`
- **BOM**: `BOMTable.tsx`, `BOMWorkspace.tsx`, `BOMExportPanel.tsx`, `CostBreakdown.tsx`
- **PCB**: `BoardCanvas.tsx`, `ComponentPlacement.tsx`
- **Simulation**: `PowerAnalysis.tsx`, `ThermalRiskPanel.tsx`
- **Procurement**: `ProcurementHeatmap.tsx`, `ReceiptExplorer.tsx`
- **Release**: `ExecutionReadiness.tsx`, `GanttRoadmap.tsx`, `AuditTrail.tsx`
- **System / Operations**: `AgentRegistry.tsx`, `AgentCapabilityPanel.tsx`, `AgentTaskPanel.tsx`, `AgentExecutionTimeline.tsx`, `ExternalAgentsPanel.tsx`
- **Contextual AI**: `ConnectionChatbot.tsx`

### 3.3 New Components to Create
- `AppShell.tsx`: Unified workstation container with persistent sidebar, responsive topbar, and contextual workarea.
- `Sidebar.tsx`: Professional industrial sidebar with icon navigation, section badges, and active state styling.
- `Topbar.tsx`: Search bar, active project indicator, system health badge, theme toggle, and Clerk user menu.
- `ProjectOverview.tsx`: Professional engineering project dashboard showing status, timeline, completion metrics, and quick actions.
- `ProjectHeader.tsx`: Breadcrumb, project title, status badge, and action bar.
- `NewProjectModal.tsx`: Engineering project creation dialog with prompt/intent input, timeline target, and budget preferences.
- `ServiceHealthPanel.tsx`: Operational status monitor for $R_1, R_2, R_3, R_4, R_5$.

---

## 4. Preservation of Existing Backend & API Functionality
- **API Gateway**: All frontend requests route to $R_1$ (`/api/research`, `/api/packages/save`, `/api/packages/history`, `/health`).
- **Authentication**: Clerk authentication (`ClerkProvider`, `SignInButton`, `UserButton`) preserved in header and sidebar.
- **Data Persistence**: Project saving and history fetching via `localStorage` and backend profile history.
- **Zero Fake Data**: If a project has no runs, clean empty states with "Run Engineering Analysis" buttons are rendered.
