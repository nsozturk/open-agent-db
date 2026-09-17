#!/usr/bin/env python3
"""Open-Agent-DB CLI
Universal search and package manager for AI Agent Skills & MCP Servers.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# Add project root to sys.path so it works both installed and executed directly
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from cli.db import UnifiedAgentDB
from cli.installer import AssetInstaller

console = Console()


def render_banner():
    banner_text = (
        "[bold cyan]Open-Agent-DB[/bold cyan] [dim]v0.1.0[/dim] — "
        "[bold white]The Universal AI Agent Registry[/bold white]\n"
        "[dim]800K+ Agent Skills & Model Context Protocol (MCP) Servers[/dim]"
    )
    console.print(Panel(banner_text, border_style="cyan", box=box.ROUNDED))


def cmd_stats(args, db: UnifiedAgentDB):
    stats = db.get_stats()
    table = Table(title="📊 Open-Agent-DB Catalog Overview", box=box.ROUNDED)
    table.add_column("Resource Type", style="cyan", no_wrap=True)
    table.add_column("Count", style="green", justify="right")
    table.add_column("Details", style="dim")

    table.add_row("Agent Skills (Indexed)", f"{stats['total_skills']:,}", "SkillsMP, Claude, Codex, AutoGen")
    table.add_row("Downloaded Packages", f"{stats['synced_skills']:,}", "Full source code in SQLite BLOBs")
    table.add_row("MCP Servers (Total)", f"{stats['total_mcp_servers']:,}", "Glama, Smithery, Official MCP")

    for plat, count in stats.get("platforms", {}).items():
        table.add_row(f"  • {plat}", f"{count:,}", "Universal Registry")

    table.add_section()
    table.add_row("[bold white]Total Ecosystem Assets[/bold white]", f"[bold yellow]{stats['total_assets']:,}[/bold yellow]", "[bold]All Sources Combined[/bold]")
    console.print(table)


def cmd_search(args, db: UnifiedAgentDB):
    query = " ".join(args.query) if args.query else ""
    results = db.search(
        query=query,
        asset_type=args.type,
        platform=args.platform,
        min_stars=args.min_stars,
        limit=args.limit,
    )

    if not results:
        console.print(f"[yellow]No skills or MCP servers found matching '{query}'.[/yellow]")
        return

    table = Table(
        title=f"🔎 Search Results: '{query}' ({len(results)} matches)",
        box=box.ROUNDED,
        header_style="bold magenta",
    )
    table.add_column("ID / Name", style="bold cyan")
    table.add_column("Type", style="bright_blue")
    table.add_column("Platform", style="blue")
    table.add_column("Author", style="dim")
    table.add_column("Stars", justify="right", style="yellow")
    table.add_column("Description", style="white", max_width=45, overflow="ellipsis")

    for r in results:
        type_str = "[green]MCP[/green]" if r.get("item_type") == "mcp_server" else "[cyan]Skill[/cyan]"
        stars_str = f"⭐ {r.get('stars', 0):,}" if r.get("stars") else "-"
        table.add_row(
            r.get("name") or r.get("id"),
            type_str,
            r.get("source_platform", "registry"),
            (r.get("author") or "unknown")[:16],
            stars_str,
            (r.get("description") or "No description").strip().replace("\n", " "),
        )

    console.print(table)
    console.print("[dim]Tip: Run 'open-agent info <id>' for details or 'open-agent install <id>' to install.[/dim]\n")


def cmd_info(args, db: UnifiedAgentDB):
    item = db.get_item(args.identifier)
    if not item:
        console.print(f"[red]Error: Asset '{args.identifier}' not found.[/red]")
        return

    name = item.get("name") or item.get("id")
    itype = item.get("item_type", "skill").upper()
    platform = item.get("source_platform", "unknown")
    stars = item.get("stars", 0)

    details = [
        f"[bold cyan]Name:[/bold cyan] {name}",
        f"[bold cyan]Type:[/bold cyan] {itype} ({platform})",
        f"[bold cyan]Author:[/bold cyan] {item.get('author', 'Unknown')}",
        f"[bold cyan]Stars:[/bold cyan] ⭐ {stars:,}",
        f"[bold cyan]GitHub:[/bold cyan] {item.get('github_url') or 'N/A'}",
        f"[bold cyan]Install Command:[/bold cyan] [bold green]{item.get('install_command') or 'N/A'}[/bold green]",
        "",
        "[bold white]Description:[/bold white]",
        item.get("description") or "No description provided.",
    ]

    files = item.get("files", [])
    if files:
        details.append("")
        details.append(f"[bold white]Files Manifest ({len(files)} files):[/bold white]")
        for f in files[:8]:
            details.append(f"  • {f.get('path')} ({f.get('size', 0):,} bytes)")
        if len(files) > 8:
            details.append(f"  [dim]... and {len(files) - 8} more files[/dim]")

    console.print(Panel("\n".join(details), title=f"📦 {name}", border_style="cyan", box=box.ROUNDED))


def cmd_install(args, db: UnifiedAgentDB):
    item = db.get_item(args.identifier)
    if not item:
        console.print(f"[red]Error: Asset '{args.identifier}' not found in database.[/red]")
        return

    itype = item.get("item_type", "skill")

    if itype == "mcp_server":
        config = AssetInstaller.generate_mcp_config(item)
        console.print(Panel(
            json.dumps(config, indent=2),
            title=f"🔌 MCP Server Configuration for [{item.get('name')}]",
            subtitle="Add this snippet to claude_desktop_config.json or cursor mcp.json",
            border_style="green",
            box=box.ROUNDED,
        ))
        if item.get("install_command"):
            console.print(f"\nOr install via CLI: [bold green]{item.get('install_command')}[/bold green]\n")
    else:
        harness = args.target or "claude"
        if not db.skills_db_path:
            console.print("[red]Error: skillsmp.db database file not found locally to extract files.[/red]")
            return
        ok, msg = AssetInstaller.install_skill(db.skills_db_path, item, harness=harness)
        if ok:
            console.print(f"[bold green]✓ {msg}[/bold green]")
        else:
            console.print(f"[bold red]✗ Failed to install: {msg}[/bold red]")


def cmd_serve(args, db: UnifiedAgentDB):
    web_dir = Path(__file__).resolve().parent.parent / "web"
    serve_script = web_dir / "serve.py"
    port = args.port or 8080
    console.print(f"[cyan]🚀 Launching Open-Agent-DB Web Explorer on http://localhost:{port}...[/cyan]")
    cmd = [sys.executable, str(serve_script), "--port", str(port)]
    subprocess.run(cmd)


def cli_entrypoint():
    parser = argparse.ArgumentParser(
        prog="open-agent",
        description="Universal AI Agent Skills & MCP Server Package Manager",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # stats
    subparsers.add_parser("stats", help="Show database catalog overview & counts")

    # search
    search_p = subparsers.add_parser("search", help="Search skills and MCP servers")
    search_p.add_argument("query", nargs="*", help="Keywords to search for")
    search_p.add_argument("--type", choices=["skill", "mcp_server", "cursor_rule", "all"], default=None, help="Filter by item type")
    search_p.add_argument("--platform", type=str, default=None, help="Filter by platform (smithery, glama, skillsmp, etc.)")
    search_p.add_argument("--min-stars", type=int, default=0, help="Minimum star rating")
    search_p.add_argument("--limit", type=int, default=25, help="Number of results to display")

    # info
    info_p = subparsers.add_parser("info", help="Display full metadata for an asset")
    info_p.add_argument("identifier", help="Skill ID, MCP name, or slug")

    # install
    install_p = subparsers.add_parser("install", help="Install a skill or get MCP config")
    install_p.add_argument("identifier", help="Skill ID or MCP name to install")
    install_p.add_argument("--target", choices=["claude", "codex", "cursor", "agents"], default="claude", help="Agent harness target")

    # serve
    serve_p = subparsers.add_parser("serve", help="Launch interactive web search UI")
    serve_p.add_argument("--port", type=int, default=8080, help="Port to bind server (default: 8080)")

    args = parser.parse_args()

    render_banner()
    db = UnifiedAgentDB()

    if args.command == "stats":
        cmd_stats(args, db)
    elif args.command == "search":
        cmd_search(args, db)
    elif args.command == "info":
        cmd_info(args, db)
    elif args.command == "install":
        cmd_install(args, db)
    elif args.command == "serve":
        cmd_serve(args, db)
    else:
        parser.print_help()


if __name__ == "__main__":
    cli_entrypoint()
