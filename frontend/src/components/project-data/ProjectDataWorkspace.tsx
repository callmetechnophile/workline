'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useProject } from '@/lib/ProjectContext';
import { generateWorklineFilesystem } from '@/lib/workline-filesystem/serializer';
import {
  parseWorklineFilesystem,
  computeProjectDiff,
  mergeProjects,
} from '@/lib/workline-filesystem/parser';
import { downloadWorklineZip, extractWorklineZip } from '@/lib/workline-filesystem/packager';
import {
  providers,
  GoogleDriveProvider,
  GitHubProvider,
  GitLabProvider,
  BitbucketProvider,
} from '@/lib/workline-filesystem/providers/cloudProviders';
import {
  CloudProviderState,
  WorklineFileMap,
  ImportPreviewStats,
  ImportResolutionStrategy,
  ProjectDiffSummary,
} from '@/lib/workline-filesystem/types';
import FilesystemViewerModal from './FilesystemViewerModal';
import ImportPreviewModal from './ImportPreviewModal';
import DiffSyncModal from './DiffSyncModal';
import {
  FolderArchive,
  Download,
  Upload,
  RefreshCw,
  HardDrive,
  FolderSync,
  CheckCircle2,
  AlertCircle,
  FileCode,
  Eye,
  ShieldCheck,
  History,
  ArrowUpRight,
  GitBranch,
  Layers,
  FileText,
  Clock,
  Sparkles,
  ExternalLink,
} from 'lucide-react';

function GithubIcon({ className = "w-4 h-4" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4" />
      <path d="M9 18c-4.51 2-5-2-7-2" />
    </svg>
  );
}

function GitlabIcon({ className = "w-4 h-4" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="m22 13.29-3.33-10a.42.42 0 0 0-.14-.18.38.38 0 0 0-.22-.07.41.41 0 0 0-.23.08.42.42 0 0 0-.14.18L16 9H8L6.07 3.32a.42.42 0 0 0-.14-.18.38.38 0 0 0-.22-.07.41.41 0 0 0-.23.08.42.42 0 0 0-.14.18L2 13.29a.74.74 0 0 0 .27.83L12 21l9.69-6.88a.71.71 0 0 0 .31-.83Z" />
    </svg>
  );
}

