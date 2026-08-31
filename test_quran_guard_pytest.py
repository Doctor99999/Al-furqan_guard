"""
Al-Furqan AI - Rigorous PyTest Test Suite
Unit and regression tests for Ground Truth Anti-Hallucination Engine.
"""

import pytest
from quran_guard import QuranEngine, QuranGuard, AhkamExtractor


@pytest.fixture(scope="module")
def engine():
    return QuranEngine()


@pytest.fixture(scope="module")
def guard(engine):
    return QuranGuard(engine)


@pytest.fixture(scope="module")
def ahkam(engine):
    return AhkamExtractor(engine)


# 1. Corpus & Manifest Integrity Tests
def test_verify_full_text_compat_contract(guard):
    """Guard report must expose claims_detected/is_valid/violations for bot.py & ui/app.js."""
    result = guard.verify_full_text("Простой текст без цитат Корана.")
    for key in ("claims_detected", "is_valid", "violations"):
        assert key in result, f"Guard report must expose compat key '{key}'"
    assert isinstance(result["claims_detected"], bool)
    assert isinstance(result["is_valid"], bool)
    assert isinstance(result["violations"], list)
    # Each violation must carry 'details' consumed by the UI display
    for v in result["violations"]:
        assert "details" in v


def test_manifest_dimensions(engine):
    assert len(engine.ayahs) == 6236, "Must contain exactly 6,236 Ayahs"
    assert engine.total_tokens == 130030, "Must contain exactly 130,030 sub-tokens"
    assert len(engine.all_roots) == 1651, "Must contain exactly 1,651 roots"


def test_damir_mahzoof_tokens(engine):
    """Verifies that all 208 zero-form tokens are strictly Damir Mahzoof ('PRON', 'SUFF', '1S')."""
    zero_tokens = []
    for ayah in engine.ayahs.values():
        for t in ayah['tokens']:
            if t.get('form') == "":
                zero_tokens.append(t)
    assert len(zero_tokens) == 208
    for t in zero_tokens:
        flags = tuple(t.get('flags', []))
        assert flags == ('PRON', 'SUFF', '1S'), f"Unexpected zero token flags: {flags}"


# 2. Contextual Anchor & Non-Quran Noise Rejection Tests
def test_rejection_of_timestamps_and_scores(guard):
    """Ensures timestamps like 14:30 or game scores 3:0 do NOT trigger false hallucination warnings."""
    benign_texts = [
        "Встреча назначена на 14:30 в главном офисе.",
        "Футбольный матч закончился со счетом 3:0 в пользу хозяев.",
        "Версия пакета обновлена до 2:1 на сервере.",
        "Соотношение сторон экрана составляет 16:9."
    ]
    for text in benign_texts:
        res = guard.verify_full_text(text)
        assert res["total_citations_found"] == 0, f"False positive citation detected in: '{text}'"
        assert res["hallucinations_count"] == 0
        assert res["verdict"] == "NO_CITATIONS_FOUND"


# 3. Invalid Coordinates Detection
def test_invalid_coordinates(guard):
    text = "Как сказано в суре 2 аяте 300, верующие должны быть терпеливы."
    res = guard.verify_full_text(text)
    assert res["hallucinations_count"] == 1
    assert res["hallucinations"][0]["type"] == "INVALID_COORDINATE"
    assert res["trust_score"] < 100.0


# 4. Multi-Quote Bipartite Alignment
def test_multi_quote_alignment(guard):
    """Ensures two consecutive quotes are paired with their respective coordinates without cross-wiring."""
    text = (
        "Первый аят суры 114: بِسْمِ اللَّهِ الرَّحْمَـٰنِ الرَّحِيمِ قُلْ أَعُوذُ بِرَبِّ النَّاسِ (114:1). "
        "А также первый аят суры 112: بِسْمِ اللَّهِ الرَّحْمَـٰنِ الرَّحِيمِ قُلْ هُوَ اللَّهُ أَحَدٌ (112:1)."
    )
    res = guard.verify_full_text(text)
    assert res["total_citations_found"] == 2
    assert res["hallucinations_count"] == 0
    assert len(res["verified_items"]) == 2
    assert res["trust_score"] == 100.0


# 5. Tashkeel Distortion & Span-Safe Auto-Correction
def test_tashkeel_distortion_and_correction(engine, guard):
    distorted = "Аят аль-Курси (2:255): اللَّهُ لَا إِلَـٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ لَا تَأْخُذُهُ سِنَةٌ وَلَا نَوْمٌ"
    res = guard.verify_full_text(distorted)
    assert res["hallucinations_count"] == 1
    assert res["hallucinations"][0]["type"] in ["TASHKEEL_DISTORTION", "TEXT_MUTATION"]
    assert res["corrected_text"] != distorted
    assert engine.get_ayah(2, 255)["text"] in res["corrected_text"]


