"""
Al-Furqan AI - Configuration and Environment Settings
Provides portable, cross-platform paths for manifest, reference corpora, and translations.
"""

import os
from pathlib import Path

# Base project directory (auto-detected relative to this config file or via ENV)
BASE_DIR = Path(os.getenv("QURAN_BASE_DIR", Path(__file__).resolve().parent.parent))

# Dataset filepaths
MANIFEST_PATH = os.getenv("QURAN_MANIFEST_PATH", str(BASE_DIR / "security_manifest.jsonl"))
TRANSLATIONS_PATH = os.getenv("QURAN_TRANSLATIONS_PATH", str(BASE_DIR / "translations" / "translations.json"))
UI_DIR = os.getenv("QURAN_UI_DIR", str(BASE_DIR / "ui"))

# Server settings
DEFAULT_HOST = os.getenv("HOST", "127.0.0.1")
DEFAULT_PORT = int(os.getenv("PORT", 8000))
# Explicit allow-list only (comma-separated origins). Empty = same-origin policy, no cross-origin browser access.
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]
