import { 
  Plus, 
  FolderKanban, 
  MessageSquare, 
  CheckSquare, 
  BookOpen, 
  Database, 
  Network, 
  Cpu, 
  Layers, 
  CircuitBoard, 
  Zap, 
  ShoppingCart, 
  PackageCheck, 
  Bot, 
  Activity, 
  Blocks, 
  Settings,
  CreditCard,
  Server,
  ChevronRight
} from 'lucide-react';
import { UserButton, SignInButton, useAuth } from '@clerk/nextjs';

export type NavSection = 
  | 'overview'
  | 'requirements'
  | 'research'
  | 'knowledge'
  | 'architecture'
  | 'components'
  | 'bom'
  | 'pcb'
  | 'simulation'
  | 'procurement'
  | 'release'
  | 'projects'
  | 'conversations'
  | 'agents'
  | 'services'
  | 'payments'
  | 'health'
  | 'integrations'
  | 'settings';

interface SidebarProps {
  activeSection: NavSection;
  onSelectSection: (section: NavSection) => void;
  onOpenNewProject: () => void;
  projectName?: string;
  hasProject: boolean;
}

export default function Sidebar({
  activeSection,
  onSelectSection,
  onOpenNewProject,
  projectName,
  hasProject,
}: SidebarProps) {
  const { isSignedIn } = useAuth();

  const engineeringNavItems = [
    { id: 'overview' as NavSection, label: 'Overview', icon: FolderKanban },
    { id: 'requirements' as NavSection, label: 'Requirements', icon: CheckSquare },
    { id: 'research' as NavSection, label: 'Research', icon: BookOpen },
    { id: 'knowledge' as NavSection, label: 'Knowledge Base', icon: Database },
    { id: 'architecture' as NavSection, label: 'Architecture', icon: Network },
    { id: 'components' as NavSection, label: 'Components', icon: Cpu },
    { id: 'bom' as NavSection, label: 'BOM & Sourcing', icon: Layers },
    { id: 'pcb' as NavSection, label: 'PCB & Layout', icon: CircuitBoard },
    { id: 'simulation' as NavSection, label: 'Simulation & PINN', icon: Zap },
    { id: 'procurement' as NavSection, label: 'Procurement & Sourcing', icon: ShoppingCart },
    { id: 'release' as NavSection, label: 'Release Gate', icon: PackageCheck },
  ];

  const systemNavItems = [
    { id: 'agents' as NavSection, label: 'Agent Operations', icon: Bot },
    { id: 'services' as NavSection, label: 'API Services', icon: Server },
    { id: 'payments' as NavSection, label: 'x402 Payments', icon: CreditCard },
    { id: 'health' as NavSection, label: 'Service Health', icon: Activity },
    { id: 'integrations' as NavSection, label: 'Integrations', icon: Blocks },
    { id: 'settings' as NavSection, label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-slate-950 border-r border-slate-800 flex flex-col justify-between select-none z-30 flex-shrink-0 h-screen sticky top-0">
      {/* Brand Header */}
      <div>
        <div className="h-14 px-4 flex items-center gap-3 border-b border-slate-800 bg-slate-950/80">
          <img src="/icon.png" alt="Workline Logo" className="w-6 h-6 object-contain" />
          <div className="flex flex-col">
            <span className="font-mono text-xs font-black tracking-widest text-slate-100 uppercase">
              WORKLINE AI
            </span>
            <span className="text-[10px] text-slate-400 font-mono">
              Engineering Workbench
            </span>
          </div>
        </div>

        {/* Workspace Quick Actions */}
        <div className="p-3">
          <button
            onClick={onOpenNewProject}
            className="w-full flex items-center justify-center gap-2 py-2 px-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-md text-xs font-semibold shadow-sm transition-all focus:outline-none focus:ring-2 focus:ring-indigo-400 cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            <span>New Project</span>
          </button>
        </div>

        {/* Navigation Sections */}
        <div className="px-3 py-1 space-y-4 overflow-y-auto max-h-[calc(100vh-210px)] text-xs">
          {/* Workspace Category */}
          <div>
            <div className="px-2 pb-1.5 text-[10px] font-mono font-bold tracking-wider text-slate-500 uppercase">
              Workspace
            </div>
            <div className="space-y-0.5">
              <button
                onClick={() => onSelectSection('projects')}
                className={`w-full flex items-center justify-between px-2.5 py-1.5 rounded text-xs transition-colors cursor-pointer ${
                  activeSection === 'projects'
                    ? 'bg-slate-800/90 text-indigo-400 font-medium'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                }`}
              >
                <div className="flex items-center gap-2.5">
                  <FolderKanban className="w-4 h-4" />
                  <span>Projects</span>
                </div>
              </button>

              <button
                onClick={() => onSelectSection('conversations')}
                className={`w-full flex items-center justify-between px-2.5 py-1.5 rounded text-xs transition-colors cursor-pointer ${
                  activeSection === 'conversations'
                    ? 'bg-slate-800/90 text-indigo-400 font-medium'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                }`}
              >
                <div className="flex items-center gap-2.5">
                  <MessageSquare className="w-4 h-4" />
                  <span>Conversations</span>
                </div>
              </button>
            </div>
          </div>

          {/* Active Project Engineering Lifecycle */}
          <div>
            <div className="px-2 pb-1.5 flex items-center justify-between">
              <span className="text-[10px] font-mono font-bold tracking-wider text-slate-500 uppercase">
                Engineering
              </span>
              {hasProject && (
                <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-indigo-950/60 text-indigo-300 border border-indigo-800/50 truncate max-w-[90px]">
                  {projectName || 'Active'}
                </span>
              )}
            </div>

            <div className="space-y-0.5">
              {engineeringNavItems.map((item) => {
                const Icon = item.icon;
                const isActive = activeSection === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => onSelectSection(item.id)}
                    className={`w-full flex items-center justify-between px-2.5 py-1.5 rounded text-xs transition-colors cursor-pointer ${
                      isActive
                        ? 'bg-indigo-950/50 text-indigo-300 font-medium border border-indigo-500/30'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                    }`}
                  >
                    <div className="flex items-center gap-2.5">
                      <Icon className={`w-4 h-4 ${isActive ? 'text-indigo-400' : 'text-slate-400'}`} />
                      <span>{item.label}</span>
                    </div>
                    {isActive && <ChevronRight className="w-3.5 h-3.5 text-indigo-400" />}
                  </button>
                );
              })}
            </div>
          </div>

          {/* System & Operations */}
          <div>
            <div className="px-2 pb-1.5 text-[10px] font-mono font-bold tracking-wider text-slate-500 uppercase">
              System
            </div>
            <div className="space-y-0.5">
              {systemNavItems.map((item) => {
                const Icon = item.icon;
                const isActive = activeSection === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => onSelectSection(item.id)}
                    className={`w-full flex items-center justify-between px-2.5 py-1.5 rounded text-xs transition-colors cursor-pointer ${
                      isActive
                        ? 'bg-slate-800/90 text-indigo-400 font-medium'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                    }`}
                  >
                    <div className="flex items-center gap-2.5">
                      <Icon className="w-4 h-4" />
                      <span>{item.label}</span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* User Account Section */}
      <div className="p-3 border-t border-slate-800 bg-slate-950/90 flex items-center justify-between">
        {isSignedIn ? (
          <div className="flex items-center gap-3 w-full">
            <UserButton />
            <div className="flex flex-col text-left overflow-hidden">
              <span className="text-xs font-semibold text-slate-200 truncate">Engineer Profile</span>
              <span className="text-[10px] text-emerald-400 font-mono flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span> Verified Session
              </span>
            </div>
          </div>
        ) : (
          <div className="w-full flex items-center justify-between gap-2">
            <SignInButton mode="modal">
              <button className="w-full py-1.5 px-3 text-xs font-mono font-bold rounded border border-slate-700 bg-slate-900 hover:bg-slate-800 text-slate-200 transition-all cursor-pointer">
                Sign In
              </button>
            </SignInButton>
          </div>
        )}
      </div>
    </aside>
  );
}
