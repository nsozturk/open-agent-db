#!/usr/bin/env python3
"""Build Static Web Index for GitHub Pages & Local Explorer
Extracts, classifies, and curates top skills & MCP servers from SQLite into a compact, minified JSON index
with rich Domain and Category taxonomy (like skillsmp.com).
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


def classify_mcp(name: str, desc: str) -> tuple:
    """Classify MCP servers into domain and category based on keywords."""
    text = f"{name} {desc or ''}".lower()
    if any(k in text for k in ["postgres", "mysql", "sqlite", "mongo", "redis", "prisma", "database", "sql", "vector", "supabase"]):
        return "Databases", "Databases"
    if any(k in text for k in ["git", "docker", "k8s", "kubernetes", "aws", "azure", "gcp", "cloud", "ci/cd", "deploy"]):
        return "DevOps", "DevOps & Cloud"
    if any(k in text for k in ["browser", "search", "brave", "puppeteer", "playwright", "scrape", "crawl", "fetch"]):
        return "Tools", "Web & Automation"
    if any(k in text for k in ["llm", "ai", "openai", "anthropic", "rag", "embedding", "model", "agent", "gemini"]):
        return "Data & AI", "LLM & AI"
    if any(k in text for k in ["slack", "discord", "telegram", "email", "gmail", "notion", "linear", "jira", "trello", "crm"]):
        return "Business", "Productivity & Collab"
    if any(k in text for k in ["security", "auth", "audit", "scan", "test", "vulnerability", "protect"]):
        return "Testing & Security", "Security"
    if any(k in text for k in ["code", "python", "typescript", "react", "rust", "go", "node", "compiler", "debug", "api"]):
        return "Development", "Developer Tools"
    return "Tools", "Utilities"


def build_index(max_mcp: int = 12000, max_skills: int = 15000):
    print("🚀 Extracting curated assets with Domain & Category taxonomy...")
    db = UnifiedAgentDB()

    items = []
    seen_ids = set()
    domain_counts = {}
    category_counts = {}

    def track_counts(dom, cat):
        domain_counts[dom] = domain_counts.get(dom, 0) + 1
        category_counts[cat] = category_counts.get(cat, 0) + 1

    # 1. Extract from Universal Registry (MCP Servers, Tools, Rules)
    if db.registry_db_path and db.registry_db_path.exists():
        print(f"📦 Reading Universal Registry from {db.registry_db_path}...")
        conn = sqlite3.connect(f"file:{db.registry_db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row

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

            dom, cat = classify_mcp(r["name"] or "", r["description"] or "")
            if r["item_type"] == "cursor_rule":
                dom = "Development"
                cat = "Cursor Rules"

            track_counts(dom, cat)

            items.append({
                "id": sid,
                "n": r["name"] or sid,
                "a": r["author"] or "unknown",
                "d": (r["description"] or "").strip()[:240],
                "s": int(r["stars"] or 0),
                "u": int(r["use_count"] or 0),
                "p": r["source_platform"] or "registry",
                "t": r["item_type"] or "mcp_server",
                "dom": dom,
                "cat": cat,
                "g": r["github_url"] or "",
                "i": r["install_command"] or "",
                "v": int(r["verified"] or 0),
            })
        conn.close()
        print(f"  ✓ Added {len(items):,} items from Universal Registry.")

    # 2. Extract from SkillsMP with Skill Categories & Domains
    if db.skills_db_path and db.skills_db_path.exists():
        print(f"📦 Reading SkillsMP Catalog with categories from {db.skills_db_path}...")
        conn = sqlite3.connect(f"file:{db.skills_db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row

        query = """
        SELECT s.id, s.name, s.author, s.description, s.stars, s.forks,
               s.github_url, s.skill_url, s.is_synced,
               c.title as cat_title, c.domain
        FROM skills s
        LEFT JOIN skill_categories sc ON s.id = sc.skill_id
        LEFT JOIN categories c ON sc.category_slug = c.slug
        WHERE s.stars >= 2 OR s.is_synced = 1
        ORDER BY s.stars DESC, s.forks DESC
        LIMIT ?
        """
        rows = conn.execute(query, (max_skills,)).fetchall()
        skills_added = 0
        for r in rows:
            sid = r["id"]
            if sid in seen_ids:
                continue
            seen_ids.add(sid)

            dom = r["domain"] or "Development"
            cat = r["cat_title"] or "General Skill"
            track_counts(dom, cat)

            items.append({
                "id": sid,
                "n": r["name"] or sid,
                "a": r["author"] or "unknown",
                "d": (r["description"] or "").strip()[:240],
                "s": int(r["stars"] or 0),
                "u": int(r["forks"] or 0),
                "p": "skillsmp",
                "t": "skill",
                "dom": dom,
                "cat": cat,
                "g": r["github_url"] or "",
                "i": f"open-agent install {sid}",
                "v": 0,
            })
            skills_added += 1
        conn.close()
        print(f"  ✓ Added {skills_added:,} items from SkillsMP.")

    # Sort domain & category statistics
    sorted_domains = sorted(
        [{"domain": d, "count": cnt} for d, cnt in domain_counts.items()],
        key=lambda x: x["count"],
        reverse=True,
    )
    sorted_categories = sorted(
        [{"category": c, "count": cnt} for c, cnt in category_counts.items()],
        key=lambda x: x["count"],
        reverse=True,
    )

    # Global Stats
    global_stats = db.get_stats()
    stats_payload = {
        "total_ecosystem_assets": global_stats.get("total_assets", 0),
        "total_skills_indexed": global_stats.get("total_skills", 0),
        "total_skills_synced": global_stats.get("synced_skills", 0),
        "total_mcp_servers": global_stats.get("total_mcp_servers", 0),
        "web_index_count": len(items),
        "domains": sorted_domains,
        "categories": sorted_categories,
        "platforms": global_stats.get("platforms", {}),
    }

    # Write files
    print(f"💾 Writing {len(items):,} items to {INDEX_FILE}...")
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, separators=(",", ":"))

    print(f"📊 Writing catalog stats with taxonomy to {STATS_FILE}...")
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats_payload, f, indent=2, ensure_ascii=False)

    size_mb = INDEX_FILE.stat().st_size / (1024 * 1024)
    print(f"✨ Successfully generated classified web index! ({size_mb:.2f} MB uncompressed)")


if __name__ == "__main__":
    build_index()
