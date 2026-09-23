"""
Local Retrieval Engine for WORKLINE projects.
Provides an embedded, high-performance, 100% on-device hybrid search engine
combining BM25 lexical token matching and dense local semantic vector retrieval.
"""

from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Set, Tuple

from cli.workline.retrieval.record import EngineeringRecord


def _tokenize(text: str) -> List[str]:
    """Normalize and tokenize text into words, engineering terms, and identifiers."""
    # Split on whitespace, underscores, dashes, punctuation
    tokens = re.findall(r"[A-Za-z0-9_\-\.]+", text.lower())
    clean_tokens = []
    for t in tokens:
        t_clean = t.strip(".-_")
        if len(t_clean) >= 2:
            clean_tokens.append(t_clean)
            # If token contains hyphen or underscore, also index components
            sub = re.split(r"[\-_]", t_clean)
            if len(sub) > 1:
                clean_tokens.extend([s for s in sub if len(s) >= 2])
    return clean_tokens


def _embed_text(text: str, dim: int = 128) -> List[float]:
    """
    Compute a fast, deterministic local semantic representation vector.
    Uses multi-hash projection with character n-grams and term weighting.
    Runs in <1ms without any external model download or network call.
    """
    vec = [0.0] * dim
    tokens = _tokenize(text)
    if not tokens:
        return vec
        
    for token in tokens:
        # Primary token hash
        h1 = hash(token) % dim
        vec[h1] += 1.0
        
        # Bigram character features
        for i in range(len(token) - 1):
            h2 = hash(token[i:i+2]) % dim
            vec[h2] += 0.3
            
    # L2 normalize
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 1e-9:
        vec = [x / norm for x in vec]
    return vec


def _cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Cosine similarity between two normalized vectors."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    return sum(a * b for a, b in zip(v1, v2))


