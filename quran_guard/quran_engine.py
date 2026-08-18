"""
Al-Furqan AI - Quran Core Engine
High-performance in-memory indexing, AST parsing, and morphology resolution for the Quran.
"""

import json
import re
import unicodedata
from typing import Dict, List, Optional, Any, Set, Tuple
from .transliteration import arabic_to_latin_transliteration
from .config import MANIFEST_PATH, TRANSLATIONS_PATH


def strip_tashkeel(text: str) -> str:
    """Removes all Arabic diacritics (tashkeel/harakat/tanween) from text."""
    if not text:
        return ""
    # Unicode categories for marks: Mn (Nonspacing Mark), Me (Enclosing Mark)
    # Also handle dagger alif and special Quranic marks
    marks = {'\u064B', '\u064C', '\u064D', '\u064E', '\u064F', '\u0650', '\u0651', '\u0652', 
             '\u0653', '\u0654', '\u0655', '\u0656', '\u0657', '\u0658', '\u0659', '\u065A',
             '\u065B', '\u065C', '\u065D', '\u065E', '\u065F', '\u0670', '\u06D6', '\u06D7',
             '\u06D8', '\u06D9', '\u06DA', '\u06DB', '\u06DC', '\u06DF', '\u06E0', '\u06E1',
             '\u06E2', '\u06E3', '\u06E4', '\u06E5', '\u06E6', '\u06E7', '\u06E8', '\u06EA',
             '\u06EB', '\u06EC', '\u06ED'}
    return "".join(ch for ch in text if ch not in marks and unicodedata.category(ch) != 'Mn')


def normalize_arabic(text: str) -> str:
    """Normalizes Arabic text for robust search matching (alifs, yaas, taa marbuta)."""
    if not text:
        return ""
    text = strip_tashkeel(text)
    # Normalize Alifs
    text = re.sub(r'[إأآٱآ]', 'ا', text)
    # Normalize Taa Marbuta
    text = re.sub(r'ة', 'ه', text)
    # Normalize Yaa / Alif Maqsura
    text = re.sub(r'[يىئ]', 'ي', text)
    # Remove Tatweel / Kashida
    text = re.sub(r'ـ', '', text)
    # Normalize Hamza
    text = re.sub(r'[ؤ]', 'و', text)
    # Collapse multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text