# 6. Exact Root Claim Verification
def test_root_claims(guard):
    # Valid claim: Rahman -> r-h-m
    valid = guard.verify_root_claim("الرَّحْمَـٰنِ", "رحم", context_id="1:1")
    assert valid["is_valid"] is True
    assert valid["canonical_root"] == "رحم"

    # Hallucinated claim: Rahman -> r-m-h (lance/spear)
    invalid = guard.verify_root_claim("الرَّحْمَـٰنِ", "رمح", context_id="1:1")
    assert invalid["is_valid"] is False
    assert "Галлюцинация корня" in invalid["message"]


# 7. Muqatta'at Letters (Surah 42:2)
def test_muqattaat_verse_handling(guard):
    text = "Сура 42 аят 2: عٓسٓقٓ"
    res = guard.verify_full_text(text)
    assert res["hallucinations_count"] == 0
    assert len(res["verified_items"]) == 1


# 7a. Honest verdict semantics: coordinates-only citations must NOT be claimed as "verified content"
def test_coordinates_only_verdict_is_not_canonical(guard):
    """A citation with a valid sura:ayah but NO Arabic quote text must surface as
    VERIFIED_COORDINATES_ONLY (content never diffed against canonical Tanzil)."""
    text = "Как указано в суре 2 аяте 255, Аллах управляет мирами, и этот аят часто читают дома."
    res = guard.verify_full_text(text)
    assert res["hallucinations_count"] == 0
    assert res["is_valid"] is True
    assert res["verdict"] == "VERIFIED_COORDINATES_ONLY"
    assert res["content_verified_count"] == 0
    assert res["coordinate_only_count"] == 1
    assert res["contains_unverified_content"] is True
    assert res["verified_items"][0]["type"] == "VALID_COORDINATE"
    assert res["verified_items"][0]["content_verified"] is False


def test_exact_quote_is_canonical_verified(guard):
    """A citation WITH matching Arabic quote must be EXACT_CITATION / VERIFIED_CANONICAL."""
    canon = guard.engine.get_ayah(2, 255)["text"]
    text = f"Аят аль-Курси (2:255): {canon}"
    res = guard.verify_full_text(text)
    assert res["hallucinations_count"] == 0
    assert res["verdict"] == "VERIFIED_CANONICAL"
    assert res["content_verified_count"] == 1
    assert res["coordinate_only_count"] == 0
    assert res["contains_unverified_content"] is False
    assert res["verified_items"][0]["type"] == "EXACT_CITATION"
    assert res["verified_items"][0]["content_verified"] is True


def test_partial_verification_verdict(guard):
    """Mixed input: one exact Arabic quote + one coordinates-only cite => PARTIAL, not 100%."""
    canon = guard.engine.get_ayah(2, 255)["text"]
    text = f"Аят аль-Курси (2:255): {canon}. А также упоминается сура 112 аят 1 в тексте."
    res = guard.verify_full_text(text)
    assert res["hallucinations_count"] == 0
    assert res["total_citations_found"] == 2
    assert res["verdict"] == "VERIFIED_CANONICAL_PARTIAL"
    assert res["content_verified_count"] == 1
    assert res["coordinate_only_count"] == 1
    assert res["contains_unverified_content"] is True
    assert res["is_valid"] is True


def test_guard_report_exposes_verification_metrics(guard):
    """New verbosity fields must always be present (incl. the no-citation path)."""
    res = guard.verify_full_text("Обычный текст без цитат.")
    for key in ("content_verified_count", "coordinate_only_count", "contains_unverified_content"):
        assert key in res, f"Guard report must expose '{key}'"
        assert res["content_verified_count"] == 0
        assert res["coordinate_only_count"] == 0
    assert res["contains_unverified_content"] is False


# 8. Shariah Contextual Screener (Riba vs Discount)
def test_shariah_contract_screening(ahkam):
    # Riba loan -> Flagged
    loan_clause = "Кредитный договор: заём выдается под 18% годовых с начислением пени 0.1% за каждый день просрочки."
    audit_loan = ahkam.audit_contract_clause(loan_clause)
    assert audit_loan["is_compliant"] is False
    assert audit_loan["findings"][0]["risk_type"] == "RIBA_RISK"
    assert "disclaimer" in audit_loan

    # Innocent discount % -> COMPLIANT (No false positive)
    discount_clause = "В честь праздника предоставляется скидка 15% на все товары в магазине."
    audit_discount = ahkam.audit_contract_clause(discount_clause)
    assert audit_discount["is_compliant"] is True
    assert audit_discount["findings_count"] == 0
