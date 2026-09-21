/**
 * WORKLINE Project Filesystem (.wl) Types and Schemas
 *
 * Defines the contract for the portable .wl filesystem format
 * consumed by WORKLINE Web, WORKLINE CLI (wg), WORKLINE SDK, and AI Agents.
 */

export interface WorklineFileMap {
  [filePath: string]: string;
}

export interface WorklineManifestResource {
  path: string;
  count?: number;
  description?: string;
  checksum?: string;
}

export interface WorklineManifest {
  schema_version: string;
  export_version: string;
  generated_at: string;
  source_workline_version: string;
  project: {
    id: string;
    name: string;
    description: string;
    domain: string;
    status: string;
    version: string;
    author?: string;
  };
  resources: {
    requirements: WorklineManifestResource;
    architecture: WorklineManifestResource;
    components: WorklineManifestResource;
    bom: WorklineManifestResource;
    research: WorklineManifestResource;
    documents: WorklineManifestResource;
    analysis: WorklineManifestResource;
    decisions: WorklineManifestResource;
    tasks: WorklineManifestResource;
    team: WorklineManifestResource;
    agents: WorklineManifestResource;
    history: WorklineManifestResource;
    exports: WorklineManifestResource;
  };
  file_count: number;
  total_bytes: number;
  checksums: Record<string, string>;
}

export interface ImportPreviewStats {
  projectId: string;
  projectName: string;
  version: string;
  schemaVersion: string;
  generatedAt: string;
  requirementsCount: number;
  componentsCount: number;
  documentsCount: number;
  researchPapersCount: number;
  bomItemsCount: number;
  tasksCount: number;
  decisionsCount: number;
  teamMembersCount: number;
  agentsCount: number;
}

export type ImportResolutionStrategy = 'CREATE_NEW' | 'MERGE' | 'REPLACE';

export interface DiffItem {
  id: string;
  category: 'requirements' | 'components' | 'bom' | 'architecture' | 'research' | 'tasks' | 'decisions';
  type: 'ADDED' | 'MODIFIED' | 'REMOVED';
  name: string;
  details: string;
}

export interface ProjectDiffSummary {
  localChanges: DiffItem[];
  remoteChanges: DiffItem[];
  hasConflicts: boolean;
}

export type CloudProviderId = 'google_drive' | 'github' | 'gitlab' | 'bitbucket';

export interface CloudProviderState {
  id: CloudProviderId;
  name: string;
  connected: boolean;
  account?: string;
  target?: string;
  branch?: string;
  lastSync?: string;
  syncDirection?: 'LOCAL_TO_REMOTE' | 'REMOTE_TO_LOCAL' | 'BIDIRECTIONAL';
  lastCommitHash?: string;
  remoteVersion?: string;
  localVersion?: string;
  error?: string | null;
}
