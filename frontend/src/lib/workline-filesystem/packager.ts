/**
 * WORKLINE ZIP Packager & Extractor
 *
 * Handles self-contained .workline.zip generation, client-side downloading,
 * and zip file decompression.
 */

import JSZip from 'jszip';
import { WorklineFileMap } from './types';

/**
 * Sanitizes project name for filename use
 */
export function sanitizeFileName(name: string): string {
  return name
    .trim()
    .replace(/[<>:"/\\|?*\x00-\x1F]/g, '_')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .slice(0, 80);
}

/**
 * Packs a .wl filesystem into a downloadable .workline.zip archive
 */
export async function downloadWorklineZip(
  fileMap: WorklineFileMap,
  projectName: string = 'workline-project'
): Promise<{ filename: string; sizeBytes: number }> {
  const zip = new JSZip();

  // Add all files preserving relative path hierarchy
  for (const [filePath, content] of Object.entries(fileMap)) {
    zip.file(filePath, content);
  }

  // Generate binary blob
  const blob = await zip.generateAsync({
    type: 'blob',
    compression: 'DEFLATE',
    compressionOptions: { level: 6 },
  });

  const sanitized = sanitizeFileName(projectName || 'workline-project');
  const filename = `${sanitized}.workline.zip`;

  // Trigger browser download
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);

  setTimeout(() => URL.revokeObjectURL(url), 5000);

  return { filename, sizeBytes: blob.size };
}

/**
 * Decompresses an uploaded .workline.zip or .zip file into a WorklineFileMap
 */
export async function extractWorklineZip(file: File | Blob): Promise<WorklineFileMap> {
  const zip = new JSZip();
  const loadedZip = await zip.loadAsync(file);
  const fileMap: WorklineFileMap = {};

  const entries = Object.entries(loadedZip.files);
  for (const [relPath, zipEntry] of entries) {
    if (zipEntry.dir) continue;
    // Normalize path separators to forward slash
    const normalizedPath = relPath.replace(/\\/g, '/');

    // Strip top-level folder prefix if the zip was created with a parent folder (e.g., project-name/README.wl)
    let cleanPath = normalizedPath;
    const slashIdx = normalizedPath.indexOf('/');
    if (slashIdx !== -1) {
      const firstSegment = normalizedPath.slice(0, slashIdx);
      if (
        !firstSegment.startsWith('.') &&
        firstSegment !== 'requirements' &&
        firstSegment !== 'architecture' &&
        firstSegment !== 'components' &&
        firstSegment !== 'bom' &&
        firstSegment !== 'research' &&
        firstSegment !== 'documents' &&
        firstSegment !== 'analysis' &&
        firstSegment !== 'decisions' &&
        firstSegment !== 'tasks' &&
        firstSegment !== 'team' &&
        firstSegment !== 'agents' &&
        firstSegment !== 'history' &&
        firstSegment !== 'exports'
      ) {
        // It's an outer wrapper folder, strip it
        cleanPath = normalizedPath.slice(slashIdx + 1);
      }
    }

    try {
      const text = await zipEntry.async('text');
      fileMap[cleanPath] = text;
    } catch (err) {
      console.warn(`Could not read binary or encrypted entry: ${normalizedPath}`, err);
    }
  }

  return fileMap;
}
