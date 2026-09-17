"""Unified Database Access Layer for Open-Agent-DB
Searches across both SkillsMP Catalog (637k+ skills) and Universal MCP Registry (150k+ MCP servers/tools)
with full Domain, Category, and SOC-aligned Occupation taxonomy support and fast FTS5 queries.
"""

import json
import os
import re
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

DEFAULT_SEARCH_PATHS = [
    Path("./data"),
    Path(__file__).resolve().parent.parent / "data",
    Path("/Users/ns0bj/Development/Fun/sirket/skills-task/data"),
    Path.home() / ".cache" / "open-agent-db",
]

INDEX_FALLBACK_PATH = Path(__file__).resolve().parent.parent / "web" / "data" / "catalog_index.json"
STATS_PATH = Path(__file__).resolve().parent.parent / "web" / "data" / "stats.json"

OCCUPATION_DEFINITIONS = [
    {
        "id": "software-engineer",
        "title": "Software & Web Engineers",
        "soc": "SOC 15-1252",
        "icon": "💻",
        "desc": "Full-stack, backend, frontend, architecture patterns, and coding workflows.",
    },
    {
        "id": "devops-sre",
        "title": "DevOps & SRE Engineers",
        "soc": "SOC 15-1250",
        "icon": "🚀",
        "desc": "CI/CD pipelines, container orchestration, Kubernetes, Docker, and cloud infrastructure.",
    },
    {
        "id": "ai-data-scientist",
        "title": "AI Specialists & Data Scientists",
        "soc": "SOC 15-2051",
        "icon": "🧠",
        "desc": "LLM prompts, machine learning models, RAG systems, embeddings, and data analysis.",
    },
    {
        "id": "database-admin",
        "title": "Database Administrators & Engineers",
        "soc": "SOC 15-1242",
        "icon": "🗄️",
        "desc": "SQL optimization, database connections, schema migrations, and vector stores.",
    },
    {
        "id": "security-qa",
        "title": "Security Analysts & QA Engineers",
        "soc": "SOC 15-1212",
        "icon": "🛡️",
        "desc": "Vulnerability auditing, code review, fuzzing, testing, and compliance.",
    },
    {
        "id": "product-pm",
        "title": "Product & Project Managers",
        "soc": "SOC 11-1021",
        "icon": "📈",
        "desc": "Agile roadmaps, task coordination, Linear, Jira, and team communication.",
    },
    {
        "id": "designer-media",
        "title": "UI/UX Designers & Media Creators",
        "soc": "SOC 27-1024",
        "icon": "🎨",
        "desc": "Design systems, SVG icons, Figma assets, and creative media generation.",
    },
    {
        "id": "researcher",
        "title": "Researchers & Academic Scientists",
        "soc": "SOC 19-1029",
        "icon": "🔬",
        "desc": "Literature search, arXiv, PubMed, bioinformatics, chemistry, and LaTeX.",
    },
    {
        "id": "business-finance",
        "title": "Business & Financial Analysts",
        "soc": "SOC 13-2051",
        "icon": "📊",
        "desc": "Market intelligence, valuation models, spreadsheets, and financial metrics.",
    },
    {
        "id": "tech-writer",
        "title": "Technical Writers & Educators",
        "soc": "SOC 27-3042",
        "icon": "📚",
        "desc": "API documentation, markdown linting, developer guides, and wikis.",
    },
]

OCCUPATION_MAP = {o["id"]: o for o in OCCUPATION_DEFINITIONS}


def classify_mcp(name: str, desc: str) -> Tuple[str, str]:
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


