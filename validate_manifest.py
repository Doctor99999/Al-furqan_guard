import json
import sys

canonical_ayah_counts = [
    7, 286, 200, 176, 120, 165, 206, 75, 129, 109,
    123, 111, 43, 52, 99, 128, 111, 110, 98, 135,
    112, 78, 118, 64, 77, 227, 93, 88, 69, 60,
    34, 30, 73, 54, 45, 83, 182, 88, 75, 85,
    54, 53, 89, 59, 37, 35, 38, 29, 18, 45,
    60, 49, 62, 55, 78, 96, 29, 22, 24, 13,
    14, 11, 11, 18, 12, 12, 30, 52, 52, 44,
    28, 28, 20, 56, 40, 31, 50, 40, 46, 42,
    29, 19, 36, 25, 22, 17, 19, 26, 30, 20,
    15, 21, 11, 8, 8, 19, 5, 8, 8, 11,
    11, 8, 3, 9, 5, 4, 7, 3, 6, 3,
    5, 4, 5, 6
]

manifest_path = "f:/qoran/security_manifest.jsonl"

errors = []
warnings = []

total_lines = 0
valid_json_count = 0
surahs_found = {}
all_ids = set()
total_tokens = 0
total_lemmas = 0

with open(manifest_path, 'r', encoding='utf-8') as f:
    for line_num, line in enumerate(f, 1):
        total_lines += 1
        line_str = line.strip()
        if not line_str:
            warnings.append(f"Line {line_num}: Empty line")
            continue
        try:
            data = json.loads(line_str)
            valid_json_count += 1
        except Exception as e:
            errors.append(f"Line {line_num}: Invalid JSON - {e}")
            continue
            
        required_keys = ['id', 'sura', 'ayah', 'text', 'tokens', 'lemmas']
        for k in required_keys:
            if k not in data:
                errors.append(f"Line {line_num} ({data.get('id')}): Missing key {k}")
                
        sura = data.get('sura')
        ayah = data.get('ayah')
        item_id = data.get('id')
        
        if item_id != f"{sura}:{ayah}":
            errors.append(f"Line {line_num}: ID mismatch: {item_id} != {sura}:{ayah}")
            
        if item_id in all_ids:
            errors.append(f"Line {line_num}: Duplicate ID: {item_id}")
        all_ids.add(item_id)
        
        if sura not in surahs_found:
            surahs_found[sura] = []
        surahs_found[sura].append(ayah)
        
        # Token checks
        tokens = data.get('tokens', [])
        if not isinstance(tokens, list):
            errors.append(f"Line {line_num} ({item_id}): tokens is not a list")
        elif len(tokens) == 0:
            errors.append(f"Line {line_num} ({item_id}): tokens list is empty")
        else:
            total_tokens += len(tokens)
            prev_i = 0
            prev_j = 0
            for t_idx, token in enumerate(tokens):
                for tk_key in ['i', 'j', 'form', 'pos', 'lemma', 'root', 'flags']:
                    if tk_key not in token:
                        errors.append(f"Line {line_num} ({item_id}) token {t_idx}: missing token key {tk_key}")
                i_val = token.get('i', 0)
                j_val = token.get('j', 0)
                if i_val < prev_i:
                    errors.append(f"Line {line_num} ({item_id}) token {t_idx}: i decreased from {prev_i} to {i_val}")
                elif i_val == prev_i and j_val <= prev_j:
                    errors.append(f"Line {line_num} ({item_id}) token {t_idx}: j did not increase for word {i_val}: {prev_j} -> {j_val}")
                prev_i = i_val
                prev_j = j_val

        lemmas = data.get('lemmas', [])
        if not isinstance(lemmas, list):
            errors.append(f"Line {line_num} ({item_id}): lemmas is not a list")
        else:
            total_lemmas += len(lemmas)

print(f"Total lines: {total_lines}")
print(f"Valid JSON objects: {valid_json_count}")
print(f"Total unique IDs: {len(all_ids)}")
print(f"Surahs found: {len(surahs_found)} / 114")
print(f"Total tokens parsed: {total_tokens}")
print(f"Total lemmas recorded: {total_lemmas}")

# Check Ayah counts per Surah
for s_idx, expected_count in enumerate(canonical_ayah_counts, 1):
    if s_idx not in surahs_found:
        errors.append(f"Surah {s_idx} completely missing!")
    else:
        actual_ayahs = surahs_found[s_idx]
        if len(actual_ayahs) != expected_count:
            errors.append(f"Surah {s_idx}: expected {expected_count} ayahs, got {len(actual_ayahs)}")
        expected_range = list(range(1, expected_count + 1))
        if actual_ayahs != expected_range:
            errors.append(f"Surah {s_idx}: ayah numbers not strictly 1..{expected_count}")

print(f"\n--- Validation Summary ---")
print(f"Total Errors found: {len(errors)}")
print(f"Total Warnings found: {len(warnings)}")

if errors:
    print("\nErrors (sample of first 20):")
    for e in errors[:20]:
        print(" [ERROR]", e)
if warnings:
    print("\nWarnings (sample of first 20):")
    for w in warnings[:20]:
        print(" [WARNING]", w)
