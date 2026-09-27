#!/usr/bin/env python3
"""
Merge MCP Registries (Glama, Official MCP, Smithery, Awesome MCP) from
universal_registry.db into github_universal_assets.db (assets & files tables).
"""

import os
import sys
import json
import time
import signal
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
REGISTRY_DB = BASE_DIR / "data" / "universal_registry.db"
ASSETS_DB = BASE_DIR / "data" / "github_universal_assets.db"

def get_harvester_pid():
    pid_file = BASE_DIR / "data" / "github_universal_harvester.pid"
    if pid_file.exists():
        try:
            with open(pid_file) as f:
                pid = int(f.read().strip())
            # Check if running
            os.kill(pid, 0)
            return pid
        except (ValueError, OSError):
            pass
    return None

def run_migration(batch_size=5000):
    print(f"[*] Reading registry items from {REGISTRY_DB}...")
    reg_conn = sqlite3.connect(f"file:{REGISTRY_DB}?mode=ro", uri=True)
    reg_conn.row_factory = sqlite3.Row
    reg_cur = reg_conn.cursor()

    reg_cur.execute("""
        SELECT id, source_platform, item_type, name, author, description, 
               stars, use_count, github_url, registry_url, install_command, 
               verified, raw_json, crawled_at
        FROM registry_items
    """)
    rows = reg_cur.fetchall()
    total_items = len(rows)
    print(f"[✓] Found {total_items:,} items to merge.")

    harvester_pid = get_harvester_pid()
    if harvester_pid:
        print(f"[*] Pausing background harvester PID {harvester_pid} for atomic write...")
        try:
            os.kill(harvester_pid, signal.SIGSTOP)
        except OSError as e:
            print(f"[!] Warning: Could not pause PID {harvester_pid}: {e}")
            harvester_pid = None

    try:
        t0 = time.time()
        print(f"[*] Connecting to {ASSETS_DB}...")
        assets_conn = sqlite3.connect(str(ASSETS_DB), timeout=60.0)
        assets_conn.execute("PRAGMA journal_mode = WAL;")
        assets_conn.execute("PRAGMA synchronous = NORMAL;")
        assets_cur = assets_conn.cursor()

        assets_batch = []
        files_batch = []
        inserted_count = 0

        for r in rows:
            item_id = r["id"]
            source_platform = r["source_platform"] or "mcp"
            item_type = r["item_type"] or "mcp_server"
            name = r["name"] or item_id
            author = r["author"] or ""
            desc = r["description"] or ""
            stars = r["stars"] or 0
            use_count = r["use_count"] or 0
            github_url = r["github_url"] or ""
            registry_url = r["registry_url"] or ""
            install_cmd = r["install_command"] or ""
            verified = r["verified"] or 0
            raw_json = r["raw_json"] or "{}"
            crawled_at = r["crawled_at"] or time.strftime("%Y-%m-%d %H:%M:%S")

            # Determine ecosystem & asset_kind
            if item_type == "mcp_server":
                ecosystem = "mcp"
                asset_kind = "mcp_server"
                path = "mcp.json"
                file_format = "json"
            elif item_type == "cursor_rule":
                ecosystem = "cursor"
                asset_kind = "trigger_rule"
                path = ".cursorrules"
                file_format = "markdown"
            else:
                ecosystem = "universal"
                asset_kind = "skill"
                path = "SKILL.md"
                file_format = "markdown"

            metadata = {
                "source_platform": source_platform,
                "registry_url": registry_url,
                "install_command": install_cmd,
                "verified": bool(verified),
                "use_count": use_count
            }
            metadata_json = json.dumps(metadata, ensure_ascii=False)
            canonical_key = f"{ecosystem}:{source_platform}:{name.lower()[:80]}"
            source_path = registry_url or install_cmd or f"mcp://{source_platform}/{name}"

            assets_batch.append((
                item_id, ecosystem, asset_kind, file_format, name, desc, author,
                stars, 0, github_url, registry_url, "", source_path, canonical_key,
                crawled_at, raw_json, metadata_json, 1
            ))

            content_bytes = raw_json.encode("utf-8")
            files_batch.append((
                item_id, path, len(content_bytes), content_bytes, 0
            ))

            if len(assets_batch) >= batch_size:
                assets_cur.executemany("""
                    INSERT OR REPLACE INTO assets (
                        id, ecosystem, asset_kind, file_format, name, description, author,
                        stars, forks, github_url, raw_url, branch, source_path, canonical_key,
                        crawled_at, content_raw, parsed_metadata_json, is_synced
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, assets_batch)

                assets_cur.executemany("""
                    INSERT OR REPLACE INTO files (
                        asset_id, path, size, content, is_compressed
                    ) VALUES (?, ?, ?, ?, ?)
                """, files_batch)

                assets_conn.commit()
                inserted_count += len(assets_batch)
                sys.stdout.write(f"\rProgress: {inserted_count:,} / {total_items:,} ({(inserted_count/total_items)*100:.1f}%) in {time.time()-t0:.1f}s")
                sys.stdout.flush()
                assets_batch.clear()
                files_batch.clear()

        if assets_batch:
            assets_cur.executemany("""
                INSERT OR REPLACE INTO assets (
                    id, ecosystem, asset_kind, file_format, name, description, author,
                    stars, forks, github_url, raw_url, branch, source_path, canonical_key,
                    crawled_at, content_raw, parsed_metadata_json, is_synced
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, assets_batch)

            assets_cur.executemany("""
                INSERT OR REPLACE INTO files (
                    asset_id, path, size, content, is_compressed
                ) VALUES (?, ?, ?, ?, ?)
            """, files_batch)

            assets_conn.commit()
            inserted_count += len(assets_batch)

        print(f"\n[✓] Successfully migrated {inserted_count:,} items into {ASSETS_DB} in {time.time()-t0:.2f}s!")

        # Verify
        assets_cur.execute("SELECT count(*) FROM assets WHERE ecosystem = 'mcp'")
        mcp_count = assets_cur.fetchone()[0]
        assets_cur.execute("SELECT count(*) FROM assets")
        total_count = assets_cur.fetchone()[0]
        print(f"[✓] Verification: Total assets: {total_count:,} (MCP servers: {mcp_count:,})")

        assets_conn.close()
    finally:
        if harvester_pid:
            print(f"[*] Resuming harvester PID {harvester_pid}...")
            try:
                os.kill(harvester_pid, signal.SIGCONT)
                print(f"[✓] Harvester PID {harvester_pid} resumed successfully.")
            except OSError as e:
                print(f"[!] Warning: Could not resume PID {harvester_pid}: {e}")

    reg_conn.close()

if __name__ == "__main__":
    run_migration()