def classify_occupation(name: str, desc: str, dom: str, cat: str) -> str:
    """Map any Skill or MCP server to an SOC-aligned occupation."""
    text = f"{name} {desc or ''}".lower()
    if dom == "Databases" or any(k in cat for k in ["Databases", "SQL Databases", "Database Tools"]) or any(k in text for k in ["postgres", "mysql", "sqlite", "redis", "mongodb", "prisma", "supabase"]):
        return "database-admin"
    if dom == "DevOps" or any(k in cat for k in ["DevOps", "CI/CD", "Git Workflows", "Containers", "Monitoring", "Cloud"]) or any(k in text for k in ["docker", "k8s", "kubernetes", "terraform", "aws", "azure", "gcp", "deploy"]):
        return "devops-sre"
    if dom == "Data & AI" or any(k in cat for k in ["LLM & AI", "Machine Learning", "Data Analysis", "Data Engineering"]) or any(k in text for k in ["openai", "anthropic", "rag", "embedding", "model", "agent", "gemini", "deepseek"]):
        return "ai-data-scientist"
    if dom == "Testing & Security" or any(k in cat for k in ["Security", "Testing", "Code Quality"]) or any(k in text for k in ["security", "vulnerability", "penetration", "audit", "scan", "fuzz"]):
        return "security-qa"
    if cat in ["Project Management", "Productivity & Collab"] or any(k in text for k in ["jira", "linear", "trello", "notion", "slack", "roadmap", "agile", "scrum", "project management"]):
        return "product-pm"
    if dom == "Research" or any(k in cat for k in ["Academic", "Bioinformatics", "Computational Chemistry", "Scientific Computing"]) or any(k in text for k in ["arxiv", "pubmed", "scholar", "paper", "literature review", "bioinformatics"]):
        return "researcher"
    if dom == "Content & Media" or cat in ["Design", "Media", "Content Creation"] or any(k in text for k in ["figma", "svg", "ui/ux", "canvas", "color palette", "sketch", "illustration"]):
        return "designer-media"
    if dom == "Business" or cat in ["Finance & Investment", "E-commerce", "Sales & Marketing", "Real Estate & Legal", "DeFi"] or any(k in text for k in ["finance", "stock", "accounting", "salesforce", "stripe", "invoice", "crypto trading"]):
        return "business-finance"
    if dom == "Documentation" or cat in ["Technical Docs", "Knowledge Base", "Education"] or any(k in text for k in ["markdown", "docs", "readme", "documentation", "wiki", "tutorial"]):
        return "tech-writer"
    return "software-engineer"


