import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

surahs_no_bismillah = []
with open('f:/qoran/security_manifest.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        item = json.loads(line)
        if item['ayah'] == 1:
            if 'بِسْمِ اللَّهِ الرَّحْمَـٰنِ الرَّحِيمِ' not in item['text']:
                surahs_no_bismillah.append((item['sura'], item['text']))

print(f"Surahs where Ayah 1 doesn't have standard Bismillah prefix in 'text':")
for s, txt in surahs_no_bismillah:
    print(f"Surah {s}: {txt}")
