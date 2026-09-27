<div align="center">

# 🤖 Open-Agent-DB

<p>
  <img src="https://img.shields.io/badge/version-2.0.0-blue?style=flat-square" alt="Version" />
  <img src="https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/node-%3E%3D18.0-339933?style=flat-square&logo=nodedotjs&logoColor=white" alt="Node" />
  <img src="https://img.shields.io/badge/total%20assets-3.48M%2B-purple?style=flat-square" alt="Total Assets" />
  <img src="https://img.shields.io/badge/ecosystems-7%20Supported-orange?style=flat-square" alt="Ecosystems" />
  <img src="https://img.shields.io/badge/vector%20db-Parquet%20Dense%20Embeddings-success?style=flat-square" alt="Vector DB" />
  <img src="https://img.shields.io/badge/database-SQLite%20FTS5-blue?style=flat-square&logo=sqlite&logoColor=white" alt="Database" />
  <img src="https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Datasets%20%26%20Vectors-yellow?style=flat-square" alt="Hugging Face" />
  <img src="https://img.shields.io/npm/v/open-agent-db?style=flat-square&color=cb3837&logo=npm" alt="NPM Version" />
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License" />
</p>

**The Universal Open Database and Semantic Vector Search Engine for AI Agent Skills, MCP Servers, Project Directives, and Rules.**