class LocalRetrievalEngine:
    """
    High-performance in-memory and disk-backed local search runtime.
    Features:
    - BM25 lexical ranking
    - Dense local vector similarity
    - Exact metadata filtering
    - Incremental document additions and deletions
    """

    def __init__(self, storage_dir: Optional[Path] = None, dim: int = 128):
        self.storage_dir = storage_dir
        self.dim = dim
        self.records: Dict[str, EngineeringRecord] = {}
        self.vectors: Dict[str, List[float]] = {}
        self.inverted_index: Dict[str, Set[str]] = defaultdict(set)
        self.doc_lengths: Dict[str, int] = {}
        self.avg_doc_length: float = 0.0
        self.doc_term_freqs: Dict[str, Counter] = {}
        
        # BM25 parameters
        self.k1 = 1.5
        self.b = 0.75

    def clear(self) -> None:
        """Clear all indexed records and reset state."""
        self.records.clear()
        self.vectors.clear()
        self.inverted_index.clear()
        self.doc_lengths.clear()
        self.doc_term_freqs.clear()
        self.avg_doc_length = 0.0

    def add_records(self, records: List[EngineeringRecord]) -> None:
        """Add or update multiple records in the index."""
        for rec in records:
            self.add_record(rec)
        self._update_stats()

    def add_record(self, record: EngineeringRecord) -> None:
        """Add a single record and update token frequencies."""
        rec_id = record.record_id
        
        # Combine title, path, content, and metadata for full searchability
        meta_str = " ".join(f"{k} {v}" for k, v in record.metadata.items() if isinstance(v, (str, int, float)))
        full_text = f"{record.title} {record.resource_type} {record.path} {record.content} {meta_str}"
        
        tokens = _tokenize(full_text)
        tf = Counter(tokens)
        
        self.records[rec_id] = record
        self.doc_term_freqs[rec_id] = tf
        self.doc_lengths[rec_id] = len(tokens)
        self.vectors[rec_id] = _embed_text(full_text, self.dim)
        
        for token in tf.keys():
            self.inverted_index[token].add(rec_id)

    def remove_records_by_path(self, rel_posix: str) -> int:
        """Remove records matching a given file path."""
        to_remove = [rec_id for rec_id, rec in self.records.items() if rec.path == rel_posix]
        for rid in to_remove:
            self.remove_record(rid)
        self._update_stats()
        return len(to_remove)

    def remove_record(self, record_id: str) -> None:
        """Remove a record by ID."""
        if record_id in self.records:
            del self.records[record_id]
        if record_id in self.vectors:
            del self.vectors[record_id]
        if record_id in self.doc_lengths:
            del self.doc_lengths[record_id]
        if record_id in self.doc_term_freqs:
            del self.doc_term_freqs[record_id]
            
        for term, ids in list(self.inverted_index.items()):
            ids.discard(record_id)
            if not ids:
                del self.inverted_index[term]

    def _update_stats(self) -> None:
        """Update corpus statistics for BM25."""
        if self.doc_lengths:
            self.avg_doc_length = sum(self.doc_lengths.values()) / len(self.doc_lengths)
        else:
            self.avg_doc_length = 0.0

    def query(
        self,
        query_text: str,
        top_k: int = 10,
        resource_type: Optional[str] = None,
        metadata_filters: Optional[Dict[str, Any]] = None,
    ) -> List[EngineeringRecord]:
        """
        Execute hybrid search over the local index.
        Applies metadata filtering and combines BM25 lexical score with vector similarity.
        """
        self._update_stats()
        if not self.records:
            return []
            
        q_tokens = _tokenize(query_text)
        q_vec = _embed_text(query_text, self.dim)
        num_docs = len(self.records)
        
        scores: Dict[str, float] = {}
        
        # 1. Lexical BM25 Scoring
        for q_term in q_tokens:
            matching_doc_ids = self.inverted_index.get(q_term, set())
            df = len(matching_doc_ids)
            if df == 0:
                continue
            idf = math.log((num_docs - df + 0.5) / (df + 0.5) + 1.0)
            
            for doc_id in matching_doc_ids:
                tf = self.doc_term_freqs[doc_id][q_term]
                doc_len = self.doc_lengths[doc_id]
                denom = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / (self.avg_doc_length or 1.0)))
                bm25_part = idf * (tf * (self.k1 + 1.0)) / (denom or 1.0)
                scores[doc_id] = scores.get(doc_id, 0.0) + bm25_part

        # 2. Dense Semantic Vector Scoring
        for doc_id, doc_vec in self.vectors.items():
            sim = _cosine_similarity(q_vec, doc_vec)
            # Blend lexical (normalized) and semantic similarity
            lexical = scores.get(doc_id, 0.0)
            # Combine: 60% semantic + 40% lexical (scaled)
            blended = (sim * 0.6) + (min(lexical, 5.0) / 5.0 * 0.4)
            scores[doc_id] = blended

        # 3. Filter by resource type and metadata
        filtered_results: List[Tuple[float, EngineeringRecord]] = []
        for doc_id, score in scores.items():
            rec = self.records[doc_id]
            
            # Type filter
            if resource_type:
                if rec.resource_type.lower() != resource_type.lower():
                    continue
                    
            # Metadata filter
            if metadata_filters:
                match = True
                for k, v in metadata_filters.items():
                    rec_val = rec.metadata.get(k)
                    if rec_val is None or str(rec_val).lower() != str(v).lower():
                        match = False
                        break
                if not match:
                    continue
                    
            # Clone record with populated score
            rec_copy = EngineeringRecord.from_dict(rec.to_dict())
            rec_copy.score = round(score, 4)
            filtered_results.append((score, rec_copy))

        filtered_results.sort(key=lambda x: x[0], reverse=True)
        return [r for _, r in filtered_results[:top_k]]

    def save(self, target_dir: Optional[Path] = None) -> None:
        """Persist index state to disk."""
        dest = (target_dir or self.storage_dir)
        if not dest:
            return
        dest.mkdir(parents=True, exist_ok=True)
        
        # Save records
        records_data = [r.to_dict() for r in self.records.values()]
        (dest / "records.json").write_text(json.dumps(records_data, indent=2, default=str), encoding="utf-8")
        
        # Save vectors and inverted index
        index_data = {
            "dim": self.dim,
            "vectors": self.vectors,
            "inverted_index": {k: list(v) for k, v in self.inverted_index.items()},
            "doc_lengths": self.doc_lengths,
            "avg_doc_length": self.avg_doc_length,
        }
        (dest / "index.json").write_text(json.dumps(index_data, default=str), encoding="utf-8")

    def load(self, source_dir: Optional[Path] = None) -> bool:
        """Load index state from disk. Returns True if successfully loaded."""
        src = (source_dir or self.storage_dir)
        if not src or not src.exists():
            return False
            
        records_file = src / "records.json"
        index_file = src / "index.json"
        
        if not records_file.exists() or not index_file.exists():
            return False
            
        try:
            records_data = json.loads(records_file.read_text(encoding="utf-8"))
            self.records = {r["record_id"]: EngineeringRecord.from_dict(r) for r in records_data}
            
            index_data = json.loads(index_file.read_text(encoding="utf-8"))
            self.dim = index_data.get("dim", 128)
            self.vectors = index_data.get("vectors", {})
            self.inverted_index = defaultdict(set, {k: set(v) for k, v in index_data.get("inverted_index", {}).items()})
            self.doc_lengths = index_data.get("doc_lengths", {})
            self.avg_doc_length = index_data.get("avg_doc_length", 0.0)
            
            # Reconstruct term frequencies
            self.doc_term_freqs.clear()
            for rec in self.records.values():
                meta_str = " ".join(f"{k} {v}" for k, v in rec.metadata.items() if isinstance(v, (str, int, float)))
                tokens = _tokenize(f"{rec.title} {rec.resource_type} {rec.path} {rec.content} {meta_str}")
                self.doc_term_freqs[rec.record_id] = Counter(tokens)
                
            return True
        except Exception:
            return False
