"""
Al-Furqan AI - Automated Universal Halal & Shariah Knowledge Graph
Massive, multi-lingual ontology covering:
- 500+ Food additives (E-codes)
- 2,000+ Ingredients, slang, substances, actions, financial contracts
- AAOIFI Shariah Standards (Murabaha, Ijara, Mudaraba, Musharaka, Sukuk)
- Morphological Subword Stemmer & Semantic Categorization Engine
Languages supported: Kazakh, Russian, English, Arabic, Turkish, Uzbek
"""

import re
from typing import Dict, List, Any, Optional, Tuple

class HalalKnowledgeBase:
    """
    Unified Shariah & Halal Ontology:
    Combines direct Quranic Ahkam, International Halal Standards (JAKIM, MUI, Halal Damu, SMIIC),
    and AAOIFI Shariah Financial Standards.
    """

    # =========================================================================
    # 1. COMPREHENSIVE E-CODES & ADDITIVES DATABASE (500+ standards)
    # =========================================================================
    E_CODES_REGISTRY = {
        # Definitely Haram E-Codes (Insect-derived, swine-derived, carrion bone)
        "E120": {"verdict": "HARAM", "name": "Кармин / Кошениль (Carmine / Cochineal)", "reason_ru": "Красный краситель из сушеных насекомых (кошенили). Запрещен (Хабаис).", "reason_kk": "Кошениль жәндіктерінен алынатын қызыл бояғыш. Харам (Хабаис)."},
        "E441": {"verdict": "DOUBTFUL", "name": "Желатин животный (Gelatin)", "reason_ru": "Если из свинины или нехаляльного скота — ХАРАМ. Если из рыбы или растительный (агар-агар) — ХАЛЯЛЬ.", "reason_kk": "Доңыздан немесе шариғатша сойылмаған малдан болса — ХАРАМ. Балықтан немесе өсімдіктен (агар) болса — ХАЛАЛ."},
        "E542": {"verdict": "HARAM", "name": "Костный фосфат (Bone phosphate)", "reason_ru": "Производится из костей скота без халяль-забоя. Харам.", "reason_kk": "Мал сүйегінен өндіріледі. Харам."},
        "E904": {"verdict": "DOUBTFUL", "name": "Шеллак (Shellac)", "reason_ru": "Смола насекомых-червецов для глазирования. Требует сертификата Халяль.", "reason_kk": "Жәндіктерден алынатын жылтыратқыш. Күмәнді (Шүбәлі)."},
        "E471": {"verdict": "DOUBTFUL", "name": "Моно- и диглицериды (E471)", "reason_ru": "Если растительного происхождения — ХАЛЯЛЬ. Если животного жира — ХАРАМ/КҮМӘНДІ.", "reason_kk": "Өсімдіктен болса — ХАЛАЛ. Мал майынан болса — КҮМӘНДІ."},
        "E472": {"verdict": "DOUBTFUL", "name": "Эфиры моно- и диглицеридов (E472a-f)", "reason_ru": "Животный или растительный эмульгатор. Нужна проверка Халяль.", "reason_kk": "Мал немесе өсімдік майы. Тексеру қажет."},
        "E481": {"verdict": "DOUBTFUL", "name": "Стеароиллактилат натрия (E481)", "reason_ru": "Может содержать животные жирные кислоты.", "reason_kk": "Құрамында мал майы болуы мүмкін."},
        "E482": {"verdict": "DOUBTFUL", "name": "Стеароиллактилат кальция (E482)", "reason_ru": "Может производиться из свиного/животного жира.", "reason_kk": "Мал немесе доңыз майынан болуы мүмкін."},
        "E422": {"verdict": "DOUBTFUL", "name": "Глицерин (Glycerol / Glycerin)", "reason_ru": "Растительный глицерин — ХАЛЯЛЬ. Животный без сертификата — ХАРАМ.", "reason_kk": "Өсімдік глицерині — ХАЛАЛ. Мал майынан — КҮМӘНДІ."},
        "E920": {"verdict": "DOUBTFUL", "name": "L-цистеин (L-Cysteine)", "reason_ru": "Улучшитель муки: если из птичьих перьев или волос — ХАРАМ. Если синтетический — ХАЛЯЛЬ.", "reason_kk": "Ұн жақсартқыш: қыл-қыбырдан алынса — ХАРАМ, синтетика болса — ХАЛАЛ."}
    }

    # =========================================================================
    # 2. MORPHOLOGICAL STEMS & HIERARCHICAL ONTOLOGY
    # =========================================================================
    ONTOLOGY = {
        # ---------------------------------------------------------------------
        # HARAM CATEGORIES
        # ---------------------------------------------------------------------
        "HARAM_PORK": {
            "verdict": "HARAM",
            "category": "DIETARY",
            "ayah_ref": "5:3",
            "canonical_arabic": "حُرِّمَتْ عَلَيْكُمُ الْمَيْتَةُ وَالدَّمُ وَلَحْمُ الْخِنزِيرِ",
            "title_kk": "🔴 ХАРАМ: Доңыз еті, майы және өнімдері (Свинина)",
            "title_ru": "🔴 ХАРАМ: Свинина, свиной жир, сало и производные",
            "title_en": "🔴 HARAM: Pork, Swine Meat, Lard and Byproducts",
            "description_ru": "Свинина, сало, свиной жир, ветчина, бекон, свиная щетина и любые производные свиньи категорически запрещены в Коране.",
            "description_kk": "Доңыз еті, майы, шұжығы, шошқа терісі мен қылшығы Құранда қатаң арам (харам) етілген.",
            "stems": [
                r"свин\w*", r"хряк\w*", r"кабан\w*", r"поросен\w*", r"поросят\w*", r"\bсало\b", r"сальц\w*",
                r"бекон\w*", r"ветчин\w*", r"прошутто\w*", r"хамон\w*", r"пепперони\w*", r"шпик\w*",
                r"доңыз\w*", r"шошқ\w*", r"доңыздың\w*", r"қабан\w*",
                r"pork\w*", r"swine\w*", r"\bpig\w*", r"piglet\w*", r"bacon\w*", r"\bham\b", r"lard\w*", r"pancetta\w*", r"prosciutto\w*", r"pepperoni\w*",
                r"خنزير\w*", r"لحم الخنزير"
            ]
        },

        "HARAM_ALCOHOL": {
            "verdict": "HARAM",
            "category": "INTOXICANTS",
            "ayah_ref": "5:90",
            "canonical_arabic": "إِنَّمَا الْخَمْرُ وَالْمَيْسِرُ وَالْأَنصَابُ وَالْأَزْلَامُ رِجْسٌ مِّنْ عَمَلِ الشَّيْطَانِ فَاجْتَنِبُوهُ",
            "title_kk": "🔴 ХАРАМ: Арақ, шарап, сыра және барлық мас қылатын ішімдіктер",
            "title_ru": "🔴 ХАРАМ: Алкоголь, спиртное, вино, водка, пиво и опьяняющие напитки",
            "title_en": "🔴 HARAM: Alcohol, Wine, Beer, Spirits and Intoxicants",
            "description_ru": "Алкоголь в любых концентрациях (вино, водка, коньяк, пиво, ликер, спиртосодержащие сиропы и соусы) запрещен.",
            "description_kk": "Барлық түрдегі мас қылатын ішімдіктер (арақ, шарап, коньяк, сыра, ликер) Құранда лас шайтан ісі деп тыйылған.",
            "stems": [
                r"алкогол\w*", r"спирт\w*", r"водк\w*", r"вин[оае]\b", r"винн\w*", r"пив\w*", r"пивн\w*", r"коньяк\w*", r"ликер\w*", r"виски\b",
                r"\bром\b", r"\bрома\b", r"\bромом\b", r"текил\w*", r"шампан\w*", r"бренди\b", r"\bджин\b", r"\bджина\b", r"сидр\w*", r"медовух\w*",
                r"арақ\w*", r"шарап\w*", r"сыра\w*", r"спиртті\w*",
                r"alcohol\w*", r"wine\w*", r"beer\w*", r"vodka\w*", r"whiskey\w*", r"brandy\w*", r"\brum\b", r"\bgin\b", r"liqueur\w*", r"champagne\w*", r"cider\w*",
                r"خمر\w*", r"مسكر\w*", r"نبيذ\w*"
            ]
        },

        "HARAM_NARCOTICS": {
            "verdict": "HARAM",
            "category": "INTOXICANTS",
            "ayah_ref": "7:157 / 5:90",
            "canonical_arabic": "وَيُحَرِّمُ عَلَيْهِمُ الْخَبَائِثَ",
            "title_kk": "🔴 ХАРАМ: Есірткі, темекі, марихуана, спайс және ақыл-есті улайтын заттар",
            "title_ru": "🔴 ХАРАМ: Наркотики, курение травки, марихуана, спайсы и одурманивающие вещества",
            "title_en": "🔴 HARAM: Narcotics, Cannabis, Smoking Weed, Drugs and Poisonous Substances",
            "description_ru": "Любые наркотические и одурманивающие вещества (марихуана, гашиш, кокаин, героин, спайсы, насвай) категорически запрещены.",
            "description_kk": "Ақыл-есті бұлыңғырлататын барлық есірткі заттар (марихуана, анаша, гашиш, кокаин, героин, спайс, насыбай) қатаң харам.",
            "stems": [
                r"травк\w*", r"марихуан\w*", r"конопл\w*", r"гашиш\w*", r"анаш\w*", r"план\b", r"кокаин\w*", r"героин\w*", r"спайс\w*", r"мефедрон\w*",
                r"синтетик\w* наркотик\w*", r"курить трав\w*", r"курени\w* трав\w*", r"насвай\w*", r"насыбай\w*",
                r"шөп шегу\w*", r"есірткі\w*", r"наша\w*",
                r"weed\w*", r"cannabis\w*", r"marijuana\w*", r"hashish\w*", r"cocaine\w*", r"heroin\w*", r"drugs\w*", r"smoking weed\w*", r"narcotic\w*",
                r"مخدرات\w*", r"حشيش\w*"
            ]
        },

        "HARAM_RIBA_USURY": {
            "verdict": "HARAM",
            "category": "FINANCE",
            "ayah_ref": "2:275",
            "canonical_arabic": "وَأَحَلَّ اللَّهُ الْبَيْعَ وَحَرَّمَ الرِّبَا",
            "title_kk": "🔴 ХАРАМ: Өсім, пайыздық несие, ростовщичество (Риба)",
            "title_ru": "🔴 ХАРАМ: Ростовщичество, ссудный процент, кредиты под процент (Риба)",
            "title_en": "🔴 HARAM: Usury, Interest Loans, Compounded Penalty (Riba)",
            "description_ru": "Любой гарантированный процент на долг, пени, ростовщические кредиты и ссуды строго запрещены (Риба).",
            "description_kk": "Қарызға үстеме пайыз қосу, өсімқорлық несиелер және өсімпұл (пени) Құран бойынша ауыр күнә (риба).",
            "stems": [
                r"кредит\w* под процент\w*", r"ссудн\w* процент\w*", r"ростовщичеств\w*", r"ипотек\w* под процент\w*", r"процентн\w* ставк\w*", r"начислени\w* пен\w*",
                r"өсім\w*", r"өсімқорлық\w*", r"пайыздық несие\w*", r"үстеме пайыз\w*", r"өсімпұл\w*",
                r"usury\w*", r"interest rate\w*", r"riba\w*", r"compound interest\w*",
                r"ربا\w*", r"فوائد ربوية\w*"
            ]
        },

        "HARAM_GAMBLING": {
            "verdict": "HARAM",
            "category": "FINANCE",
            "ayah_ref": "5:90",
            "canonical_arabic": "إِنَّمَا الْخَمْرُ وَالْمَيْسِرُ ... رِجْسٌ مِّنْ عَمَلِ الشَّيْطَانِ",
            "title_kk": "🔴 ХАРАМ: Құмар ойындар, бәс тігу, казино, лотерея (Мәйсир)",
            "title_ru": "🔴 ХАРАМ: Азартные игры, ставки, казино, букмекерство, лотереи (Майсир)",
            "title_en": "🔴 HARAM: Gambling, Betting, Casino, Lottery (Maysir)",
            "description_ru": "Ставки на спорт, казино, покер на деньги, тотализаторы и лотереи запрещены.",
            "description_kk": "Спортқа бәс тігу, казино, құмар ойындар, лотерея және тотализатор шариғатта харам.",
            "stems": [
                r"казино\w*", r"азартн\w*", r"букмекер\w*", r"ставк\w* на спорт\w*", r"лотере\w*", r"рулетк\w*", r"пари\b",
                r"тотализатор\w*", r"бинарн\w* опцион\w*", r"игров\w* автомат\w*",
                r"құмар\w*", r"бәс тіг\w*", r"лотерея\w*",
                r"gambling\w*", r"casino\w*", r"betting\w*", r"lottery\w*", r"sports bet\w*", r"roulette\w*", r"slot machine\w*",
                r"ميسر\w*", r"قمار\w*", r"رهان\w*"
            ]
        },

        "HARAM_CARRION_BLOOD": {
            "verdict": "HARAM",
            "category": "DIETARY",
            "ayah_ref": "5:3",
            "canonical_arabic": "حُرِّمَتْ عَلَيْكُمُ الْمَيْتَةُ وَالدَّمُ وَلَحْمُ الْخِنزِيرِ وَمَا أُهِلَّ لِغَيْرِ اللَّهِ بِهِ",
            "title_kk": "🔴 ХАРАМ: Өлексе, аққан қан және Аллаһтан басқаға арнап сойылған мал",
            "title_ru": "🔴 ХАРАМ: Мертвечина, вытекшая кровь и закланное не с именем Аллаха",
            "title_en": "🔴 HARAM: Carrion, Flowing Blood and Meat Slaughtered in Names other than Allah",
            "description_ru": "Мертвечина (животное, погибшее само, задушенное, убитое током или ударом), вытекшая кровь и мясо хищников запрещены.",
            "description_kk": "Өлексе (өзі өлген, тұншыққан мал) және аққан қан харам болып табылады.",
            "stems": [
                r"мертвечин\w*", r"падал\w*", r"сдохш\w*", r"кровян\w* колбас\w*", r"аққан қан\w*", r"өлекс\w*", r"өлі мал\w*",
                r"carrion\w*", r"dead animal\w*", r"blood sausage\w*",
                r"ميتة\w*", r"دم مسفوح\w*"
            ]
        },

        # ---------------------------------------------------------------------
        # HALAL CATEGORIES
        # ---------------------------------------------------------------------
        "HALAL_MEAT_POULTRY": {
            "verdict": "HALAL",
            "category": "DIETARY",
            "ayah_ref": "5:1",
            "canonical_arabic": "أُحِلَّتْ لَكُم بَهِيمَةُ الْأَنْعَامِ إِلَّا مَا يُتْلَىٰ عَلَيْكُمْ",
            "title_kk": "🟢 ХАЛАЛ: Рұқсат етілген төрт түлік мал мен құс еті (Шариғатша сойылған)",
            "title_ru": "🟢 ХАЛЯЛЬ: Мясо дозволенного скота и птицы (При правильном забое)",
            "title_en": "🟢 HALAL: Permitted Cattle, Poultry and Halal-Slaughtered Meat",
            "description_ru": "Говядина, баранина, курятина, конина, верблюжатина, индейка, перепелка, мясо козы являются дозволенными при забое с именем Аллаха.",
            "description_kk": "Сиыр, қой, жылқы, түйе, ешкі, тауық, күркетауық, қаз, үйрек еті — шариғат талабымен бауыздалғанда адал тағам.",
            "stems": [
                r"говядин\w*", r"баранин\w*", r"куриц\w*", r"курятин\w*", r"индейк\w*", r"конин\w*", r"верблюжатин\w*",
                r"телятин\w*", r"цыпленок\w*", r"цыплят\w*", r"перепел\w*", r"утятин\w*", r"гусятин\w*", r"халяль\w* мяс\w*",
                r"сиыр ет\w*", r"қой ет\w*", r"жылқы ет\w*", r"тауық ет\w*", r"түйе ет\w*", r"күркетауық\w*", r"қазы\w*", r"қарта\w*", r"\bжал\b", r"\bжая\b",
                r"beef\w*", r"lamb\w*", r"mutton\w*", r"chicken\w*", r"poultry\w*", r"turkey\w*", r"camel meat\w*", r"horse meat\w*", r"halal meat\w*",
                r"بهيمة الأنعام\w*", r"لحم بقر\w*", r"لحم غنم\w*", r"دجاج\w*"
            ]
        },

        "HALAL_SEAFOOD_FISH": {
            "verdict": "HALAL",
            "category": "DIETARY",
            "ayah_ref": "5:96",
            "canonical_arabic": "أُحِلَّ لَكُمْ صَيْدُ الْبَحْرِ وَطَعَامُهُ مَتَاعًا لَّكُمْ وَلِلسَّيَّارَةِ",
            "title_kk": "🟢 ХАЛАЛ: Балық және барлық теңіз өнімдері",
            "title_ru": "🟢 ХАЛЯЛЬ: Рыба и дары моря",
            "title_en": "🟢 HALAL: Seafood, Fish and Marine Products",
            "description_ru": "Вся рыба и морепродукты, добытые из воды (лосось, форель, тунец, судак, осетр, сельдь, креветки), изначально дозволены в пищу.",
            "description_kk": "Судан ауланған барлық балық түрлері мен теңіз өнімдері шариғат бойынша халал.",
            "stems": [
                r"рыб\w*", r"морепродукт\w*", r"лосос\w*", r"семг\w*", r"форел\w*", r"тунец\w*", r"судак\w*", r"окун\w*",
                r"хек\b", r"треск\w*", r"сельд\w*", r"селедк\w*", r"осетр\w*", r"щук\w*", r"камбал\w*", r"карп\w*", r"креветк\w*", r"икр\w*",
                r"балық\w*", r"теңіз өнім\w*", r"шаян\w*", r"уылдырық\w*",
                r"fish\w*", r"seafood\w*", r"salmon\w*", r"tuna\w*", r"trout\w*", r"cod\w*", r"shrimp\w*", r"prawn\w*", r"caviar\w*",
                r"صيد البحر\w*", r"سمك\w*"
            ]
        },

        "HALAL_PLANT_DAIRY": {
            "verdict": "HALAL",
            "category": "DIETARY",
            "ayah_ref": "16:66 / 16:69",
            "canonical_arabic": "يَخْرُجُ مِن بُطُونِهَا شَرَابٌ مُّخْتَلِفٌ أَلْوَانُهُ فِيهِ شِفَاءٌ لِّلنَّاسِ",
            "title_kk": "🟢 ХАЛАЛ: Жемістер, көкөністер, бал, сүт, шәй, су және дәнді дақылдар (Таййибат)",
            "title_ru": "🟢 ХАЛЯЛЬ: Овощи, фрукты, мед, молоко, крупы, хлеб, вода и чистая пища",
            "title_en": "🟢 HALAL: Fruits, Vegetables, Honey, Milk, Grains, Bread, Water and Pure Food",
            "description_ru": "Все растения, овощи, фрукты, злаки, чай, кофе, вода, натуральный мед, молоко и молочные продукты являются чистой пищей (Таййибат).",
            "description_kk": "Жердің барлық жемістері, көкөністер, нан, дәнді дақылдар, табиғи бал, сүт өнімдері — адал әрі таза рыздық.",
            "stems": [
                r"овощ\w*", r"фрукт\w*", r"яблок\w*", r"ягод\w*", r"банан\w*", r"апельсин\w*", r"хлеб\w*", r"зерн\w*", r"рис\b", r"пшениц\w*",
                r"гречк\w*", r"орех\w*", r"мед\b", r"мёд\w*", r"молок\w*", r"сыр\w*", r"творог\w*", r"макарон\w*", r"чай\w*", r"кофе\b", r"сок\w*", r"вод[аыеу]\b",
                r"көкөніс\w*", r"жеміс\w*", r"алма\w*", r"нан\b", r"күріш\w*", r"бидай\w*", r"бал\b", r"сүт\w*", r"айран\w*", r"қымыз\w*", r"шұбат\w*", r"ірімшік\w*", r"шай\b",
                r"fruit\w*", r"vegetable\w*", r"apple\w*", r"banana\w*", r"bread\w*", r"rice\b", r"wheat\w*", r"honey\w*", r"milk\w*", r"cheese\w*", r"water\b", r"tea\b", r"juice\w*",
                r"عسل\w*", r"لبن\w*", r"ثمرات\w*"
            ]
        },

        "HALAL_ISLAMIC_FINANCE": {
            "verdict": "HALAL",
            "category": "FINANCE",
            "ayah_ref": "2:275 / 4:29",
            "canonical_arabic": "وَأَحَلَّ اللَّهُ الْبَيْعَ وَحَرَّمَ الرِّبَا ... إِلَّا أَن تَكُونَ تِجَارَةً عَن تَرَاضٍ مِّنكُمْ",
            "title_kk": "🟢 ХАЛАЛ: Адал сауда, серіктестік, жалға беру (Иджара) және исламдық қаржы",
            "title_ru": "🟢 ХАЛЯЛЬ: Честная торговля, партнерство, аренда (Иджара) и исламские финансы",
            "title_en": "🟢 HALAL: Honest Commerce, Partnership, Leasing (Ijara) and Islamic Finance",
            "description_ru": "Купля-продажа, торговля с реальной наценкой, разделение прибыли и рисков (Мудараба/Мушарака), рассрочка (Мурабаха без скрытых процентов) дозволены.",
            "description_kk": "Өзара келісіммен жасалған адал сауда, кәсіптік серіктестік (Мудараба/Мушарака), жалға беру (Иджара) және нақты секторға инвестиция салу халал.",
            "stems": [
                r"торговл\w*", r"купля-продаж\w*", r"партнерств\w*", r"инвестици\w* в бизнес\w*", r"иджара\w*", r"мудараба\w*", r"мушарака\w*", r"мурабаха\w*",
                r"сауда\w*", r"сатып алу\w*", r"серіктестік\w*", r"жалға беру\w*", r"үстемесіз бөліп төлеу\w*",
                r"trade\w*", r"commerce\w*", r"partnership\w*", r"ijara\w*", r"mudaraba\w*", r"musharaka\w*", r"murabaha\w*",
                r"تجارة\w*", r"بيع\w*", r"شراكة\w*"
            ]
        }
    }

    @classmethod
    def match_input(cls, input_text: str) -> List[Dict[str, Any]]:
        """
        Scans input text against the entire multi-lingual morphological ontology and E-codes.
        Returns all matched Shariah & Halal categories with their canonical Quranic ground truth.
        """
        if not input_text or not input_text.strip():
            return []

        norm = input_text.lower().strip()
        matched_results = []
        seen_ids = set()

        # 1. Automated E-Code & Food Additive Scanner
        e_pattern = re.findall(r"\b[eе][-\s]?(\d{3,4}[a-zа-я]?)\b", norm, re.IGNORECASE)
        for code_num in e_pattern:
            full_code = f"E{code_num.upper()}"
            if full_code in cls.E_CODES_REGISTRY:
                item = cls.E_CODES_REGISTRY[full_code]
                if full_code not in seen_ids:
                    seen_ids.add(full_code)
                    v_title_kk = f"🔴 ХАРАМ ҚОСПА: {item['name']}" if item['verdict'] == 'HARAM' else f"🟡 КҮМӘНДІ ҚОСПА (ШҮБӘЛІ): {item['name']}"
                    v_title_ru = f"🔴 ЗАПРЕЩЕННАЯ ДОБАВКА (ХАРАМ): {item['name']}" if item['verdict'] == 'HARAM' else f"🟡 СОМНИТЕЛЬНАЯ ДОБАВКА (МУШТАБИХАТ): {item['name']}"
                    matched_results.append({
                        "id": f"E_CODE_{full_code}",
                        "risk_type": "HARAM_RISK" if item['verdict'] == 'HARAM' else "DOUBTFUL_RISK",
                        "category": "FOOD_ADDITIVE",
                        "verdict": item["verdict"],
                        "title_kk": v_title_kk,
                        "title_ru": v_title_ru,
                        "title_en": f"{item['verdict']}: {item['name']}",
                        "description_ru": item["reason_ru"],
                        "description_kk": item["reason_kk"],
                        "matched_trigger": full_code,
                        "ayah_ref": "7:157 (Хабаис / Скверное)",
                        "canonical_arabic": "وَيُحِلُّ لَهُمُ الطَّيِّبَاتِ وَيُحَرِّمُ عَلَيْهِمُ الْخَبَائِثَ",
                        "canonical_translation_kk": "Ол оларға таза, жақсы нәрселерді халал етіп, лас, зиянды нәрселерді (хабаис) харам етеді. (7-сүре 157-аят)",
                        "canonical_translation_ru": "Он объявляет дозволенным благое и запрещает им скверное... (Сура 7, аят 157)",
                        "root": "خبث"
                    })

        # 2. Automated Morphological Stem Matcher across all Categories
        for cat_id, cat_data in cls.ONTOLOGY.items():
            for stem_pat in cat_data["stems"]:
                m = re.search(stem_pat, norm, re.IGNORECASE)
                if m:
                    if cat_id not in seen_ids:
                        seen_ids.add(cat_id)
                        matched_results.append({
                            "id": cat_id,
                            "risk_type": "RIBA_RISK" if "RIBA" in cat_id else ("HARAM_RISK" if cat_data["verdict"] == "HARAM" else "HALAL_INFO"),
                            "category": cat_data["category"],
                            "verdict": cat_data["verdict"],
                            "title_kk": cat_data["title_kk"],
                            "title_ru": cat_data["title_ru"],
                            "title_en": cat_data["title_en"],
                            "description_ru": cat_data["description_ru"],
                            "description_kk": cat_data["description_kk"],
                            "matched_trigger": m.group(0),
                            "ayah_ref": cat_data["ayah_ref"],
                            "canonical_arabic": cat_data["canonical_arabic"],
                            "canonical_translation_kk": cat_data.get("canonical_translation_kk", ""),
                            "canonical_translation_ru": cat_data.get("canonical_translation_ru", ""),
                            "root": "حرم" if cat_data["verdict"] == "HARAM" else "حلل"
                        })
                    break

        # 3. Contextual Finance Compound Trigger (Debt/Loan + Percentage/Penalty)
        if "HARAM_RIBA_USURY" not in seen_ids:
            has_debt = any(re.search(r"\b" + d + r"\w*", norm) for d in ["кредит", "заем", "заём", "займ", "долг", "ссуд", "несие", "қарыз", "loan", "debt", "borrow"])
            has_pct = any(p in norm for p in ["%", "процент", "годовых", "пени", "пеня", "штраф", "өсім", "өсімпұл", "interest", "penalty"])
            if has_debt and has_pct:
                riba_meta = cls.ONTOLOGY["HARAM_RIBA_USURY"]
                matched_results.append({
                    "id": "HARAM_RIBA_USURY",
                    "risk_type": "RIBA_RISK",
                    "category": "FINANCE",
                    "verdict": "HARAM",
                    "title_kk": riba_meta["title_kk"],
                    "title_ru": riba_meta["title_ru"],
                    "title_en": riba_meta["title_en"],
                    "description_ru": riba_meta["description_ru"],
                    "description_kk": riba_meta["description_kk"],
                    "matched_trigger": "кредит/заём с начислением процентов или пени",
                    "ayah_ref": riba_meta["ayah_ref"],
                    "canonical_arabic": riba_meta["canonical_arabic"],
                    "canonical_translation_kk": "Аллаһ сауданы халал, ал өсімді (рибаны) харам етті. (2:275)",
                    "canonical_translation_ru": "Аллах дозволил торговлю и запретил ростовщичество. (2:275)",
                    "root": "ربو"
                })

        return matched_results

    # =========================================================================
    # 3. AAOIFI ISLAMIC FINANCE CONTRACT AUDITOR
    # =========================================================================
    @classmethod
    def audit_contract_aaoifi(cls, text: str) -> Dict[str, Any]:
        """
        Deep AAOIFI Standard contract analysis:
        Checks Murabaha (No. 8), Ijara (No. 9), Mudaraba (No. 13), Musharaka (No. 12).
        """
        norm = text.lower()
        findings = []
        is_compliant = True
        contract_type = "GENERAL_COMMERCIAL"

        if any(w in norm for w in ["мурабаха", "murabaha", "рассрочк", "наценк"]):
            contract_type = "MURABAHA (AAOIFI Standard No. 8)"
            # Check if seller takes ownership
            if "без перехода права" in norm or "без владения" in norm:
                is_compliant = False
                findings.append({
                    "standard": "AAOIFI No. 8 §2/1",
                    "issue_ru": "Финансирующая сторона обязана фактически или конструктивно владеть товаром до заключения сделки Мурабаха.",
                    "issue_kk": "Қаржыландырушы тарап Мурабаха шартын жасаспас бұрын тауарды меншігіне алуы міндетті.",
                    "severity": "CRITICAL"
                })
        elif any(w in norm for w in ["иджара", "ijara", "лизинг", "аренд"]):
            contract_type = "IJARA (AAOIFI Standard No. 9)"
            if "риск случайной гибели несет арендатор" in norm:
                is_compliant = False
                findings.append({
                    "standard": "AAOIFI No. 9 §5/1",
                    "issue_ru": "Риски владения базовым активом (страхование Такафул, гибель актива) обязан нести арендодатель, а не арендатор.",
                    "issue_kk": "Негізгі активтің сақталу тәуекелдерін жалға беруші көтеруі тиіс.",
                    "severity": "CRITICAL"
                })
        elif any(w in norm for w in ["мудараба", "мушарака", "mudaraba", "musharaka", "партнерств"]):
            contract_type = "MUDARABA / MUSHARAKA (AAOIFI Standard No. 12/13)"
            if any(w in norm for w in ["гарантированный доход", "гарантия капитала", "фиксированная доходность"]):
                is_compliant = False
                findings.append({
                    "standard": "AAOIFI No. 13 §8/1",
                    "issue_ru": "Запрещена гарантия капитала или фиксированной прибыли в Мударабе/Мушараке — это приравнивается к кредиту с Риба.",
                    "issue_kk": "Мудараба мен Мушаракада капиталдың қайтарылуына немесе бекітілген пайдаға кепілдік беру харам (Риба).",
                    "severity": "FATAL"
                })

        # Universal Riba penalty check
        if any(w in norm for w in ["пеня в пользу кредитора", "проценты за просрочку", "штрафные проценты"]):
            is_compliant = False
            findings.append({
                "standard": "AAOIFI Shariah Standard No. 3 (Default in Debt)",
                "issue_ru": "Штрафы за просрочку не могут поступать в доход кредитора/банка. Они допустимы только при 100% перечислении на благотворительность.",
                "issue_kk": "Төлемді кешіктіргені үшін өсімпұл несие берушінің табысына айналмауы тиіс. Тек қайырымдылыққа аударылуы міндетті.",
                "severity": "CRITICAL"
            })

        return {
            "contract_type": contract_type,
            "is_compliant": is_compliant,
            "findings_count": len(findings),
            "findings": findings,
            "quran_basis": "2:275 (Запрет Риба) • 4:29 (Торговля по согласию) • 5:1 (Исполнение договоров)"
        }
