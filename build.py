#!/usr/bin/env python3
"""
Sketchbook static site generator.

Usage:
    1. Drop images (.jpg/.png) and text files (.txt) into src/
    2. Run: python build.py
    3. git add . && git commit && git push

Text files become text blocks in the grid.
Everything is shuffled with a deterministic seed based on file count.
"""

import hashlib
import json
import random
import re
import sys
from pathlib import Path

from PIL import Image

from config import (
    BASE_DIR, SRC_DIR, PHOTOS_DIR, THUMB_DIR, FULL_DIR, TEMPLATES_DIR,
    OUTPUT_HTML, THUMB_MAX, FULL_MAX, JPEG_QUALITY,
    IMAGE_EXTENSIONS, TEXT_EXTENSIONS,
    SITE_TITLE, SITE_SUBTITLE, CONTACT, COPYRIGHT_YEAR,
)


def make_id(filename):
    """Generate a short hash-based ID for URL fragments."""
    name = Path(filename).stem
    h = hashlib.md5(name.encode()).hexdigest()[:2]
    # Extract any number from filename, or use hash
    nums = re.findall(r'\d+', name)
    num = nums[-1][-4:] if nums else h
    return f"{h}-{num}"


def resize_and_save(img, max_size, output_path):
    """Resize image preserving aspect ratio, save as JPEG."""
    w, h = img.size
    if max(w, h) > max_size:
        ratio = max_size / max(w, h)
        new_size = (int(w * ratio), int(h * ratio))
        img = img.resize(new_size, Image.LANCZOS)

    # Convert to RGB if needed (handles RGBA, palette, etc.)
    if img.mode not in ('RGB',):
        img = img.convert('RGB')

    img.save(output_path, 'JPEG', quality=JPEG_QUALITY, optimize=True)
    return img.size


def process_images():
    """Process all image files from src/ into thumb/ and full/ directories."""
    THUMB_DIR.mkdir(parents=True, exist_ok=True)
    FULL_DIR.mkdir(parents=True, exist_ok=True)

    image_items = []

    for src_file in sorted(SRC_DIR.iterdir()):
        if src_file.suffix.lower() not in IMAGE_EXTENSIONS:
            continue

        item_id = make_id(src_file.name)
        out_name = f"{item_id}.jpg"
        thumb_path = THUMB_DIR / out_name
        full_path = FULL_DIR / out_name

        print(f"  [img] {src_file.name} → {item_id}")

        img = Image.open(src_file)

        # Auto-rotate based on EXIF orientation
        try:
            from PIL import ImageOps
            img = ImageOps.exif_transpose(img)
        except Exception:
            pass

        w, h = img.size

        # Generate thumb and full
        resize_and_save(img, THUMB_MAX, thumb_path)
        resize_and_save(img, FULL_MAX, full_path)

        image_items.append({
            "type": "image",
            "id": item_id,
            "thumb": f"photos/thumb/{out_name}",
            "full": f"photos/full/{out_name}",
            "aspect": round(w / h, 3),
            "src_name": src_file.name,
        })

    return image_items


def process_texts():
    """Process all .txt files from src/ into text items."""
    text_items = []

    for src_file in sorted(SRC_DIR.iterdir()):
        if src_file.suffix.lower() not in TEXT_EXTENSIONS:
            continue

        item_id = make_id(src_file.name)
        content = src_file.read_text(encoding="utf-8").strip()

        if not content:
            continue

        print(f"  [txt] {src_file.name} → {item_id}")

        # Escape HTML
        content = (content
                   .replace("&", "&amp;")
                   .replace("<", "&lt;")
                   .replace(">", "&gt;")
                   .replace('"', "&quot;"))

        text_items.append({
            "type": "text",
            "id": item_id,
            "text": content,
            "src_name": src_file.name,
        })

    return text_items


def shuffle_items(items):
    """Shuffle with seed based on number of files (deterministic until new files added)."""
    seed = len(items)
    rng = random.Random(seed)
    rng.shuffle(items)
    return items


def generate_html(items):
    """Generate index.html from template and items data."""
    # Read templates
    css = (TEMPLATES_DIR / "style.css").read_text(encoding="utf-8")
    js = (TEMPLATES_DIR / "script.js").read_text(encoding="utf-8")
    html = (TEMPLATES_DIR / "base.html").read_text(encoding="utf-8")

    # Prepare items JSON (strip src_name from output)
    items_clean = []
    for item in items:
        clean = {k: v for k, v in item.items() if k != "src_name"}
        items_clean.append(clean)

    items_json = json.dumps(items_clean, indent=2, ensure_ascii=False)

    # Replace JS placeholder
    js = js.replace("__ITEMS_JSON__", items_json)

    # Assemble HTML
    html = (html
            .replace("__CSS__", css)
            .replace("__JS__", js)
            .replace("__SITE_TITLE__", SITE_TITLE)
            .replace("__SITE_SUBTITLE__", SITE_SUBTITLE)
            .replace("__CONTACT__", CONTACT)
            .replace("__COPYRIGHT_YEAR__", COPYRIGHT_YEAR))

    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(f"  Generated {OUTPUT_HTML}")


def main():
    print(f"Building {SITE_TITLE}...\n")

    if not SRC_DIR.exists():
        SRC_DIR.mkdir()
        print(f"Created {SRC_DIR}/ — drop your files there and re-run.")
        sys.exit(0)

    # Process content
    image_items = process_images()
    text_items = process_texts()

    all_items = image_items + text_items
    print(f"\n  {len(image_items)} images, {len(text_items)} text blocks")

    if not all_items:
        print("  No content found in src/. Add .jpg/.png/.txt files.")
        sys.exit(1)

    # Shuffle
    all_items = shuffle_items(all_items)
    print(f"  Shuffled with seed={len(all_items)}")

    # Generate
    generate_html(all_items)

    # Write robots.txt
    robots = PHOTOS_DIR.parent / "robots.txt"
    robots.write_text(
        "User-agent: Googlebot-Image\nDisallow: /photos/\n\n"
        "User-agent: Bingbot\nDisallow: /photos/\n\n"
        "User-agent: *\nDisallow: /photos/thumb/\nDisallow: /photos/full/\n",
        encoding="utf-8"
    )

    print(f"\nDone. {len(all_items)} items total. Ready to commit & push.")


if __name__ == "__main__":
    main()
