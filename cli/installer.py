"""Asset Installer for Open-Agent-DB
Installs Skills and MCP servers into Claude Code, OpenAI Codex, Cursor, and standard harnesses.
"""

import json
import os
import shutil
import sqlite3
import sys
import zlib
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


HARNESS_SKILL_PATHS = {
    "claude": Path.home() / ".claude" / "skills",
    "codex": Path.home() / ".codex" / "skills",
    "cursor": Path.cwd() / ".cursor" / "rules",
    "agents": Path.home() / ".agents" / "skills",
}

CLAUDE_DESKTOP_CONFIG = (
    Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
)


class AssetInstaller:
    @staticmethod
    def extract_skill_files(
        db_path: Path, skill_id: str, target_dir: Path
    ) -> Tuple[bool, int, str]:
        """Extract all files for a skill from SQLite compressed BLOBs onto disk."""
        if not db_path.exists():
            return False, 0, f"Database not found at {db_path}"

        target_dir.mkdir(parents=True, exist_ok=True)
        count = 0

        try:
            conn = sqlite3.connect(f"file:{db_path.resolve()}?mode=ro", uri=True)
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT path, content, is_compressed FROM files WHERE skill_id = ?",
                (skill_id,),
            ).fetchall()

            if not rows:
                # Skill files might not be downloaded yet in this DB instance
                return False, 0, "No downloaded file contents found for this skill in the local database."

            for r in rows:
                p = r["path"]
                content = r["content"]
                if not content:
                    continue
                if r["is_compressed"]:
                    try:
                        content = zlib.decompress(content)
                    except Exception:
                        pass
                dest_file = target_dir / p
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                dest_file.write_bytes(content)
                count += 1

            conn.close()
            return count > 0, count, f"Successfully extracted {count} files to {target_dir}"
        except Exception as e:
            return False, 0, str(e)

    @staticmethod
    def install_skill(
        db_path: Path, skill_data: Dict[str, Any], harness: str = "claude"
    ) -> Tuple[bool, str]:
        """Install a skill package directly into the requested AI agent harness directory."""
        skill_id = skill_data.get("id") or skill_data.get("name")
        skill_name = skill_data.get("name") or skill_id

        dest_base = HARNESS_SKILL_PATHS.get(harness.lower())
        if not dest_base:
            return False, f"Unknown harness '{harness}'. Supported: claude, codex, cursor, agents"

        target_dir = dest_base / skill_name
        ok, count, msg = AssetInstaller.extract_skill_files(db_path, skill_id, target_dir)

        if not ok:
            # Fallback: Write a minimal SKILL.md from metadata if BLOB was missing
            target_dir.mkdir(parents=True, exist_ok=True)
            skill_md = target_dir / "SKILL.md"
            meta = [
                f"# {skill_name}",
                f"**Author**: {skill_data.get('author', 'Unknown')}",
                f"**Source**: {skill_data.get('github_url', 'N/A')}",
                "",
                "## Description",
                skill_data.get("description", "No description provided."),
            ]
            skill_md.write_text("\n".join(meta), encoding="utf-8")
            return True, f"Created {skill_md} ({harness.capitalize()} harness)"

        return True, f"Installed {count} files to {target_dir} ({harness.capitalize()} harness)"

    @staticmethod
    def generate_mcp_config(mcp_item: Dict[str, Any]) -> Dict[str, Any]:
        """Generate MCP client JSON configuration for Claude Desktop / Cursor."""
        name = mcp_item.get("name", "mcp-server")
        cmd = mcp_item.get("install_command") or ""

        # Default fallback standard npx/uvx runner
        args = []
        command = "npx"

        if "@smithery/cli" in cmd:
            parts = cmd.split()
            command = parts[0]
            args = parts[1:]
        elif cmd.startswith("npx"):
            parts = cmd.split()
            command = "npx"
            args = parts[1:]
        else:
            args = ["-y", name]

        return {
            "mcpServers": {
                name: {
                    "command": command,
                    "args": args,
                }
            }
        }
