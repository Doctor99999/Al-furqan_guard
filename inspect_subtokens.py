import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('f:/qoran/security_manifest.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        item = json.loads(line)
        if item['id'] == '2:54':
            print("2:54 text:", item['text'])
            print("Word 5 tokens:")
            for t in item['tokens']:
                if t['i'] == 5:
                    print("  ", t)
        if item['id'] == '2:126':
            print("2:126 text:", item['text'])
            print("Word 4 tokens:")
            for t in item['tokens']:
                if t['i'] == 4:
                    print("  ", t)
