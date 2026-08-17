import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

stems = {
    'HARAM_PORK': [r'свин\w*', r'хряк\w*', r'кабан\w*', r'доңыз\w*', r'шошқ\w*', r'бекон\w*', r'ветчин\w*', r'сало\b', r'pork\w*', r'swine\w*', r'pig\w*', r'bacon\w*', r'ham\b', r'lard\w*'],
    'HARAM_INTOXICANT_DRUG': [r'травк\w*', r'марихуан\w*', r'гашиш\w*', r'конопл\w*', r'наркот\w*', r'косяк\w*', r'анаш\w*', r'планчик\w*', r'шөп\w*', r'есіртк\w*', r'наша\w*', r'weed\w*', r'cannabis\w*', r'marijuana\w*', r'drug\w*'],
    'HARAM_ALCOHOL': [r'алког\w*', r'водк\w*', r'вин[оаыеу]\w*', r'пив\w*', r'спирт\w*', r'коньяк\w*', r'виски\w*', r'ликер\w*', r'арақ\w*', r'шарап\w*', r'сыра\w*', r'ішімдік\w*', r'beer\w*', r'wine\w*', r'vodka\w*', r'liquor\w*'],
    'HARAM_SMOKING': [r'кур[ияе]\w*', r'сигарет\w*', r'табак\w*', r'вейп\w*', r'кальян\w*', r'насвай\w*', r'темек\w*', r'шылым\w*', r'қорқор\w*', r'smok\w*', r'vape\w*', r'cigar\w*']
}

test_variations = [
    "покурить косячок на балконе",
    "шашлык из свининки с лучком",
    "доңыздың майы қосылған тағам",
    "выпить немного пивка и вина",
    "домашний сыр из молока",
    "вейпить электронку"
]

for sent in test_variations:
    matched = []
    for cat, patterns in stems.items():
        for pat in patterns:
            if re.search(pat, sent, re.IGNORECASE):
                matched.append(cat)
                break
    print(f"Sentence: '{sent}' -> Matched: {matched}")
