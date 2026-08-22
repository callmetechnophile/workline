/**
 * Docling text normalization utilities.
 */

export class DoclingNormalization {
  public static cleanText(text: string): string {
    return text
      .replace(/\r\n/g, "\n")
      .replace(/\t/g, " ")
      .replace(/[ \u00A0]+/g, " ")
      .trim();
  }
}