class QuranEngine:
    """
    In-memory indexed engine providing O(1) coordinate lookups, inverted root/lemma indexes,
    and fast token-level AST analysis for all 6,236 Ayahs and 130,030 sub-tokens.
    """

    CANONICAL_AYAH_COUNTS = [
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

    SURAH_NAMES = {
        "kk": [
            "Фатиха", "Бақара", "Әли Имран", "Ниса", "Мәида",
            "Әнғам", "Ағраф", "Әнфәл", "Тәубе", "Юнус",
            "Һуд", "Юсуф", "Рағыд", "Ибраһим", "Хижр",
            "Нахыл", "Исра", "Кәһф", "Мәриям", "Та Һа",
            "Әнбия", "Хаж", "Муминун", "Нұр", "Фурқан",
            "Шуғара", "Нәміл", "Қасас", "Әнкәбут", "Рум",
            "Лұқман", "Сәжде", "Ахзаб", "Сәбә", "Фатыр",
            "Йа Син", "Саффат", "Сад", "Зүмәр", "Ғафир",
            "Фуссиләт", "Шура", "Зухруф", "Духан", "Жасия",
            "Ахқаф", "Мұхаммед", "Фатх", "Хужурат", "Қаф",
            "Зарият", "Тур", "Нәжм", "Қамар", "Рахман",
            "Уақиға", "Хадид", "Мужәдәлә", "Хашыр", "Мумтәхина",
            "Саф", "Жұма", "Мунафиқун", "Тәғабун", "Талақ",
            "Тахрим", "Мүлік", "Қалам", "Хаққа", "Мағариж",
            "Нұх", "Жын", "Муззәммил", "Муддәссир", "Қиямет",
            "Инсан", "Мурсәләт", "Нәбә", "Назиғат", "Абаса",
            "Тәкуир", "Инфитар", "Мутаффифин", "Иншиқақ", "Буруж",
            "Тарық", "Ағлә", "Ғашия", "Фәжр", "Бәләд",
            "Шәмс", "Ләйіл", "Дұха", "Шәрх", "Тин",
            "Аләқ", "Қадір", "Бәйинә", "Зәлзәлә", "Ғадият",
            "Қариға", "Тәкәсур", "Асыр", "Һумәзә", "Фил",
            "Құрайыш", "Мағун", "Кәусәр", "Кәфирун", "Насыр",
            "Мәсәд", "Ықылас", "Фәләқ", "Нас"
        ],
        "ru": [
            "Аль-Фатиха (Открывающая)", "Аль-Бакара (Корова)", "Аль Имран (Семейство Имрана)", "Ан-Ниса (Женщины)", "Аль-Маида (Трапеза)",
            "Аль-Анам (Скот)", "Аль-Араф (Ограды)", "Аль-Анфаль (Трофеи)", "Ат-Тауба (Покаяние)", "Юнус (Иона)",
            "Худ (Худ)", "Юсуф (Иосиф)", "Ар-Раад (Гром)", "Ибрахим (Авраам)", "Аль-Хиджр (Хиджр)",
            "Ан-Нахль (Пчелы)", "Аль-Исра (Ночной перенос)", "Аль-Кахф (Пещера)", "Марьям (Мария)", "Та Ха (Та Ха)",
            "Аль-Анбия (Пророки)", "Аль-Хаджж (Паломничество)", "Аль-Муминун (Верующие)", "Ан-Нур (Свет)", "Аль-Фуркан (Различение)",
            "Аш-Шуара (Поэты)", "Ан-Намль (Муравьи)", "Аль-Касас (Рассказ)", "Аль-Анкабут (Паук)", "Ар-Рум (Римляне)",
            "Лукман (Лукман)", "Ас-Саджда (Земной поклон)", "Аль-Ахзаб (Союзники)", "Саба (Сава)", "Фатыр (Творец)",
            "Йа Син (Йа Син)", "Ас-Саффат (Выстроившиеся в ряды)", "Сад (Сад)", "Аз-Зумар (Толпы)", "Гафир (Прощающий)",
            "Фуссилат (Разъяснены)", "Аш-Шура (Совет)", "Аз-Зухруф (Украшения)", "Ад-Духан (Дым)", "Аль-Джасия (Коленопреклоненные)",
            "Аль-Ахкаф (Барханы)", "Мухаммад (Мухаммад)", "Аль-Фатх (Победа)", "Аль-Худжурат (Комнаты)", "Каф (Каф)",
            "Аз-Зарият (Рассеивающие)", "Ат-Тур (Гора)", "Ан-Наджм (Звезда)", "Аль-Камар (Месяц)", "Ар-Рахман (Милостивый)",
            "Аль-Вакиа (Событие)", "Аль-Хадид (Железо)", "Аль-Муджадила (Препирающаяся)", "Аль-Хашр (Сбор)", "Аль-Мумтахана (Испытуемая)",
            "Ас-Сафф (Ряды)", "Аль-Джумуа (Пятница)", "Аль-Мунафикун (Лицемеры)", "Ат-Тагабун (Взаимное обделение)", "Ат-Таляк (Развод)",
            "Ат-Тахрим (Запрещение)", "Аль-Мульк (Власть)", "Аль-Калям (Письменная трость)", "Аль-Хакка (Неминуемое)", "Аль-Мааридж (Ступени)",
            "Нух (Ной)", "Аль-Джинн (Джинны)", "Аль-Муззаммиль (Закутавшийся)", "Аль-Муддассир (Завернувшийся)", "Аль-Кияма (Воскресение)",
            "Аль-Инсан (Человек)", "Аль-Мурсалят (Посылаемые)", "Ан-Наба (Весть)", "Ан-Назиат (Исторгающие)", "Абаса (Нахмурился)",
            "Ат-Таквир (Скручивание)", "Аль-Инфитар (Раскалывание)", "Аль-Мутаффифин (Обвешивающие)", "Аль-Иншикак (Разверзание)", "Аль-Бурудж (Созвездия)",
            "Ат-Тарик (Ночной путник)", "Аль-Аля (Всевышний)", "Аль-Гашия (Покрывающее)", "Аль-Фаджр (Заря)", "Аль-Баляд (Город)",
            "Аш-Шамс (Солнце)", "Аль-Лейль (Ночь)", "Ад-Духа (Утро)", "Аш-Шарх (Раскрытие)", "Ат-Тин (Смоковница)",
            "Аль-Аляк (Сгусток)", "Аль-Кадр (Предопределение)", "Аль-Баййина (Ясное знамение)", "Аз-Зальзаля (Землетрясение)", "Аль-Адият (Скачущие)",
            "Аль-Кариа (Великое бедствие)", "Ат-Такасур (Охота к умножению)", "Аль-Аср (Предвечернее время)", "Аль-Хумаза (Хулитель)", "Аль-Филь (Слон)",
            "Курайш (Курайшиты)", "Аль-Маун (Подаяние)", "Аль-Каусар (Изобилие)", "Аль-Кафирун (Неверующие)", "Ан-Наср (Помощь)",
            "Аль-Масад (Пальмовые волокна)", "Аль-Ихлас (Искренность)", "Аль-Фаляк (Рассвет)", "Ан-Нас (Люди)"
        ],
        "en": [
            "Al-Fatiha (The Opener)", "Al-Baqarah (The Cow)", "Ali 'Imran (Family of Imran)", "An-Nisa (The Women)", "Al-Ma'idah (The Table Spread)",
            "Al-An'am (The Cattle)", "Al-A'raf (The Heights)", "Al-Anfal (The Spoils of War)", "At-Tawbah (The Repentance)", "Yunus (Jonah)",
            "Hud (Hud)", "Yusuf (Joseph)", "Ar-Ra'd (The Thunder)", "Ibrahim (Abraham)", "Al-Hijr (The Rocky Tract)",
            "An-Nahl (The Bee)", "Al-Isra (The Night Journey)", "Al-Kahf (The Cave)", "Maryam (Mary)", "Ta-Ha (Ta-Ha)",
            "Al-Anbiya (The Prophets)", "Al-Hajj (The Pilgrimage)", "Al-Mu'minun (The Believers)", "An-Nur (The Light)", "Al-Furqan (The Criterion)",
            "Ash-Shu'ara (The Poets)", "An-Naml (The Ant)", "Al-Qasas (The Stories)", "Al-'Ankabut (The Spider)", "Ar-Rum (The Romans)",
            "Luqman (Luqman)", "As-Sajdah (The Prostration)", "Al-Ahzab (The Combined Forces)", "Saba (Sheba)", "Fatir (Originator)",
            "Ya-Sin (Ya-Sin)", "As-Saffat (Those who set the Ranks)", "Sad (The Letter Sad)", "Az-Zumar (The Troops)", "Ghafir (The Forgiver)",
            "Fussilat (Explained in Detail)", "Ash-Shura (The Consultation)", "Az-Zukhruf (The Ornaments of Gold)", "Ad-Dukhan (The Smoke)", "Al-Jathiyah (The Crouching)",
            "Al-Ahqaf (The Wind-Curved Sandhills)", "Muhammad (Muhammad)", "Al-Fath (The Victory)", "Al-Hujurat (The Rooms)", "Qaf (The Letter Qaf)",
            "Adh-Dhariyat (The Winnowing Winds)", "At-Tur (The Mount)", "An-Najm (The Star)", "Al-Qamar (The Moon)", "Ar-Rahman (The Beneficent)",
            "Al-Waqi'ah (The Inevitable)", "Al-Hadid (The Iron)", "Al-Mujadila (The Pleading Woman)", "Al-Hashr (The Exile)", "Al-Mumtahanah (She That Is To Be Examined)",
            "As-Saff (The Ranks)", "Al-Jumu'ah (The Congregation)", "Al-Munafiqun (The Hypocrites)", "At-Taghabun (The Mutual Disillusion)", "At-Talaq (The Divorce)",
            "At-Tahrim (The Prohibition)", "Al-Mulk (The Sovereignty)", "Al-Qalam (The Pen)", "Al-Haqqah (The Reality)", "Al-Ma'arij (The Ascending Stairways)",
            "Nuh (Noah)", "Al-Jinn (The Jinn)", "Al-Muzzammil (The Enshrouded One)", "Al-Muddaththir (The Cloaked One)", "Al-Qiyamah (The Resurrection)",
            "Al-Insan (The Man)", "Al-Mursalat (The Emissaries)", "An-Naba (The Tidings)", "An-Nazi'at (Those Who Drag Forth)", "'Abasa (He Frowned)",
            "At-Takwir (The Overthrowing)", "Al-Infitar (The Cleaving)", "Al-Mutaffifin (The Defrauding)", "Al-Inshiqaq (The Sundering)", "Al-Buruj (The Mansions of the Stars)",
            "At-Tariq (The Nightcomer)", "Al-A'la (The Most High)", "Al-Ghashiyah (The Overwhelming)", "Al-Fajr (The Dawn)", "Al-Balad (The City)",
            "Ash-Shams (The Sun)", "Al-Layl (The Night)", "Ad-Duhaa (The Morning Hours)", "Ash-Sharh (The Relief)", "At-Tin (The Fig)",
            "Al-'Alaq (The Clot)", "Al-Qadr (The Power)", "Al-Bayyinah (The Clear Proof)", "Az-Zalzalah (The Earthquake)", "Al-'Adiyat (The Courser)",
            "Al-Qari'ah (The Calamity)", "At-Takathur (The Rivalry in World Increase)", "Al-'Asr (The Declining Day)", "Al-Humazah (The Traducer)", "Al-Fil (The Elephant)",
            "Quraysh (Quraysh)", "Al-Ma'un (The Small Kindnesses)", "Al-Kawthar (The Abundance)", "Al-Kafirun (The Disbelievers)", "An-Nasr (The Divine Support)",
            "Al-Masad (The Palm Fiber)", "Al-Ikhlas (The Sincerity)", "Al-Falaq (The Daybreak)", "An-Nas (Mankind)"
        ],
        "ar": [
            "الفاتحة", "البقرة", "آل عمران", "النساء", "المائدة",
            "الأنعام", "الأعراف", "الأنفال", "التوبة", "يونس",
            "هود", "يوسف", "الرعد", "إبراهيم", "الحجر",
            "النحل", "الإسراء", "الكهف", "مريم", "طه",
            "الأنبياء", "الحج", "المؤمنون", "النور", "الفرقان",
            "الشعراء", "النمل", "القصص", "العنكبوت", "الروم",
            "لقمان", "السجدة", "الأحزاب", "سبإ", "فاطر",
            "يس", "الصافات", "ص", "الزمر", "غافر",
            "فصلت", "الشورى", "الزخرف", "الدخان", "الجاثية",
            "الأحقاف", "محمد", "الفتح", "الحجرات", "ق",
            "الذاريات", "الطور", "النجم", "القمر", "الرحمن",
            "الواقعة", "الحديد", "المجادلة", "الحشر", "الممتحنة",
            "الصف", "الجمعة", "المنافقون", "التغابن", "الطلاق",
            "التحريم", "الملك", "القلم", "الحاقة", "المعارج",
            "نوح", "الجن", "المزمل", "المدثر", "القيامة",
            "الإنسان", "المرسلات", "النبإ", "النازعات", "عبس",
            "التكوير", "الانفطار", "المطففين", "الانشقاق", "البروج",
            "الطارق", "الأعلى", "الغاشية", "الفجر", "البلد",
            "الشمس", "الليل", "الضحى", "الشرح", "التين",
            "العلق", "القدر", "البينة", "الزلزلة", "العاديات",
            "القارعة", "التكاثر", "العصر", "الهمزة", "الفيل",
            "قريش", "الماعون", "الكوثر", "الكافرون", "النصر",
            "المسد", "الإخلاص", "الفلق", "الناس"
        ]
    }
    SURAH_NAMES_RU = SURAH_NAMES["ru"]

    def __init__(self, manifest_path: Optional[str] = None, translations_path: Optional[str] = None):
        """
        Initializes the Quran engine.
        Note on Morphological AST Structure:
        The manifest contains 130,030 sub-tokens. 208 of these sub-tokens have form: "" with flags ('PRON', 'SUFF', '1S').
        This is a precise linguistic feature representing orthographically elided 1st-person pronoun morphemes (ياء المتكلم المحذوفة)
        in vocative Quranic constructions (e.g. رَبِّ 'My Lord').
        """
        self.manifest_path = manifest_path or MANIFEST_PATH
        self.translations_path = translations_path or TRANSLATIONS_PATH
        self.ayahs: Dict[str, Dict[str, Any]] = {}
        self.translations: Dict[str, Dict[str, str]] = {}
        self.surahs: Dict[int, List[Dict[str, Any]]] = {}
        self.root_index: Dict[str, List[Tuple[str, int, int]]] = {}  # root -> [(ayah_id, word_i, subtoken_j)]
        self.lemma_index: Dict[str, List[str]] = {}                  # lemma -> [ayah_id]
        self.normalized_ayahs: Dict[str, str] = {}                   # ayah_id -> normalized_text
        self.all_roots: Set[str] = set()
        self.all_lemmas: Set[str] = set()
        self.total_tokens: int = 0

        self._load_translations()
        self._load_manifest()

    def _load_translations(self) -> None:
        """Loads offline multi-language translations (kk, ru, en, tr, uz, id) for all 6,236 ayahs."""
        import os
        if os.path.exists(self.translations_path):
            try:
                with open(self.translations_path, 'r', encoding='utf-8') as f:
                    self.translations = json.load(f)
            except Exception as e:
                print(f"Warning: could not load translations: {e}")

    def _load_manifest(self) -> None:
        """Loads and indexes the security manifest into RAM."""
        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                ayah_id = data['id']
                sura = data['sura']
                ayah_num = data['ayah']

                data['transliteration'] = arabic_to_latin_transliteration(data['text'])
                data['translations'] = self.translations.get(ayah_id, {})
                self.ayahs[ayah_id] = data

                if sura not in self.surahs:
                    self.surahs[sura] = []
                self.surahs[sura].append(data)

                # Normalized string for full-text search
                self.normalized_ayahs[ayah_id] = normalize_arabic(data['text'])

                # Token-level indexing
                for token in data['tokens']:
                    self.total_tokens += 1
                    root = token.get('root')
                    lemma = token.get('lemma')
                    i = token['i']
                    j = token['j']

                    if root:
                        self.all_roots.add(root)
                        if root not in self.root_index:
                            self.root_index[root] = []
                        self.root_index[root].append((ayah_id, i, j))

                    if lemma:
                        self.all_lemmas.add(lemma)
                        if lemma not in self.lemma_index:
                            self.lemma_index[lemma] = []
                        if ayah_id not in self.lemma_index[lemma]:
                            self.lemma_index[lemma].append(ayah_id)

    def get_ayah(self, sura: int, ayah: int) -> Optional[Dict[str, Any]]:
        """O(1) lookup of an Ayah record."""
        return self.ayahs.get(f"{sura}:{ayah}")

    def get_ayah_by_id(self, ayah_id: str) -> Optional[Dict[str, Any]]:
        """O(1) lookup by string coordinate (e.g. '2:255')."""
        return self.ayahs.get(ayah_id)

    def is_valid_coordinate(self, sura: int, ayah: int) -> Tuple[bool, str]:
        """Validates if sura:ayah strictly exists in the canonical Quran."""
        if not (1 <= sura <= 114):
            return False, f"Сура {sura} не существует. В Коране ровно 114 сур."
        max_ayahs = self.CANONICAL_AYAH_COUNTS[sura - 1]
        if not (1 <= ayah <= max_ayahs):
            surah_name = self.SURAH_NAMES_RU[sura - 1]
            return False, f"В суре {sura} ({surah_name}) всего {max_ayahs} аятов, запрошен аят {ayah}."
        return True, "OK"

    def search_by_root(self, root: str) -> List[Dict[str, Any]]:
        """Finds all Ayahs and specific words containing the given 3/4-letter root."""
        root_norm = normalize_arabic(root).replace(" ", "")
        # Exact root match
        matches = []
        target_root = None
        for r in self.all_roots:
            if normalize_arabic(r) == root_norm or r == root:
                target_root = r
                break

        if not target_root or target_root not in self.root_index:
            return []

        seen_ayahs = set()
        results = []
        for ayah_id, word_i, sub_j in self.root_index[target_root]:
            if ayah_id not in seen_ayahs:
                seen_ayahs.add(ayah_id)
                ayah_data = self.ayahs[ayah_id]
                # Extract specific matching tokens
                matching_tokens = [t for t in ayah_data['tokens'] if t.get('root') == target_root]
                results.append({
                    "id": ayah_id,
                    "sura": ayah_data['sura'],
                    "ayah": ayah_data['ayah'],
                    "surah_name": self.SURAH_NAMES_RU[ayah_data['sura'] - 1],
                    "text": ayah_data['text'],
                    "transliteration": ayah_data.get('transliteration', ''),
                    "translations": ayah_data.get('translations', {}),
                    "matching_tokens": matching_tokens
                })
        return results

    def search_by_lemma(self, lemma: str) -> List[Dict[str, Any]]:
        """Finds all Ayahs containing the given lemma."""
        norm_target = normalize_arabic(lemma)
        target_lemmas = [l for l in self.all_lemmas if normalize_arabic(l) == norm_target]
        results = []
        seen = set()
        for l in target_lemmas:
            for ayah_id in self.lemma_index.get(l, []):
                if ayah_id not in seen:
                    seen.add(ayah_id)
                    ayah_data = self.ayahs[ayah_id]
                    results.append({
                        "id": ayah_id,
                        "sura": ayah_data['sura'],
                        "ayah": ayah_data['ayah'],
                        "surah_name": self.SURAH_NAMES_RU[ayah_data['sura'] - 1],
                        "text": ayah_data['text']
                    })
        return results

    def search_text(self, query: str, lang: str = "all", limit: int = 30) -> List[Dict[str, Any]]:
        """
        Universal Multi-Language Full-Text Search across:
        1. Canonical Arabic text (normalized)
        2. Latin Transliteration
        3. 7-Language Translations (kk, ru, en, ar, tr, uz, id)
        4. Coordinate queries (e.g. '2:255', '112:1')
        """
        if not query or not query.strip():
            return []

        q_clean = query.strip()
        q_lower = q_clean.lower()
        norm_arabic_q = normalize_arabic(q_clean)
        
        # Check coordinate pattern (e.g. 2:255 or 2 255)
        coord_match = re.match(r'^(\d{1,3})[:\s\-](\d{1,3})$', q_clean)
        if coord_match:
            s_num = int(coord_match.group(1))
            a_num = int(coord_match.group(2))
            if 1 <= s_num <= 114:
                ayah_data = self.get_ayah(s_num, a_num)
                if ayah_data:
                    return [{
                        "id": f"{s_num}:{a_num}",
                        "sura": s_num,
                        "ayah": a_num,
                        "surah_name_ru": self.SURAH_NAMES_RU[s_num - 1],
                        "text_uthmani": ayah_data.get("text_uthmani", ayah_data.get("text")),
                        "transliteration": ayah_data.get("transliteration", ""),
                        "translations": ayah_data.get("translations", {}),
                        "match_type": "exact_coordinate"
                    }]

        results = []
        for ayah_id, ayah_data in self.ayahs.items():
            sura = ayah_data['sura']
            ayah = ayah_data['ayah']
            ar_text = ayah_data.get("text_uthmani") or ayah_data.get("text", "")
            norm_ar = self.normalized_ayahs.get(ayah_id, "")
            translit = ayah_data.get("transliteration", "")
            translations = ayah_data.get("translations", {})
            
            matched = False
            match_source = ""
            
            # 1. Match Arabic
            if norm_arabic_q and norm_arabic_q in norm_ar:
                matched = True
                match_source = "arabic"
            # 2. Match Transliteration
            elif q_lower in translit.lower():
                matched = True
                match_source = "transliteration"
            # 3. Match Translations
            else:
                for t_lang, t_text in translations.items():
                    if t_text and q_lower in t_text.lower():
                        matched = True
                        match_source = f"translation_{t_lang}"
                        break

            if matched:
                results.append({
                    "id": ayah_id,
                    "sura": sura,
                    "ayah": ayah,
                    "surah_name_ru": self.SURAH_NAMES_RU[sura - 1],
                    "text_uthmani": ar_text,
                    "transliteration": translit,
                    "translations": translations,
                    "match_type": match_source
                })
                if len(results) >= limit:
                    break

        return results

    def get_stats(self) -> Dict[str, Any]:
        """Returns comprehensive corpus statistics."""
        return {
            "total_surahs": len(self.surahs),
            "total_ayahs": len(self.ayahs),
            "total_tokens": self.total_tokens,
            "unique_roots": len(self.all_roots),
            "unique_lemmas": len(self.all_lemmas),
            "manifest_path": self.manifest_path
        }
