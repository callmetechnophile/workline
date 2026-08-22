/**
 * Cached embedding generation service.
 */

import { knowledgeCache } from "../cache/cache";
import { CacheKeyGenerator } from "../cache/keys";
import { CacheObjectType } from "../cache/metadata";

export class CachedEmbeddingService {
  private defaultModel: string;
  private defaultDimension: number;

  constructor(defaultModel: string = "text-embedding-3-small", defaultDimension: number = 384) {
    this.defaultModel = defaultModel;
    this.defaultDimension = defaultDimension;
  }

  public async getEmbedding(
    text: string,
    projectId: string,
    model?: string,
    dimension?: number
  ): Promise<number[]> {
    const selectedModel = model ?? this.defaultModel;
    const selectedDim = dimension ?? this.defaultDimension;
    const contentHash = CacheKeyGenerator.hash(text);

    const cacheKey = CacheKeyGenerator.generateEmbeddingKey(
      contentHash,
      selectedModel,
      "v1",
      selectedDim
    );

    // 1. Check cache
    const cached = await knowledgeCache.get<number[]>(cacheKey, CacheObjectType.EMBEDDING);
    if (cached) {
      return cached;
    }

    // 2. Generate embedding (deterministic pseudo-embedding for testing/runtime)
    const embedding = this.generateDeterministicVector(text, selectedDim);

    // 3. Cache result
    await knowledgeCache.set(
      cacheKey,
      embedding,
      CacheObjectType.EMBEDDING,
      {
        projectId,
        sourceHash: contentHash,
        model: selectedModel,
        embeddingDimension: selectedDim,
      }
    );

    return embedding;
  }

  private generateDeterministicVector(text: string, dim: number): number[] {
    const vec: number[] = [];
    let seed = 0;
    for (let i = 0; i < text.length; i++) {
      seed = (seed * 31 + text.charCodeAt(i)) & 0xffffffff;
    }
    for (let i = 0; i < dim; i++) {
      seed = (seed * 1664525 + 1013904223) & 0xffffffff;
      vec.push((seed / 0xffffffff) * 2 - 1);
    }
    // L2 Normalize
    const norm = Math.sqrt(vec.reduce((acc, v) => acc + v * v, 0)) || 1.0;
    return vec.map((v) => v / norm);
  }
}