def match_occupation_query(occ_id: str, query: str) -> bool:
    """Helper to check if occupation ID or title matches query string."""
    q = query.lower().strip()
    if q in ("all", "*"):
        return True
    if occ_id.lower() == q:
        return True
    occ_info = OCCUPATION_MAP.get(occ_id)
    if occ_info:
        if q in occ_info["title"].lower() or q in occ_info["id"].lower() or q in occ_info["soc"].lower():
            return True
    return False


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

    def get_occupations(self) -> List[Dict[str, Any]]:
        """Return list of SOC-aligned occupations with total and breakdown counts."""
        if STATS_PATH.exists():
            try:
                with open(STATS_PATH, "r", encoding="utf-8") as f:
                    stats = json.load(f)
                if "occupations" in stats:
                    return stats["occupations"]
            except Exception:
                pass
        return OCCUPATION_DEFINITIONS

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
        domain: Optional[str] = None,      # 'Data & AI', 'DevOps', 'Databases', etc.
        category: Optional[str] = None,    # 'Machine Learning', 'PostgreSQL', etc.
        occupation: Optional[str] = None,  # 'software-engineer', 'devops-sre', etc.
        limit: int = 40,
    ) -> List[Dict[str, Any]]:
        """Search across both Skills and MCP registries with unified ranking and taxonomy filtering."""
        results = []
        cleaned_query = query.strip()

        # 1. Search Universal Registry (MCPs, tools, multi-source skills)
        if self.registry_db_path and (not asset_type or asset_type in ("mcp_server", "cursor_rule", "all")):
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
                    fetch_limit = limit * 4 if (domain or category or occupation) else limit
                    query_sql = f"""
                    SELECT id, name, author, description, stars, use_count,
                           source_platform, item_type, github_url, install_command, verified
                    FROM registry_items
                    {where_sql}
                    ORDER BY verified DESC, stars DESC, use_count DESC
                    LIMIT ?
                    """
                    params.append(fetch_limit)
                    rows = conn.execute(query_sql, params).fetchall()

                    for r in rows:
                        d = dict(r)
                        dom, cat = classify_mcp(d.get("name") or "", d.get("description") or "")
                        if d.get("item_type") == "cursor_rule":
                            dom = "Development"
                            cat = "Cursor Rules"

                        occ = classify_occupation(d.get("name") or "", d.get("description") or "", dom, cat)
                        occ_meta = OCCUPATION_MAP.get(occ, {})

                        if domain and domain.lower() != "all" and dom.lower() != domain.lower():
                            continue
                        if category and category.lower() != "all" and cat.lower() != category.lower():
                            continue
                        if occupation and not match_occupation_query(occ, occupation):
                            continue

                        d["domain"] = dom
                        d["category"] = cat
                        d["occupation"] = occ
                        d["occupation_title"] = occ_meta.get("title", occ)
                        d["soc"] = occ_meta.get("soc", "")
                        results.append(d)
                except Exception:
                    pass
                finally:
                    conn.close()

        # 2. Search SkillsMP (637k+ skills) with fast FTS5
        if self.skills_db_path and (not asset_type or asset_type in ("skill", "all")):
            conn = self._connect_ro(self.skills_db_path)
            if conn:
                try:
                    tokens = re.findall(r"\w+", cleaned_query) if cleaned_query else []
                    fts_query = " ".join(tokens) if tokens else ""

                    where_clauses = []
                    params = []

                    if min_stars > 0:
                        where_clauses.append("s.stars >= ?")
                        params.append(min_stars)

                    if domain and domain.lower() != "all":
                        where_clauses.append("c.domain = ?")
                        params.append(domain)

                    if category and category.lower() != "all":
                        where_clauses.append("(c.title = ? OR c.slug = ?)")
                        params.extend([category, category])

                    fetch_limit = limit * 3 if occupation else limit

                    if not fts_query and not domain and not category:
                        where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
                        query_sql = f"""
                        SELECT s.id, s.name, s.author, s.description, s.stars, s.forks,
                               s.github_url, s.skill_url, s.is_synced,
                               (SELECT c.domain FROM skill_categories sc JOIN categories c ON sc.category_slug = c.slug WHERE sc.skill_id = s.id LIMIT 1) as domain,
                               (SELECT c.title FROM skill_categories sc JOIN categories c ON sc.category_slug = c.slug WHERE sc.skill_id = s.id LIMIT 1) as category
                        FROM skills s
                        {where_sql}
                        ORDER BY s.stars DESC
                        LIMIT ?
                        """
                        exec_params = params + [fetch_limit]
                    elif fts_query:
                        where_sql = ("AND " + " AND ".join(where_clauses)) if where_clauses else ""
                        query_sql = f"""
                        SELECT s.id, s.name, s.author, s.description, s.stars, s.forks,
                               s.github_url, s.skill_url, s.is_synced,
                               MAX(c.domain) as domain, MAX(c.title) as category
                        FROM skills_fts f
                        JOIN skills s ON f.rowid = s.rowid
                        LEFT JOIN skill_categories sc ON s.id = sc.skill_id
                        LEFT JOIN categories c ON sc.category_slug = c.slug
                        WHERE skills_fts MATCH ? {where_sql}
                        GROUP BY s.id
                        ORDER BY s.stars DESC
                        LIMIT ?
                        """
                        exec_params = [fts_query] + params + [fetch_limit]
                    else:
                        where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
                        query_sql = f"""
                        SELECT s.id, s.name, s.author, s.description, s.stars, s.forks,
                               s.github_url, s.skill_url, s.is_synced,
                               MAX(c.domain) as domain, MAX(c.title) as category
                        FROM skills s
                        LEFT JOIN skill_categories sc ON s.id = sc.skill_id
                        LEFT JOIN categories c ON sc.category_slug = c.slug
                        {where_sql}
                        GROUP BY s.id
                        ORDER BY s.stars DESC
                        LIMIT ?
                        """
                        exec_params = params + [fetch_limit]

                    rows = conn.execute(query_sql, exec_params).fetchall()
                    for r in rows:
                        d = dict(r)
                        dom = d.get("domain") or "Development"
                        cat = d.get("category") or "General Skill"
                        occ = classify_occupation(d.get("name") or "", d.get("description") or "", dom, cat)
                        occ_meta = OCCUPATION_MAP.get(occ, {})

                        if occupation and not match_occupation_query(occ, occupation):
                            continue

                        d["source_platform"] = "skillsmp"
                        d["item_type"] = "skill"
                        d["domain"] = dom
                        d["category"] = cat
                        d["occupation"] = occ
                        d["occupation_title"] = occ_meta.get("title", occ)
                        d["soc"] = occ_meta.get("soc", "")
                        d["use_count"] = d.get("forks", 0)
                        d["install_command"] = f"open-agent install {d['id']}"
                        results.append(d)
                except Exception as e:
                    pass
                finally:
                    conn.close()

        # 3. Fallback to catalog_index.json if databases are not available locally
        if not results and not self.skills_db_path and not self.registry_db_path and INDEX_FALLBACK_PATH.exists():
            try:
                with open(INDEX_FALLBACK_PATH, "r", encoding="utf-8") as f:
                    cached_items = json.load(f)
                tokens = cleaned_query.lower().split() if cleaned_query else []
                for item in cached_items:
                    if asset_type and asset_type != "all" and item.get("t") != asset_type:
                        continue
                    if platform and platform != "all" and item.get("p") != platform:
                        continue
                    if min_stars > 0 and item.get("s", 0) < min_stars:
                        continue
                    if domain and domain.lower() != "all" and item.get("dom", "").lower() != domain.lower():
                        continue
                    if category and category.lower() != "all" and item.get("cat", "").lower() != category.lower():
                        continue
                    occ = item.get("occ") or classify_occupation(item.get("n", ""), item.get("d", ""), item.get("dom", ""), item.get("cat", ""))
                    if occupation and not match_occupation_query(occ, occupation):
                        continue
                    if tokens:
                        blob = f"{item.get('n', '')} {item.get('d', '')} {item.get('a', '')} {item.get('dom', '')} {item.get('cat', '')} {occ}".lower()
                        if not all(t in blob for t in tokens):
                            continue

                    occ_meta = OCCUPATION_MAP.get(occ, {})
                    results.append({
                        "id": item.get("id"),
                        "name": item.get("n"),
                        "author": item.get("a"),
                        "description": item.get("d"),
                        "stars": item.get("s", 0),
                        "use_count": item.get("u", 0),
                        "source_platform": item.get("p"),
                        "item_type": item.get("t"),
                        "domain": item.get("dom"),
                        "category": item.get("cat"),
                        "occupation": occ,
                        "occupation_title": occ_meta.get("title", occ),
                        "soc": occ_meta.get("soc", ""),
                        "github_url": item.get("g"),
                        "install_command": item.get("i"),
                        "verified": item.get("v", 0),
                    })
            except Exception:
                pass

        # Re-sort combined results by verified, stars, usage
        results.sort(key=lambda x: (x.get("verified", 0), x.get("stars", 0) or 0, x.get("use_count", 0) or 0), reverse=True)
        return results[:limit]

    def get_item(self, identifier: str) -> Optional[Dict[str, Any]]:
        """Retrieve full details of an asset by ID or name."""
        # 1. Try Universal Registry
        if self.registry_db_path:
            conn = self._connect_ro(self.registry_db_path)
            if conn:
                try:
                    row = conn.execute("SELECT * FROM registry_items WHERE id = ? OR name = ?", (identifier, identifier)).fetchone()
                    if row:
                        d = dict(row)
                        dom, cat = classify_mcp(d.get("name") or "", d.get("description") or "")
                        occ = classify_occupation(d.get("name") or "", d.get("description") or "", dom, cat)
                        occ_meta = OCCUPATION_MAP.get(occ, {})
                        d["domain"] = dom
                        d["category"] = cat
                        d["occupation"] = occ
                        d["occupation_title"] = occ_meta.get("title", occ)
                        d["soc"] = occ_meta.get("soc", "")
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
                        files = conn.execute(
                            "SELECT path, size, (content IS NOT NULL) as has_content FROM files WHERE skill_id = ?",
                            (d["id"],)
                        ).fetchall()
                        d["files"] = [dict(f) for f in files]
                        d["source_platform"] = "skillsmp"
                        d["item_type"] = "skill"
                        d["install_command"] = f"open-agent install {d['id']}"

                        cat_row = conn.execute(
                            """
                            SELECT c.domain, c.title as category
                            FROM skill_categories sc
                            JOIN categories c ON sc.category_slug = c.slug
                            WHERE sc.skill_id = ?
                            LIMIT 1
                            """,
                            (d["id"],)
                        ).fetchone()
                        if cat_row:
                            d["domain"] = cat_row["domain"]
                            d["category"] = cat_row["category"]
                        else:
                            d["domain"] = "Development"
                            d["category"] = "General Skill"

                        occ = classify_occupation(d.get("name") or "", d.get("description") or "", d["domain"], d["category"])
                        occ_meta = OCCUPATION_MAP.get(occ, {})
                        d["occupation"] = occ
                        d["occupation_title"] = occ_meta.get("title", occ)
                        d["soc"] = occ_meta.get("soc", "")

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

        # 3. Try catalog_index.json fallback
        if INDEX_FALLBACK_PATH.exists():
            try:
                with open(INDEX_FALLBACK_PATH, "r", encoding="utf-8") as f:
                    cached_items = json.load(f)
                for item in cached_items:
                    if item.get("id") == identifier or (item.get("n") and item.get("n").lower() == identifier.lower()):
                        occ = item.get("occ") or classify_occupation(item.get("n", ""), item.get("d", ""), item.get("dom", ""), item.get("cat", ""))
                        occ_meta = OCCUPATION_MAP.get(occ, {})
                        return {
                            "id": item.get("id"),
                            "name": item.get("n"),
                            "author": item.get("a"),
                            "description": item.get("d"),
                            "stars": item.get("s", 0),
                            "use_count": item.get("u", 0),
                            "source_platform": item.get("p"),
                            "item_type": item.get("t"),
                            "domain": item.get("dom"),
                            "category": item.get("cat"),
                            "occupation": occ,
                            "occupation_title": occ_meta.get("title", occ),
                            "soc": occ_meta.get("soc", ""),
                            "github_url": item.get("g"),
                            "install_command": item.get("i"),
                            "verified": item.get("v", 0),
                        }
            except Exception:
                pass

        return None
