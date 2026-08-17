import urllib.request
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

url = 'https://api.alquran.cloud/v1/edition'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=5) as response:
    data = json.loads(response.read().decode('utf-8'))
    editions = data.get('data', [])
    for ed in editions:
        if ed.get('language') in ['kk', 'kz', 'ru', 'en', 'tr', 'uz', 'id']:
            print(f"Lang: {ed.get('language')} | ID: {ed.get('identifier')} | Name: {ed.get('englishName')} | Format: {ed.get('format')}")
