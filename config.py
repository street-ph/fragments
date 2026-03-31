"""Sketchbook site configuration."""
from pathlib import Path

# Directories
BASE_DIR = Path(__file__).parent
SRC_DIR = BASE_DIR / "src"
PHOTOS_DIR = BASE_DIR / "photos"
THUMB_DIR = PHOTOS_DIR / "thumb"
FULL_DIR = PHOTOS_DIR / "full"
TEMPLATES_DIR = BASE_DIR / "templates"
OUTPUT_HTML = BASE_DIR / "index.html"

# Image processing
THUMB_MAX = 800
FULL_MAX = 2000
JPEG_QUALITY = 82

# Site
SITE_TITLE = "fragments"
SITE_SUBTITLE = "dmitrii kremenskii"
CONTACT = "hi@kremenskii.art"
COPYRIGHT_YEAR = "2026"

# Supported file types
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}
TEXT_EXTENSIONS = {".txt"}
