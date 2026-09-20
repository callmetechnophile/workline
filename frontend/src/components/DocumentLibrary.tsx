"use client";

import React, { useState, useEffect } from "react";
import {
  FileText,
  Upload,
  RefreshCw,
  Trash2,
  CheckCircle2,
  AlertCircle,
  Search,
  ExternalLink,
  PlusCircle,
  BookmarkPlus,
  Zap,
  Tag,
  Boxes,
  DollarSign,
  Calendar,
  Layers,
  Info,
} from "lucide-react";

export interface DocumentItem {
  documentId: string;
  projectId: string;
  filename: string;
  title: string;
  sourceType: string;
  status: "DISCOVERED" | "INGESTING" | "PARSED" | "ENRICHED" | "INDEXED" | "FAILED" | "STALE";
  sectionsCount: number;
  updatedAt: number;
  metadata?: Record<string, any>;
}

export interface NexarComponentResult {
  component_id?: string;
  manufacturer?: string;
  manufacturer_part_number?: string;
  mpn?: string;
  product_name?: string;
  category?: string;
  description?: string;
  electrical?: {
    nominal_voltage?: number;
    voltage_min?: number;
    voltage_max?: number;
    current_max?: number;
    current?: number;
  };
  physical?: {
    package?: string;
    dimensions?: string;
    mounting?: string;
    pin_count?: number;
  };
  availability?: {
    stock?: number;
    in_stock?: boolean;
    lead_time_days?: number;
  };
  pricing?: {
    unit_price?: number;
    currency?: string;
    quantity_breaks?: Record<string, number>;
  };
  datasheet?: {
    datasheet_id?: string;
    url?: string;
    title?: string;
    document_type?: string;
    verification_status?: string;
  };
  vendor?: {
    name?: string;
    location?: string;
    product_url?: string;
  };
}

interface DocumentLibraryProps {
  documents?: DocumentItem[];
  selectedDocId?: string;
  projectId?: string;
  apiBase?: string;
  onSelectDocument?: (docId: string) => void;
  onIngestFile?: (file: File) => Promise<void>;
  onReindex?: (docId: string) => Promise<void>;
  onDelete?: (docId: string) => Promise<void>;
  onKnowledgeBaseGenerated?: () => void;
}

type FilterSource = "ALL" | "LOCAL" | "OCTOPART_NEXAR";

