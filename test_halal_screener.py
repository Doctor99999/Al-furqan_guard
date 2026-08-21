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

def query_audit(text: str):
    try:
        req_data = json.dumps({"text": text}).encode("utf-8")
        req = urllib.request.Request("http://127.0.0.1:8000/api/audit/contract", data=req_data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=2) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        from server import app
        from fastapi.testclient import TestClient
        client = TestClient(app)
        res = client.post("/api/audit/contract", json={"text": text})
        return res.json()

for t in test_inputs:
    data = query_audit(t)
    print(f"Input: '{t}' -> Verdict: {data['overall_verdict']}")
    if data["findings"]:
        print(f"   -> Title: {data['findings'][0]['title_ru']}")
