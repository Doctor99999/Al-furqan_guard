import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

test_inputs = [
    "Курить травку",
    "шөп шегу",
    "марихуана мен анаша",
    "курение сигарет и вейп",
    "кальян",
    "краситель кармин E120",
    "мармелад с желатином",
    "говядина халяль"
]

for t in test_inputs:
    req_data = json.dumps({"text": t}).encode("utf-8")
    req = urllib.request.Request("http://127.0.0.1:8000/api/audit/contract", data=req_data, headers={"Content-Type": "application/json"})
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read().decode("utf-8"))
    print(f"Input: '{t}' -> Verdict: {data['overall_verdict']}")
    if data["findings"]:
        print(f"   -> Title: {data['findings'][0]['title_ru']}")
