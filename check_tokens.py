import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Let's inspect how token 'form' reconstructs words and whether bismillah in ayah 1 is represented in tokens
sura_1_tokens = []
sura_2_ayah_1_tokens = []

import os
manifest_path = os.path.join(os.path.dirname(__file__), "security_manifest.jsonl")

with open(manifest_path, 'r', encoding='utf-8') as f:
    for line in f:
        item = json.loads(line)
        if item['id'] == '1:1':
            sura_1_tokens = [t['form'] for t in item['tokens']]
        if item['id'] == '2:1':
            sura_2_ayah_1_tokens = [t['form'] for t in item['tokens']]

print("Sura 1:1 token forms:", sura_1_tokens)
print("Sura 2:1 token forms:", sura_2_ayah_1_tokens)

# Check tokens across all 6236 ayahs: are there any None/empty values in unexpected places?
empty_forms = 0
invalid_flags = 0
pos_types = set()

with open(manifest_path, 'r', encoding='utf-8') as f:
    for line in f:
        item = json.loads(line)
        for t in item['tokens']:
            if not t.get('form'):
                empty_forms += 1
            if not isinstance(t.get('flags'), list):
                invalid_flags += 1
            pos_types.add(t.get('pos'))

print(f"Empty forms: {empty_forms}")
print(f"Invalid flags: {invalid_flags}")
print(f"All POS types: {pos_types}")
