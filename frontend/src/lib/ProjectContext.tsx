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

export interface ProjectState {
  /** Full pipeline data from /api/research */
  projectData: any | null;
  /** Human-readable project name / intent */
  projectName: string;
  /** Target execution timeline in days */
  targetDays: number;
  /** Whether a project is actively loaded */
  hasProject: boolean;
  /** Loading state for project operations */
  isLoading: boolean;
  /** Error message if last operation failed */
  error: string | null;
  /** API base URL for R1 gateway */
  apiBase: string;
  /** Set active project data */
  setProject: (data: any, name: string, days: number) => void;
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
  const [projectName, setProjectName] = useState<string>('');
  const [targetDays, setTargetDays] = useState<number>(30);
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
            setProjectName(parsed.name || '');
            setTargetDays(parsed.days || 30);
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
    } catch (err) {
      console.error('Failed to fetch session history:', err);
    }
  }, [userId, apiBase, getToken]);

  useEffect(() => {
    refreshHistory();
  }, [refreshHistory]);

  const setProject = useCallback((data: any, name: string, days: number) => {
    setProjectData(data);
    setProjectName(name);
    setTargetDays(days);
    setError(null);

    // Cache to localStorage (supplemental)
    if (typeof window !== 'undefined') {
      localStorage.setItem(
        'workline_active_project',
        JSON.stringify({ name, days, data })
      );
    }
  }, []);

  const clearProject = useCallback(() => {
    setProjectData(null);
    setProjectName('');
    setTargetDays(30);
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
          intent: projectName || projectData.intent,
          readiness_score: projectData.validation?.readiness_score,
          risk_score: projectData.validation?.risk_score,
          optimization_score: projectData.optimization?.optimization_score,
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
  }, [projectData, projectName, apiBase, getToken, refreshHistory]);

  const value: ProjectState = {
    projectData,
    projectName,
    targetDays,
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
