#!/usr/bin/env python3
"""
Open-Agent-DB Monthly Sync & Automated Release Pipeline
Orchestrates:
1. Incremental delta crawl / MCP sync
2. Merge MCP registry into universal assets DB
3. Rebuilding dense vector embeddings Parquet dataset
4. Safe online SQLite snapshot & multi-core zstd compression
5. Automated upload to Hugging Face Datasets Hub (ns0bj/open-agent-db)
6. Updating dataset metrics & sync ledger
"""

import os
import sys
import time
import signal
import sqlite3
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"
SCRIPTS_DIR = BASE_DIR / "scripts"
ASSETS_DB = DATA_DIR / "github_universal_assets.db"
REGISTRY_DB = DATA_DIR / "universal_registry.db"
VECTOR_PARQUET = DATA_DIR / "open_agent_db_vectors.parquet"
SNAPSHOT_SQLITE = DATA_DIR / "open_agent_db_sql.sqlite"
SNAPSHOT_ZST = DATA_DIR / "open_agent_db_sql.sqlite.zst"

HF_REPO_ID = "ns0bj/open-agent-db"

def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{ts}] {msg}"
    print(formatted)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with open(LOG_DIR / "monthly_sync.log", "a", encoding="utf-8") as f:
        f.write(formatted + "\n")

def get_harvester_pid():
    pid_file = DATA_DIR / "github_universal_harvester.pid"
    if pid_file.exists():
        try:
            with open(pid_file) as f:
                pid = int(f.read().strip())
            os.kill(pid, 0)
            return pid
        except (ValueError, OSError):
            pass
    return None

def init_sync_ledger():
    conn = sqlite3.connect(str(ASSETS_DB))
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sync_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sync_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_assets INTEGER,
                mcp_servers INTEGER,
                vector_records INTEGER,
                duration_seconds REAL,
                status TEXT
            );
        """)
    conn.close()

def step1_merge_mcp():
    log("Step 1/5: Merging MCP Registry into Universal Assets DB...")
    merge_script = SCRIPTS_DIR / "merge_mcp_into_assets.py"
    res = subprocess.run([sys.executable, str(merge_script)], capture_output=True, text=True)
    if res.returncode != 0:
        log(f"[!] Warning: MCP merge returned error:\n{res.stderr}")
    else:
        log("[✓] MCP Registry merged successfully.")

def step2_export_vectors(limit=50000):
    log(f"Step 2/5: Updating Semantic Vector DB (Top {limit:,} records)...")
    from cli.vector_engine import build_vector_dataset_from_sqlite
    build_vector_dataset_from_sqlite(str(ASSETS_DB), str(VECTOR_PARQUET), limit=limit, dimensions=128)
    log(f"[✓] Vector dataset generated at: {VECTOR_PARQUET}")

def step3_snapshot_and_compress():
    log("Step 3/5: Taking online SQLite snapshot and compressing with zstd...")
    harvester_pid = get_harvester_pid()
    if harvester_pid:
        log(f"[*] Pausing background harvester PID {harvester_pid} for atomic snapshot...")
        try:
            os.kill(harvester_pid, signal.SIGSTOP)
        except OSError:
            harvester_pid = None

    t0 = time.time()
    try:
        # 1. Online SQLite backup
        if SNAPSHOT_SQLITE.exists():
            SNAPSHOT_SQLITE.unlink()

        src = sqlite3.connect(f"file:{ASSETS_DB}?mode=ro", uri=True)
        dst = sqlite3.connect(str(SNAPSHOT_SQLITE))
        src.backup(dst, pages=25000)
        dst.close()
        src.close()
        log(f"[✓] Online backup finished in {time.time()-t0:.1f}s")
    finally:
        if harvester_pid:
            try:
                os.kill(harvester_pid, signal.SIGCONT)
                log(f"[✓] Background harvester PID {harvester_pid} resumed.")
            except OSError:
                pass

    # 2. Multi-core Zstandard compression
    if SNAPSHOT_ZST.exists():
        SNAPSHOT_ZST.unlink()

    log("[*] Compressing snapshot with zstd -T0 -3...")
    t_comp = time.time()
    res = subprocess.run(["zstd", "-T0", "-3", str(SNAPSHOT_SQLITE), "-o", str(SNAPSHOT_ZST)], capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"zstd compression failed: {res.stderr}")
    
    comp_size_mb = SNAPSHOT_ZST.stat().st_size / (1024 * 1024)
    log(f"[✓] Compressed to {comp_size_mb:,.1f} MB in {time.time()-t_comp:.1f}s")

    # Clean uncompressed snapshot immediately
    if SNAPSHOT_SQLITE.exists():
        SNAPSHOT_SQLITE.unlink()
        log("[✓] Removed uncompressed snapshot to save disk space.")

def step4_upload_to_huggingface():
    log("Step 4/5: Uploading Vector DB and SQL Database to Hugging Face...")
    from export_to_huggingface import upload_dataset, get_hf_token

    token = get_hf_token()
    if not token:
        raise RuntimeError("No Hugging Face token found! Set HF_TOKEN or run 'hf auth login'.")

    # 1. Upload Vectors
    log(f"[*] Uploading {VECTOR_PARQUET.name}...")
    upload_dataset(HF_REPO_ID, str(VECTOR_PARQUET), token=token)

    # 2. Upload SQL DB archive
    log(f"[*] Uploading {SNAPSHOT_ZST.name}...")
    upload_dataset(HF_REPO_ID, str(SNAPSHOT_ZST), token=token)

    # 3. Clean local .zst to maintain 100+ GB free disk space
    if SNAPSHOT_ZST.exists():
        SNAPSHOT_ZST.unlink()
        log("[✓] Removed local .zst upload archive.")

def step5_record_stats(start_time: float):
    log("Step 5/5: Recording sync statistics...")
    conn = sqlite3.connect(str(ASSETS_DB))
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM assets")
    total_assets = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM assets WHERE ecosystem = 'mcp'")
    mcp_count = cur.fetchone()[0]
    duration = time.time() - start_time

    cur.execute("""
        INSERT INTO sync_history (total_assets, mcp_servers, vector_records, duration_seconds, status)
        VALUES (?, ?, ?, ?, ?)
    """, (total_assets, mcp_count, 50000, duration, "SUCCESS"))
    conn.commit()
    conn.close()

    log(f"🎉 Monthly Sync Completed Successfully in {duration/60:.1f} minutes!")
    log(f"📊 Total Assets: {total_assets:,} | MCP Servers: {mcp_count:,}")

def main():
    parser = argparse.ArgumentParser(description="Open-Agent-DB Monthly Sync Pipeline")
    parser.add_argument("--skip-mcp", action="store_true", help="Skip MCP registry merge")
    parser.add_argument("--skip-vectors", action="store_true", help="Skip vector embedding generation")
    parser.add_argument("--skip-upload", action="store_true", help="Skip Hugging Face upload")
    parser.add_argument("--vector-limit", type=int, default=50000, help="Number of records to vectorize")
    args = parser.parse_args()

    start_time = time.time()
    log("==================================================")
    log("🚀 Starting Open-Agent-DB Monthly Sync Pipeline")
    log("==================================================")

    init_sync_ledger()

    if not args.skip_mcp:
        step1_merge_mcp()

    if not args.skip_vectors:
        step2_export_vectors(limit=args.vector_limit)

    step3_snapshot_and_compress()

    if not args.skip_upload:
        step4_upload_to_huggingface()

    step5_record_stats(start_time)

if __name__ == "__main__":
    main()
