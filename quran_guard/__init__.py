"""
Al-Furqan AI Package
Ground Truth Verification, Anti-Hallucination Guardrail, and Morphology Engine for the Quran.
"""

from .quran_engine import QuranEngine, strip_tashkeel, normalize_arabic
from .validator import QuranGuard
from .ahkam_extractor import AhkamExtractor

__all__ = ["QuranEngine", "QuranGuard", "AhkamExtractor", "strip_tashkeel", "normalize_arabic"]
