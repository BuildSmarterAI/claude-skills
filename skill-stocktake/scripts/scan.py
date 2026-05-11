#!/usr/bin/env python3
"""scan.py — Python replacement for scan.sh on machines without jq.

Enumerates skill files under ~/.claude/skills/ (and optionally a project
skills dir), extracts frontmatter (name + description), records UTC mtime,
and emits the same JSON shape as scan.sh:

    {
      "scan_summary": {
        "global":  {"found": bool, "count": int},
        "project": {"found": bool, "path": str, "count": int}
      },
      "skills": [
        {"path": "~/...", "name": "...", "description": "...",
         "use_7d": 0, "use_30d": 0, "mtime": "YYYY-MM-DDTHH:MM:SSZ"}
      ]
    }

Usage:
    python scan.py                # default: $PWD/.claude/skills as project
    python scan.py <project_dir>  # explicit project skills dir
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


HOME = Path(os.path.expanduser("~"))
GLOBAL_DIR = Path(os.environ.get("SKILL_STOCKTAKE_GLOBAL_DIR", HOME / ".claude" / "skills"))

if len(sys.argv) > 1:
    CWD_SKILLS_DIR = Path(sys.argv[1])
else:
    CWD_SKILLS_DIR = Path(os.environ.get("SKILL_STOCKTAKE_PROJECT_DIR",
                                         Path.cwd() / ".claude" / "skills"))


def extract_frontmatter(path: Path) -> tuple[str, str]:
    """Return (name, description) from YAML frontmatter, or empty strings."""
    name = ""
    desc = ""
    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError:
        return name, desc

    in_fm = False
    seen_marker = 0
    for line in lines:
        if line.rstrip() == "---":
            seen_marker += 1
            if seen_marker == 1:
                in_fm = True
                continue
            else:
                break
        if in_fm:
            m = re.match(r'^(\w+):\s*(.*)$', line.rstrip("\n"))
            if not m:
                continue
            key, val = m.group(1), m.group(2).strip()
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1]
            if key == "name":
                name = val
            elif key == "description":
                desc = val
    return name, desc


def mtime_iso(path: Path) -> str:
    ts = path.stat().st_mtime
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def display_path(p: Path) -> str:
    s = str(p).replace("\\", "/")
    home_norm = str(HOME).replace("\\", "/")
    if s.startswith(home_norm):
        s = "~" + s[len(home_norm):]
    return s


def scan_dir(d: Path) -> list[dict]:
    if not d.is_dir():
        return []
    out = []
    for md in sorted(d.rglob("*.md")):
        name, desc = extract_frontmatter(md)
        out.append({
            "path": display_path(md),
            "name": name,
            "description": desc,
            "use_7d": 0,
            "use_30d": 0,
            "mtime": mtime_iso(md),
        })
    return out


def main() -> int:
    global_found = GLOBAL_DIR.is_dir()
    global_skills = scan_dir(GLOBAL_DIR) if global_found else []

    project_found = CWD_SKILLS_DIR.is_dir() and CWD_SKILLS_DIR != GLOBAL_DIR
    project_skills = scan_dir(CWD_SKILLS_DIR) if project_found else []

    result = {
        "scan_summary": {
            "global": {"found": global_found, "count": len(global_skills)},
            "project": {
                "found": project_found,
                "path": str(CWD_SKILLS_DIR) if project_found else "",
                "count": len(project_skills),
            },
        },
        "skills": global_skills + project_skills,
    }
    json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
