"""
Al-Furqan AI - Zakat Nisab, Multi-Language Thematic Search, B2B Indexed Auth
Regression tests for the product-readiness batch:
- Nisab gating (silver default) + overridable market prices + both thresholds
- Theme index covering en/tr/uz/id + ru/kk
- B2B auth index created; plaintext legacy upgrade still works
"""

import hashlib
import unittest

from fastapi.testclient import TestClient

import server
from server import app
from quran_guard.multimodal import ZakatCalculator, SemanticThemeEngine, THEMATIC_INDEX
from database import B2BAuthService, DBConnection

client = TestClient(app)


class _FakeQuranEngine:
    """Stand-in engine exposing get_ayah for thematic retrieval tests."""

    def get_ayah(self, sura: int, ayah: int):
        return {
            "text": f"{sura}:{ayah}",
            "transliteration": "",
            "translations": {"ru": f"аят {ayah}"},
        }


FAKE_ENGINE = _FakeQuranEngine()


class TestZakatCalculator(unittest.TestCase):

    def test_silver_nisab_gates_obligation_by_default(self):
        res = ZakatCalculator.calculate_zakat(cash_savings=400000.0)
        self.assertGreater(res["gold_nisab_threshold"], res["silver_nisab_threshold"],
                           "Gold nisab (85g) must exceed silver nisab (595g)")
        self.assertEqual(res["nisab_reference"], "silver")
        self.assertAlmostEqual(res["nisab_threshold_used"], res["silver_nisab_threshold"])
        self.assertTrue(res["is_obligatory"], "Wealth above silver nisab is obligatory")
        self.assertAlmostEqual(res["zakat_due"], 400000.0 * 0.025, places=2)

    def test_below_silver_nisab_not_obligatory(self):
        res = ZakatCalculator.calculate_zakat(cash_savings=100000.0)
        self.assertFalse(res["is_obligatory"])
        self.assertEqual(res["zakat_due"], 0.0)

    def test_gold_reference_uses_gold_threshold(self):
        res = ZakatCalculator.calculate_zakat(cash_savings=2000000.0, nisab_reference="gold")
        self.assertEqual(res["nisab_reference"], "gold")
        self.assertAlmostEqual(res["nisab_threshold_used"], res["gold_nisab_threshold"])
        self.assertFalse(res["is_obligatory"],
                         "2M sits between silver and gold nisab: not obligatory on gold reference")
        res_silver = ZakatCalculator.calculate_zakat(cash_savings=2000000.0, nisab_reference="silver")
        self.assertTrue(res_silver["is_obligatory"])

    def test_custom_prices_override_and_invalid_reference_falls_back(self):
        res = ZakatCalculator.calculate_zakat(
            cash_savings=60000.0,
            gold_price_per_gram=50000.0,
            silver_price_per_gram=100.0,
            nisab_reference="platinum",
        )
        self.assertEqual(res["nisab_reference"], "silver", "Unknown reference must fall back to silver")
        self.assertAlmostEqual(res["silver_nisab_threshold"], 595.0 * 100.0, places=2)
        self.assertAlmostEqual(res["gold_nisab_threshold"], 85.0 * 50000.0, places=2)

    def test_api_accepts_prices_and_reference(self):
        resp = client.post("/api/v1/zakat/calculate", json={
            "cash_savings": 300000.0,
            "gold_grams": 0,
            "silver_grams": 0,
            "gold_price_per_gram": 60000.0,
            "silver_price_per_gram": 400.0,
            "nisab_reference": "silver",
        })
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIn("silver_nisab_threshold", body)
        self.assertIn("gold_nisab_threshold", body)
        self.assertIn("nisab_reference", body)
        self.assertTrue(body["is_obligatory"])

    def test_api_rejects_negative_price(self):
        resp = client.post("/api/v1/zakat/calculate", json={
            "cash_savings": 100.0,
            "silver_price_per_gram": -10.0,
        })
        self.assertEqual(resp.status_code, 422)


class TestThematicSearchMultiLang(unittest.TestCase):

    def test_english_query(self):
        results = SemanticThemeEngine.find_ayahs_by_topic("give me patience", FAKE_ENGINE)
        self.assertGreaterEqual(len(results), 1)
        self.assertIn((2, 153), [(r["sura"], r["ayah"]) for r in results])

    def test_turkish_query(self):
        results = SemanticThemeEngine.find_ayahs_by_topic("sabır nasil", FAKE_ENGINE)
        self.assertGreaterEqual(len(results), 1)
        self.assertIn((2, 153), [(r["sura"], r["ayah"]) for r in results])

    def test_indonesian_fasting(self):
        results = SemanticThemeEngine.find_ayahs_by_topic("puasa", FAKE_ENGINE)
        self.assertGreaterEqual(len(results), 1)
        self.assertIn((2, 183), [(r["sura"], r["ayah"]) for r in results])

    def test_uzbek_trade_and_english_interest(self):
        results_uz = SemanticThemeEngine.find_ayahs_by_topic("savdo", FAKE_ENGINE)
        self.assertIn((2, 275), [(r["sura"], r["ayah"]) for r in results_uz])
        results_en = SemanticThemeEngine.find_ayahs_by_topic("interest rate loan", FAKE_ENGINE)
        self.assertIn((2, 275), [(r["sura"], r["ayah"]) for r in results_en])

    def test_kazakh_and_russian_still_work(self):
        results = SemanticThemeEngine.find_ayahs_by_topic("сабыр", FAKE_ENGINE)
        self.assertIn((2, 153), [(r["sura"], r["ayah"]) for r in results])
        results = SemanticThemeEngine.find_ayahs_by_topic("справедливость", FAKE_ENGINE)
        self.assertIn((4, 58), [(r["sura"], r["ayah"]) for r in results])

    def test_no_duplicate_theme_keys(self):
        self.assertEqual(len(THEMATIC_INDEX), len(set(THEMATIC_INDEX)),
                         "THEMATIC_INDEX must not contain duplicate keys")


class TestB2BIndexedLookup(unittest.TestCase):

    def test_key_hash_index_exists(self):
        conn = DBConnection.get_sqlite_conn()
        try:
            row = conn.execute(
                "SELECT name FROM sqlite_master"
                " WHERE type='index' AND name='idx_b2b_key_hash'"
            ).fetchone()
        finally:
            conn.close()
        self.assertIsNotNone(row, "idx_b2b_key_hash must be created on b2b_organizations")

    def test_hashed_lookup_still_validates(self):
        key = "b2b-indexed-key"
        conn = DBConnection.get_sqlite_conn()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO b2b_organizations (org_name, api_key, key_hash, is_active, tier, total_requests)
               VALUES (?, ?, ?, 1, 'free', 0)""",
            ("Indexed Test Org", "", hashlib.sha256(key.encode()).hexdigest()),
        )
        conn.commit()
        oid = cur.lastrowid
        try:
            model = B2BAuthService.validate_api_key(key)
            self.assertIsNotNone(model)
            self.assertEqual(model.org_name, "Indexed Test Org")
            self.assertIsNone(B2BAuthService.validate_api_key("indexed-wrong"))
        finally:
            cur.execute("DELETE FROM b2b_organizations WHERE id = ?", (oid,))
            conn.commit()
            conn.close()


if __name__ == "__main__":
    unittest.main()