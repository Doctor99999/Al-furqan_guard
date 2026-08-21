import json
import unicodedata

import os
manifest_path = os.path.join(os.path.dirname(__file__), "security_manifest.jsonl")

bismillah_prefix = "بِسْمِ اللَّهِ الرَّحْمَـٰنِ الرَّحِيمِ"
bismillah_prefix_norm = "".join(c for c in bismillah_prefix if unicodedata.category(c) != 'Mn')

stats = {
    "ayahs_with_bismillah_text": 0,
    "bismillah_in_tokens_sura_1": False,
    "bismillah_in_tokens_other_suras": 0,
    "null_roots_count": 0,
    "non_null_roots_count": 0,
    "pos_distribution": {},
    "unique_roots": set(),
    "unique_lemmas": set()
}

with open(manifest_path, 'r', encoding='utf-8') as f:
    for line in f:
        item = json.loads(line)
        sura = item['sura']
        ayah = item['ayah']
        text = item['text']
        tokens = item['tokens']
        
        # Check Bismillah in text
        if text.startswith(bismillah_prefix):
            stats["ayahs_with_bismillah_text"] += 1
            
        for t in tokens:
            pos = t.get('pos')
            stats["pos_distribution"][pos] = stats["pos_distribution"].get(pos, 0) + 1
            
            root = t.get('root')
            if root:
                stats["non_null_roots_count"] += 1
                stats["unique_roots"].add(root)
            else:
                stats["null_roots_count"] += 1
                
            lemma = t.get('lemma')
            if lemma:
                stats["unique_lemmas"].add(lemma)

print(f"Stats:")
print(f"Ayahs with Bismillah in 'text': {stats['ayahs_with_bismillah_text']}")
print(f"Unique Roots found: {len(stats['unique_roots'])}")
print(f"Unique Lemmas found: {len(stats['unique_lemmas'])}")
print(f"Total Morphological Tokens: {stats['non_null_roots_count'] + stats['null_roots_count']}")
print(f"Tokens with semantic root: {stats['non_null_roots_count']}")
print(f"Tokens without root (particles/pronouns/etc): {stats['null_roots_count']}")
print(f"POS Distribution: {stats['pos_distribution']}")
