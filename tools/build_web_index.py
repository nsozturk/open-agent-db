#!/usr/bin/env python3
"""Build Static Web Index for GitHub Pages & Local Explorer
Extracts and curates top skills & MCP servers from SQLite into a compact, minified JSON index.
"""

import gzip
import json
import os
import sqlite3
import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from cli.db import UnifiedAgentDB

OUTPUT_DIR = ROOT_DIR / "web" / "data"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
INDEX_FILE = OUTPUT_DIR / "catalog_index.json"
STATS_FILE = OUTPUT_DIR / "stats.json"


def build_index(max_mcp: int = 12000, max_skills: int = 15000):
    print("🚀 Extracting curated assets from SQLite databases...")
    db = UnifiedAgentDB()

    items = []
    seen_ids = set()

    # 1. Extract from Universal Registry (MCP Servers, Tools, Rules)
    if db.registry_db_path and db.registry_db_path.exists():
        print(f"📦 Reading Universal Registry from {db.registry_db_path}...")
        conn = sqlite3.connect(f"file:{db.registry_db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        
        # Priority: verified first, then stars desc, use_count desc
        query = """
        SELECT id, name, author, description, stars, use_count,
               source_platform, item_type, github_url, install_command, verified
        FROM registry_items
        ORDER BY verified DESC, stars DESC, use_count DESC
        LIMIT ?
        """
        rows = conn.execute(query, (max_mcp,)).fetchall()
        for r in rows:
            sid = r["id"]
            if sid in seen_ids:
                continue
            seen_ids.add(sid)
            items.append({
                "id": sid,
                "n": r["name"] or sid,
                "a": r["author"] or "unknown",
                "d": (r["description"] or "").strip()[:240],
                "s": int(r["stars"] or 0),
                "u": int(r["use_count"] or 0),
                "p": r["source_platform"] or "registry",
                "t": r["item_type"] or "mcp_server",
                "g": r["github_url"] or "",
                "i": r["install_command"] or "",
                "v": int(r["verified"] or 0),
            })
        conn.close()
        print(f"  ✓ Added {len(items):,} items from Universal Registry.")

    # 2. Extract from SkillsMP (Top Starred Agent Skills)
    if db.skills_db_path and db.skills_db_path.exists():
        print(f"📦 Reading SkillsMP Catalog from {db.skills_db_path}...")
        conn = sqlite3.connect(f"file:{db.skills_db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row

        query = """
        SELECT id, name, author, description, stars, forks, github_url, skill_url, is_synced
        FROM skills
        WHERE stars >= 2 OR is_synced = 1
        ORDER BY stars DESC, forks DESC
        LIMIT ?
        """
        rows = conn.execute(query, (max_skills,)).fetchall()
        skills_added = 0
        for r in rows:
            sid = r["id"]
            if sid in seen_ids:
                continue
            seen_ids.add(sid)
            items.append({
                "id": sid,
                "n": r["name"] or sid,
                "a": r["author"] or "unknown",
                "d": (r["description"] or "").strip()[:240],
                "s": int(r["stars"] or 0),
                "u": int(r["forks"] or 0),
                "p": "skillsmp",
                "t": "skill",
                "g": r["github_url"] or "",
                "i": f"open-agent install {sid}",
                "v": 0,
            })
            skills_added += 1
        conn.close()
        print(f"  ✓ Added {skills_added:,} items from SkillsMP.")

    # Global Stats
    global_stats = db.get_stats()
    stats_payload = {
        "total_ecosystem_assets": global_stats.get("total_assets", 0),
        "total_skills_indexed": global_stats.get("total_skills", 0),
        "total_skills_synced": global_stats.get("synced_skills", 0),
        "total_mcp_servers": global_stats.get("total_mcp_servers", 0),
        "web_index_count": len(items),
        "platforms": global_stats.get("platforms", {}),
    }

    # Write files
    print(f"💾 Writing {len(items):,} items to {INDEX_FILE}...")
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, separators=(",", ":"))

    print(f"📊 Writing catalog stats to {STATS_FILE}...")
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats_payload, f, indent=2, ensure_ascii=False)

    size_mb = INDEX_FILE.stat().st_size / (1024 * 1024)
    print(f"✨ Successfully generated web index! ({size_mb:.2f} MB uncompressed)")


if __name__ == "__main__":
    build_index()
