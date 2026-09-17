"""Unified Database Access Layer for Open-Agent-DB
Searches across both SkillsMP Catalog (637k+ skills) and Universal MCP Registry (150k+ MCP servers/tools).
"""

import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


DEFAULT_SEARCH_PATHS = [
    Path("./data"),
    Path(__file__).resolve().parent.parent / "data",
    Path("/Users/ns0bj/Development/Fun/sirket/skills-task/data"),
    Path.home() / ".cache" / "open-agent-db",
]


class UnifiedAgentDB:
    def __init__(
        self,
        skills_db_path: Optional[str] = None,
        registry_db_path: Optional[str] = None,
    ):
        self.skills_db_path = self._resolve_db_path(
            skills_db_path, "skillsmp.db", "OPEN_AGENT_SKILLS_DB"
        )
        self.registry_db_path = self._resolve_db_path(
            registry_db_path, "universal_registry.db", "OPEN_AGENT_REGISTRY_DB"
        )

    def _resolve_db_path(
        self, override: Optional[str], default_name: str, env_var: str
    ) -> Optional[Path]:
        if override and Path(override).exists():
            return Path(override)
        env_val = os.environ.get(env_var)
        if env_val and Path(env_val).exists():
            return Path(env_val)
        for base in DEFAULT_SEARCH_PATHS:
            p = base / default_name
            if p.exists():
                return p
        return None

    def _connect_ro(self, db_path: Optional[Path]) -> Optional[sqlite3.Connection]:
        if not db_path or not db_path.exists():
            return None
        try:
            conn = sqlite3.connect(f"file:{db_path.resolve()}?mode=ro", uri=True, timeout=10.0)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception:
            return None

    def get_stats(self) -> Dict[str, Any]:
        """Aggregate totals across all connected database files."""
        stats = {
            "skillsmp_available": self.skills_db_path is not None,
            "registry_available": self.registry_db_path is not None,
            "total_skills": 0,
            "synced_skills": 0,
            "total_mcp_servers": 0,
            "platforms": {},
        }

        # SkillsMP DB
        if self.skills_db_path:
            conn = self._connect_ro(self.skills_db_path)
            if conn:
                try:
                    stats["total_skills"] = conn.execute("SELECT COUNT(*) FROM skills").fetchone()[0]
                    stats["synced_skills"] = conn.execute("SELECT COUNT(*) FROM skills WHERE is_synced = 1").fetchone()[0]
                except Exception:
                    pass
                finally:
                    conn.close()

        # Universal Registry DB
        if self.registry_db_path:
            conn = self._connect_ro(self.registry_db_path)
            if conn:
                try:
                    rows = conn.execute(
                        "SELECT source_platform, item_type, COUNT(*) FROM registry_items GROUP BY source_platform, item_type"
                    ).fetchall()
                    for plat, itype, cnt in rows:
                        stats["platforms"][f"{plat}:{itype}"] = cnt
                        if itype == "mcp_server":
                            stats["total_mcp_servers"] += cnt
                except Exception:
                    pass
                finally:
                    conn.close()

        stats["total_assets"] = stats["total_skills"] + sum(stats["platforms"].values())
        return stats

    def search(
        self,
        query: str,
        asset_type: Optional[str] = None,  # 'skill', 'mcp_server', 'cursor_rule', or None for all
        platform: Optional[str] = None,    # 'smithery', 'glama', 'official_mcp', 'skillsmp', etc.
        min_stars: int = 0,
        limit: int = 40,
    ) -> List[Dict[str, Any]]:
        """Search across both Skills and MCP registries with unified ranking."""
        results = []
        cleaned_query = query.strip()

        # 1. Search Universal Registry (MCPs, tools, multi-source skills)
        if self.registry_db_path:
            conn = self._connect_ro(self.registry_db_path)
            if conn:
                try:
                    where_clauses = []
                    params: List[Any] = []

                    if cleaned_query:
                        where_clauses.append(
                            "(name LIKE ? OR description LIKE ? OR author LIKE ?)"
                        )
                        like_q = f"%{cleaned_query}%"
                        params.extend([like_q, like_q, like_q])

                    if asset_type and asset_type != "all":
                        where_clauses.append("item_type = ?")
                        params.append(asset_type)

                    if platform:
                        where_clauses.append("source_platform = ?")
                        params.append(platform)

                    if min_stars > 0:
                        where_clauses.append("stars >= ?")
                        params.append(min_stars)

                    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
                    query_sql = f"""
                    SELECT id, name, author, description, stars, use_count,
                           source_platform, item_type, github_url, install_command, verified
                    FROM registry_items
                    {where_sql}
                    ORDER BY verified DESC, stars DESC, use_count DESC
                    LIMIT ?
                    """
                    params.append(limit)
                    rows = conn.execute(query_sql, params).fetchall()
                    for r in rows:
                        d = dict(r)
                        d["category"] = d["item_type"].replace("_", " ").title()
                        results.append(d)
                except Exception:
                    pass
                finally:
                    conn.close()

        # 2. Search SkillsMP (637k+ skills)
        if self.skills_db_path and (not asset_type or asset_type in ("skill", "all")):
            conn = self._connect_ro(self.skills_db_path)
            if conn:
                try:
                    where_clauses = []
                    params = []

                    if cleaned_query:
                        where_clauses.append("(name LIKE ? OR description LIKE ? OR author LIKE ?)")
                        like_q = f"%{cleaned_query}%"
                        params.extend([like_q, like_q, like_q])

                    if min_stars > 0:
                        where_clauses.append("stars >= ?")
                        params.append(min_stars)

                    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
                    query_sql = f"""
                    SELECT id, name, author, description, stars, forks,
                           github_url, skill_url, is_synced
                    FROM skills
                    {where_sql}
                    ORDER BY stars DESC
                    LIMIT ?
                    """
                    params.append(limit)
                    rows = conn.execute(query_sql, params).fetchall()
                    for r in rows:
                        d = dict(r)
                        d["source_platform"] = "skillsmp"
                        d["item_type"] = "skill"
                        d["category"] = "Agent Skill"
                        d["use_count"] = d.get("forks", 0)
                        d["install_command"] = f"open-agent install {d['id']}"
                        results.append(d)
                except Exception:
                    pass
                finally:
                    conn.close()

        # Re-sort combined results by stars
        results.sort(key=lambda x: (x.get("verified", 0), x.get("stars", 0) or 0, x.get("use_count", 0) or 0), reverse=True)
        return results[:limit]

    def get_item(self, identifier: str) -> Optional[Dict[str, Any]]:
        """Retrieve full details of an asset by ID."""
        # 1. Try Universal Registry
        if self.registry_db_path:
            conn = self._connect_ro(self.registry_db_path)
            if conn:
                try:
                    row = conn.execute("SELECT * FROM registry_items WHERE id = ? OR name = ?", (identifier, identifier)).fetchone()
                    if row:
                        d = dict(row)
                        if d.get("raw_json"):
                            try:
                                d["raw"] = json.loads(d["raw_json"])
                            except Exception:
                                pass
                        return d
                except Exception:
                    pass
                finally:
                    conn.close()

        # 2. Try SkillsMP DB
        if self.skills_db_path:
            conn = self._connect_ro(self.skills_db_path)
            if conn:
                try:
                    row = conn.execute("SELECT * FROM skills WHERE id = ? OR name = ?", (identifier, identifier)).fetchone()
                    if row:
                        d = dict(row)
                        # Fetch files list
                        files = conn.execute(
                            "SELECT path, size, (content IS NOT NULL) as has_content FROM files WHERE skill_id = ?",
                            (d["id"],)
                        ).fetchall()
                        d["files"] = [dict(f) for f in files]
                        d["source_platform"] = "skillsmp"
                        d["item_type"] = "skill"
                        d["install_command"] = f"open-agent install {d['id']}"
                        if d.get("raw_json"):
                            try:
                                d["raw"] = json.loads(d["raw_json"])
                            except Exception:
                                pass
                        return d
                except Exception:
                    pass
                finally:
                    conn.close()

        return None
