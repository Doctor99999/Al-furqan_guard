import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

test_suite = [
    # Category 1: Food & Meat
    {"category": "🍖 Еда и Мясо", "input": "Шашлык из свинины и бекон"},
    {"category": "🍖 Еда и Мясо", "input": "Қой етінен және сиыр етінен жасалған қуырдақ"},
    {"category": "🍖 Еда и Мясо", "input": "Свежая семга, форель и креветки"},
    
    # Category 2: Food Additives & E-Codes
    {"category": "🧪 Пищевые добавки", "input": "Йогурт с клубникой и красителем Кармин E-120"},
    {"category": "🧪 Пищевые добавки", "input": "Мармелад жевательный с желатином E441"},
    {"category": "🧪 Пищевые добавки", "input": "Шоколад с эмульгатором E471"},
    
    # Category 3: Drinks & Intoxicants
    {"category": "🍷 Напитки и Алкоголь", "input": "Красное полусладкое вино и пиво"},
    {"category": "🍷 Напитки и Алкоголь", "input": "Табиғи бал, айран және сүт"},
    {"category": "🍷 Напитки и Алкоголь", "input": "Шөп шегу (марихуана мен наша)"},
    {"category": "🍷 Напитки и Алкоголь", "input": "Электронные сигареты, кальян и вейп"},
    
    # Category 4: Finance & Contracts
    {"category": "💰 Финансы и Сделки", "input": "Кредит в банке под 18.5% годовых с начислением пени за просрочку"},
    {"category": "💰 Финансы и Сделки", "input": "Букмекерлік кеңседе футболға бәс тігу және казино"},
    {"category": "💰 Финансы и Сделки", "input": "Инвестиции в торговый бизнес на условиях Мушарака (разделение прибыли)"},
    {"category": "💰 Финансы и Сделки", "input": "Үстемесіз бөліп төлеу (Рассрочка 0% без скрытых комиссий)"}
]

print("=" * 80)
print("LIVE SHARIAH & HALAL COMPLIANCE TEST SUITE")
print("=" * 80)

for item in test_suite:
    req_data = json.dumps({"text": item["input"]}).encode("utf-8")
    req = urllib.request.Request("http://127.0.0.1:8000/api/audit/contract", data=req_data, headers={"Content-Type": "application/json"})
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read().decode("utf-8"))
    
    verdict = data["overall_verdict"]
    verdict_emoji = "🔴 ХАРАМ" if verdict == "HARAM" else ("🟡 ШҮБӘЛІ" if verdict == "DOUBTFUL" else "🟢 ХАЛАЛ")
    trigger = data["findings"][0]["matched_trigger"] if data["findings"] else "Принцип Ибаха"
    ayah = data["findings"][0]["ayah_ref"] if data["findings"] else "16:69 / 5:1"
    
    print(f"[{item['category']}]")
    print(f"  Ввод:    \"{item['input']}\"")
    print(f"  Вердикт: {verdict_emoji} ({verdict})")
    print(f"  Триггер: [{trigger}] | Ссылка: {ayah}")
    print("-" * 80)
