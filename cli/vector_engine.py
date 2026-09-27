"""Vector & Semantic Search Engine for Open-Agent-DB
Enables neural and dense vector embeddings over Agent Skills, MCP Servers, and Directives.
Outputs Hugging Face-ready Parquet datasets with vector columns and provides sub-second semantic search.
"""

import os
import sys
import json
import sqlite3
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import TruncatedSVD
    from sklearn.preprocessing import normalize
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False


class VectorSearchEngine:
    """Local and Hugging Face compatible Vector Search Engine."""

    def __init__(self, n_dimensions: int = 128):
        self.n_dimensions = n_dimensions
        self.vectorizer = None
        self.reducer = None
        self.doc_vectors = None
        self.doc_metadata = []

    def fit_transform(self, corpus: List[str], metadata: List[Dict[str, Any]]) -> np.ndarray:
        """Computes dense normalized vector embeddings for a corpus of texts."""
        if not HAS_SKLEARN:
            raise RuntimeError("scikit-learn is required for local vector generation. Install with 'pip install scikit-learn'.")

        print(f"[*] Vectorizing {len(corpus):,} agent skills and directives...")
        # 1. High-ngram TF-IDF representation
        self.vectorizer = TfidfVectorizer(
            max_features=50000,
            ngram_range=(1, 2),
            stop_words="english",
            sublinear_tf=True
        )
        tfidf_matrix = self.vectorizer.fit_transform(corpus)

        # 2. Dimensionality reduction to dense semantic vector space (LSA)
        actual_dims = min(self.n_dimensions, tfidf_matrix.shape[1] - 1)
        self.reducer = TruncatedSVD(n_components=actual_dims, random_state=42)
        dense_vectors = self.reducer.fit_transform(tfidf_matrix)

        # 3. L2 unit normalization for exact cosine similarity via dot product
        self.doc_vectors = normalize(dense_vectors, norm="l2", axis=1).astype(np.float32)
        self.doc_metadata = metadata
        print(f"[✓] Generated dense vector matrix: shape {self.doc_vectors.shape} (dtype: float32)")
        return self.doc_vectors

    def query_vector(self, text: str) -> np.ndarray:
        """Transforms a natural language query into a unit-normalized vector."""
        if self.vectorizer is None or self.reducer is None:
            raise ValueError("Engine has not been fitted yet.")
        tfidf = self.vectorizer.transform([text])
        dense = self.reducer.transform(tfidf)
        return normalize(dense, norm="l2", axis=1).astype(np.float32)[0]

    def search(self, query: str, top_k: int = 10, min_score: float = 0.1) -> List[Dict[str, Any]]:
        """Performs semantic vector search using cosine similarity."""
        if self.doc_vectors is None or len(self.doc_metadata) == 0:
            return []

        q_vec = self.query_vector(query)
        # Cosine similarity is simply dot product on L2-normalized vectors
        scores = np.dot(self.doc_vectors, q_vec)

        # Top K indices
        if len(scores) <= top_k:
            top_indices = np.argsort(scores)[::-1]
        else:
            top_indices = np.argpartition(scores, -top_k)[-top_k:]
            top_indices = top_indices[np.argsort(scores[top_indices])[::-1]]

        results = []
        for idx in top_indices:
            score = float(scores[idx])
            if score < min_score:
                continue
            item = dict(self.doc_metadata[idx])
            item["similarity_score"] = round(score, 4)
            results.append(item)

        return results

    def export_parquet(self, output_path: str):
        """Exports metadata and vector embeddings to Parquet for Hugging Face Datasets."""
        if self.doc_vectors is None:
            raise ValueError("No vectors to export.")

        print(f"[*] Packaging vector dataset into Parquet format: {output_path}...")
        records = []
        for i, meta in enumerate(self.doc_metadata):
            rec = dict(meta)
            rec["embedding"] = self.doc_vectors[i].tolist()
            records.append(rec)

        df = pd.DataFrame(records)
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        df.to_parquet(output_path, engine="pyarrow", compression="snappy", index=False)
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"[✓] Exported {len(df):,} vector records to {output_path} ({size_mb:.2f} MB)")


def build_vector_dataset_from_sqlite(
    db_path: str,
    output_parquet: str = "data/open_agent_db_vectors.parquet",
    limit: Optional[int] = 50000,
    dimensions: int = 128
) -> VectorSearchEngine:
    """Builds a vector dataset from SQLite assets database and exports to Parquet."""
    print(f"[*] Loading assets from {db_path}...")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Determine table name (assets or skills)
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cur.fetchall()]

    corpus = []
    metadata = []

    if "assets" in tables:
        q = """
        SELECT id, ecosystem, asset_kind, name, description, author, stars, github_url, source_path
        FROM assets
        ORDER BY stars DESC
        """
        if limit:
            q += f" LIMIT {limit}"
        cur.execute(q)
        for r in cur:
            desc = r[4] or ""
            text = f"{r[3]} ({r[1]} {r[2]}): {desc}"
            corpus.append(text)
            metadata.append({
                "id": r[0],
                "ecosystem": r[1],
                "asset_kind": r[2],
                "name": r[3],
                "description": desc,
                "author": r[5] or "",
                "stars": r[6] or 0,
                "github_url": r[7] or "",
                "source_path": r[8] or ""
            })
    elif "skills" in tables:
        q = "SELECT id, name, description, author, stars, github_url FROM skills ORDER BY stars DESC"
        if limit:
            q += f" LIMIT {limit}"
        cur.execute(q)
        for r in cur:
            desc = r[2] or ""
            text = f"{r[1]}: {desc}"
            corpus.append(text)
            metadata.append({
                "id": r[0],
                "ecosystem": "universal",
                "asset_kind": "skill",
                "name": r[1],
                "description": desc,
                "author": r[3] or "",
                "stars": r[4] or 0,
                "github_url": r[5] or ""
            })
    else:
        conn.close()
        raise ValueError(f"No recognizable assets or skills table in {db_path}")

    conn.close()

    engine = VectorSearchEngine(n_dimensions=dimensions)
    engine.fit_transform(corpus, metadata)
    engine.export_parquet(output_parquet)
    return engine
