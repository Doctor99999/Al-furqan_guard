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
QURAN_TXT_PATH = os.getenv("QURAN_TXT_PATH", str(BASE_DIR / "quran.txt"))
TRANSLATIONS_PATH = os.getenv("QURAN_TRANSLATIONS_PATH", str(BASE_DIR / "translations" / "translations.json"))
UI_DIR = os.getenv("QURAN_UI_DIR", str(BASE_DIR / "ui"))

# Server settings
DEFAULT_HOST = os.getenv("HOST", "127.0.0.1")
DEFAULT_PORT = int(os.getenv("PORT", 8000))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
