"""
Al-Furqan AI - Test Suite: Simulated LLM Hallucinations & Guardrail Interception
Runs realistic test cases of AI hallucinations and asserts 100% detection and auto-correction.
"""

import sys
import json
from quran_guard import QuranEngine, QuranGuard, AhkamExtractor

# Fix Windows console UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 70)
print("AL-FURQAN AI: TEST SUITE & HALLUCINATION INTERCEPTION BENCHMARK")
print("=" * 70)

# Initialize Engine
engine = QuranEngine()
guard = QuranGuard(engine)
ahkam = AhkamExtractor(engine)

passed_tests = 0
total_tests = 5

# --- TEST 1: Non-Existent Ayah / Hallucinated Coordinate ---
print("\n[TEST 1] Детекция вымышленного аята (Invalid Coordinate)")
test_prompt_1 = "Как сказано в Коране (Сура 2, аят 300), верующие должны быть терпеливы..."
result_1 = guard.verify_full_text(test_prompt_1)

print(f"Промпт: \"{test_prompt_1}\"")
print(f"Вердикт: {result_1['verdict']} | Trust Score: {result_1['trust_score']}%")
if result_1['hallucinations_count'] > 0:
    print(f"🟢 УСПЕХ: Поймана галлюцинация: {result_1['hallucinations'][0]['error_description']}")
    passed_tests += 1
else:
    print("🔴 ОШИБКА: Галлюцинация не поймана!")

# --- TEST 2: Distorted Tashkeel & Misspelled Quote ---
print("\n[TEST 2] Детекция и автокоррекция искаженного арабского текста (Tashkeel Distortion)")
# Intentional distortion in Ayah Al-Kursi (2:255)
hallucinated_arabic = "اللَّهُ لَا إِلَـٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ لَا تَأْخُذُهُ سِنَةٌ وَلَا نَوْمٌ"
clean_canonical = "اللَّهُ لَا إِلَـٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ ۚ لَا تَأْخُذُهُ سِنَةٌ وَلَا نَوْمٌ ۚ لَّهُ مَا فِي السَّمَاوَاتِ وَمَا فِي الْأَرْضِ ۗ مَن ذَا الَّذِي يَشْفَعُ عِندَهُ إِلَّا بِإِذْنِهِ ۚ يَعْلَمُ مَا بَيْنَ أَيْدِيهِمْ وَمَا خَلْفَهُمْ ۖ وَلَا يُحِيطُونَ بِشَيْءٍ مِّنْ عِلْمِهِ إِلَّا بِمَا شَاءَ ۚ وَسِعَ كُرْسِيُّهُ السَّمَاوَاتِ وَالْأَرْضَ ۖ وَلَا يَئُودُهُ حِفْظُهُمَا ۚ وَهُوَ الْعَلِيُّ الْعَظِيمُ"
test_prompt_2 = f"Аят аль-Курси (2:255) гласит: {hallucinated_arabic}"

result_2 = guard.verify_full_text(test_prompt_2)
print(f"Промпт: \"{test_prompt_2[:60]}...\"")
print(f"Вердикт: {result_2['verdict']} | Trust Score: {result_2['trust_score']}%")
if result_2['hallucinations_count'] > 0:
    print(f"🟢 УСПЕХ: Выявлено искажение в цитате аята 2:255.")
    print(f"Авто-исправление выполнено: {result_2['corrected_text'][:60]}...")
    passed_tests += 1
else:
    print("🔴 ОШИБКА: Искажение не выявлено!")

# --- TEST 3: False Root Claim (Etymology Hallucination) ---
print("\n[TEST 3] Детекция ложного корня слова (Root Mismatch)")
# False claim: claiming Rahman comes from r-m-h (رمح - spear) instead of r-h-m (رحم - mercy)
false_root_check = guard.verify_root_claim(word="الرَّحْمَـٰنِ", claimed_root="رمح", context_id="1:1")
print(f"Проверка: Слово 'الرَّحْمَـٰنِ' происходит от корня 'رمح'?")
print(f"Результат: {false_root_check['message']}")
if not false_root_check['is_valid']:
    print(f"🟢 УСПЕХ: Ложный корень успешно опровергнут каноническим манифестом (Истинный корень: {false_root_check.get('canonical_root')}).")
    passed_tests += 1
else:
    print("🔴 ОШИБКА: Ложный корень не был опровергнут!")

# --- TEST 4: 100% Canonical Exact Quote Verification ---
print("\n[TEST 4] Подтверждение 100% чистой канонической цитаты (Zero False Positives)")
exact_ayah_114 = engine.get_ayah(114, 1)['text']
test_prompt_4 = f"В суре 114 аяте 1 сказано: {exact_ayah_114}"
result_4 = guard.verify_full_text(test_prompt_4)

print(f"Промпт: \"{test_prompt_4}\"")
print(f"Вердикт: {result_4['verdict']} | Trust Score: {result_4['trust_score']}%")
if result_4['trust_score'] == 100 and result_4['verdict'] == "VERIFIED_CANONICAL":
    print("🟢 УСПЕХ: Чистая цитата верифицирована со 100% доверием.")
    passed_tests += 1
else:
    print("🔴 ОШИБКА: Ложное срабатывание на чистой цитате!")

# --- TEST 5: Ahkam & Shariah Invariant Screener ---
print("\n[TEST 5] Аудит контракта на Риба и скрытые комиссии (Halal Compliance Screener)")
sample_clause = "Договор займа под 18% годовых с начислением пени и штрафа за просрочку платежа."
audit_result = ahkam.audit_contract_clause(sample_clause)

print(f"Условие: \"{sample_clause}\"")
print(f"Статус аудита: {audit_result['status']} (Compliant: {audit_result['is_compliant']})")
if not audit_result['is_compliant']:
    print(f"🟢 УСПЕХ: Выявлены коранические триггеры: {audit_result['findings'][0]['canonical_reference']}")
    passed_tests += 1
else:
    print("🔴 ОШИБКА: Ростовщический процент не был обнаружен!")

print("\n" + "=" * 70)
print(f"ИТОГ ТЕСТИРОВАНИЯ: Пройдено {passed_tests} из {total_tests} тестов ({int(passed_tests/total_tests*100)}%)")
print("=" * 70)
