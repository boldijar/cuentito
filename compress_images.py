#!/usr/bin/env python3
"""
Remove transparency (composite onto white) and compress images in place.
Defaults to the project images/ folder. Overwrites originals with compressed PNGs.
Usage: python3 compress_images.py [folder]
       (default folder: images)
"""
import os
import sys
from pathlib import Path

from PIL import Image

# White background when removing transparency (use (0,0,0) for black)
BG_COLOR = (255, 255, 255)
# PNG compression: 9 = max (smaller file, slower)
PNG_COMPRESS_LEVEL = 9


def remove_transparency(img, bg_color=(255, 255, 255)):
    """Composite image onto a solid background. Returns RGB image."""
    if img.mode in ("RGBA", "LA"):
        background = Image.new("RGB", img.size, bg_color)
        if img.mode == "RGBA":
            background.paste(img, mask=img.split()[-1])  # use alpha as mask
        else:
            background.paste(img, mask=img.split()[-1])
        return background
    if img.mode == "P":
        if "transparency" in img.info:
            img = img.convert("RGBA")
            background = Image.new("RGB", img.size, bg_color)
            background.paste(img, mask=img.split()[-1])
            return background
        return img.convert("RGB")
    if "transparency" in img.info:
        img = img.convert("RGBA")
        background = Image.new("RGB", img.size, bg_color)
        background.paste(img, mask=img.split()[-1])
        return background
    return img.convert("RGB")


def compress_image(path: Path) -> None:
    """Overwrite path with compressed, non-transparent PNG."""
    try:
        with Image.open(path) as img:
            img = remove_transparency(img, BG_COLOR)
            # Write to temp then replace, so we don't corrupt on failure
            tmp = path.with_suffix(path.suffix + ".tmp")
            img.save(
                tmp,
                format="PNG",
                compress_level=PNG_COMPRESS_LEVEL,
                optimize=True,
            )
            tmp.replace(path)
        print(f"✔ {path.name}")
    except Exception as e:
        print(f"✘ {path.name}: {e}")


def main():
    root = Path(__file__).resolve().parent
    if len(sys.argv) > 1:
        folder = Path(sys.argv[1])
        if not folder.is_absolute():
            folder = root / folder
    else:
        folder = root / "images"

    if not folder.is_dir():
        print(f"Folder does not exist: {folder}")
        sys.exit(1)

    exts = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff")
    count = 0
    for path in sorted(folder.iterdir()):
        if path.suffix.lower() in exts:
            compress_image(path)
            count += 1

    if count == 0:
        print("No images found.")
    else:
        print(f"Done. Processed {count} image(s) in {folder}")


if __name__ == "__main__":
    main()
