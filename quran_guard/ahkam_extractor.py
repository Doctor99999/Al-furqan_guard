"""
Al-Furqan AI - Universal Halal & Shariah Compliance Screener
Powered by HalalKnowledgeBase (Morphological Stemming & 2000+ Term Knowledge Graph).
"""

from typing import Dict, List, Any, Optional
from .quran_engine import QuranEngine
from .halal_knowledge_base import HalalKnowledgeBase


class AhkamExtractor:
    """
    Comprehensive Islamic Compliance Classifier & Ahkam Screener:
    - Analyzes direct Quranic prohibitions (Haram).
    - Analyzes direct Quranic permissions (Halal).
    - Analyzes 500+ Food Additives (E-numbers), ingredients, and chemicals.
    - Automated Subword Stemming for Kazakh, Russian, English, and Arabic.
    """

    DISCLAIMER_KK = (
        "Ескерту: Бұл жүйе Құран үкімдері мен халықаралық Халал стандарттарының (E-кодтар, қоспалар базасы) "
        "бастапқы детерминирленген скринингі. Бұл ресми пәтуа (фатва) болып табылмайды."
    )

    DISCLAIMER_RU = (
        "Дисклеймер: Данная система выполняет детерминированный скрининг на основе аятов Корана и международных стандартов Халяль "
        "(база E-кодов и пищевых добавок). Она не является персональной фатвой."
    )

    def __init__(self, engine: Optional[QuranEngine] = None):
        self.engine = engine or QuranEngine()

    def get_category_ayahs(self, category: str, limit: int = 50) -> Dict[str, Any]:
        """Returns Ahkam records for a specific category."""
        roots_map = {
            "tahrim": ["حرم", "جنب", "نهي", "فحش", "رجس", "أثم", "خنز", "خمر", "ربو", "يسر", "موت"],
            "ibaha": ["حلل", "طيب", "نعم", "صيد", "بحر", "تجر", "بيع"],
            "wajib": ["كتب", "أمر", "فرض", "وفى", "عقد", "زكو"],
            "finance": ["ربو", "يسر", "عقد", "تجر", "وفى"],
            "justice": ["عدل", "قسط", "ظلم", "صدق", "أمن"]
        }
        if category not in roots_map:
            return {"error": f"Category '{category}' not found."}

        target_roots = roots_map[category]
        items = []
        seen = set()
        for r in target_roots:
            for match in self.engine.search_by_root(r):
                if match["id"] not in seen:
                    seen.add(match["id"])
                    items.append({
                        "id": match["id"],
                        "sura": match["sura"],
                        "ayah": match["ayah"],
                        "surah_name": match["surah_name"],
                        "text": match["text"],
                        "transliteration": match.get("transliteration", ""),
                        "translations": match.get("translations", {}),
                        "matching_tokens": match["matching_tokens"],
                        "primary_root": r
                    })
        return {
            "category": category,
            "title": category.capitalize(),
            "description": "Коранические нормы и предписания",
            "total_found": len(items),
            "items": items[:limit]
        }

    def audit_contract_clause(self, input_text: str) -> Dict[str, Any]:
        """
        Universal Halal / Haram Screener:
        Evaluates input text using the automated HalalKnowledgeBase (Stemming + Ontologies).
        """
        if not input_text or not input_text.strip():
            return {
                "is_compliant": True,
                "status": "EMPTY_INPUT",
                "overall_verdict": "UNKNOWN",
                "findings_count": 0,
                "findings": [],
                "disclaimer_kk": self.DISCLAIMER_KK,
                "disclaimer_ru": self.DISCLAIMER_RU,
                "disclaimer": self.DISCLAIMER_RU
            }

        # Match against 2,000+ morphological stems and E-codes
        findings = HalalKnowledgeBase.match_input(input_text)

        is_haram = any(f["verdict"] == "HARAM" for f in findings)
        is_doubtful = any(f["verdict"] == "DOUBTFUL" for f in findings)
        is_halal = any(f["verdict"] == "HALAL" for f in findings)

        if is_haram:
            overall_verdict = "HARAM"
            status_message = "ТЫЙЫМ САЛЫНҒАН (ХАРАМ) / ОБНАРУЖЕНЫ ПРИЗНАКИ ХАРАМА"
        elif is_doubtful:
            overall_verdict = "DOUBTFUL"
            status_message = "ШҮБӘЛІ / СОМНИТЕЛЬНОЕ (МУШТАБИХАТ - ҚҰРАМЫН ТЕКСЕРУ ҚАЖЕТ)"
        elif is_halal:
            overall_verdict = "HALAL"
            status_message = "РҰҚСАТ ЕТІЛГЕН (ХАЛАЛ) / РАЗРЕШЕНО (ХАЛЯЛЬ)"
        else:
            overall_verdict = "HALAL_DEFAULT"
            status_message = "ХАЛАЛ (НЕГІЗГІ ЕРЕЖЕ: ТЫЙЫМ БОЛМАҒАН БАРЛЫҚ НӘРСЕ АДАЛ)"

        return {
            "is_compliant": not is_haram,
            "overall_verdict": overall_verdict,
            "status_message": status_message,
            "findings_count": len(findings),
            "findings": findings,
            "disclaimer_kk": self.DISCLAIMER_KK,
            "disclaimer_ru": self.DISCLAIMER_RU,
            "disclaimer": self.DISCLAIMER_RU
        }
