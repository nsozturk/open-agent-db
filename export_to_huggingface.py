#!/usr/bin/env python3
"""
Hugging Face Dataset Publisher for Open-Agent-DB
Exports SQLite database records and vector datasets to Hugging Face Datasets.
"""

import os
import sys
import json
import sqlite3
import argparse
from datetime import datetime
from huggingface_hub import HfApi, login

DEFAULT_REPO_ID = "ns0bj/open-agent-db"
DEFAULT_DB_PATH = "data/github_universal_assets.db"

def get_hf_token() -> str:
    # 1. Environment variable
    token = os.environ.get("HF_TOKEN")
    if token:
        return token
    # 2. Hugging Face local cache token
    token_file = os.path.expanduser("~/.cache/huggingface/token")
    if os.path.exists(token_file):
        with open(token_file, "r") as f:
            token = f.read().strip()
            if token:
                return token
    return ""

def export_metadata_jsonl(db_path: str, output_jsonl: str, limit: int = None):
    """Exports assets table (metadata without huge raw BLOBs) to JSONL for Hugging Face."""
    print(f"[*] Connecting to {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    query = """
    SELECT id, ecosystem, asset_kind, file_format, name, description, author, 
           stars, forks, github_url, raw_url, branch, source_path, crawled_at, parsed_metadata_json
    FROM assets
    """
    if limit:
        query += f" LIMIT {limit}"
        
    cursor.execute(query)
    count = 0
    os.makedirs(os.path.dirname(os.path.abspath(output_jsonl)), exist_ok=True)
    
    print(f"[*] Exporting to {output_jsonl}...")
    with open(output_jsonl, "w", encoding="utf-8") as out:
        for row in cursor:
            record = {
                "id": row[0],
                "ecosystem": row[1],
                "asset_kind": row[2],
                "file_format": row[3],
                "name": row[4],
                "description": row[5],
                "author": row[6],
                "stars": row[7],
                "forks": row[8],
                "github_url": row[9],
                "raw_url": row[10],
                "branch": row[11],
                "source_path": row[12],
                "crawled_at": row[13],
                "metadata": json.loads(row[14]) if row[14] else {}
            }
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1
            if count % 100000 == 0:
                print(f"    Exported {count:,} records...")
                
    conn.close()
    print(f"[✓] Exported {count:,} records to {output_jsonl}")

def export_vectors(db_path: str, output_parquet: str, limit: int = 50000, dimensions: int = 128):
    """Generates dense vector embeddings and exports to Parquet for Hugging Face."""
    from cli.vector_engine import build_vector_dataset_from_sqlite
    print(f"[*] Building vector index from {db_path} (limit={limit}, dims={dimensions})...")
    build_vector_dataset_from_sqlite(db_path, output_parquet, limit=limit, dimensions=dimensions)

def upload_dataset(repo_id: str, file_path: str, token: str = None, private: bool = False):
    """Uploads exported file to Hugging Face Dataset repository."""
    hf_token = token or get_hf_token()
    if not hf_token:
        print("[!] Error: No Hugging Face token found. Run 'hf auth login' or provide --token.")
        sys.exit(1)
        
    api = HfApi(token=hf_token)
    user = api.whoami()
    print(f"[*] Authenticated as HF User: @{user['name']}")
    
    print(f"[*] Ensuring dataset repository exists: {repo_id}...")
    api.create_repo(repo_id=repo_id, repo_type="dataset", exist_ok=True, private=private)
    
    filename = os.path.basename(file_path)
    print(f"[*] Uploading {file_path} to {repo_id}/{filename}...")
    api.upload_file(
        path_or_fileobj=file_path,
        path_in_repo=filename,
        repo_id=repo_id,
        repo_type="dataset"
    )
    print(f"[✓] Successfully uploaded to: https://huggingface.co/datasets/{repo_id}")

def main():
    parser = argparse.ArgumentParser(description="Export and publish Open-Agent-DB Assets & Vectors to Hugging Face Datasets")
    parser.add_argument("--db", default=DEFAULT_DB_PATH, help=f"Path to SQLite database (default: {DEFAULT_DB_PATH})")
    parser.add_argument("--out", default="data/open_agent_db_metadata.jsonl", help="Output JSONL path")
    parser.add_argument("--vectors", action="store_true", help="Generate and upload Vector DB (Parquet with dense embeddings)")
    parser.add_argument("--vector-out", default="data/open_agent_db_vectors.parquet", help="Output Vector Parquet path")
    parser.add_argument("--vector-limit", type=int, default=50000, help="Number of records to vectorize (default: 50,000)")
    parser.add_argument("--repo-id", default=DEFAULT_REPO_ID, help=f"Hugging Face dataset repo id (default: {DEFAULT_REPO_ID})")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of rows to export for JSONL")
    parser.add_argument("--export-only", action="store_true", help="Only export, do not upload")
    parser.add_argument("--upload-only", action="store_true", help="Skip export, upload existing output file directly")
    parser.add_argument("--upload-file", help="Directly upload a specific file (e.g. SQLite database or archive) to dataset repo")
    parser.add_argument("--private", action="store_true", help="Create dataset as private")
    args = parser.parse_args()

    if args.upload_file:
        upload_dataset(args.repo_id, args.upload_file, private=args.private)
        return

    target_file = args.vector_out if args.vectors else args.out

    if not args.upload_only:
        if args.vectors:
            export_vectors(args.db, args.vector_out, limit=args.vector_limit)
        else:
            export_metadata_jsonl(args.db, args.out, limit=args.limit)

    if not args.export_only:
        upload_dataset(args.repo_id, target_file, private=args.private)

if __name__ == "__main__":
    main()