export const DocumentLibrary: React.FC<DocumentLibraryProps> = ({
  documents: initialDocuments = [],
  selectedDocId,
  projectId = "default-project",
  apiBase: propApiBase,
  onSelectDocument,
  onIngestFile,
  onReindex,
  onDelete,
  onKnowledgeBaseGenerated,
}) => {
  const [isUploading, setIsUploading] = useState(false);
  const [isGeneratingKB, setIsGeneratingKB] = useState(false);
  const [filterSource, setFilterSource] = useState<FilterSource>("ALL");
  const [searchQuery, setSearchQuery] = useState("");
  const [isSearchingNexar, setIsSearchingNexar] = useState(false);
  const [nexarResults, setNexarResults] = useState<NexarComponentResult[]>([]);
  const [actionNotice, setActionNotice] = useState<{ type: "success" | "error" | "info"; message: string } | null>(null);
  const [selectedDetails, setSelectedDetails] = useState<NexarComponentResult | null>(null);
  const [localDocs, setLocalDocs] = useState<DocumentItem[]>(initialDocuments);

  const apiBase = propApiBase || (typeof window !== "undefined" && window.location.hostname === "localhost" ? "http://localhost:8000" : "");

  // Load documents from backend on mount or when projectId changes
  const fetchDocuments = async () => {
    try {
      const res = await fetch(`${apiBase}/api/documents${projectId ? `?project_id=${projectId}` : ""}`);
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data)) {
          const mapped: DocumentItem[] = data.map((d: any) => ({
            documentId: d.document_id,
            projectId: d.project_id,
            filename: d.filename,
            title: d.title,
            sourceType: d.source_type,
            status: d.status,
            sectionsCount: (d.sections || []).length,
            updatedAt: d.updated_at ? d.updated_at * 1000 : Date.now(),
            metadata: d.metadata || {},
          }));
          setLocalDocs(mapped);
        }
      }
    } catch {
      // Offline fallback to initialDocuments
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, [projectId]);

  useEffect(() => {
    if (initialDocuments && initialDocuments.length > 0) {
      setLocalDocs(initialDocuments);
    }
  }, [initialDocuments]);

  // Execute Nexar MCP Search
  const handleNexarSearch = async (queryToSearch?: string) => {
    const q = (queryToSearch !== undefined ? queryToSearch : searchQuery).trim();
    if (!q) return;

    setIsSearchingNexar(true);
    setActionNotice(null);
    try {
      const res = await fetch(`${apiBase}/api/documents/nexar/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: q, limit: 8, project_id: projectId }),
      });
      if (res.ok) {
        const payload = await res.json();
        setNexarResults(payload.results || []);
        if ((payload.results || []).length === 0) {
          setActionNotice({ type: "info", message: `No components found on Octopart / Nexar for "${q}".` });
        }
      } else {
        const err = await res.json().catch(() => ({ detail: "Search request failed" }));
        setActionNotice({ type: "error", message: `Nexar search error: ${err.detail || "Server error"}` });
      }
    } catch (e: any) {
      setActionNotice({ type: "error", message: `Could not connect to Nexar MCP: ${e.message || "Network error"}` });
    } finally {
      setIsSearchingNexar(false);
    }
  };

  // Quick search button triggers
  const handleQuickSearch = (term: string) => {
    setSearchQuery(term);
    setFilterSource("OCTOPART_NEXAR");
    handleNexarSearch(term);
  };

  // Action: Save to Knowledge Base
  const handleSaveToKnowledge = async (comp: NexarComponentResult) => {
    const mpn = comp.manufacturer_part_number || comp.mpn || "COMPONENT";
    try {
      const res = await fetch(`${apiBase}/api/documents/nexar/save-to-knowledge`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project_id: projectId,
          component_data: comp,
        }),
      });
      if (res.ok) {
        const result = await res.json();
        setActionNotice({
          type: "success",
          message: result.status === "EXISTING"
            ? `Component ${mpn} is already indexed in Knowledge Base.`
            : `Successfully indexed ${mpn} into Knowledge Base & SurrealDB graph.`,
        });
        await fetchDocuments();
      } else {
        setActionNotice({ type: "error", message: `Failed to save ${mpn} to Knowledge Base.` });
      }
    } catch (e: any) {
      setActionNotice({ type: "error", message: `Error saving to Knowledge Base: ${e.message}` });
    }
  };

  // Action: Add to BOM
  const handleAddToBom = async (comp: NexarComponentResult) => {
    const mpn = comp.manufacturer_part_number || comp.mpn || "COMPONENT";
    try {
      const res = await fetch(`${apiBase}/api/documents/nexar/add-to-bom`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project_id: projectId,
          component_data: comp,
          quantity: 1,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setActionNotice({
          type: "success",
          message: `Added ${mpn} to project BOM (${data.total_items} items total).`,
        });
      } else {
        setActionNotice({ type: "error", message: `Failed to add ${mpn} to BOM.` });
      }
    } catch (e: any) {
      setActionNotice({ type: "error", message: `Error adding to BOM: ${e.message}` });
    }
  };

  const handleAutoGenerateKB = async () => {
    setIsGeneratingKB(true);
    setActionNotice(null);
    try {
      const res = await fetch(`${apiBase}/api/documents/nexar/generate-knowledge-base`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ project_id: projectId }),
      });
      if (res.ok) {
        const payload = await res.json();
        await fetchDocuments();
        setActionNotice({
          type: "success",
          message: `Engineering Knowledge Base synthesized! Indexed ${payload.indexed_count || 0} components and verified datasheets via Octopart / Nexar.`,
        });
        if (onKnowledgeBaseGenerated) {
          onKnowledgeBaseGenerated();
        }
      } else {
        const err = await res.json().catch(() => ({ detail: "Synthesis failed" }));
        setActionNotice({ type: "error", message: `Synthesis error: ${err.detail || "Server error"}` });
      }
    } catch (err: any) {
      setActionNotice({ type: "error", message: `Knowledge Base synthesis error: ${err.message || "Network error"}` });
    } finally {
      setIsGeneratingKB(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && onIngestFile) {
      setIsUploading(true);
      try {
        await onIngestFile(file);
        await fetchDocuments();
      } finally {
        setIsUploading(false);
      }
    }
  };

  // Filter local documents
  const filteredLocalDocs = localDocs.filter((doc) => {
    if (filterSource === "OCTOPART_NEXAR") {
      return doc.sourceType === "OCTOPART_NEXAR";
    }
    if (filterSource === "LOCAL") {
      return doc.sourceType !== "OCTOPART_NEXAR";
    }
    return true;
  }).filter((doc) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return (
      doc.title.toLowerCase().includes(q) ||
      doc.filename.toLowerCase().includes(q) ||
      (doc.metadata?.mpn && doc.metadata.mpn.toLowerCase().includes(q))
    );
  });

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 flex flex-col gap-4 text-zinc-100">
      {/* Header with Title and Ingest */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-zinc-800 pb-4">
        <div className="flex items-center gap-2">
          <FileText className="w-5 h-5 text-indigo-400" />
          <div>
            <h3 className="text-base font-bold text-zinc-100">Engineering Knowledge Base & Documents Index</h3>
            <p className="text-xs text-zinc-400">Integrated with Octopart / Nexar Component Intelligence & SurrealDB</p>
          </div>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <button
            onClick={() => fetchDocuments()}
            title="Refresh Knowledge Base"
            className="p-1.5 text-zinc-400 hover:text-zinc-200 border border-zinc-800 rounded hover:bg-zinc-800 transition cursor-pointer"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={handleAutoGenerateKB}
            disabled={isGeneratingKB}
            title="Auto-Generate Knowledge Base & Datasheets via Nexar API"
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white rounded cursor-pointer transition shadow-sm"
          >
            {isGeneratingKB ? (
              <>
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                <span>Generating KB...</span>
              </>
            ) : (
              <>
                <Zap className="w-3.5 h-3.5" />
                <span>Auto-Generate KB (Nexar API)</span>
              </>
            )}
          </button>
          <label className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white rounded cursor-pointer transition shadow-sm">
            <Upload className="w-3.5 h-3.5" />
            <span>{isUploading ? "Ingesting..." : "Ingest Local File"}</span>
            <input type="file" className="hidden" onChange={handleFileUpload} accept=".pdf,.md,.txt,.html" />
          </label>
        </div>
      </div>

      {/* Filter Tabs & Search Bar */}
      <div className="flex flex-col gap-3">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div className="flex items-center bg-zinc-950 p-1 rounded-lg border border-zinc-800 text-xs font-medium">
            <button
              onClick={() => setFilterSource("ALL")}
              className={`px-3 py-1 rounded transition ${filterSource === "ALL" ? "bg-indigo-600 text-white" : "text-zinc-400 hover:text-zinc-200"}`}
            >
              ALL
            </button>
            <button
              onClick={() => setFilterSource("LOCAL")}
              className={`px-3 py-1 rounded transition ${filterSource === "LOCAL" ? "bg-indigo-600 text-white" : "text-zinc-400 hover:text-zinc-200"}`}
            >
              LOCAL DOCUMENTS
            </button>
            <button
              onClick={() => setFilterSource("OCTOPART_NEXAR")}
              className={`px-3 py-1 rounded transition flex items-center gap-1.5 ${filterSource === "OCTOPART_NEXAR" ? "bg-emerald-600 text-white font-semibold" : "text-emerald-400 hover:text-emerald-300"}`}
            >
              <Zap className="w-3 h-3" />
              OCTOPART / NEXAR
            </button>
          </div>

          {/* Quick Search Chips */}
          <div className="flex items-center gap-1.5 text-[11px] font-mono text-zinc-400 overflow-x-auto py-1">
            <span className="text-zinc-500 text-[10px] uppercase font-bold tracking-wider">Examples:</span>
            {["BQ76952", "INA226", "SN65HVD230", "CSD19536", "LM5164", "ESP32-S3", "BME280"].map((chip) => (
              <button
                key={chip}
                onClick={() => handleQuickSearch(chip)}
                className="px-2 py-0.5 rounded bg-zinc-800 hover:bg-zinc-700 hover:text-zinc-100 border border-zinc-700 transition"
              >
                {chip}
              </button>
            ))}
          </div>
        </div>

        {/* Search Input Box */}
        <div className="flex items-center gap-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-zinc-500 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleNexarSearch()}
              placeholder="Search components or documents (e.g. ESP32, STM32F405, MPU6050, 3.3V LDO, resistor)..."
              className="w-full bg-zinc-950 border border-zinc-800 rounded-lg pl-9 pr-4 py-2 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-indigo-500 transition"
            />
          </div>
          <button
            onClick={() => handleNexarSearch()}
            disabled={isSearchingNexar || !searchQuery.trim()}
            className="px-4 py-2 text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white rounded-lg transition flex items-center gap-1.5 shrink-0 shadow-sm"
          >
            {isSearchingNexar ? (
              <>
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                <span>Searching Nexar...</span>
              </>
            ) : (
              <>
                <Zap className="w-3.5 h-3.5" />
                <span>Search Nexar</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Action Notification Alert */}
      {actionNotice && (
        <div
          className={`p-3 rounded-lg border text-xs flex items-center justify-between ${
            actionNotice.type === "success"
              ? "bg-emerald-950/60 border-emerald-800 text-emerald-300"
              : actionNotice.type === "error"
              ? "bg-rose-950/60 border-rose-800 text-rose-300"
              : "bg-blue-950/60 border-blue-800 text-blue-300"
          }`}
        >
          <span>{actionNotice.message}</span>
          <button onClick={() => setActionNotice(null)} className="text-zinc-400 hover:text-zinc-200 text-sm ml-2">
            ✕
          </button>
        </div>
      )}

      {/* SECTION 1: OCTOPART / NEXAR COMPONENT SEARCH RESULTS */}
      {nexarResults.length > 0 && (
        <div className="flex flex-col gap-3 border border-emerald-900/50 bg-emerald-950/20 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-emerald-400 font-semibold text-sm">
              <Zap className="w-4 h-4" />
              <span>Octopart / Nexar Component Intelligence Results ({nexarResults.length})</span>
            </div>
            <button
              onClick={() => setNexarResults([])}
              className="text-xs text-zinc-400 hover:text-zinc-200"
            >
              Clear Results
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {nexarResults.map((comp, idx) => {
              const mpn = comp.manufacturer_part_number || comp.mpn || "Unknown Part";
              const mfr = comp.manufacturer || "Generic";
              const pkg = comp.physical?.package || "Standard";
              const price = comp.pricing?.unit_price ? `INR ${comp.pricing.unit_price.toFixed(2)}` : "Price on Request";
              const stock = comp.availability?.stock !== undefined ? comp.availability.stock : 0;
              const inStock = comp.availability?.in_stock ?? stock > 0;
              const dsUrl = comp.datasheet?.url;

              return (
                <div
                  key={`${mpn}-${idx}`}
                  className="bg-zinc-950 border border-zinc-800 hover:border-zinc-700 rounded-lg p-3.5 flex flex-col justify-between gap-3 text-zinc-200 transition"
                >
                  <div className="flex flex-col gap-1.5">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <span className="text-[10px] uppercase font-bold tracking-wider text-emerald-400 font-mono">
                          {mfr}
                        </span>
                        <h4 className="text-sm font-bold text-zinc-100 font-mono">{mpn}</h4>
                      </div>
                      <span
                        className={`text-[10px] font-mono px-2 py-0.5 rounded border ${
                          inStock
                            ? "bg-emerald-950/80 text-emerald-300 border-emerald-800"
                            : "bg-amber-950/80 text-amber-300 border-amber-800"
                        }`}
                      >
                        {inStock ? `${stock.toLocaleString()} in stock` : "Check Lead Time"}
                      </span>
                    </div>

                    <p className="text-xs text-zinc-400 line-clamp-2">{comp.description || comp.product_name || "Parametric electronic component"}</p>

                    <div className="flex flex-wrap items-center gap-1.5 mt-1 text-[11px] font-mono text-zinc-400">
                      <span className="px-1.5 py-0.5 bg-zinc-900 border border-zinc-800 rounded">{pkg}</span>
                      {comp.category && <span className="px-1.5 py-0.5 bg-zinc-900 border border-zinc-800 rounded">{comp.category}</span>}
                      <span className="px-1.5 py-0.5 bg-zinc-900 border border-zinc-800 text-emerald-300 font-semibold rounded">
                        {price}
                      </span>
                    </div>
                  </div>

                  {/* Actions Toolbar */}
                  <div className="flex items-center gap-1.5 pt-2 border-t border-zinc-850 flex-wrap">
                    <button
                      onClick={() => setSelectedDetails(comp)}
                      className="px-2.5 py-1 text-[11px] font-medium bg-zinc-800 hover:bg-zinc-700 text-zinc-200 rounded transition"
                    >
                      View Details
                    </button>

                    {dsUrl && (
                      <a
                        href={dsUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-2.5 py-1 text-[11px] font-medium bg-indigo-950/60 hover:bg-indigo-900/80 border border-indigo-800/80 text-indigo-300 rounded flex items-center gap-1 transition"
                      >
                        <span>Datasheet</span>
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    )}

                    <button
                      onClick={() => handleSaveToKnowledge(comp)}
                      title="Index into SurrealDB and Knowledge Base"
                      className="px-2.5 py-1 text-[11px] font-medium bg-emerald-950/80 hover:bg-emerald-900 border border-emerald-800 text-emerald-300 rounded flex items-center gap-1 transition"
                    >
                      <BookmarkPlus className="w-3 h-3" />
                      <span>Save to Knowledge Base</span>
                    </button>

                    <button
                      onClick={() => handleAddToBom(comp)}
                      title="Add component to active Project BOM"
                      className="px-2.5 py-1 text-[11px] font-semibold bg-indigo-600 hover:bg-indigo-500 text-white rounded flex items-center gap-1 transition ml-auto shadow-sm"
                    >
                      <PlusCircle className="w-3 h-3" />
                      <span>Add to BOM</span>
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* SECTION 2: INDEXED DOCUMENTS LIST */}
      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between text-xs text-zinc-400 font-medium px-1">
          <span>INDEXED DOCUMENTS ({filteredLocalDocs.length})</span>
          <span className="font-mono text-[10px]">Filter: {filterSource}</span>
        </div>

        {filteredLocalDocs.length === 0 ? (
          <div className="bg-zinc-950/60 border border-zinc-800 rounded-lg p-8 text-center">
            <FileText className="w-8 h-8 text-zinc-600 mx-auto mb-2" />
            <p className="text-xs text-zinc-400">No documents indexed in this view.</p>
            <p className="text-[10px] text-zinc-500 mt-1">
              Search for components using <span className="text-emerald-400 font-semibold">Octopart / Nexar</span> or ingest local technical specifications.
            </p>
          </div>
        ) : (
          filteredLocalDocs.map((doc) => {
            const isSelected = doc.documentId === selectedDocId;
            const isNexarDoc = doc.sourceType === "OCTOPART_NEXAR";
            const mpn = doc.metadata?.mpn;
            const dsUrl = doc.metadata?.datasheet_url;

            return (
              <div
                key={doc.documentId}
                onClick={() => onSelectDocument && onSelectDocument(doc.documentId)}
                className={`p-3.5 rounded-lg border transition cursor-pointer flex items-center justify-between gap-3 ${
                  isSelected
                    ? "bg-indigo-950/40 border-indigo-500/80 text-zinc-100"
                    : "bg-zinc-950/60 border-zinc-800 hover:border-zinc-700 text-zinc-300"
                }`}
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`p-2.5 rounded border ${
                      isNexarDoc
                        ? "bg-emerald-950/60 border-emerald-800 text-emerald-400"
                        : "bg-zinc-900 border-zinc-800 text-indigo-400"
                    }`}
                  >
                    {isNexarDoc ? <Zap className="w-4 h-4" /> : <FileText className="w-4 h-4" />}
                  </div>
                  <div className="flex flex-col">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-semibold text-zinc-100">{doc.title}</span>
                      <span
                        className={`px-1.5 py-0.5 rounded text-[10px] font-mono border ${
                          isNexarDoc
                            ? "bg-emerald-950/80 text-emerald-300 border-emerald-800"
                            : "bg-zinc-800 text-zinc-400 border-zinc-700"
                        }`}
                      >
                        {doc.sourceType}
                      </span>
                    </div>
                    <span className="text-xs text-zinc-500 font-mono mt-0.5">
                      {doc.documentId} • {doc.filename} • {doc.sectionsCount} sections
                      {mpn && ` • MPN: ${mpn}`}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {dsUrl && (
                    <a
                      href={dsUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      onClick={(e) => e.stopPropagation()}
                      title="Open Verified Datasheet"
                      className="p-1.5 text-indigo-400 hover:text-indigo-200 border border-zinc-800 rounded hover:bg-zinc-800 transition"
                    >
                      <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                  )}

                  <span
                    className={`flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-mono border ${
                      doc.status === "INDEXED"
                        ? "bg-emerald-950/60 text-emerald-300 border-emerald-800"
                        : "bg-amber-950/60 text-amber-300 border-amber-800"
                    }`}
                  >
                    <CheckCircle2 className="w-3 h-3" />
                    {doc.status}
                  </span>

                  {onReindex && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onReindex(doc.documentId);
                      }}
                      title="Reindex Document"
                      className="p-1.5 text-zinc-400 hover:text-zinc-200 border border-zinc-800 rounded hover:bg-zinc-800 transition"
                    >
                      <RefreshCw className="w-3.5 h-3.5" />
                    </button>
                  )}

                  {onDelete && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onDelete(doc.documentId);
                      }}
                      title="Delete Document"
                      className="p-1.5 text-rose-400 hover:text-rose-200 border border-zinc-800 rounded hover:bg-rose-950/60 transition"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* COMPONENT DETAILS MODAL */}
      {selectedDetails && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl max-w-lg w-full p-5 flex flex-col gap-4 text-zinc-100 shadow-xl">
            <div className="flex items-start justify-between border-b border-zinc-800 pb-3">
              <div>
                <span className="text-[10px] uppercase font-bold tracking-wider text-emerald-400 font-mono">
                  {selectedDetails.manufacturer}
                </span>
                <h3 className="text-base font-bold font-mono">
                  {selectedDetails.manufacturer_part_number || selectedDetails.mpn}
                </h3>
              </div>
              <button
                onClick={() => setSelectedDetails(null)}
                className="text-zinc-400 hover:text-zinc-200 text-lg font-bold"
              >
                ✕
              </button>
            </div>

            <div className="text-xs space-y-2.5 max-h-80 overflow-y-auto pr-1">
              <p className="text-zinc-300">{selectedDetails.description || selectedDetails.product_name}</p>

              <div className="bg-zinc-950 p-3 rounded-lg border border-zinc-800 space-y-1.5 font-mono text-[11px]">
                <div className="flex justify-between">
                  <span className="text-zinc-500">Package:</span>
                  <span className="text-zinc-200">{selectedDetails.physical?.package || "N/A"}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-zinc-500">Nominal Voltage:</span>
                  <span className="text-zinc-200">{selectedDetails.electrical?.nominal_voltage ?? "N/A"} V</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-zinc-500">Max Current:</span>
                  <span className="text-zinc-200">{selectedDetails.electrical?.current_max ?? "N/A"} A</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-zinc-500">Global Stock:</span>
                  <span className="text-emerald-400 font-semibold">
                    {selectedDetails.availability?.stock?.toLocaleString() || 0} units
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-zinc-500">Unit Price:</span>
                  <span className="text-zinc-200">
                    {selectedDetails.pricing?.currency || "INR"} {selectedDetails.pricing?.unit_price?.toFixed(2) || "N/A"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-zinc-500">Source:</span>
                  <span className="text-emerald-400">Nexar / Octopart MCP</span>
                </div>
              </div>

              {selectedDetails.datasheet?.url && (
                <div className="p-2.5 rounded bg-indigo-950/40 border border-indigo-800/60 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <FileText className="w-4 h-4 text-indigo-400" />
                    <span className="text-xs text-indigo-200 font-medium">Manufacturer Datasheet</span>
                  </div>
                  <a
                    href={selectedDetails.datasheet.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-indigo-300 hover:underline flex items-center gap-1 font-mono"
                  >
                    Open PDF <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              )}
            </div>

            <div className="flex items-center justify-end gap-2 pt-3 border-t border-zinc-800">
              <button
                onClick={() => {
                  handleSaveToKnowledge(selectedDetails);
                  setSelectedDetails(null);
                }}
                className="px-3 py-1.5 text-xs font-semibold bg-emerald-950/80 hover:bg-emerald-900 border border-emerald-800 text-emerald-300 rounded-lg transition"
              >
                Save to Knowledge Base
              </button>
              <button
                onClick={() => {
                  handleAddToBom(selectedDetails);
                  setSelectedDetails(null);
                }}
                className="px-3 py-1.5 text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition shadow-sm"
              >
                Add to BOM
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
