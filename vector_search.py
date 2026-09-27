#!/usr/bin/env python3
"""
Semantic Vector Search CLI for Open-Agent-DB
Perform natural language semantic searches across AI Agent Skills and MCP Servers.
"""

import os
import sys
import argparse
from pathlib import Path
from cli.vector_engine import VectorSearchEngine, build_vector_dataset_from_sqlite

DEFAULT_VECTOR_PATH = "data/open_agent_db_vectors.parquet"
DEFAULT_DB_PATH = "data/github_universal_assets.db"

def main():
    parser = argparse.ArgumentParser(description="Semantic Vector Search for Open-Agent-DB")
    parser.add_argument("query", nargs="?", default="", help="Natural language search query")
    parser.add_argument("--top-k", type=int, default=10, help="Number of results to return (default: 10)")
    parser.add_argument("--build", action="store_true", help="Build or rebuild the local vector index")
    parser.add_argument("--limit", type=int, default=25000, help="Maximum assets to index into vector space (default: 25,000)")
    parser.add_argument("--db", default=DEFAULT_DB_PATH, help="Path to SQLite database")
    parser.add_argument("--vectors", default=DEFAULT_VECTOR_PATH, help="Path to vectors parquet file")
    args = parser.parse_args()

    # Rebuild vector index if requested or if missing
    if args.build or not os.path.exists(args.vectors):
        print(f"[*] Initializing vector index ({args.limit:,} assets)...")
        engine = build_vector_dataset_from_sqlite(args.db, output_parquet=args.vectors, limit=args.limit)
    else:
        # Load from Parquet
        import pandas as pd
        import numpy as np
        print(f"[*] Loading pre-computed vectors from {args.vectors}...")
        df = pd.read_parquet(args.vectors)
        metadata = df.drop(columns=["embedding"]).to_dict(orient="records")
        vectors = np.array(df["embedding"].tolist(), dtype=np.float32)
        
        # Build engine from corpus
        corpus = [f"{m['name']} ({m.get('ecosystem', '')}): {m.get('description', '')}" for m in metadata]
        engine = VectorSearchEngine(n_dimensions=vectors.shape[1])
        engine.fit_transform(corpus, metadata)

    if not args.query:
        print("[!] No search query specified. Example: python3 vector_search.py 'postgres database backup'")
        sys.exit(0)

    print(f"\n🔍 Semantic Vector Search: \"{args.query}\"\n" + "=" * 65)
    results = engine.search(args.query, top_k=args.top_k)

    if not results:
        print("No matching assets found.")
        return

    for i, r in enumerate(results, 1):
        score = r.get("similarity_score", 0.0)
        eco = r.get("ecosystem", "universal")
        kind = r.get("asset_kind", "skill")
        name = r.get("name", "Unknown")
        stars = r.get("stars", 0)
        desc = r.get("description", "").strip().replace("\n", " ")
        if len(desc) > 90:
            desc = desc[:90] + "..."
        url = r.get("github_url", "")

        print(f"{i:2d}. [Score: {score:.3f}] {name}  ({eco} · {kind})  ⭐ {stars}")
        if desc:
            print(f"    {desc}")
        if url:
            print(f"    🔗 {url}")
        print()

if __name__ == "__main__":
    main()
