/**
 * Custom error types for the Knowledge Cache layer.
 */

export class CacheError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "CacheError";
  }
}

export class CacheSerializationError extends CacheError {
  constructor(message: string) {
    super(`Serialization failure: ${message}`);
    this.name = "CacheSerializationError";
  }
}

export class CacheIsolationError extends CacheError {
  constructor(message: string) {
    super(`Isolation violation: ${message}`);
    this.name = "CacheIsolationError";
  }
}
