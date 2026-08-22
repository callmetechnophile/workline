/**
 * spaCy NLP linguistic enrichment, sentence segmenter, and engineering NER.
 */

import { SectionElement, StructuredDocument } from "../docling/schemas";
import { EngineeringEntity, EngineeringEntityType } from "../entities/engineering-entities";
import { EntityNormalizer } from "../entities/entity-normalizer";
import { LinguisticAnnotation, SentenceSpan } from "./schemas";

export class SpacyClient {
  public enrich(document: StructuredDocument): {
    linguistics: LinguisticAnnotation;
    entities: EngineeringEntity[];
  } {
    const sentences: SentenceSpan[] = [];
    const entities: EngineeringEntity[] = [];
    let entityCounter = 1;

    for (const section of document.sections) {
      for (const p of section.paragraphs) {
        // Sentence segmentation
        const rawSents = p.split(/(?<=[.?!])\s+/);
        let offset = 0;

        for (const s of rawSents) {
          sentences.push({
            text: s,
            startOffset: offset,
            endOffset: offset + s.length,
            pageNumber: section.pageNumber,
            sectionId: section.sectionId,
          });
          offset += s.length + 1;

          // Detect Voltage patterns (e.g. 3.3V, 5V, 12V, 3V3)
          const vMatches = s.matchAll(/\b(\d+(?:\.\d+)?\s*(?:V|mV|kV)|\d+V\d+)\b/gi);
          for (const m of vMatches) {
            const raw = m[0];
            const norm = EntityNormalizer.normalizeVoltage(raw);
            entities.push({
              entityId: `${document.documentId}_ent_${entityCounter++}`,
              projectId: document.projectId,
              documentId: document.documentId,
              entityType: EngineeringEntityType.VOLTAGE,
              originalText: raw,
              normalizedValue: norm.normalized,
              unit: norm.unit,
              pageNumber: section.pageNumber,
              section: section.heading,
              confidence: 0.95,
              sourceSpan: s,
              createdAt: Date.now(),
            });
          }

          // Detect Current patterns (e.g. 3A, 500mA, 2.5 A)
          const cMatches = s.matchAll(/\b(\d+(?:\.\d+)?\s*(?:A|mA|uA|µA))\b/gi);
          for (const m of cMatches) {
            const raw = m[0];
            const norm = EntityNormalizer.normalizeCurrent(raw);
            entities.push({
              entityId: `${document.documentId}_ent_${entityCounter++}`,
              projectId: document.projectId,
              documentId: document.documentId,
              entityType: EngineeringEntityType.CURRENT,
              originalText: raw,
              normalizedValue: norm.normalized,
              unit: norm.unit,
              pageNumber: section.pageNumber,
              section: section.heading,
              confidence: 0.92,
              sourceSpan: s,
              createdAt: Date.now(),
            });
          }

          // Detect IC / Part Number components (e.g. TPS62130, STM32F401, LM2596)
          const icMatches = s.matchAll(/\b([A-Z]{2,}[0-9]+[A-Z0-9_-]*)\b/g);
          for (const m of icMatches) {
            const raw = m[0];
            entities.push({
              entityId: `${document.documentId}_ent_${entityCounter++}`,
              projectId: document.projectId,
              documentId: document.documentId,
              entityType: EngineeringEntityType.COMPONENT,
              originalText: raw,
              normalizedValue: raw.toUpperCase(),
              pageNumber: section.pageNumber,
              section: section.heading,
              confidence: 0.96,
              sourceSpan: s,
              createdAt: Date.now(),
            });
          }
        }
      }
    }

    return {
      linguistics: {
        sentences,
        nounPhrases: [],
        tokensCount: sentences.reduce((acc, s) => acc + s.text.split(" ").length, 0),
      },
      entities,
    };
  }
}

export const spacyClient = new SpacyClient();
