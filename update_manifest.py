#!/usr/bin/env python3
"""Update stories/manifest.json with all story JSON filenames (without .json) in stories/."""
import json
from pathlib import Path

root = Path(__file__).resolve().parent
stories_dir = root / "stories"
names = sorted(p.stem for p in stories_dir.glob("*.json") if p.name != "manifest.json")
(stories_dir / "manifest.json").write_text(json.dumps(names, indent=2) + "\n", encoding="utf-8")
print("manifest.json updated:", names)