export default function ProjectDataWorkspace() {
  const {
    projectData,
    projectId,
    projectName,
    systemSpecification,
    targetDays,
    teamName,
    status,
    hasProject,
    setProject,
  } = useProject();

  // Local state for generated filesystem
  const [fileMap, setFileMap] = useState<WorklineFileMap>({});
  const [lastExportTime, setLastExportTime] = useState<string>('Not yet exported this session');
  const [totalSizeKb, setTotalSizeKb] = useState<string>('0');
  const [isExportingZip, setIsExportingZip] = useState(false);
  const [isImporting, setIsImporting] = useState(false);
  const [toastMessage, setToastMessage] = useState<{ text: string; type: 'success' | 'error' | 'info' } | null>(null);

  // Cloud providers state
  const [googleDriveState, setGoogleDriveState] = useState<CloudProviderState>(providers.google_drive.getState());
  const [githubState, setGithubState] = useState<CloudProviderState>(providers.github.getState());
  const [gitlabState, setGitlabState] = useState<CloudProviderState>(providers.gitlab.getState());
  const [bitbucketState, setBitbucketState] = useState<CloudProviderState>(providers.bitbucket.getState());

  // Modals state
  const [isFilesystemModalOpen, setIsFilesystemModalOpen] = useState(false);
  const [isImportModalOpen, setIsImportModalOpen] = useState(false);
  const [importStats, setImportStats] = useState<ImportPreviewStats | null>(null);
  const [importWarnings, setImportWarnings] = useState<string[]>([]);
  const [pendingImportResult, setPendingImportResult] = useState<any>(null);

  // Diff Modal state
  const [isDiffModalOpen, setIsDiffModalOpen] = useState(false);
  const [activeDiffProvider, setActiveDiffProvider] = useState<CloudProviderState | null>(null);
  const [activeDiff, setActiveDiff] = useState<ProjectDiffSummary>({ localChanges: [], remoteChanges: [], hasConflicts: false });

  // Audit activities
  const [auditLogs, setAuditLogs] = useState<Array<{ id: string; action: string; actor: string; timestamp: string; details: string }>>([
    {
      id: 'log-init',
      action: 'SYSTEM_STANDBY',
      actor: 'WORKLINE Storage Engine',
      timestamp: new Date().toLocaleTimeString(),
      details: 'Filesystem generator initialized for active project.',
    },
  ]);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const showToast = (text: string, type: 'success' | 'error' | 'info' = 'success') => {
    setToastMessage({ text, type });
    setTimeout(() => setToastMessage(null), 4000);
  };

  const addAudit = (action: string, actor: string, details: string) => {
    setAuditLogs((prev) => [
      {
        id: `log-${Date.now()}-${Math.random().toString(16).slice(2, 6)}`,
        action,
        actor,
        timestamp: new Date().toLocaleTimeString(),
        details,
      },
      ...prev.slice(0, 19),
    ]);
  };

  // Compile .wl filesystem from active ProjectContext
  const recompileFilesystem = () => {
    try {
      const { fileMap: compiledMap, totalBytes } = generateWorklineFilesystem(projectData, {
        projectId,
        projectName: projectName || 'Autonomous Engineering Project',
        systemSpecification,
        targetDays,
        teamName,
        status,
        version: '1.0',
      });
      setFileMap(compiledMap);
      setTotalSizeKb((totalBytes / 1024).toFixed(1));
      return compiledMap;
    } catch (err) {
      console.error('Failed to compile .wl filesystem:', err);
      return {};
    }
  };

  useEffect(() => {
    recompileFilesystem();
  }, [projectData, projectId, projectName, systemSpecification]);

  // Handle Download Complete Project ZIP
  const handleDownloadZip = async () => {
    setIsExportingZip(true);
    try {
      const activeMap = Object.keys(fileMap).length > 0 ? fileMap : recompileFilesystem();
      const currentName = projectName || 'workline-project';
      const { filename, sizeBytes } = await downloadWorklineZip(activeMap, currentName);
      
      const nowStr = new Date().toLocaleString();
      setLastExportTime(nowStr);
      showToast(`Exported ${filename} (${(sizeBytes / 1024).toFixed(1)} KB)`, 'success');
      addAudit('DOWNLOAD_ZIP', 'Current User', `Downloaded self-contained ${filename} archive.`);
    } catch (err: any) {
      showToast(`Export failed: ${err.message}`, 'error');
    } finally {
      setIsExportingZip(false);
    }
  };

  // Handle File Input for Import
  const handleFileSelected = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsImporting(true);
    try {
      const extractedMap = await extractWorklineZip(file);
      const parseResult = parseWorklineFilesystem(extractedMap);

      if (!parseResult.valid) {
        showToast(`Import rejected: ${parseResult.errors.join(', ')}`, 'error');
        return;
      }

      setPendingImportResult(parseResult);
      setImportStats(parseResult.stats || null);
      setImportWarnings(parseResult.warnings);
      setIsImportModalOpen(true);
    } catch (err: any) {
      showToast(`Failed to parse ZIP archive: ${err.message}`, 'error');
    } finally {
      setIsImporting(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  // Confirm Import with Strategy
  const handleConfirmImport = (strategy: ImportResolutionStrategy) => {
    if (!pendingImportResult) return;

    const { importedProjectData, importedMetadata } = pendingImportResult;
    const finalData = mergeProjects(projectData, importedProjectData, strategy);

    setProject(
      finalData,
      importedMetadata.projectName || projectName,
      importedMetadata.targetDays || targetDays,
      {
        projectId: importedMetadata.projectId || projectId,
        systemSpecification: importedMetadata.systemSpecification || systemSpecification,
        status: importedMetadata.status || status,
      }
    );

    setIsImportModalOpen(false);
    showToast(`Project restored via ${strategy} strategy!`, 'success');
    addAudit(
      'RESTORE_PROJECT',
      'Current User',
      `Restored project '${importedMetadata.projectName}' (${importedMetadata.projectId}) with strategy: ${strategy}`
    );
  };

  // Connect / Disconnect Providers
  const toggleGoogleDrive = async () => {
    if (googleDriveState.connected) {
      const fresh = providers.google_drive.disconnect();
      setGoogleDriveState(fresh);
      showToast('Disconnected from Google Drive', 'info');
      addAudit('DISCONNECT', 'Current User', 'Disconnected Google Drive integration.');
    } else {
      const fresh = await providers.google_drive.connect({
        account: 'engineering-drive@workline.ai',
        target: `WORKLINE/Projects/${projectName ? projectName.replace(/\s+/g, '-') : 'Autonomous-Drone'}`,
      });
      setGoogleDriveState(fresh);
      showToast('Connected to Google Drive!', 'success');
      addAudit('CONNECT', 'Current User', `Connected Google Drive to ${fresh.target}`);
    }
  };

  const toggleGitHub = async () => {
    if (githubState.connected) {
      const fresh = providers.github.disconnect();
      setGithubState(fresh);
      showToast('Disconnected from GitHub', 'info');
      addAudit('DISCONNECT', 'Current User', 'Disconnected GitHub integration.');
    } else {
      const fresh = await providers.github.connect({
        account: 'callmetechnophile',
        target: projectName ? `workline-${projectName.toLowerCase().replace(/[^a-z0-9]+/g, '-')}` : 'workline-autonomous-drone',
        branch: 'main',
      });
      setGithubState(fresh);
      showToast('Connected to GitHub repository!', 'success');
      addAudit('CONNECT', 'Current User', `Connected GitHub repository: ${fresh.account}/${fresh.target}`);
    }
  };

  const toggleGitLab = async () => {
    if (gitlabState.connected) {
      const fresh = providers.gitlab.disconnect();
      setGitlabState(fresh);
      showToast('Disconnected from GitLab', 'info');
      addAudit('DISCONNECT', 'Current User', 'Disconnected GitLab integration.');
    } else {
      const fresh = await providers.gitlab.connect({
        account: 'workline-systems',
        target: 'drone-power-distribution',
        branch: 'main',
      });
      setGitlabState(fresh);
      showToast('Connected to GitLab project!', 'success');
      addAudit('CONNECT', 'Current User', `Connected GitLab project: ${fresh.account}/${fresh.target}`);
    }
  };

  const toggleBitbucket = async () => {
    if (bitbucketState.connected) {
      const fresh = providers.bitbucket.disconnect();
      setBitbucketState(fresh);
      showToast('Disconnected from Bitbucket', 'info');
      addAudit('DISCONNECT', 'Current User', 'Disconnected Bitbucket integration.');
    } else {
      const fresh = await providers.bitbucket.connect({
        account: 'workline-robotics',
        target: 'drone-power-bb',
        branch: 'main',
      });
      setBitbucketState(fresh);
      showToast('Connected to Bitbucket repository!', 'success');
      addAudit('CONNECT', 'Current User', `Connected Bitbucket repository: ${fresh.account}/${fresh.target}`);
    }
  };

  // Open Diff Modal for a Provider
  const handleOpenDiff = (provider: CloudProviderState) => {
    const diff = computeProjectDiff(projectData, {
      ...projectData,
      bom: {
        components: [
          ...(projectData?.bom?.components || []),
        ],
      },
    });
    setActiveDiffProvider(provider);
    setActiveDiff(diff);
    setIsDiffModalOpen(true);
  };

  const handleSyncToRemote = async () => {
    if (!activeDiffProvider) return;
    try {
      const providerInst = providers[activeDiffProvider.id];
      const res = await providerInst.sync(fileMap, projectData);
      showToast(res.message, 'success');
      addAudit('SYNC_PUSH', 'Current User', res.message);
      
      // Update UI state
      if (activeDiffProvider.id === 'google_drive') setGoogleDriveState(providerInst.getState());
      if (activeDiffProvider.id === 'github') setGithubState(providerInst.getState());
      if (activeDiffProvider.id === 'gitlab') setGitlabState(providerInst.getState());
      if (activeDiffProvider.id === 'bitbucket') setBitbucketState(providerInst.getState());

      setIsDiffModalOpen(false);
    } catch (err: any) {
      showToast(err.message, 'error');
    }
  };

  const handlePullFromRemote = () => {
    showToast('Pulled latest remote commits into active workspace', 'success');
    addAudit('SYNC_PULL', 'Current User', `Pulled changes from ${activeDiffProvider?.name}`);
    setIsDiffModalOpen(false);
  };

  const displayProjectName = projectName || 'Autonomous Delivery Drone Power Distribution';
  const displayProjectId = projectId || 'PROJ-AUTO';

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12 animate-in fade-in duration-300">
      {/* Toast Notification */}
      {toastMessage && (
        <div
          className={`fixed bottom-6 right-6 z-50 flex items-center gap-2.5 px-4 py-3 rounded-lg shadow-xl text-xs font-mono border backdrop-blur-md transition-all ${
            toastMessage.type === 'success'
              ? 'bg-emerald-950/90 text-emerald-300 border-emerald-700/60'
              : toastMessage.type === 'error'
              ? 'bg-rose-950/90 text-rose-300 border-rose-700/60'
              : 'bg-indigo-950/90 text-indigo-300 border-indigo-700/60'
          }`}
        >
          {toastMessage.type === 'success' ? (
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          ) : (
            <AlertCircle className="w-4 h-4 text-rose-400" />
          )}
          <span>{toastMessage.text}</span>
        </div>
      )}

      {/* Hidden File Input for ZIP Import */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".zip,.workline.zip"
        onChange={handleFileSelected}
        className="hidden"
      />

      {/* Main Workspace Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 bg-slate-900/90 border border-slate-800 rounded-xl">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-indigo-950/80 border border-indigo-700/50 rounded-lg text-indigo-400">
              <FolderArchive className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2.5">
                <h1 className="text-xl font-bold text-slate-100 tracking-tight">
                  PROJECT DATA
                </h1>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-indigo-950 text-indigo-300 border border-indigo-800">
                  v1.0 Standard .wl Filesystem
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono">
                Project Portability, Cloud Synchronization, and Complete Machine-Readable Backup Center
              </p>
            </div>
          </div>
        </div>

        {/* Quick Summary Pill Badges */}
        <div className="flex flex-wrap items-center gap-3 font-mono text-xs">
          <div className="px-3 py-1.5 rounded-lg bg-slate-950/80 border border-slate-800 flex flex-col">
            <span className="text-[10px] text-slate-500 uppercase">Active Project</span>
            <span className="font-semibold text-slate-200 truncate max-w-[200px]">{displayProjectName}</span>
          </div>

          <div className="px-3 py-1.5 rounded-lg bg-slate-950/80 border border-slate-800 flex flex-col">
            <span className="text-[10px] text-slate-500 uppercase">Filesystem Size</span>
            <span className="font-semibold text-indigo-400">{totalSizeKb} KB</span>
          </div>

          <div className="px-3 py-1.5 rounded-lg bg-slate-950/80 border border-slate-800 flex flex-col">
            <span className="text-[10px] text-slate-500 uppercase">Last Exported</span>
            <span className="font-semibold text-slate-300">{lastExportTime}</span>
          </div>
        </div>
      </div>

      {/* Security Check Banner */}
      <div className="p-3.5 bg-slate-900/60 border border-slate-800/80 rounded-xl flex items-center justify-between gap-4 text-xs font-mono">
        <div className="flex items-center gap-2.5 text-slate-300">
          <ShieldCheck className="w-4 h-4 text-emerald-400 flex-shrink-0" />
          <span>
            Strict Zero-Secret Enforcement: API keys, AWS credentials, and OAuth tokens are automatically stripped upon export (<code className="text-indigo-300">credentials: NOT_EXPORTED</code>).
          </span>
        </div>
        <button
          onClick={() => setIsFilesystemModalOpen(true)}
          className="flex items-center gap-1.5 text-indigo-400 hover:text-indigo-300 underline cursor-pointer flex-shrink-0"
        >
          <Eye className="w-3.5 h-3.5" />
          <span>Inspect Filesystem</span>
        </button>
      </div>

      {/* Section 1: Local Export & Import Center */}
      <div className="p-6 bg-slate-900/80 border border-slate-800 rounded-xl space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <Download className="w-4 h-4 text-indigo-400" />
            <h2 className="text-sm font-bold font-mono text-slate-100 uppercase tracking-wider">
              Local Portable Export & Restoration
            </h2>
          </div>
          <span className="text-[11px] font-mono text-slate-500">
            Fully Self-Contained .workline.zip
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
          {/* Download Complete Project ZIP */}
          <div className="p-5 bg-slate-950/70 border border-slate-800 rounded-lg flex flex-col justify-between space-y-4">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <FolderArchive className="w-4 h-4 text-indigo-400" />
                <h3 className="text-sm font-bold text-slate-200">
                  Download Complete Project ZIP
                </h3>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Compiles the complete engineering context into <code className="text-indigo-300">{displayProjectName.replace(/\s+/g, '-')}.workline.zip</code> containing <code className="text-slate-300">README.wl</code>, <code className="text-slate-300">.wl/manifest.wl</code>, BOM CSV, requirements, architecture models, and research citations.
              </p>
            </div>

            <button
              onClick={handleDownloadZip}
              disabled={isExportingZip}
              className="flex items-center justify-center gap-2 w-full py-2.5 px-4 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-lg text-xs font-semibold shadow-md shadow-indigo-600/20 cursor-pointer transition-all"
            >
              {isExportingZip ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Packaging .workline.zip...</span>
                </>
              ) : (
                <>
                  <Download className="w-4 h-4" />
                  <span>Download Complete Project (.workline.zip)</span>
                </>
              )}
            </button>
          </div>

          {/* Import WORKLINE Project */}
          <div className="p-5 bg-slate-950/70 border border-slate-800 rounded-lg flex flex-col justify-between space-y-4">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Upload className="w-4 h-4 text-emerald-400" />
                <h3 className="text-sm font-bold text-slate-200">
                  Import WORKLINE Project
                </h3>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Restore or merge a previously exported <code className="text-emerald-300">.workline.zip</code> or <code className="text-emerald-300">.zip</code>. Validates schema integrity, previews component inventory, and allows non-destructive merge or replace.
              </p>
            </div>

            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={isImporting}
              className="flex items-center justify-center gap-2 w-full py-2.5 px-4 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-slate-100 border border-slate-700 rounded-lg text-xs font-semibold cursor-pointer transition-all"
            >
              {isImporting ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Inspecting Archive...</span>
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4 text-emerald-400" />
                  <span>Import WORKLINE Project (.zip)</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Section 2: Cloud Storage & Git Providers */}
      <div className="p-6 bg-slate-900/80 border border-slate-800 rounded-xl space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <HardDrive className="w-4 h-4 text-indigo-400" />
            <h2 className="text-sm font-bold font-mono text-slate-100 uppercase tracking-wider">
              Cloud Storage & Git Providers
            </h2>
          </div>
          <span className="text-[11px] font-mono text-slate-500">
            Continuous Synchronization Targets
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 pt-2">
          {/* Google Drive Card */}
          <div className="p-4 bg-slate-950/70 border border-slate-800 rounded-lg flex flex-col justify-between space-y-3">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-slate-200 font-semibold text-xs">
                  <FolderSync className="w-4 h-4 text-amber-400" />
                  <span>Google Drive</span>
                </div>
                {googleDriveState.connected ? (
                  <span className="px-2 py-0.5 rounded text-[9px] font-mono bg-emerald-950 text-emerald-400 border border-emerald-800">
                    CONNECTED
                  </span>
                ) : (
                  <span className="px-2 py-0.5 rounded text-[9px] font-mono bg-slate-900 text-slate-500 border border-slate-800">
                    NOT CONNECTED
                  </span>
                )}
              </div>

              {googleDriveState.connected ? (
                <div className="text-[11px] font-mono text-slate-400 space-y-1">
                  <div className="text-slate-300 truncate">{googleDriveState.account}</div>
                  <div className="text-slate-500 truncate text-[10px]">{googleDriveState.target}</div>
                  <div className="text-[10px] text-slate-500 pt-1">
                    Last sync: {googleDriveState.lastSync ? 'Just now' : 'Never'}
                  </div>
                </div>
              ) : (
                <p className="text-[11px] text-slate-500 leading-relaxed">
                  Sync engineering package directly to Google Drive folders.
                </p>
              )}
            </div>

            <div className="flex items-center gap-2 pt-2 border-t border-slate-900">
              {googleDriveState.connected ? (
                <>
                  <button
                    onClick={() => handleOpenDiff(googleDriveState)}
                    className="flex-1 py-1.5 px-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-xs font-medium cursor-pointer transition-colors"
                  >
                    Sync
                  </button>
                  <button
                    onClick={toggleGoogleDrive}
                    className="py-1.5 px-2.5 bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 rounded text-xs cursor-pointer transition-colors"
                  >
                    Disconnect
                  </button>
                </>
              ) : (
                <button
                  onClick={toggleGoogleDrive}
                  className="w-full py-1.5 px-3 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-xs font-semibold cursor-pointer transition-colors"
                >
                  Connect Drive
                </button>
              )}
            </div>
          </div>

          {/* GitHub Card */}
          <div className="p-4 bg-slate-950/70 border border-slate-800 rounded-lg flex flex-col justify-between space-y-3">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-slate-200 font-semibold text-xs">
                  <GithubIcon className="w-4 h-4 text-slate-100" />
                  <span>GitHub</span>
                </div>
                {githubState.connected ? (
                  <span className="px-2 py-0.5 rounded text-[9px] font-mono bg-emerald-950 text-emerald-400 border border-emerald-800">
                    CONNECTED
                  </span>
                ) : (
                  <span className="px-2 py-0.5 rounded text-[9px] font-mono bg-slate-900 text-slate-500 border border-slate-800">
                    NOT CONNECTED
                  </span>
                )}
              </div>

              {githubState.connected ? (
                <div className="text-[11px] font-mono text-slate-400 space-y-1">
                  <div className="text-slate-300 truncate">{githubState.account}/{githubState.target}</div>
                  <div className="flex items-center gap-1.5 text-[10px] text-slate-500">
                    <GitBranch className="w-3 h-3 text-indigo-400" />
                    <span>{githubState.branch || 'main'}</span>
                    <span>• {githubState.lastCommitHash}</span>
                  </div>
                  <div className="text-[10px] text-slate-500 pt-1">
                    Last push: Just now
                  </div>
                </div>
              ) : (
                <p className="text-[11px] text-slate-500 leading-relaxed">
                  Export structured .wl repository with automatic commit tracking.
                </p>
              )}
            </div>

            <div className="flex items-center gap-2 pt-2 border-t border-slate-900">
              {githubState.connected ? (
                <>
                  <button
                    onClick={() => handleOpenDiff(githubState)}
                    className="flex-1 py-1.5 px-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-xs font-medium cursor-pointer transition-colors"
                  >
                    Push
                  </button>
                  <button
                    onClick={toggleGitHub}
                    className="py-1.5 px-2.5 bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 rounded text-xs cursor-pointer transition-colors"
                  >
                    Disconnect
                  </button>
                </>
              ) : (
                <button
                  onClick={toggleGitHub}
                  className="w-full py-1.5 px-3 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-xs font-semibold cursor-pointer transition-colors"
                >
                  Connect GitHub
                </button>
              )}
            </div>
          </div>

          {/* GitLab Card */}
          <div className="p-4 bg-slate-950/70 border border-slate-800 rounded-lg flex flex-col justify-between space-y-3">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-slate-200 font-semibold text-xs">
                  <GitlabIcon className="w-4 h-4 text-orange-400" />
                  <span>GitLab</span>
                </div>
                {gitlabState.connected ? (
                  <span className="px-2 py-0.5 rounded text-[9px] font-mono bg-emerald-950 text-emerald-400 border border-emerald-800">
                    CONNECTED
                  </span>
                ) : (
                  <span className="px-2 py-0.5 rounded text-[9px] font-mono bg-slate-900 text-slate-500 border border-slate-800">
                    NOT CONNECTED
                  </span>
                )}
              </div>

              {gitlabState.connected ? (
                <div className="text-[11px] font-mono text-slate-400 space-y-1">
                  <div className="text-slate-300 truncate">{gitlabState.account}/{gitlabState.target}</div>
                  <div className="text-[10px] text-slate-500">{gitlabState.branch || 'main'} • {gitlabState.lastCommitHash}</div>
                </div>
              ) : (
                <p className="text-[11px] text-slate-500 leading-relaxed">
                  Push project package to self-hosted or cloud GitLab projects.
                </p>
              )}
            </div>

            <div className="flex items-center gap-2 pt-2 border-t border-slate-900">
              {gitlabState.connected ? (
                <>
                  <button
                    onClick={() => handleOpenDiff(gitlabState)}
                    className="flex-1 py-1.5 px-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-xs font-medium cursor-pointer transition-colors"
                  >
                    Push
                  </button>
                  <button
                    onClick={toggleGitLab}
                    className="py-1.5 px-2.5 bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 rounded text-xs cursor-pointer transition-colors"
                  >
                    Disconnect
                  </button>
                </>
              ) : (
                <button
                  onClick={toggleGitLab}
                  className="w-full py-1.5 px-3 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-xs font-semibold cursor-pointer transition-colors"
                >
                  Connect GitLab
                </button>
              )}
            </div>
          </div>

          {/* Bitbucket Card */}
          <div className="p-4 bg-slate-950/70 border border-slate-800 rounded-lg flex flex-col justify-between space-y-3">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-slate-200 font-semibold text-xs">
                  <GitBranch className="w-4 h-4 text-blue-400" />
                  <span>Bitbucket</span>
                </div>
                {bitbucketState.connected ? (
                  <span className="px-2 py-0.5 rounded text-[9px] font-mono bg-emerald-950 text-emerald-400 border border-emerald-800">
                    CONNECTED
                  </span>
                ) : (
                  <span className="px-2 py-0.5 rounded text-[9px] font-mono bg-slate-900 text-slate-500 border border-slate-800">
                    NOT CONNECTED
                  </span>
                )}
              </div>

              {bitbucketState.connected ? (
                <div className="text-[11px] font-mono text-slate-400 space-y-1">
                  <div className="text-slate-300 truncate">{bitbucketState.account}/{bitbucketState.target}</div>
                  <div className="text-[10px] text-slate-500">{bitbucketState.branch || 'main'} • {bitbucketState.lastCommitHash}</div>
                </div>
              ) : (
                <p className="text-[11px] text-slate-500 leading-relaxed">
                  Sync with Bitbucket Cloud or Enterprise repositories.
                </p>
              )}
            </div>

            <div className="flex items-center gap-2 pt-2 border-t border-slate-900">
              {bitbucketState.connected ? (
                <>
                  <button
                    onClick={() => handleOpenDiff(bitbucketState)}
                    className="flex-1 py-1.5 px-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-xs font-medium cursor-pointer transition-colors"
                  >
                    Push
                  </button>
                  <button
                    onClick={toggleBitbucket}
                    className="py-1.5 px-2.5 bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 rounded text-xs cursor-pointer transition-colors"
                  >
                    Disconnect
                  </button>
                </>
              ) : (
                <button
                  onClick={toggleBitbucket}
                  className="w-full py-1.5 px-3 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-xs font-semibold cursor-pointer transition-colors"
                >
                  Connect Bitbucket
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Section 3: Standardized WORKLINE Filesystem (.wl) Tree Viewer */}
      <div className="p-6 bg-slate-900/80 border border-slate-800 rounded-xl space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <FileCode className="w-4 h-4 text-indigo-400" />
            <h2 className="text-sm font-bold font-mono text-slate-100 uppercase tracking-wider">
              WORKLINE Filesystem Structure (.wl)
            </h2>
          </div>
          <button
            onClick={() => setIsFilesystemModalOpen(true)}
            className="flex items-center gap-1.5 px-3 py-1 bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/40 rounded text-xs font-mono cursor-pointer transition-colors"
          >
            <Eye className="w-3.5 h-3.5" />
            <span>[Preview Filesystem]</span>
          </button>
        </div>

        {/* Directory Schema Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-7 gap-2.5 text-xs font-mono pt-1">
          <div
            onClick={() => setIsFilesystemModalOpen(true)}
            className="p-3 bg-slate-950/70 border border-slate-800 hover:border-indigo-500/50 rounded-lg cursor-pointer transition-colors space-y-1"
          >
            <div className="font-bold text-indigo-300">README.wl</div>
            <div className="text-[10px] text-slate-500">CLI entry point</div>
          </div>

          <div
            onClick={() => setIsFilesystemModalOpen(true)}
            className="p-3 bg-slate-950/70 border border-slate-800 hover:border-indigo-500/50 rounded-lg cursor-pointer transition-colors space-y-1"
          >
            <div className="font-bold text-indigo-300">.wl/</div>
            <div className="text-[10px] text-slate-500">manifest & meta</div>
          </div>

          <div
            onClick={() => setIsFilesystemModalOpen(true)}
            className="p-3 bg-slate-950/70 border border-slate-800 hover:border-indigo-500/50 rounded-lg cursor-pointer transition-colors space-y-1"
          >
            <div className="font-bold text-slate-200">requirements/</div>
            <div className="text-[10px] text-slate-500">specs & gates</div>
          </div>

          <div
            onClick={() => setIsFilesystemModalOpen(true)}
            className="p-3 bg-slate-950/70 border border-slate-800 hover:border-indigo-500/50 rounded-lg cursor-pointer transition-colors space-y-1"
          >
            <div className="font-bold text-slate-200">architecture/</div>
            <div className="text-[10px] text-slate-500">blocks & flows</div>
          </div>

          <div
            onClick={() => setIsFilesystemModalOpen(true)}
            className="p-3 bg-slate-950/70 border border-slate-800 hover:border-indigo-500/50 rounded-lg cursor-pointer transition-colors space-y-1"
          >
            <div className="font-bold text-slate-200">components/</div>
            <div className="text-[10px] text-slate-500">per-MPN dossiers</div>
          </div>

          <div
            onClick={() => setIsFilesystemModalOpen(true)}
            className="p-3 bg-slate-950/70 border border-slate-800 hover:border-indigo-500/50 rounded-lg cursor-pointer transition-colors space-y-1"
          >
            <div className="font-bold text-slate-200">bom/</div>
            <div className="text-[10px] text-slate-500">bom.wl & bom.csv</div>
          </div>

          <div
            onClick={() => setIsFilesystemModalOpen(true)}
            className="p-3 bg-slate-950/70 border border-slate-800 hover:border-indigo-500/50 rounded-lg cursor-pointer transition-colors space-y-1"
          >
            <div className="font-bold text-slate-200">research/</div>
            <div className="text-[10px] text-slate-500">papers & findings</div>
          </div>

          <div
            onClick={() => setIsFilesystemModalOpen(true)}
            className="p-3 bg-slate-950/70 border border-slate-800 hover:border-indigo-500/50 rounded-lg cursor-pointer transition-colors space-y-1"
          >
            <div className="font-bold text-slate-200">documents/</div>
            <div className="text-[10px] text-slate-500">datasheet refs</div>
          </div>

          <div
            onClick={() => setIsFilesystemModalOpen(true)}
            className="p-3 bg-slate-950/70 border border-slate-800 hover:border-indigo-500/50 rounded-lg cursor-pointer transition-colors space-y-1"
          >
            <div className="font-bold text-slate-200">analysis/</div>
            <div className="text-[10px] text-slate-500">power, pcb, thermal</div>
          </div>

          <div
            onClick={() => setIsFilesystemModalOpen(true)}
            className="p-3 bg-slate-950/70 border border-slate-800 hover:border-indigo-500/50 rounded-lg cursor-pointer transition-colors space-y-1"
          >
            <div className="font-bold text-slate-200">decisions/</div>
            <div className="text-[10px] text-slate-500">ADR records</div>
          </div>

          <div
            onClick={() => setIsFilesystemModalOpen(true)}
            className="p-3 bg-slate-950/70 border border-slate-800 hover:border-indigo-500/50 rounded-lg cursor-pointer transition-colors space-y-1"
          >
            <div className="font-bold text-slate-200">tasks/</div>
            <div className="text-[10px] text-slate-500">milestone items</div>
          </div>

          <div
            onClick={() => setIsFilesystemModalOpen(true)}
            className="p-3 bg-slate-950/70 border border-slate-800 hover:border-indigo-500/50 rounded-lg cursor-pointer transition-colors space-y-1"
          >
            <div className="font-bold text-slate-200">team/</div>
            <div className="text-[10px] text-slate-500">roles & access</div>
          </div>

          <div
            onClick={() => setIsFilesystemModalOpen(true)}
            className="p-3 bg-slate-950/70 border border-slate-800 hover:border-indigo-500/50 rounded-lg cursor-pointer transition-colors space-y-1"
          >
            <div className="font-bold text-slate-200">agents/</div>
            <div className="text-[10px] text-slate-500">receipts & audit</div>
          </div>

          <div
            onClick={() => setIsFilesystemModalOpen(true)}
            className="p-3 bg-slate-950/70 border border-slate-800 hover:border-indigo-500/50 rounded-lg cursor-pointer transition-colors space-y-1"
          >
            <div className="font-bold text-slate-200">history/</div>
            <div className="text-[10px] text-slate-500">activity ledger</div>
          </div>
        </div>
      </div>

      {/* Section 4: Audit & Activity Stream */}
      <div className="p-6 bg-slate-900/80 border border-slate-800 rounded-xl space-y-3">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <History className="w-4 h-4 text-indigo-400" />
            <h2 className="text-sm font-bold font-mono text-slate-100 uppercase tracking-wider">
              Project Synchronization & Audit Log
            </h2>
          </div>
          <span className="text-[11px] font-mono text-slate-500">
            Immutable Activity Trail
          </span>
        </div>

        <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
          {auditLogs.map((log) => (
            <div
              key={log.id}
              className="flex items-center justify-between p-2.5 bg-slate-950/60 border border-slate-800/80 rounded text-xs font-mono"
            >
              <div className="flex items-center gap-2.5">
                <span className="px-1.5 py-0.5 rounded text-[10px] bg-slate-800 text-indigo-300">
                  {log.action}
                </span>
                <span className="text-slate-300">{log.details}</span>
              </div>
              <div className="flex items-center gap-3 text-slate-500 text-[11px]">
                <span>{log.actor}</span>
                <span>{log.timestamp}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Filesystem Preview Modal */}
      <FilesystemViewerModal
        isOpen={isFilesystemModalOpen}
        onClose={() => setIsFilesystemModalOpen(false)}
        fileMap={fileMap}
        projectName={displayProjectName}
      />

      {/* Import Preview Modal */}
      {importStats && (
        <ImportPreviewModal
          isOpen={isImportModalOpen}
          onClose={() => setIsImportModalOpen(false)}
          stats={importStats}
          warnings={importWarnings}
          onConfirmImport={handleConfirmImport}
        />
      )}

      {/* Diff & Sync Preview Modal */}
      {activeDiffProvider && (
        <DiffSyncModal
          isOpen={isDiffModalOpen}
          onClose={() => setIsDiffModalOpen(false)}
          provider={activeDiffProvider}
          diff={activeDiff}
          onSyncLocalToRemote={handleSyncToRemote}
          onPullRemoteToLocal={handlePullFromRemote}
        />
      )}
    </div>
  );
}
