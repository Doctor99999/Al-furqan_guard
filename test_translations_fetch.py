import urllib.request
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

url = 'https://api.alquran.cloud/v1/surah/1/editions/quran-uthmani,kk.altai,ru.kuliev,en.sahih'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=5) as response:
    data = json.loads(response.read().decode('utf-8'))
    for item in data.get('data', []):
        edition_meta = item.get('edition', {})
        ayahs = item.get('ayahs', [])
        print(f"Lang: {edition_meta.get('language')}, Identifier: {edition_meta.get('identifier')}, Author: {edition_meta.get('englishName')}")
        if ayahs:
            print(f"  Ayah 1: {ayahs[0].get('text')}")
            print(f"  Ayah 2: {ayahs[1].get('text')}")
