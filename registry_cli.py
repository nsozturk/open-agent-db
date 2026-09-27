#!/usr/bin/env python3
"""
Universal AI Agent Registry CLI
Search, inspect, and install across 147,000+ indexed MCP servers, Agent Skills, and Cursor Rules.
"""

import sys
import os
import sqlite3
import argparse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "universal_registry.db"

def get_conn():
    if not DB_PATH.exists():
        print(f"Error: Database not found at {DB_PATH}")
        sys.exit(1)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def cmd_stats(args):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT count(*) FROM registry_items;")
    total = c.fetchone()[0]

    print("=" * 65)
    print("🌐 UNIVERSAL AI AGENT REGISTRY — GLOBAL INDEX TELEMETRY")
    print("=" * 65)
    print(f"Total Capabilities & Servers Indexed: {total:,}\n")

    print(f"{'Platform':<18} | {'Type':<14} | {'Items Count':>12} | {'Share':>7}")
    print("-" * 65)
    c.execute("""
        SELECT source_platform, item_type, count(*) as cnt 
        FROM registry_items 
        GROUP BY source_platform, item_type 
        ORDER BY cnt DESC;
    """)
    for row in c.fetchall():
        share = (row['cnt'] / total) * 100 if total > 0 else 0
        print(f"{row['source_platform']:<18} | {row['item_type']:<14} | {row['cnt']:>12,} | {share:>6.1f}%")
    print("=" * 65)
    conn.close()

def cmd_search(args):
    conn = get_conn()
    c = conn.cursor()
    query = f"%{args.query}%"
    
    filter_sql = ""
    params = [query, query, query]
    if args.platform:
        filter_sql += " AND source_platform = ?"
        params.append(args.platform)
    if args.type:
        filter_sql += " AND item_type = ?"
        params.append(args.type)

    sql = f"""
        SELECT id, source_platform, item_type, name, description, stars, use_count, registry_url, install_command
        FROM registry_items
        WHERE (name LIKE ? OR description LIKE ? OR id LIKE ?) {filter_sql}
        ORDER BY stars DESC, use_count DESC
        LIMIT ?;
    """
    params.append(args.limit)
    c.execute(sql, params)
    rows = c.fetchall()

    print("=" * 80)
    print(f"🔍 Search results for: '{args.query}' (Found {len(rows)} matches, showing top {args.limit})")
    print("=" * 80)
    
    if not rows:
        print("No matches found.")
        conn.close()
        return

    for idx, r in enumerate(rows, 1):
        score_badge = f"⭐ {r['stars']:,}" if r['stars'] > 0 else ""
        if r['use_count'] > 0:
            score_badge += f" | ⬇️ {r['use_count']:,}"
            
        print(f"\n[{idx}] {r['name']} ({r['item_type'].upper()}) — [{r['source_platform']}] {score_badge}")
        print(f"    ID: {r['id']}")
        if r['description']:
            desc_snip = (r['description'][:140] + '...') if len(r['description']) > 140 else r['description']
            print(f"    Desc: {desc_snip}")
        if r['install_command']:
            print(f"    Install: \033[0;32m{r['install_command']}\033[0m")
        if r['registry_url']:
            print(f"    URL: {r['registry_url']}")

    print("\n" + "=" * 80)
    conn.close()

def cmd_info(args):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM registry_items WHERE id = ? OR id LIKE ?;", (args.id, f"%{args.id}%"))
    row = c.fetchone()
    if not row:
        print(f"No item found with ID matching '{args.id}'")
        conn.close()
        return

    print("=" * 70)
    print(f"📌 {row['name']}")
    print("=" * 70)
    print(f"ID:          {row['id']}")
    print(f"Platform:    {row['source_platform']}")
    print(f"Type:        {row['item_type']}")
    print(f"Author:      {row['author'] or 'N/A'}")
    print(f"Stars/Score: {row['stars']:,}")
    print(f"Use Count:   {row['use_count']:,}")
    print(f"Verified:    {'Yes' if row['verified'] else 'No'}")
    print(f"GitHub:      {row['github_url'] or 'N/A'}")
    print(f"Registry:    {row['registry_url'] or 'N/A'}")
    print(f"Install:     {row['install_command'] or 'N/A'}")
    print("\nDescription:")
    print(row['description'] or "(No description)")
    print("=" * 70)
    conn.close()

def main():
    parser = argparse.ArgumentParser(description="Universal AI Agent Registry CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    p_stats = subparsers.add_parser("stats", help="Show registry statistics")
    p_stats.set_defaults(func=cmd_stats)

    p_search = subparsers.add_parser("search", help="Search registry items")
    p_search.add_argument("query", type=str, help="Search term (name, desc, tags)")
    p_search.add_argument("--platform", type=str, help="Filter by platform")
    p_search.add_argument("--type", type=str, help="Filter by item_type (mcp_server, skill, cursor_rule)")
    p_search.add_argument("--limit", type=int, default=10, help="Max results (default: 10)")
    p_search.set_defaults(func=cmd_search)

    p_info = subparsers.add_parser("info", help="Get item detail by ID")
    p_info.add_argument("id", type=str, help="Item ID")
    p_info.set_defaults(func=cmd_info)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
