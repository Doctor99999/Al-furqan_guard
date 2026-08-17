"""
Al-Furqan AI - Latin Transliteration & Pronunciation Engine
Deterministic phonetic conversion of vocalized Quranic Arabic text (with Tashkeel) into standard Latin pronunciation.
"""

import re
import unicodedata


def arabic_to_latin_transliteration(arabic_text: str) -> str:
    """
    Converts Quranic Arabic with harakat/tashkeel to clean standard Latin transliteration.
    Example: 'بِسْمِ اللَّهِ الرَّحْمَـٰنِ الرَّحِيمِ' -> 'Bismi-Llāhir-Raḥmānir-Raḥīm'
    """
    if not arabic_text:
        return ""

    # Common honorific and frequent phrases quick lookup
    quick_map = {
        "بِسْمِ اللَّهِ الرَّحْمَـٰنِ الرَّحِيمِ": "Bismi-Llāhir-Raḥmānir-Raḥīm",
        "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ": "Al-ḥamdu li-Llāhi Rabbil-'ālamīn",
        "الرَّحْمَـٰنِ الرَّحِيمِ": "Ar-Raḥmānir-Raḥīm",
        "مَالِكِ يَوْمِ الدِّينِ": "Māliki yawmid-dīn",
        "إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ": "Iyyāka na'budu wa-iyyāka nasta'īn",
        "اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ": "Ihdinaṣ-ṣirāṭal-mustaqīm",
        "قُلْ هُوَ اللَّهُ أَحَدٌ": "Qul Huwa-Llāhu Aḥad",
        "اللَّهُ الصَّمَدُ": "Allāhuṣ-Ṣamad",
        "لَمْ يَلِدْ وَلَمْ يُولَدْ": "Lam yalid wa-lam yūlad",
        "وَلَمْ يَكُن لَّهُ كُفُوًا أَحَدٌ": "Wa-lam yakul-lahū kufuwan aḥad",
        "قُلْ أَعُوذُ بِرَبِّ الْفَلَقِ": "Qul a'ūdhu bi-Rabbil-falaq",
        "قُلْ أَعُوذُ بِرَبِّ النَّاسِ": "Qul a'ūdhu bi-Rabbin-nās",
        "مَلِكِ النَّاسِ": "Malikin-nās",
        "إِلَـٰهِ النَّاسِ": "Ilāhin-nās",
    }

    clean_text = arabic_text.strip()
    if clean_text in quick_map:
        return quick_map[clean_text]

    # Character mapping table
    consonants = {
        'ا': '', 'أ': "'", 'إ': "'", 'آ': 'ā', 'ٱ': '',
        'ب': 'b', 'ت': 't', 'ث': 'th', 'ج': 'j', 'ح': 'ḥ',
        'خ': 'kh', 'د': 'd', 'ذ': 'dh', 'ر': 'r', 'ز': 'z',
        'س': 's', 'ش': 'sh', 'ص': 'ṣ', 'ض': 'ḍ', 'ط': 'ṭ',
        'ظ': 'ẓ', 'ع': "'", 'غ': 'gh', 'ف': 'f', 'ق': 'q',
        'ك': 'k', 'ل': 'l', 'م': 'm', 'ن': 'n', 'ه': 'h',
        'و': 'w', 'ي': 'y', 'ى': 'ā', 'ة': 'h', 'ء': "'",
        'ئ': "'", 'ؤ': "'", 'ـ': '',
    }

    # Quranic stop marks to ignore
    stops = {'ۛ', 'ۖ', 'ۗ', 'ۚ', 'ۙ', 'ۜ', '۝', '۞', '۟', '۠', 'ۢ', 'ۣ', 'ۤ'}

    vowels = {
        '\u064E': 'a',   # Fatha
        '\u064F': 'u',   # Damma
        '\u0650': 'i',   # Kasra
        '\u064B': 'an',  # Fathatan
        '\u064C': 'un',  # Dammatan
        '\u064D': 'in',  # Kasratan
        '\u0652': '',    # Sukun
        '\u0670': 'ā',   # Dagger Alif
        '\u0653': '',    # Maddah
        '\u0654': "'",   # Hamza above
        '\u0655': "'",   # Hamza below
    }

    chars = list(clean_text)
    n = len(chars)
    result = []
    i = 0

    while i < n:
        c = chars[i]
        if c in stops:
            i += 1
            continue

        # Check if next character is Shaddah (\u0651)
        has_shaddah = False
        if i + 1 < n and chars[i + 1] == '\u0651':
            has_shaddah = True

        if c in consonants:
            lat = consonants[c]
            if has_shaddah and lat:
                lat = lat + lat
            result.append(lat)
        elif c in vowels:
            result.append(vowels[c])
        elif c == ' ':
            result.append(' ')
        elif c == '\u0651':
            pass
        i += 1

    trans = "".join(result)

    # Phonetic polishings:
    # Prolonged vowels
    trans = re.sub(r'aā|aa|a\'a', 'ā', trans)
    trans = re.sub(r'iy|ii', 'ī', trans)
    trans = re.sub(r'uw|uu', 'ū', trans)
    # Definite article polish (al-)
    trans = re.sub(r'\ba l\b|\bal ', 'al-', trans)
    # Capitalize first letter of words
    trans = re.sub(r'\s+', ' ', trans).strip()
    if trans:
        trans = trans[0].upper() + trans[1:]

    return trans
