'use client';

import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { useAuth } from '@clerk/nextjs';

/**
 * Workline AI — Authoritative Project Context
 *
 * Every engineering module MUST obtain the current project through
 * this context. No component may silently fall back to fabricated data.
 *
 * States:
 *   - NO_PROJECT: User is authenticated but no project selected
 *   - LOADING:    Project data is being fetched/created
 *   - ERROR:      API call failed
 *   - READY:      Project data loaded from backend
 */

export interface ProjectMetadata {
  projectId?: string;
  projectName?: string;
  systemSpecification?: string;
  targetDays?: number;
  engineeringTemplate?: string;
  teamId?: string;
  teamName?: string;
  ownerId?: string;
  status?: string;
  createdAt?: string;
  updatedAt?: string;
}

export interface ProjectState {
  /** Full pipeline data from /api/research */
  projectData: any | null;
  /** Authoritative Project ID */
  projectId: string;
  /** Human-readable project name */
  projectName: string;
  /** Technical System Specification & Engineering Goal */
  systemSpecification: string;
  /** Target execution timeline in days */
  targetDays: number;
  /** Optional engineering template used */
  engineeringTemplate?: string;
  /** Team context */
  teamName: string;
  /** Project status */
  status: string;
  /** Whether a project is actively loaded */
  hasProject: boolean;
  /** Loading state for project operations */
  isLoading: boolean;
  /** Error message if last operation failed */
  error: string | null;
  /** API base URL for R1 gateway */
  apiBase: string;
  /** Set active project data */
  setProject: (
    data: any,
    name: string,
    days: number,
    metadata?: ProjectMetadata
  ) => void;
  /** Clear current project */
  clearProject: () => void;
  /** Saved session history */
  savedHistory: any[];
  /** Refresh session history from backend */
  refreshHistory: () => Promise<void>;
  /** Whether spec is being saved */
  isSaving: boolean;
  /** Save current spec to user profile */
  saveSpec: () => Promise<void>;
}

const ProjectContext = createContext<ProjectState | undefined>(undefined);

export function useProject(): ProjectState {
  const context = useContext(ProjectContext);
  if (!context) {
    throw new Error('useProject must be used within a ProjectProvider');
  }
  return context;
}

interface ProjectProviderProps {
  children: ReactNode;
}

