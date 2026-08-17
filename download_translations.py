import os
import json
import urllib.request
import sys

sys.stdout.reconfigure(encoding='utf-8')

editions = {
    "kk": "kk.khalifahaltai",
    "ru": "ru.kuliev",
    "en": "en.sahih",
    "tr": "tr.diyanet",
    "uz": "uz.sodik",
    "id": "id.indonesian"
}

out_dir = "f:/qoran/translations"
os.makedirs(out_dir, exist_ok=True)
all_translations = {}  # "sura:ayah" -> { "kk": "...", "ru": "...", "en": "...", ... }

print("Downloading authentic translations for all 6,236 Ayahs...")

for lang, ed_id in editions.items():
    print(f"Fetching {lang} ({ed_id})...")
    url = f"https://api.alquran.cloud/v1/quran/{ed_id}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            surahs = data.get('data', {}).get('surahs', [])
            count = 0
            for s in surahs:
                sura_num = s.get('number')
                for a in s.get('ayahs', []):
                    ayah_num = a.get('numberInSurah')
                    text = a.get('text', '').strip()
                    key = f"{sura_num}:{ayah_num}"
                    if key not in all_translations:
                        all_translations[key] = {}
                    all_translations[key][lang] = text
                    count += 1
            print(f"  -> Successfully loaded {count} ayahs for {lang}")
    except Exception as e:
        print(f"  -> Error fetching {lang}: {e}")

# Save to local file
out_file = os.path.join(out_dir, "translations.json")
with open(out_file, 'w', encoding='utf-8') as f:
    json.dump(all_translations, f, ensure_ascii=False, indent=2)

print(f"\nAll translations saved to {out_file} (Total Ayahs: {len(all_translations)})")
