# v2.0.0 — The Universal AI Agent & MCP Hub Release

Open-Agent-DB is the comprehensive, offline-first open database and semantic vector search engine for the AI Agent era.

### 🌟 Key Highlights

- **3,480,000+ Agent Assets**: Aggregated across 7 major ecosystems (Anthropic Claude Code, Cursor, OpenAI Codex, Google Gemini, GitHub Copilot, OpenCode, and Universal Agent Standards).
- **113,000+ MCP Servers**: Unified from Official Anthropic Registry, Glama.ai, Smithery.ai, and Awesome MCP.
- **Dual Hugging Face Engine (`ns0bj/open-agent-db`)**:
  - `open_agent_db_vectors.parquet` (~20 MB): Dense 128-dimensional vector embeddings for sub-millisecond similarity search via FAISS.
  - `open_agent_db_sql.sqlite.zst` (~12.5 GB): Full 30+ GB SQLite database with FTS5 search and source code BLOBs, compressed with zstd.
- **Zero-Install Run**: Try immediately via `npx open-agent-db search "<query>"`.
- **Standalone Documentation**: Official live docs deployed at https://nsozturk.github.io/open-agent-db/

### 📦 Quick Start

```bash
# Search across all indexed assets
npx open-agent-db search "postgres"

# Inspect server details & install command
npx open-agent-db info "Prisma Postgres"

# Load Vector DB in Python in 2 lines
from datasets import load_dataset
dataset = load_dataset("ns0bj/open-agent-db", data_files="open_agent_db_vectors.parquet", split="train")
```
