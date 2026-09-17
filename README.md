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

### 2. Basic Usage & Taxonomy Search

```bash
# Check database catalog metrics
open-agent stats

# Search for PostgreSQL capabilities (skills or MCP servers)
open-agent search "postgres"

# Filter by Domain (Alan)
open-agent search "docker" --domain "DevOps"

# Filter by Subcategory (Kategori)
open-agent search "neural" --domain "Data & AI" --category "Machine Learning"

# Filter by Type, Domain, and minimum stars
open-agent search "database" --type mcp_server --domain "Databases" --min-stars 50

# Inspect asset details and files manifest
open-agent info "Prisma Postgres"

# Install a skill into Claude Code
open-agent install "caching-strategy-selector" --target claude

# Generate Claude Desktop MCP JSON config
open-agent install "Prisma Postgres"
```

---

## 🧭 Taxonomy & Ecosystem Domains

Open-Agent-DB structures the entire ecosystem across **12 Core Domains** and **70+ Specialized Subcategories** (compatible with SkillsMP taxonomy):

| Icon | Domain (Alan) | Key Subcategories | Typical Assets |
| :---: | :--- | :--- | :--- |
| 🧠 | **Data & AI** | Machine Learning, LLM Prompts, Data Analysis, Data Engineering | Prompt templates, RAG pipelines, model fine-tuning |
| 🛠️ | **Tools** | Debugging, Web & Automation, Utilities, System Admin | Browser automation, scrapers, shell assistants |
| 💻 | **Development** | Frontend, Backend, Developer Tools, Architecture, Mobile | React, TypeScript, Rust, API generators, Cursor rules |
| 🛡️ | **Testing & Security** | Security, Code Quality, Penetration Testing, Audits | Vulnerability scanners, SAST rules, test harnesses |
| 📈 | **Business** | Sales & Marketing, Finance, Project Management, CRM | Notion/Linear sync, financial models, SEO agents |
| 🚀 | **DevOps** | DevOps & Cloud, Git Workflows, CI/CD, Containers | Docker, Kubernetes, AWS/GCP, GitHub Actions tools |
| 📚 | **Documentation** | Technical Docs, Knowledge Base, API Specs, Education | Doc generators, markdown helpers, wikis |
| 🎨 | **Content & Media** | Documents, Design, Image/Audio Media, Copywriting | Figma integrations, SVG tools, media transcoders |
| 🔬 | **Research** | Academic, Scientific Computing, Bioinformatics, Chemistry | PubMed searchers, LaTeX formatters, lab workflows |
| 🗄️ | **Databases** | SQL Databases, Database Tools, Vector DBs, NoSQL | PostgreSQL Ops, Prisma, Redis, MongoDB servers |
| 🌱 | **Lifestyle** | Philosophy, Health & Wellness, Writing, Arts | Personal knowledge management, habits |
| ⛓️ | **Blockchain** | Smart Contracts, Web3 Tools, DeFi Protocols | Solidity auditors, Ethereum/Solana RPC tools |

---

## 💼 Career Occupations (SOC Classification) — Skills & MCPs Unified

Beyond domain categorization, Open-Agent-DB aligns all Agent Skills and Model Context Protocol (MCP) servers with the **U.S. Bureau of Labor Statistics Standard Occupational Classification (SOC)**.

This allows developers and organizations to discover complete AI tool stacks curated for real-world engineering careers:

| Icon | Career Occupation | SOC Code | Skills | MCPs | Total | Core Automation Focus |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| 💻 | **Software & Web Engineers** | `SOC 15-1252` | 4,398 | 1,539 | **5,937** | Full-stack, backend, frontend, architecture, and coding workflows |
| 🚀 | **DevOps & SRE Engineers** | `SOC 15-1250` | 2,370 | 391 | **2,761** | CI/CD pipelines, Kubernetes, Docker, Terraform, and cloud infrastructure |
| 🧠 | **AI Specialists & Data Scientists** | `SOC 15-2051` | 8,591 | 2,342 | **10,933** | LLMs, embeddings, RAG pipelines, model training, and data analysis |
| 🗄️ | **Database Administrators & Engineers** | `SOC 15-1242` | 490 | 240 | **730** | SQL query optimization, connection pools, migrations, vector stores |
| 🛡️ | **Security Analysts & QA Engineers** | `SOC 15-1212` | 2,262 | 197 | **2,459** | Vulnerability auditing, code review, fuzzing, testing, compliance |
| 📈 | **Product & Project Managers** | `SOC 11-1021` | 378 | 59 | **437** | Agile roadmaps, task coordination, Linear, Jira, team communication |
| 🎨 | **UI/UX Designers & Media Creators** | `SOC 27-1024` | 859 | 19 | **878** | Design systems, SVG icons, Figma assets, and creative media generation |
| 🔬 | **Researchers & Academic Scientists** | `SOC 19-1029` | 492 | 19 | **511** | Literature search, arXiv, PubMed, bioinformatics, LaTeX |
| 📊 | **Business & Financial Analysts** | `SOC 13-2051` | 1,164 | 74 | **1,238** | Market intelligence, valuation models, financial metrics, spreadsheets |
| 📚 | **Technical Writers & Educators** | `SOC 27-3042` | 935 | 111 | **1,046** | API documentation, markdown linting, developer guides, and wikis |

### Filtering by Occupation in CLI

```bash
# List all career tracks and asset counts
open-agent occupations
# Or via Node/npx:
npx open-agent-db occupations

# Search for assets under DevOps & SRE
open-agent search --occupation devops-sre
npx open-agent-db search --occupation devops-sre

# Combine query keywords with career tracks
open-agent search "docker" --occupation devops-sre
open-agent search "vector" --occupation ai-data-scientist
```

### Filtering by Occupation on Web

In the Web Explorer (`http://localhost:8080` or GitHub Pages):
1. Click **`[ 💼 Browse by Occupation (SOC) ]`** at the top of the browse panel.
2. Select any career pill (e.g. `🚀 DevOps & SRE Engineers (SOC 15-1250)`).
3. Result cards highlight career tags and let you jump directly to all tools for that role!

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
