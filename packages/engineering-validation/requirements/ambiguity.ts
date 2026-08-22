/**
 * Detects qualitative and non-deterministic requirement terms.
 */

export class AmbiguityDetector {
  private static readonly VAGUE_TERMS = [
    "low power",
    "ultra low power",
    "compact",
    "small form factor",
    "fast",
    "high speed",
    "efficient",
    "cheap",
    "low cost",
    "heavy duty",
    "rugged",
    "lightweight",
  ];

  public static checkAmbiguity(text: string): { isAmbiguous: boolean; detectedTerms: string[] } {
    const lower = text.toLowerCase();
    const detected: string[] = [];

    for (const term of this.VAGUE_TERMS) {
      if (lower.includes(term)) {
        detected.push(term);
      }
    }

    return {
      isAmbiguous: detected.length > 0,
      detectedTerms: detected,
    };
  }
}
