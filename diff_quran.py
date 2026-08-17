import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

quran_txt_map = {}
with open('f:/qoran/quran.txt', 'r', encoding='utf-8') as f:
    for line in f:
        parts = line.strip().split('|')
        if len(parts) == 3:
            s, a, t = parts
            quran_txt_map[f"{s}:{a}"] = t

manifest_map = {}
with open('f:/qoran/security_manifest.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        item = json.loads(line)
        manifest_map[item['id']] = item['text']

diffs = []
for k in quran_txt_map:
    if k not in manifest_map:
        diffs.append((k, "Missing in manifest", quran_txt_map[k], ""))
    elif quran_txt_map[k] != manifest_map[k]:
        diffs.append((k, "Text mismatch", quran_txt_map[k], manifest_map[k]))

print(f"Total entries compared: {len(quran_txt_map)}")
print(f"Total text differences between quran.txt and security_manifest.jsonl: {len(diffs)}")
if diffs:
    print("Sample differences:")
    for k, reason, t1, t2 in diffs[:10]:
        print(f"Ayah {k}: {reason}")
        print(f"  quran.txt: {t1}")
        print(f"  manifest:  {t2}")
