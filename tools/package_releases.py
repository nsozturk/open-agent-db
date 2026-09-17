#!/usr/bin/env python3
"""Release Packaging Tool for Open-Agent-DB
Compresses and splits large SQLite databases into GitHub Release compatible chunks (<95MB).
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DIST_DIR = ROOT_DIR / "dist"
CHUNK_SIZE_MB = 90


def package_db(db_path: Path, output_prefix: str):
    if not db_path.exists():
        print(f"❌ Error: Database {db_path} does not exist.")
        return

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    archive_path = DIST_DIR / f"{output_prefix}.tar.gz"

    print(f"\n📦 Compressing {db_path.name} ({db_path.stat().st_size / (1024*1024):.1f} MB)...")
    cmd_tar = [
        "tar", "-czf", str(archive_path),
        "-C", str(db_path.parent), db_path.name
    ]
    subprocess.run(cmd_tar, check=True)

    archive_size_mb = archive_path.stat().st_size / (1024 * 1024)
    print(f"✓ Created compressed archive: {archive_path.name} ({archive_size_mb:.1f} MB)")

    if archive_size_mb > CHUNK_SIZE_MB:
        print(f"✂️ Splitting archive into {CHUNK_SIZE_MB}MB chunks for GitHub Releases...")
        split_prefix = str(DIST_DIR / f"{output_prefix}.tar.gz.part_")
        cmd_split = ["split", "-b", f"{CHUNK_SIZE_MB}m", str(archive_path), split_prefix]
        subprocess.run(cmd_split, check=True)
        archive_path.unlink()  # Remove unsplit file

        parts = sorted(DIST_DIR.glob(f"{output_prefix}.tar.gz.part_*"))
        print(f"✓ Generated {len(parts)} release parts:")
        for p in parts:
            print(f"   • {p.name} ({p.stat().st_size / (1024*1024):.1f} MB)")
    else:
        print(f"✓ Archive is under {CHUNK_SIZE_MB}MB, ready for GitHub release as a single file.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Package databases for GitHub Releases")
    parser.add_argument("--registry-only", action="store_true", help="Package only universal_registry.db")
    args = parser.parse_args()

    reg_db = Path("/Users/ns0bj/Development/Fun/sirket/skills-task/data/universal_registry.db")
    if reg_db.exists():
        package_db(reg_db, "universal_registry_v0.1")

    if not args.registry_only:
        skills_db = Path("/Users/ns0bj/Development/Fun/sirket/skills-task/data/skillsmp.db")
        if skills_db.exists():
            package_db(skills_db, "skillsmp_v0.1")
