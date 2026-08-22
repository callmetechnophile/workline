/**
 * spaCy enrichment schemas.
 */

export interface SentenceSpan {
  text: string;
  startOffset: number;
  endOffset: number;
  pageNumber: number;
  sectionId: string;
}

export interface LinguisticAnnotation {
  sentences: SentenceSpan[];
  nounPhrases: string[];
  tokensCount: number;
}
