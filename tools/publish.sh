#!/usr/bin/env bash
# Open-Agent-DB Dual-Publish Script (PyPI + NPM)
set -e

DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$DIR"

echo "============================================================"
echo "🚀 Open-Agent-DB Release & Publish Pre-Flight Checks"
echo "============================================================"

# 1. NPM Dry-Run
echo "📦 1. Verifying NPM Package..."
npm pack --dry-run
echo "✓ NPM package tarball verified!"

# 2. PyPI Build & Check
echo ""
echo "🐍 2. Building PyPI Wheel & Source Distribution..."
python3 -m pip install --quiet build twine || true
python3 -m build
python3 -m twine check dist/*
echo "✓ PyPI distribution verified!"

echo ""
echo "============================================================"
echo "✨ Pre-flight checks passed! To publish live:"
echo "============================================================"
echo "👉 To publish to NPM (npx open-agent-db):"
echo "   npm publish --access public"
echo ""
echo "👉 To publish to PyPI (pip install open-agent-db):"
echo "   twine upload dist/*"
echo "============================================================"
