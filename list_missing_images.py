#!/usr/bin/env python3
"""
List missing story images. For each missing image, prints the filename to use
and the full prompt (base style + story prompt) for AI image generation.
Searches the stories/ folder for *.json. Expects images in ./images/.
Usage: python3 list_missing_images.py
"""

import json
import os
import sys
from pathlib import Path

STORIES_DIR = Path("stories")
IMAGES_DIR = Path("images")
BASE_PROMPT = (
    "I am building a story app where I write different story. I need to generate images. "
    "Always use this style, transparent background and black lines, like a drawn sketch of the actual prompt. And no text. "
    "Aspect ratio 16:9. Generate image for this prompt: "
)


def collect_images(story_path: Path, data: dict) -> list[tuple[str, str]]:
    """Return list of (filename, story_prompt) for thumbnail + content images."""
    out = []
    # Thumbnail
    if "thumbnail" in data and data["thumbnail"]:
        t = data["thumbnail"]
        fn = t.get("filename", "").strip()
        if fn:
            if not fn.lower().endswith(".png"):
                fn = fn + ".png"
            out.append((fn, t.get("generation_prompt", "")))
    # Content images
    for item in data.get("content") or []:
        if item.get("type") != "image":
            continue
        fn = item.get("filename", "").strip()
        if not fn:
            continue
        if not fn.lower().endswith(".png"):
            fn = fn + ".png"
        out.append((fn, item.get("generation_prompt", "")))
    return out


def main() -> None:
    root = Path(__file__).resolve().parent
    os.chdir(root)
    images_dir = root / IMAGES_DIR
    images_dir.mkdir(exist_ok=True)

    stories_dir = root / STORIES_DIR
    paths = sorted(
        p for p in (stories_dir.glob("*.json") if stories_dir.is_dir() else [])
        if p.name != "manifest.json"
    )

    if not paths:
        print("No story JSONs found in stories/.", file=sys.stderr)
        sys.exit(1)

    base_prompt = BASE_PROMPT.strip()
    any_missing = False

    for path in sorted(paths):
        if not path.is_file():
            print(f"Skip (not a file): {path}", file=sys.stderr)
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"Error reading {path}: {e}", file=sys.stderr)
            continue

        if not isinstance(data, dict):
            continue

        images = collect_images(path, data)
        story_name = path.stem
        for filename, story_prompt in images:
            full_path = images_dir / filename
            if full_path.is_file():
                continue
            any_missing = True
            full_prompt = base_prompt + story_prompt if story_prompt else base_prompt.rstrip()
            print(f"--- {story_name}: {filename} ---")
            print(f"Save as: {filename}")
            print(f"Full prompt:\n{full_prompt}")
            print()

    if not any_missing:
        print("No missing images.")


if __name__ == "__main__":
    main()