export function ProjectProvider({ children }: ProjectProviderProps) {
  const [projectData, setProjectData] = useState<any | null>(null);
  const [projectId, setProjectId] = useState<string>('PROJ-DEFAULT');
  const [projectName, setProjectName] = useState<string>('');
  const [systemSpecification, setSystemSpecification] = useState<string>('');
  const [targetDays, setTargetDays] = useState<number>(30);
  const [engineeringTemplate, setEngineeringTemplate] = useState<string>('');
  const [teamName, setTeamName] = useState<string>('Hardware Engineering');
  const [status, setStatus] = useState<string>('active');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [savedHistory, setSavedHistory] = useState<any[]>([]);
  const [isSaving, setIsSaving] = useState(false);
  const [apiBase, setApiBase] = useState('');

  const { getToken, userId } = useAuth();

  // Resolve API base URL
  useEffect(() => {
    if (typeof window !== 'undefined') {
      if (process.env.NEXT_PUBLIC_API_URL) {
        setApiBase(process.env.NEXT_PUBLIC_API_URL);
      } else if (window.location.port === '3000') {
        setApiBase('http://localhost:8000');
      } else {
        setApiBase('https://workline-core-gateway.onrender.com');
      }

      // Load cached project (supplemental only)
      const cached = localStorage.getItem('workline_active_project');
      if (cached) {
        try {
          const parsed = JSON.parse(cached);
          if (parsed.data) {
            setProjectData(parsed.data);
            const pName = parsed.projectName || parsed.name || (parsed.data.project_name) || 'Untitled Engineering Project';
            const pId = parsed.projectId || parsed.data.project_id || `PROJ-${pName.slice(0, 4).toUpperCase()}`;
            const pSpec = parsed.systemSpecification || parsed.data.system_specification || parsed.data.intent || '';
            const tDays = parsed.targetDays || parsed.days || parsed.data.target_timeline_days || 30;

            setProjectId(pId);
            setProjectName(pName);
            setSystemSpecification(pSpec);
            setTargetDays(tDays);
            setEngineeringTemplate(parsed.engineeringTemplate || parsed.data.engineering_template || '');
            setTeamName(parsed.teamName || parsed.data.team_id || 'Hardware Engineering');
            setStatus(parsed.status || parsed.data.status || 'active');
          }
        } catch (e) {
          console.error('Failed to parse cached project:', e);
        }
      }
    }
  }, []);

  // Fetch session history when user is authenticated
  const refreshHistory = useCallback(async () => {
    if (!userId || !apiBase) return;
    try {
      const token = await getToken();
      const res = await fetch(`${apiBase}/api/packages/history`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setSavedHistory(data);
      }
    } catch (e) {
      console.error('Failed to fetch package history:', e);
    }
  }, [userId, apiBase, getToken]);

  useEffect(() => {
    refreshHistory();
  }, [refreshHistory]);

  const setProject = useCallback(
    (
      data: any,
      name: string,
      days: number,
      metadata?: ProjectMetadata
    ) => {
      const resolvedName = (name || metadata?.projectName || data?.project_name || '').trim() || 'Untitled Engineering Project';
      const resolvedSpec = (metadata?.systemSpecification || data?.system_specification || data?.intent || '').trim();
      const resolvedId = metadata?.projectId || data?.project_id || `PROJ-${resolvedName.slice(0, 4).toUpperCase()}`;
      const resolvedDays = days || metadata?.targetDays || data?.target_timeline_days || 30;
      const resolvedTemplate = metadata?.engineeringTemplate || data?.engineering_template || '';
      const resolvedTeam = metadata?.teamName || metadata?.teamId || data?.team_id || 'Hardware Engineering';
      const resolvedStatus = metadata?.status || data?.status || 'active';

      setProjectData(data);
      setProjectId(resolvedId);
      setProjectName(resolvedName);
      setSystemSpecification(resolvedSpec);
      setTargetDays(resolvedDays);
      setEngineeringTemplate(resolvedTemplate);
      setTeamName(resolvedTeam);
      setStatus(resolvedStatus);
      setError(null);

      // Cache to localStorage (supplemental)
      if (typeof window !== 'undefined') {
        localStorage.setItem(
          'workline_active_project',
          JSON.stringify({
            projectId: resolvedId,
            projectName: resolvedName,
            systemSpecification: resolvedSpec,
            targetDays: resolvedDays,
            engineeringTemplate: resolvedTemplate,
            teamName: resolvedTeam,
            status: resolvedStatus,
            data,
          })
        );
      }
    },
    []
  );

  const clearProject = useCallback(() => {
    setProjectData(null);
    setProjectId('PROJ-DEFAULT');
    setProjectName('');
    setSystemSpecification('');
    setTargetDays(30);
    setEngineeringTemplate('');
    setTeamName('Hardware Engineering');
    setStatus('active');
    setError(null);
    if (typeof window !== 'undefined') {
      localStorage.removeItem('workline_active_project');
    }
  }, []);

  const saveSpec = useCallback(async () => {
    if (!projectData) return;
    setIsSaving(true);
    try {
      const token = await getToken();
      const response = await fetch(`${apiBase}/api/packages/save`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          project_id: projectId,
          project_name: projectName || 'Untitled Engineering Project',
          system_specification: systemSpecification || projectData.intent,
          intent: systemSpecification || projectData.intent,
          target_days: targetDays,
          engineering_template: engineeringTemplate,
          team_id: teamName,
          status,
          readiness_score: projectData.validation?.readiness_score || 85,
          risk_score: projectData.validation?.risk_score || 15,
          optimization_score: projectData.optimization?.optimization_score || 90,
          data: projectData,
        }),
      });

      if (response.ok) {
        await refreshHistory();
      } else {
        throw new Error('Failed to save specification');
      }
    } catch (err: any) {
      setError(err?.message || 'Error saving specification');
    } finally {
      setIsSaving(false);
    }
  }, [
    projectData,
    projectId,
    projectName,
    systemSpecification,
    targetDays,
    engineeringTemplate,
    teamName,
    status,
    apiBase,
    getToken,
    refreshHistory,
  ]);

  const value: ProjectState = {
    projectData,
    projectId,
    projectName,
    systemSpecification,
    targetDays,
    engineeringTemplate,
    teamName,
    status,
    hasProject: Boolean(projectData),
    isLoading,
    error,
    apiBase,
    setProject,
    clearProject,
    savedHistory,
    refreshHistory,
    isSaving,
    saveSpec,
  };

  return (
    <ProjectContext.Provider value={value}>
      {children}
    </ProjectContext.Provider>
  );
}
