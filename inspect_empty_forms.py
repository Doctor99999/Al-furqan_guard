import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

empty_tokens = []
with open('f:/qoran/security_manifest.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        item = json.loads(line)
        for t in item['tokens']:
            if not t.get('form'):
                empty_tokens.append((item['id'], t))

print(f"Total tokens with empty/falsy form: {len(empty_tokens)}")
for ayah_id, t in empty_tokens[:15]:
    print(f"Ayah {ayah_id}: {t}")
