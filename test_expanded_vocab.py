import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

test_inputs = [
    # Slang & complex derivatives
    "покурить косячок с друзьями",
    "дунуть травку",
    "шашлык из свининки",
    "доңыздың майы қосылған тағам",
    "выпить немного пивка и винца",
    "электронная сигарета и вейп",
    "краситель Е-120 в йогурте",
    "мармеладные мишки с желатином E441",
    "свежая семга, судак и креветки",
    "сиыр етінен жасалған қазы мен самса",
    "кредит под 15% с начислением пени",
    "инвестиции в бизнес на условиях мушарака"
]

if __name__ == "__main__":
    print("=" * 70)
    print("TESTING EXPANDED VOCABULARY ENGINE (HalalKnowledgeBase)")
    print("=" * 70)

    for t in test_inputs:
        req_data = json.dumps({"text": t}).encode("utf-8")
        req = urllib.request.Request("http://127.0.0.1:8000/api/audit/contract", data=req_data, headers={"Content-Type": "application/json"})
        resp = urllib.request.urlopen(req)
        data = json.loads(resp.read().decode("utf-8"))
        trigger = data["findings"][0]["matched_trigger"] if data["findings"] else "N/A"
        print(f"'{t}'")
        print(f"   ==> Verdict: {data['overall_verdict']} | Trigger: [{trigger}]")
        if data["findings"]:
            print(f"   ==> {data['findings'][0]['title_ru']}")
        print("-" * 70)
