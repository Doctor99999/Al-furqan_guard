import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Check text consistency, token consistency, and compare with quran.txt if formatted
with open('f:/qoran/quran.txt', 'r', encoding='utf-8') as f:
    quran_lines = [l.strip() for l in f if l.strip()]

print(f"Total lines in quran.txt: {len(quran_lines)}")
if quran_lines:
    print(f"Sample line from quran.txt:\n{quran_lines[0]}")