[Features](#-features) • [Ecosystems](#-supported-ecosystems) • [Quick Start](#-quick-start) • [Vector Search](#-semantic-vector-search) • [Hugging Face](#-hugging-face-integration) • [Web Explorer](#-web-explorer) • [License](#-license)

</div>

---

## 🌟 What is Open-Agent-DB?

**Open-Agent-DB** is the comprehensive, offline-first open catalog and search engine for the AI Agent era. It unifies **3,480,000+ Agent Assets** and **113,000+ MCP (Model Context Protocol) Servers & Tools** across every major ecosystem:

* **Universal Agent Skills**: Canonical `SKILL.md` definitions, multi-step actions, and tool integration scripts.
* **Project System Rules**: `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, and `copilot-instructions.md`.
* **Agent Briefs & Personas**: Anthropic Claude Code (`.claude/agents/*.md`), OpenAI Codex (`.codex/agents/*.md`).
* **Context & Trigger Rules**: Cursor IDE rules (`.cursorrules`, `.cursor/rules/*.mdc`).
* **MCP Workflows & Servers**: Official Anthropic MCP Registry, Glama, Smithery, OpenCode (`opencode.json`, `mcp.json`).
* **Curated System Prompts**: High-impact operational templates and task instructions.

Every asset is indexed with author metadata, star ratings, and install commands, and stored with full source code inside SQLite FTS5 databases and dense **vector embeddings**.

---

## ⚡ Features

* 🔍 **Sub-second Full-Text Search (FTS5)**: Query 3.48M+ assets instantly via CLI or web.
* 🧠 **Semantic Vector Search**: Natural language similarity search using dense vector embeddings over skills, tools, and directives.
* ⚡ **Zero-Install `npx` Run**: Try instantly without downloading or configuring anything.
* 🚀 **1-Click Agent Installer**:
  * Automatically installs skills directly to `~/.claude/skills/`, `~/.codex/skills/`, or `.cursor/rules/`.
  * Generates ready-to-use JSON config for Claude Desktop (`claude_desktop_config.json`) and Cursor.
* 🌐 **Dual-Mode Web Explorer**:
  * **GitHub Pages Static Mode**: Zero backend required! Runs 100% in the browser using a client-side curated index.
  * **Local Mode**: Runs against the full SQLite database for unlimited deep searching.
* 📦 **Hugging Face Hub Native**: One-command pipeline to export metadata or dense vector embeddings directly into Hugging Face Datasets (`Parquet` / `Arrow`).

---

## 🧩 Supported Ecosystems

| Ecosystem | Primary Target Files | Asset Kinds | Description |
| :--- | :--- | :--- | :--- |
| **Universal** | `SKILL.md`, `AGENTS.md`, `AGENT.md` | `skill`, `project_rules` | Cross-platform agent rules and tool skills |
| **Claude Code** | `CLAUDE.md`, `.claude/agents/*.md`, `.claude/skills/*` | `project_rules`, `agent_brief`, `skill` | Anthropic Claude Code CLI configurations & personas |
| **Cursor** | `.cursorrules`, `.cursor/rules/*.mdc` | `project_rules`, `trigger_rule` | Cursor IDE rules and trigger-based `.mdc` specs |
| **OpenAI Codex** | `.codex/agents/*.md`, `.codex-plugin/*`, `mcp.json` | `agent_brief`, `workflow`, `project_rules` | OpenAI Codex CLI agents and plugin specifications |
| **Google Gemini** | `GEMINI.md`, `.gemini/config/skills/*` | `project_rules`, `skill` | Google Antigravity & Gemini CLI directives |
| **GitHub Copilot**| `copilot-instructions.md`, `.github/copilot-*` | `project_rules` | GitHub Copilot Workspace custom guidelines |
| **OpenCode** | `opencode.json`, `.opencode/*` | `workflow`, `skill` | OpenCode agent workflows and tool configs |

---

## 🚀 Quick Start

### 1. Instant Run (Zero Installation via `npx`)

You can run Open-Agent-DB immediately using Node.js without installing anything:

```bash
# Search across all indexed assets
npx open-agent-db search "postgres"

# Inspect MCP server details & install command
npx open-agent-db info "Prisma Postgres"

# Generate Claude Desktop MCP JSON config snippet
npx open-agent-db install "Prisma Postgres"
```

### 2. Global Installation (NPM or Pip)

#### Via NPM (Node.js ecosystem):
```bash
npm install -g open-agent-db
open-agent search "docker"
```

#### Via Pip (Python & AI ecosystem):
```bash
pip install open-agent-db
open-agent search "react"
```

---

## 🧠 Semantic Vector Search

Open-Agent-DB includes a native Vector Search Engine that allows natural language semantic queries:

```bash
# Natural language semantic query
python3 vector_search.py "automate database schema migrations with safety checks"

# Search for specific tools with top-K limit
python3 vector_search.py "ios swift metal shader visual effects" --top-k 5

# Rebuild local vector embeddings index from SQLite
python3 vector_search.py --build --limit 50000
```

---

## 🤗 Hugging Face Integration

Open-Agent-DB provides a unified Hub on Hugging Face Datasets ([`ns0bj/open-agent-db`](https://huggingface.co/datasets/ns0bj/open-agent-db)) hosting two core databases:

### 1. 🧠 Semantic Vector DB (`open_agent_db_vectors.parquet`)
Pre-computed dense 128-dimensional float32 vector embeddings over Agent Skills, MCP Servers, and Directives. Ready for instant semantic similarity search via FAISS, cosine distance, or LanceDB.

```python
from datasets import load_dataset

# Load vector embeddings directly from Hugging Face
dataset = load_dataset("ns0bj/open-agent-db", data_files="open_agent_db_vectors.parquet", split="train")

# Add native FAISS index for sub-millisecond similarity search
dataset.add_faiss_index(column="embedding")
scores, samples = dataset.get_nearest_examples("embedding", query_vector, k=5)
```

### 2. 🗄️ Full Universal SQL Database (`open_agent_db_sql.sqlite.zst`)
The complete 30+ GB offline SQLite database with full-text search (FTS5), schema indices, and raw BLOB files for 3.48M+ assets, compressed down to ~12 GB with Zstandard:

```bash
# Download compressed database via huggingface-cli
hf download ns0bj/open-agent-db open_agent_db_sql.sqlite.zst --repo-type dataset --local-dir ./data

# Decompress to pristine 31 GB SQLite database (takes ~10 seconds)
unzstd ./data/open_agent_db_sql.sqlite.zst -o ./data/open_agent_db.sqlite

# Query immediately with SQLite or DuckDB
sqlite3 ./data/open_agent_db.sqlite "SELECT count(*) FROM assets;"
```

---

## 🌐 Web Explorer

Open-Agent-DB includes a fast web explorer located in [`web/`](web/):

* **Static Mode**: Runs 100% on GitHub Pages without a backend.
* **Local Mode**: Point it to your local SQLite database for instantaneous queries across all 3.48M assets.

To run locally:
```bash
cd web && npx serve .
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) - see the LICENSE file for details.

Developed and maintained by **Enes Öztürk** ([@nsozturk](https://github.com/nsozturk)).
