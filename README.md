<div align="center">

# 🤖 Open-Agent-DB

**The Universal Open Registry for AI Agent Skills & Model Context Protocol (MCP) Servers**

[![Total Assets](https://img.shields.io/badge/Total%20Assets-800K%2B-emerald.svg?style=for-the-badge)](https://github.com)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-637K%2B-cyan.svg?style=for-the-badge)](https://github.com)
[![MCP Servers](https://img.shields.io/badge/MCP%20Servers-113K%2B-blue.svg?style=for-the-badge)](https://github.com)
[![NPM Version](https://img.shields.io/npm/v/open-agent-db?style=for-the-badge&color=cb3837&logo=npm)](https://www.npmjs.com/package/open-agent-db)
[![PyPI Version](https://img.shields.io/pypi/v/open-agent-db?style=for-the-badge&color=3775a9&logo=pypi)](https://pypi.org/project/open-agent-db/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-cli-usage">CLI Usage</a> •
  <a href="#-web-explorer">Web Explorer</a> •
  <a href="#-dataset--releases">Dataset & Releases</a> •
  <a href="#-schema">Schema</a>
</p>

</div>

---

## 🌟 What is Open-Agent-DB?

**Open-Agent-DB** is the comprehensive, offline-first open catalog for the AI Agent era. It unifies **637,000+ Agent Skills** and **113,000+ MCP (Model Context Protocol) Servers and Tools** across every major ecosystem:

- **Agent Skills**: Anthropic Claude Code, OpenAI Codex, AutoGen, OpenCode, SkillsMP, Skills.sh.
- **MCP Servers & Tools**: Official Anthropic MCP Registry, Glama, Smithery, MCP.Directory, Awesome-MCP.
- **IDE Capabilities**: Cursor Rules, Prompt engineering modules, autonomous workflows.

Every asset is indexed with author metadata, star ratings, install commands, tool capabilities, and stored with full source code inside SQLite FTS5 databases.

---

## ⚡ Features

- 🔍 **Sub-second Full-Text Search**: Query 800K+ assets instantly via CLI or web.
- ⚡ **Zero-Install `npx` Run**: Try instantly without downloading or configuring anything.
- 🚀 **1-Click Agent Installer**:
  - Automatically installs skills directly to `~/.claude/skills/`, `~/.codex/skills/`, or `.cursor/rules/`.
  - Generates ready-to-use JSON config for Claude Desktop (`claude_desktop_config.json`) and Cursor.
- 🌐 **Dual-Mode Web Explorer**:
  - **GitHub Pages Static Mode**: Zero backend required! Runs 100% in the browser using a client-side curated index.
  - **Local Mode**: Runs against the full 5.6 GB SQLite database for unlimited deep searching.
- 📦 **Open Data & Releases**: Download complete offline SQLite databases or Parquet datasets.

---

## 🚀 Quick Start

### 1. Instant Run (Zero Installation via `npx`)

You can run Open-Agent-DB immediately using Node.js without installing anything:

```bash
# Search across 800K+ assets
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

*(Or clone the repository and run `pip install -e .`)*

### 2. Basic Usage

```bash
# Check database catalog metrics
open-agent stats

# Search for PostgreSQL capabilities (skills or MCP servers)
open-agent search "postgres"

# Filter by MCP servers only
open-agent search "github" --type mcp_server --min-stars 50

# Inspect asset details and files manifest
open-agent info "Prisma Postgres"

# Install a skill into Claude Code
open-agent install "caching-strategy-selector" --target claude

# Generate Claude Desktop MCP JSON config
open-agent install "Prisma Postgres"
```

---

## 🖥️ Web Explorer

Open-Agent-DB comes with a modern, dark-themed responsive single-page application.

### Running Locally (Full 5.6 GB SQLite Search)

```bash
open-agent serve --port 8080
```
Open [http://localhost:8080](http://localhost:8080) in your browser to search across the entire local dataset with instant autocomplete, category filters, and 1-click copy buttons.

### Deploying to GitHub Pages

The `web/` directory is designed to work statically on GitHub Pages with zero server setup:
1. Push the repository to GitHub.
2. Go to **Settings > Pages > Build and deployment > Source: GitHub Actions**.
3. The included `.github/workflows/deploy-pages.yml` will automatically build and publish your live search catalog!

---

## 📊 Catalog Distribution

```text
╭────────────────────────────────┬─────────┬──────────────────────────────────╮
│ Resource Type                  │   Count │ Details                          │
├────────────────────────────────┼─────────┼──────────────────────────────────┤
│ Agent Skills (Indexed)         │ 637,876 │ SkillsMP, Claude, Codex, AutoGen │
│ Downloaded Packages            │ 326,702 │ Full source code in SQLite BLOBs │
│ MCP Servers (Total)            │ 113,566 │ Glama, Smithery, Official MCP    │
│   • glama:mcp_server           │  86,821 │ Universal Registry               │
│   • official_mcp:mcp_server    │  15,661 │ Universal Registry               │
│   • skills_sh:skill            │  16,356 │ Universal Registry               │
│   • mcp_directory:skill        │   9,293 │ Universal Registry               │
│   • agensi:skill               │   5,810 │ Universal Registry               │
│   • smithery:mcp_server        │   5,175 │ Universal Registry               │
│   • smithery:skill             │   5,000 │ Universal Registry               │
│   • awesome_mcp:mcp_server     │   3,893 │ Universal Registry               │
│   • cursorrules:cursor_rule    │     257 │ Universal Registry               │
├────────────────────────────────┼─────────┼──────────────────────────────────┤
│ Total Ecosystem Assets         │ 788,158 │ All Sources Combined             │
╰────────────────────────────────┴─────────┴──────────────────────────────────╯
```

---

## 📁 Repository Structure

```text
open-agent-db/
├── README.md                      # Project documentation
├── LICENSE                        # MIT License
├── pyproject.toml                 # Package specification
│
├── cli/                           # Command-Line Interface
│   ├── main.py                    # CLI entrypoint (search, info, install, serve, stats)
│   ├── db.py                      # Unified database access layer
│   └── installer.py               # Auto-installer for Claude, Codex, Cursor & MCP
│
├── web/                           # GitHub Pages Static Site + Local Explorer
│   ├── index.html                 # Single-page web app
│   ├── app.js                     # Dual-mode search engine (client-side + local API)
│   ├── style.css                  # Custom styling and transitions
│   ├── serve.py                   # Local server with SQLite FTS5 backend
│   └── data/
│       ├── catalog_index.json     # 27,000+ curated assets (instant browser search)
│       └── stats.json             # Ecosystem totals and platform breakdown
│
├── tools/                         # Maintenance and packaging scripts
│   ├── build_web_index.py         # Static web index builder
│   └── package_releases.py        # Release packager & chunk splitter for GitHub
│
└── .github/workflows/
    └── deploy-pages.yml           # GitHub Pages auto-deploy workflow
```

---

## 📜 License

- **Code & Tools**: Licensed under the [MIT License](LICENSE).
- **Aggregated Dataset**: Available for open research and public use under [ODbL / Open Data Commons](https://opendatacommons.org/licenses/odbl/).
