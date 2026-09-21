'use client';

import React, { useState } from 'react';
import { WorklineFileMap } from '@/lib/workline-filesystem/types';
import {
  X,
  FileCode,
  Folder,
  FolderOpen,
  Copy,
  Check,
  Download,
  Terminal,
  ChevronRight,
  ChevronDown,
} from 'lucide-react';

interface FilesystemViewerModalProps {
  isOpen: boolean;
  onClose: () => void;
  fileMap: WorklineFileMap;
  projectName: string;
}

export default function FilesystemViewerModal({
  isOpen,
  onClose,
  fileMap,
  projectName,
}: FilesystemViewerModalProps) {
  const filePaths = Object.keys(fileMap).sort();
  const [selectedFile, setSelectedFile] = useState<string>(filePaths[0] || 'README.wl');
  const [copied, setCopied] = useState(false);
  const [expandedFolders, setExpandedFolders] = useState<Record<string, boolean>>({
    '.wl': true,
    requirements: true,
    architecture: true,
    components: true,
    bom: true,
    research: true,
  });

  if (!isOpen) return null;

  const toggleFolder = (folder: string) => {
    setExpandedFolders((prev) => ({ ...prev, [folder]: !prev[folder] }));
  };

  const handleCopy = () => {
    const content = fileMap[selectedFile] || '';
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Group files by root directory
  const rootFiles: string[] = [];
  const directories: Record<string, string[]> = {};

  for (const path of filePaths) {
    if (path.includes('/')) {
      const topDir = path.split('/')[0];
      if (!directories[topDir]) directories[topDir] = [];
      directories[topDir].push(path);
    } else {
      rootFiles.push(path);
    }
  }

  const activeContent = fileMap[selectedFile] || '';
  const activeFileSize = activeContent ? (new Blob([activeContent]).size / 1024).toFixed(1) : '0';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="w-full max-w-6xl h-[85vh] bg-slate-900 border border-slate-800 rounded-xl shadow-2xl flex flex-col overflow-hidden">
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950/80">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-indigo-950/80 border border-indigo-700/50 rounded-lg text-indigo-400">
              <Terminal className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-bold text-slate-100">
                  WORKLINE Project Filesystem (.wl)
                </h3>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-indigo-950 text-indigo-300 border border-indigo-800">
                  v1.0 Standard
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono">
                {projectName} • {filePaths.length} Generated Files
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-100 hover:bg-slate-800 rounded-lg transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Main Body: Two-pane Explorer */}
        <div className="flex-1 flex overflow-hidden">
          {/* Left Pane: Filesystem Tree */}
          <div className="w-80 border-r border-slate-800 bg-slate-950/50 overflow-y-auto p-3 text-xs font-mono space-y-1 select-none">
            <div className="px-2 py-1 text-[10px] font-bold text-slate-500 uppercase tracking-wider">
              Project Root (/)
            </div>

            {/* Root files */}
            {rootFiles.map((file) => {
              const isSelected = selectedFile === file;
              return (
                <button
                  key={file}
                  onClick={() => setSelectedFile(file)}
                  className={`w-full flex items-center gap-2 px-2.5 py-1.5 rounded transition-colors text-left cursor-pointer ${
                    isSelected
                      ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30'
                      : 'text-slate-300 hover:bg-slate-800/60 hover:text-slate-100'
                  }`}
                >
                  <FileCode className={`w-3.5 h-3.5 flex-shrink-0 ${isSelected ? 'text-indigo-400' : 'text-slate-400'}`} />
                  <span className="truncate">{file}</span>
                </button>
              );
            })}

            {/* Subdirectories */}
            {Object.entries(directories).map(([dirName, files]) => {
              const isExpanded = expandedFolders[dirName] !== false;
              return (
                <div key={dirName} className="pt-1">
                  <button
                    onClick={() => toggleFolder(dirName)}
                    className="w-full flex items-center justify-between px-2 py-1.5 text-slate-400 hover:text-slate-200 hover:bg-slate-900 rounded cursor-pointer transition-colors"
                  >
                    <div className="flex items-center gap-1.5">
                      {isExpanded ? (
                        <FolderOpen className="w-3.5 h-3.5 text-indigo-400" />
                      ) : (
                        <Folder className="w-3.5 h-3.5 text-slate-500" />
                      )}
                      <span className="font-semibold text-slate-200">{dirName}/</span>
                    </div>
                    {isExpanded ? (
                      <ChevronDown className="w-3 h-3 text-slate-500" />
                    ) : (
                      <ChevronRight className="w-3 h-3 text-slate-500" />
                    )}
                  </button>

                  {isExpanded && (
                    <div className="pl-4 space-y-0.5 border-l border-slate-800/80 ml-2 mt-0.5">
                      {files.map((file) => {
                        const isSelected = selectedFile === file;
                        const shortName = file.replace(`${dirName}/`, '');
                        return (
                          <button
                            key={file}
                            onClick={() => setSelectedFile(file)}
                            className={`w-full flex items-center gap-2 px-2 py-1 rounded transition-colors text-left cursor-pointer ${
                              isSelected
                                ? 'bg-indigo-600/25 text-indigo-300 border border-indigo-500/30'
                                : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
                            }`}
                          >
                            <FileCode className={`w-3 h-3 flex-shrink-0 ${isSelected ? 'text-indigo-400' : 'text-slate-500'}`} />
                            <span className="truncate text-[11px]">{shortName}</span>
                          </button>
                        );
                      })}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Right Pane: Code / Content Viewer */}
          <div className="flex-1 flex flex-col bg-slate-900 overflow-hidden">
            {/* File toolbar */}
            <div className="flex items-center justify-between px-4 py-2.5 border-b border-slate-800 bg-slate-950/60">
              <div className="flex items-center gap-2 font-mono text-xs">
                <FileCode className="w-4 h-4 text-indigo-400" />
                <span className="font-semibold text-slate-200">{selectedFile}</span>
                <span className="text-[11px] text-slate-500">• {activeFileSize} KB</span>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={handleCopy}
                  className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-mono text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded transition-colors cursor-pointer"
                >
                  {copied ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-emerald-400" />
                      <span className="text-emerald-400">Copied</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5" />
                      <span>Copy</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* File Content Area */}
            <div className="flex-1 p-4 overflow-auto font-mono text-xs bg-slate-950 text-slate-200 leading-relaxed whitespace-pre selection:bg-indigo-600 selection:text-white">
              {activeContent}
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="flex items-center justify-between px-6 py-3 border-t border-slate-800 bg-slate-950/80 text-xs font-mono text-slate-400">
          <div>
            CLI Compatible: <code className="text-indigo-300">wg open ./{projectName.replace(/\s+/g, '-')}</code>
          </div>
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-xs font-semibold cursor-pointer"
          >
            Close Viewer
          </button>
        </div>
      </div>
    </div>
  );
}
