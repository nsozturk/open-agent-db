#!/usr/bin/env python3
"""Local High-Speed API & Static File Server for Open-Agent-DB
Serves the web UI locally and connects directly to local SQLite databases for full-text search.
"""

import argparse
import http.server
import json
import os
import socketserver
import sys
import urllib.parse
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from cli.db import UnifiedAgentDB

WEB_DIR = ROOT_DIR / "web"
db = UnifiedAgentDB()


class OpenAgentHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def do_HEAD(self):
        if self.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            return
        super().do_HEAD()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)

        # API: /api/status
        if path == "/api/status":
            self.send_json(200, db.get_stats())
            return

        # API: /api/occupations
        if path == "/api/occupations":
            self.send_json(200, db.get_occupations())
            return

        # API: /api/search?q=postgres&domain=Databases&category=SQL%20Databases&occupation=devops-sre&limit=30
        if path == "/api/search":
            q = params.get("q", [""])[0]
            atype = params.get("type", [None])[0]
            plat = params.get("platform", [None])[0]
            dom = params.get("domain", [None])[0]
            cat = params.get("category", [None])[0]
            occ = params.get("occupation", [None])[0]
            stars = int(params.get("min_stars", ["0"])[0] or 0)
            limit = int(params.get("limit", ["40"])[0] or 40)

            results = db.search(
                query=q,
                asset_type=atype,
                platform=plat,
                domain=dom,
                category=cat,
                occupation=occ,
                min_stars=stars,
                limit=limit,
            )
            self.send_json(200, {"query": q, "count": len(results), "results": results})
            return

        # API: /api/info?id=item_id
        if path == "/api/info":
            item_id = params.get("id", [""])[0]
            item = db.get_item(item_id)
            if item:
                self.send_json(200, item)
            else:
                self.send_json(404, {"error": "Item not found"})
            return

        # Fallback to serving static files from web/
        super().do_GET()

    def send_json(self, status_code: int, data: dict):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        # Concise logging
        sys.stderr.write(f"[Open-Agent-DB Web] {self.address_string()} - {format % args}\n")


def run_server(port: int = 8080):
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), OpenAgentHandler) as httpd:
        print(f"\n" + "=" * 65)
        print(f"🚀 Open-Agent-DB Local Web Explorer running at:")
        print(f"👉 http://localhost:{port}")
        print(f"👉 http://127.0.0.1:{port}")
        print("=" * 65)
        print(f"📁 Static Directory: {WEB_DIR}")
        print(f"💾 Skills Database: {db.skills_db_path or 'Not Connected'}")
        print(f"💾 Registry Database: {db.registry_db_path or 'Not Connected'}")
        print("Press Ctrl+C to stop.\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down server...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Open-Agent-DB Web Explorer")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on (default: 8080)")
    args = parser.parse_args()
    run_server(args.port)
