---
language:
- en
license: mit
task_categories:
- text-retrieval
- feature-extraction
tags:
- ai-agents
- mcp-servers
- model-context-protocol
- claude-skills
- cursor-rules
- vector-database
- agentic-ai
- sqlite
size_categories:
- 1M<n<10M
---

# 🤖 Open-Agent-DB — The Universal AI Agent & MCP Hub

**The Universal Open Registry and Semantic Vector Search Engine for AI Agent Skills, MCP Servers, Project Rules, and Autonomous Directives.**

- **GitHub Repository**: [https://github.com/nsozturk/open-agent-db](https://github.com/nsozturk/open-agent-db)
- **Total Ecosystem Assets**: **3,480,000+** indexed assets
- **Ecosystems**: Claude Code, Cursor, OpenAI Codex, Google Gemini, GitHub Copilot, OpenCode, and Universal Agent Standards.

---

## 📂 Repository Contents

This repository follows a **Unified Hub Model**, containing both vector embeddings and the complete offline database:

### 1. 🧠 Semantic Vector DB (`open_agent_db_vectors.parquet`)
- Dense 128-dimensional float32 vector embeddings over Agent Skills, MCP Servers, and Directives.
- Standard Parquet format, previewable directly in the Hugging Face Dataset Viewer.
- Ready for instant semantic similarity search via FAISS, cosine distance, or LanceDB.

### 2. 🗄️ Universal SQL Database (`open_agent_db_sql.sqlite.zst`)
- The full 30+ GB offline SQLite database with full-text search (FTS5), schema indices, and raw BLOB files for 3.48M+ assets.
- Highly compressed with Zstandard (~12 GB download, expands to 31 GB in ~10 seconds).
- Zero dependencies needed to query: use SQLite, DuckDB, or Python.

---

## 🚀 Quick Usage in Python

### 1. Semantic Vector Search with Hugging Face Datasets & FAISS

```python
from datasets import load_dataset
import numpy as np

# Load pre-computed vector dataset from Hugging Face
dataset = load_dataset('ns0bj/open-agent-db', data_files='open_agent_db_vectors.parquet', split='train')

print(f"Total vector records: {len(dataset):,}")
print("Sample record:", dataset[0])

# Add native FAISS index for sub-millisecond similarity search
dataset.add_faiss_index(column="embedding")

# Example query vector (128-dimensional)
query_vector = np.zeros(128, dtype=np.float32)
scores, samples = dataset.get_nearest_examples("embedding", query_vector, k=5)
```

### 2. Downloading & Using the Complete SQL Database

```bash
# Download compressed database via huggingface-cli
hf download ns0bj/open-agent-db open_agent_db_sql.sqlite.zst --repo-type dataset --local-dir ./data

# Decompress in seconds
unzstd ./data/open_agent_db_sql.sqlite.zst -o ./data/open_agent_db.sqlite

# Query immediately with SQLite
sqlite3 ./data/open_agent_db.sqlite "SELECT count(*) FROM assets;"
```

```python
import sqlite3

conn = sqlite3.connect("data/open_agent_db.sqlite")
cursor = conn.cursor()
cursor.execute("SELECT name, ecosystem, stars, github_url FROM assets WHERE stars > 1000 ORDER BY stars DESC LIMIT 10")
for row in cursor.fetchall():
    print(row)
```

---

## 📄 License

MIT License. Created and maintained by [Enes Öztürk (@nsozturk)](https://github.com/nsozturk).
