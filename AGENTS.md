# AGENTS.md — Open-Agent-DB Agent Operational Contract

This document provides a strict, non-ambiguous contract for autonomous AI coding agents (Anthropic Claude Code, OpenAI Codex, Google Gemini / Antigravity, Cursor, and OpenCode) operating within or integrating with the `open-agent-db` repository.

---

## 1. Project Purpose & Topology

Open-Agent-DB is the universal open database and semantic vector search engine for AI Agent Skills, MCP (Model Context Protocol) Servers, and Autonomous Directives.

- **Primary Repository**: `https://github.com/nsozturk/open-agent-db`
- **Hugging Face Hub**: `https://huggingface.co/datasets/ns0bj/open-agent-db`
- **Official Documentation**: `https://nsozturk.github.io/open-agent-db/`
- **Supported Ecosystems**: `claude`, `cursor`, `codex`, `gemini`, `copilot`, `opencode`, `mcp`, `universal`.

---

## 2. CLI Command Contracts

All agent commands MUST support non-interactive execution (`--quiet` or headless piping):

### Search Commands:
```bash
# 1. Zero-install Node execution
npx open-agent-db search "<query>"

# 2. Local Python search against SQLite FTS5
python3 cli/main.py search "<query>"

# 3. Filter by ecosystem
python3 cli/main.py search "postgres" --ecosystem mcp

# 4. Semantic vector search (dense embeddings)
python3 vector_search.py "<natural-language-query>" --top-k 5
```

### Installation & Inspection:
```bash
# Inspect MCP server metadata and environment parameters
open-agent info "<server-name>"

# Generate Claude Desktop MCP config snippet
open-agent install "<server-name>"
```

---

## 3. Database Architecture & Operational Truths

1. **SQLite WAL Mode**:
   - The primary database operates in WAL (`Write-Ahead Logging`) mode with `PRAGMA synchronous = NORMAL`.
   - Never hold long exclusive write locks. Background harvesters commit in atomic batches of 5,000–10,000 rows.
2. **Online Snapshots**:
   - Direct file copies (`cp`) of active SQLite databases in WAL mode risk corrupted checkpoints.
   - Always take online backups using `sqlite3.backup(dst)` or `sqlite3 db ".backup 'out.sqlite'"`.
3. **Multi-core Zstandard Compression**:
   - Database archives are compressed using `zstd -T0 -3 <file.sqlite> -o <file.sqlite.zst>`.
   - Decompression: `unzstd <file.sqlite.zst> -o <file.sqlite>`.
4. **Hugging Face LFS Artifacts**:
   - `open_agent_db_vectors.parquet` (~20 MB): 128-d dense vector embeddings over skills and tools.
   - `open_agent_db_sql.sqlite.zst` (~12.5 GB): Full 30+ GB SQLite database containing complete source code BLOBs.

---

## 4. Exit Codes & Error Fallbacks

- `0`: Success. Results found or operation completed cleanly.
- `1`: General error or missing argument.
- `2`: Database not found. Fallback: check `~/.cache/open-agent-db/` or download from Hugging Face.
- `3`: Authentication failure with Hugging Face Hub.

---

## 5. Privacy & Sanitization Gate

- NEVER commit or log API keys (`ghp_*`, `hf_*`, bearer tokens).
- NEVER log absolute user paths (e.g. `/Users/<user>`).
- Scraper engines and private crawlers MUST remain isolated in internal directories and never be ported into this public repository.
