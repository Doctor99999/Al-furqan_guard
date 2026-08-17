"""
Al-Furqan AI - Automated Unit & Regression Test Suite
Runs all critical tests using Python's built-in unittest framework.
"""

import unittest
import sys
from quran_guard import QuranEngine, QuranGuard, AhkamExtractor

sys.stdout.reconfigure(encoding='utf-8')


class TestQuranGuardSuite(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("\nLoading Quran Ground Truth Engine for testing...")
        cls.engine = QuranEngine()
        cls.guard = QuranGuard(cls.engine)
        cls.ahkam = AhkamExtractor(cls.engine)
        print("Engine Loaded successfully.\n")

    # 1. Manifest Dimensions
    def test_01_manifest_dimensions(self):
        self.assertEqual(len(self.engine.ayahs), 6236, "Must contain exactly 6,236 Ayahs")
        self.assertEqual(self.engine.total_tokens, 130030, "Must contain exactly 130,030 sub-tokens")
        self.assertEqual(len(self.engine.all_roots), 1651, "Must contain exactly 1,651 roots")

    # 2. Damir Mahzoof (208 tokens)
    def test_02_damir_mahzoof_tokens(self):
        zero_tokens = []
        for ayah in self.engine.ayahs.values():
            for t in ayah['tokens']:
                if t.get('form') == "":
                    zero_tokens.append(t)
        self.assertEqual(len(zero_tokens), 208)
        for t in zero_tokens:
            flags = tuple(t.get('flags', []))
            self.assertEqual(flags, ('PRON', 'SUFF', '1S'))

    # 3. Contextual Anchor & Non-Quran Noise Rejection
    def test_03_rejection_of_timestamps_and_scores(self):
        benign_texts = [
            "Встреча назначена на 14:30 в главном офисе.",
            "Футбольный матч закончился со счетом 3:0 в пользу хозяев.",
            "Версия пакета обновлена до 2:1 на сервере.",
            "Соотношение сторон экрана составляет 16:9."
        ]
        for text in benign_texts:
            res = self.guard.verify_full_text(text)
            self.assertEqual(res["total_citations_found"], 0, f"False positive in: {text}")
            self.assertEqual(res["hallucinations_count"], 0)
            self.assertEqual(res["verdict"], "NO_CITATIONS_FOUND")

    # 4. Invalid Coordinates Detection
    def test_04_invalid_coordinates(self):
        text = "Как сказано в суре 2 аяте 300, верующие должны быть терпеливы."
        res = self.guard.verify_full_text(text)
        self.assertEqual(res["hallucinations_count"], 1)
        self.assertEqual(res["hallucinations"][0]["type"], "INVALID_COORDINATE")
        self.assertLess(res["trust_score"], 100.0)

    # 5. Multi-Quote Bipartite Alignment
    def test_05_multi_quote_alignment(self):
        text = (
            "Первый аят суры 114: بِسْمِ اللَّهِ الرَّحْمَـٰنِ الرَّحِيمِ قُلْ أَعُوذُ بِرَبِّ النَّاسِ (114:1). "
            "А также первый аят суры 112: بِسْمِ اللَّهِ الرَّحْمَـٰنِ الرَّحِيمِ قُلْ هُوَ اللَّهُ أَحَدٌ (112:1)."
        )
        res = self.guard.verify_full_text(text)
        self.assertEqual(res["total_citations_found"], 2)
        self.assertEqual(res["hallucinations_count"], 0)
        self.assertEqual(len(res["verified_items"]), 2)
        self.assertEqual(res["trust_score"], 100.0)

    # 6. Tashkeel Distortion & Span-Safe Auto-Correction
    def test_06_tashkeel_distortion_and_correction(self):
        distorted = "Аят аль-Курси (2:255): اللَّهُ لَا إِلَـٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ لَا تَأْخُذُهُ سِنَةٌ وَلَا نَوْمٌ"
        res = self.guard.verify_full_text(distorted)
        self.assertEqual(res["hallucinations_count"], 1)
        self.assertIn(res["hallucinations"][0]["type"], ["TASHKEEL_DISTORTION", "TEXT_MUTATION"])
        self.assertNotEqual(res["corrected_text"], distorted)

    # 7. Exact Root Claim Verification
    def test_07_root_claims(self):
        valid = self.guard.verify_root_claim("الرَّحْمَٰنِ", "رحم", context_id="1:1")
        self.assertTrue(valid["is_valid"])
        self.assertEqual(valid["canonical_root"], "رحم")

        invalid = self.guard.verify_root_claim("الرَّحْمَٰنِ", "رمح", context_id="1:1")
        self.assertFalse(invalid["is_valid"])

    # 8. Muqatta'at Letters (Surah 42:2)
    def test_08_muqattaat_verse_handling(self):
        text = "Сура 42 аят 2: عٓسٓقٓ"
        res = self.guard.verify_full_text(text)
        self.assertEqual(res["hallucinations_count"], 0)
        self.assertEqual(len(res["verified_items"]), 1)

    # 9. Shariah Contextual Screener (Riba vs Discount)
    def test_09_shariah_contract_screening(self):
        loan_clause = "Кредитный договор: заём выдается под 18% годовых с начислением пени 0.1% за каждый день просрочки."
        audit_loan = self.ahkam.audit_contract_clause(loan_clause)
        self.assertFalse(audit_loan["is_compliant"])
        self.assertEqual(audit_loan["findings"][0]["risk_type"], "RIBA_RISK")
        self.assertIn("disclaimer", audit_loan)

        discount_clause = "В честь праздника предоставляется скидка 15% на все товары в магазине."
        audit_discount = self.ahkam.audit_contract_clause(discount_clause)
        self.assertTrue(audit_discount["is_compliant"])
        self.assertEqual(audit_discount["findings_count"], 0)


if __name__ == '__main__':
    unittest.main()
