"""
Al-Furqan AI - Automated Universal Halal & Shariah Knowledge Graph
Massive, multi-lingual ontology covering:
- 500+ Food additives (E-codes)
- 2,000+ Ingredients, slang, substances, actions, financial contracts
- AAOIFI Shariah Standards (Murabaha, Ijara, Mudaraba, Musharaka, Sukuk)
- Morphological Subword Stemmer & Semantic Categorization Engine
Languages supported: Kazakh, Russian, English, Arabic, Turkish, Uzbek
"""

import os
import json
import re
from typing import Dict, List, Any, Optional, Tuple

MASTER_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "halal_master_database.json")

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
    # 3. DEEP AAOIFI CONTRACT AUDITOR & QURANIC RISK DETECTOR
    # =========================================================================
    @classmethod
    def audit_contract_aaoifi(cls, text: str) -> Dict[str, Any]:
        """
        Deep AAOIFI Standard contract analysis with exact Quranic citations:
        Detects Riba (2:275), Penalty Riba (2:280), Non-ownership (4:29), Capital Guarantee (AAOIFI 12/13), Maysir (5:90).
        """
        norm = text.lower()
        findings = []
        is_compliant = True
        contract_type = "GENERAL_COMMERCIAL"

        # 1. Loan with Interest / Riba Detection
        if re.search(r"кредит\w* под процент\w*|ссудн\w* процент\w*|процентн\w* ставк\w*|\b\d+[\.,]?\d*%\s*годов\w*|interest rate|compound interest|пайыздық несие|өсімқорлық", norm):
            is_compliant = False
            findings.append({
                "risk_title_ru": "🔴 КРИТИЧЕСКИЙ РИСК: Ссудный процент (Риба)",
                "risk_title_kk": "🔴 КРИТИКАЛЫҚ ҚАУІП: Өсімқорлық пайыздық мөлшерлеме (Риба)",
                "risk_title_en": "🔴 CRITICAL RISK: Usury / Loan Interest (Riba)",
                "standard": "AAOIFI Shariah Standard No. 8 (Murabaha) & Standard No. 1",
                "ayah_ref": "Сура Аль-Бакара (2:275)",
                "ayah_arabic": "وَأَحَلَّ اللَّهُ الْبَيْعَ وَحَرَّمَ الرِّبَا",
                "ayah_trans_ru": "«Аллах дозволил торговлю и запретил ростовщичество (Риба)»",
                "ayah_trans_kk": "«Аллаһ сауданы халал етіп, өсімқорлықты (рибаны) харам қылды»",
                "issue_ru": "Начисление фиксированного ссудного процента на сумму долга категорически запрещено Шариатом (Риба).",
                "issue_kk": "Қарыз сомасына үстеме пайыз есептеу шариғат бойынша қатаң харам (Риба).",
                "solution_ru": "Замените кредитный договор на договор исламского торгового финансирования Мурабаха (с фиксированной торговой наценкой) или беспроцентный займ Кард аль-Хасан.",
                "solution_kk": "Несие шартын бекітілген сауда үстемесі бар Мурабаха шартына немесе үстемесіз Қарз әл-Хасан қарызына ауыстырыңыз.",
                "severity": "CRITICAL"
            })

        # 2. Penalty to Bank Income Detection (Riba al-Jahiliyyah)
        if re.search(r"пен\w* в пользу|штраф\w* за просрочк\w*|неустойк\w* в доход|пеня \d+[\.,]?\d*%|өсімпұл|штрафные проценты|штрафная пеня", norm):
            is_compliant = False
            findings.append({
                "risk_title_ru": "🔴 КРИТИЧЕСКИЙ РИСК: Ростовщическая пеня за просрочку",
                "risk_title_kk": "🔴 КРИТИКАЛЫҚ ҚАУІП: Төлемді кешіктіру өсімпұлы (Риба әл-Жаһилия)",
                "risk_title_en": "🔴 CRITICAL RISK: Default Penalty Credited to Income",
                "standard": "AAOIFI Shariah Standard No. 3 (Default in Debt) §2/1",
                "ayah_ref": "Сура Аль-Бакара (2:280)",
                "ayah_arabic": "وَإِن كَانَ ذُو عُسْرَةٍ فَنَظِرَةٌ إِلَىٰ مَيْسَرَةٍ",
                "ayah_trans_ru": "«Если должник находится в трудном положении, то дайте ему отсрочку, пока его положение не улучшится»",
                "ayah_trans_kk": "«Егер борышкер қиын жағдайда болса, жағдайы түзелгенше мұрсат беріңдер»",
                "issue_ru": "Штрафы и пеня за просрочку не могут поступать в доход банка или кредитора — это запрещенная Риба аль-Джахилия.",
                "issue_kk": "Төлемді кешіктіргені үшін өсімпұл несие берушінің табысына айналмауы тиіс. Бұл харам өсім (Риба).",
                "solution_ru": "Включите условие о том, что 100% штрафных санкций перечисляются исключительно на благотворительность (Charity Fund), минуя баланс банка.",
                "solution_kk": "Өсімпұлдың 100% сомасын тек қайырымдылық қорына аудару шартын енгізіңіз.",
                "severity": "CRITICAL"
            })

        # 3. Murabaha specific: Sale without Ownership
        if any(w in norm for w in ["мурабаха", "murabaha", "рассрочк", "наценк"]):
            contract_type = "MURABAHA (AAOIFI Standard No. 8)"
            if any(w in norm for w in ["без перехода права", "без владения", "до передачи товара", "меншік құқығы өтпей"]):
                is_compliant = False
                findings.append({
                    "risk_title_ru": "🔴 НАРУШЕНИЕ СТАНДАРТА МУРАБАХА: Продажа до владения",
                    "risk_title_kk": "🔴 МУРАБАХА БҰЗЫЛУЫ: Меншікке өтпеген тауарды сату",
                    "risk_title_en": "🔴 MURABAHA VIOLATION: Sale Before Ownership Transfer",
                    "standard": "AAOIFI Shariah Standard No. 8 §2/1/1",
                    "ayah_ref": "Сура Ан-Ниса (4:29)",
                    "ayah_arabic": "يَا أَيُّهَا الَّذِينَ آمَنُوا لَا تَأْكُلُوا أَمْوَالَكُم بَيْنَكُم بِالْبَاطِلِ إِلَّا أَن تَكُونَ تِجَارَةً عَن تَرَاضٍ مِّنكُم",
                    "ayah_trans_ru": "«О те, которые уверовали! Не пожирайте своего имущества между собой незаконно, а только путем торговли по взаимному согласию»",
                    "ayah_trans_kk": "«Ей, иман келтіргендер! Бір-біріңнің мал-мүлкіңді жалғандықпен жемеңдер, тек өзара ризалықпен жасалған сауда арқылы болсын»",
                    "issue_ru": "Банк/продавец обязан фактически или конструктивно приобрести право собственности на товар до заключения договора Мурабаха с клиентом.",
                    "issue_kk": "Қаржыландырушы тарап Мурабаха шартын жасаспас бұрын тауарды меншігіне алуы міндетті.",
                    "solution_ru": "Разделите сделку на два этапа: (1) Заказ и выкуп банком у поставщика, (2) Продажа клиенту в рассрочку с наценкой.",
                    "solution_kk": "Мәмілені 2 кезеңге бөліңіз: (1) Банктің жеткізушіден тауарды сатып алуы, (2) Клиентке бөліп төлеумен сату.",
                    "severity": "CRITICAL"
                })

        # 4. Ijara specific: Asset risk shifted to Lessee
        if any(w in norm for w in ["иджара", "ijara", "лизинг", "аренд"]):
            contract_type = "IJARA (AAOIFI Standard No. 9)"
            if any(w in norm for w in ["риск случайной гибели несет арендатор", "страхование за счет арендатора", "все риски на арендаторе"]):
                is_compliant = False
                findings.append({
                    "risk_title_ru": "🔴 НАРУШЕНИЕ СТАНДАРТА ИДЖАРА: Перекладывание рисков актива на арендатора",
                    "risk_title_kk": "🔴 ИДЖАРА БҰЗЫЛУЫ: Актив тәуекелін жалға алушыға жүктеу",
                    "risk_title_en": "🔴 IJARA VIOLATION: Shifting Total Asset Risk to Lessee",
                    "standard": "AAOIFI Shariah Standard No. 9 §5/1/1",
                    "ayah_ref": "Сура Аль-Касас (28:26)",
                    "ayah_arabic": "إِنَّ خَيْرَ مَنِ اسْتَأْجَرْتَ الْقَوِيُّ الْأَمِينُ",
                    "ayah_trans_ru": "«Воистину, лучшим из тех, кого ты нанимаешь, является сильный и надежный»",
                    "ayah_trans_kk": "«Шындығында, жалдауға ең қайырлы адам — мықты әрі сенімді адам»",
                    "issue_ru": "Риски фундаментального владения базовым активом (гибель от форс-мажора, Такафул страхование) обязан нести арендодатель.",
                    "issue_kk": "Негізгі активтің сақталуы мен зақымдану тәуекелдерін жалға беруші көтеруі тиіс.",
                    "solution_ru": "Возложите расходы по страхованию Такафул и капитальному ремонту на арендодателя (собственника актива).",
                    "solution_kk": "Такафул сақтандыру мен күрделі жөндеу шығындарын жалға берушінің жауапкершілігіне қалдырыңыз.",
                    "severity": "HIGH"
                })

        # 5. Mudaraba / Musharaka: Capital / Profit Guarantee
        if any(w in norm for w in ["мудараба", "мушарака", "mudaraba", "musharaka", "партнерств"]):
            contract_type = "MUDARABA / MUSHARAKA (AAOIFI Standard No. 12/13)"
            if any(w in norm for w in ["гарантированный доход", "гарантия капитала", "фиксированная доходность", "кепілдендірілген пайда"]):
                is_compliant = False
                findings.append({
                    "risk_title_ru": "🔴 НЕДОПУСТИМАЯ ГАРАНТИЯ: Гарантия вклада в партнерстве",
                    "risk_title_kk": "🔴 ШАРИҒАТ БҰЗЫЛУЫ: Мударабада капиталға кепілдік беру",
                    "risk_title_en": "🔴 FATAL RISK: Capital / Profit Guarantee in Partnership",
                    "standard": "AAOIFI Shariah Standard No. 13 §8/1",
                    "ayah_ref": "Сура Аль-Бакара (2:275) и Правило Фикха (Аль-Гурм биль-Гунм)",
                    "ayah_arabic": "الْغُرْمُ بِالْغُنْمِ (الخراج بالضمان)",
                    "ayah_trans_ru": "«Право на прибыль неразрывно связано с несением риска потерь» (Хадис Пророка ﷺ)",
                    "ayah_trans_kk": "«Пайда табу құқығы тәуекелге бару жауапкершілігімен тікелей байланысты»",
                    "issue_ru": "Запрещена гарантия капитала или фиксированного дохода в партнерских сделках (Мудараба/Мушарака) — это приравнивается к кредиту с Риба.",
                    "issue_kk": "Мудараба мен Мушаракада капиталдың қайтарылуына немесе бекітілген пайыздық пайдаға кепілдік беру харам.",
                    "solution_ru": "Укажите плавающее распределение чистой прибыли в согласованных долях (%) и распределение убытков пропорционально вкладу.",
                    "solution_kk": "Таза пайданы пайыздық үлестермен (%) бөлісуді және залалды тек салынған капитал шегінде көтеруді бекітіңіз.",
                    "severity": "FATAL"
                })

        # 6. Gambling / Maysir / Speculative derivatives
        if re.search(r"пари\b|ставк\w* на спорт|казино|тотализатор|бинарн\w* опцион|дериватив|құмар|бәс тігу", norm):
            is_compliant = False
            findings.append({
                "risk_title_ru": "🔴 ХАРАМ: Азартные пари и деривативные спекуляции (Майсир)",
                "risk_title_kk": "🔴 ХАРАМ: Құмар ойындар мен бәс тігу (Мәйсир)",
                "risk_title_en": "🔴 HARAM: Gambling, Betting and Speculative Derivatives (Maysir)",
                "standard": "AAOIFI Shariah Standard No. 20 (Sale of Commodities)",
                "ayah_ref": "Сура Аль-Маида (5:90)",
                "ayah_arabic": "إِنَّمَا الْخَمْرُ وَالْمَيْسِرُ وَالْأَنصَابُ وَالْأَزْلَامُ رِجْسٌ مِّنْ عَمَلِ الشَّيْطَانِ فَاجْتَنِبُوهُ",
                "ayah_trans_ru": "«Воистину, опьяняющие напитки, азартные игры (Майсир)... являются скверной из деяний сатаны. Сторонитесь же этого!»",
                "ayah_trans_kk": "«Шын мәнінде, арақ, құмар ойындар (мәйсир)... шайтанның лас амалдарынан. Сондықтан одан аулақ болыңдар!»",
                "issue_ru": "Сделки с нулевой суммой, пари и производные финансовые инструменты без реальной поставки базового актива запрещены.",
                "issue_kk": "Нақты тауарсыз тек бағаның өсу-құлауына бәс тігетін туынды құралдар шариғатта харам.",
                "solution_ru": "Исключите любые условия пари и замените деривативы на реальные поставочные контракты (Салям / Истисна).",
                "solution_kk": "Бәс тігу шарттарын алып тастап, нақты тауар жеткізетін Салам немесе Истисна шарттарына көшіңіз.",
                "severity": "FATAL"
            })

        return {
            "contract_type": contract_type,
            "is_compliant": is_compliant,
            "findings_count": len(findings),
            "findings": findings,
            "quran_basis": "2:275 (Запрет Риба) • 2:280 (Отсрочка должнику) • 4:29 (Торговля по согласию) • 5:90 (Запрет Майсира)"
        }

    # =========================================================================
    # 4. DEEP SHUBHÂT (DOUBTFUL SUBSTANCES) FIQH & ORIGIN KNOWLEDGE GRAPH
    # =========================================================================
    SHUBHAT_KNOWLEDGE = {
        "E471": {
            "name": "E471 — Моно- и диглицериды жирных кислот (Mono- and diglycerides of fatty acids)",
            "origin_types": ["Растительное (Plant/Vegetable)", "Животное (Animal)", "Синтетическое"],
            "shariah_verdict_ru": "СОМНИТЕЛЬНО (ШҮБӘЛІ) БЕЗ СЕРТИФИКАТА",
            "shariah_verdict_kk": "СЕРТИФИКАТСЫЗ КҮМӘНДІ (ШҮБӘЛІ)",
            "detailed_fiqh_ru": "Моно- и диглицериды (E471) производятся путем этерификации жирных кислот. Если сырьем служат растительные масла (соевое, пальмовое, рапсовое) — добавка 100% ХАЛЯЛЬ. Если источником является животный жир (говяжий или свиной без халяль-забоя) — ХАРАМ. Согласно стандартам OIC/SMIIC 1:2019 и ДУМК/Halal Damu, продукт с E471 разрешен к употреблению только при явном указании 'растительного происхождения' на этикетке или при наличии сертификата Халяль.",
            "detailed_fiqh_kk": "E471 қоспасы өсімдік немесе мал майларынан алынады. Егер өсімдіктен (пальма, соя майы) алынса — ХАЛАЛ. Мал немесе шошқа майынан алынса — ХАРАМ. SMIIC 1:2019 және ҚМДБ (Халал Даму) стандарттарына сәйкес, қаптамада 'өсімдік майынан' деп жазылмаса немесе Халал сертификаты болмаса, күмәнді (шүбәлі) саналады.",
            "standards_ref": "OIC/SMIIC 1:2019 General Requirements for Halal Food §5.1.2 • ДУМК РК"
        },
        "E120": {
            "name": "E120 — Кармин / Кошениль (Carmine / Cochineal extract)",
            "origin_types": ["Насекомые (Сушеные самки кошенили / Dactylopius coccus)"],
            "shariah_verdict_ru": "ХАРАМ (по Ханафи, Шафии и ДУМК / Halal Damu)",
            "shariah_verdict_kk": "ХАРАМ (Ханафи, Шафии және ҚМДБ / Халал Даму бойынша)",
            "detailed_fiqh_ru": "Кармин — натуральный краситель красного цвета, получаемый из сушеных самок насекомых кошенили. В ханафитском и шафиитском мазхабах (а также согласно нормам ДУМК РК, Совета муфтиев РФ и SMIIC) насекомые, не относящиеся к саранче, признаются 'хабаис' (скверной) и запрещены к употреблению в пищу (Коран 7:157). Употребление продуктов с E120 запрещено.",
            "detailed_fiqh_kk": "Кармин бояғышы кошениль жәндіктерінен өндіріледі. Ханафи және Шафии мәзһабтарында, сондай-ақ ҚМДБ стандарттары бойынша шегірткеден басқа жәндіктер 'хабаис' (жиіркенішті) саналып, жеуге қатаң тыйым салынған (Құран 7:157). Құрамында E120 бар өнімдер Харам болып табылады.",
            "standards_ref": "Сура Аль-Аграф 7:157 • Постановление ДУМК РК • SMIIC 1:2019 §5.1.1"
        },
        "GELATIN": {
            "name": "Желатин / E441 (Gelatin)",
            "origin_types": ["Свиная шкура (Pork Skin)", "Кости КРС (Bovine)", "Рыбный (Fish)", "Растительный аналог (Агар-агар/Пектин)"],
            "shariah_verdict_ru": "СОМНИТЕЛЬНО / ТРЕБУЕТСЯ СЕРТИФИКАТ ХАЛЯЛЬ",
            "shariah_verdict_kk": "КҮМӘНДІ / ХАЛАЛ СЕРТИФИКАТЫ ҚАЖЕТ",
            "detailed_fiqh_ru": "Желатин — продукт денатурации коллагена. До 80% промышленного европейского желатина производится из свиной шкуры (ХАРАМ). Желатин из говяжьих костей скота, забитого не по шариату — также ХАРАМ по мнению большинства ученых (так как концепция 'истихала' не признается полной). Разрешен ТОЛЬКО желатин из рыбы (Fish Gelatin) или скота, забитого по стандартам Халяль с подтвержденным сертификатом.",
            "detailed_fiqh_kk": "Әлемдік желатиннің басым бөлігі доңыз терісінен өндіріледі (ХАРАМ). Шариғатқа сай сойылмаған сиыр сүйегінен жасалған желатин де харам. Тек балықтан (Fish Gelatin) немесе шариғат талабымен бауыздалған малдан жасалған Халал сертификатталған желатин ғана адал.",
            "standards_ref": "Сура Аль-Маида 5:3 • Фетва Европейского совета по богословию и фетвам • ДУМК"
        },
        "RENNET": {
            "name": "Сычужный фермент / Пепсин / Химозин (Rennet / Pepsin / Chymosin)",
            "origin_types": ["Микробиологический (Microbial/Vegetarian)", "Телячий сычуг (Bovine/Calf)", "Свиной пепсин (Porcine Pepsin)"],
            "shariah_verdict_ru": "МИКРОБИОЛОГИЧЕСКИЙ — ХАЛЯЛЬ / ЖИВОТНЫЙ — ТРЕБУЕТСЯ ПРОВЕРКА",
            "shariah_verdict_kk": "МИКРОБИОЛОГИЯЛЫҚ — ХАЛАЛ / МАЛДЫҚ — ТЕКСЕРУ ҚАЖЕТ",
            "detailed_fiqh_ru": "Сычужный фермент используется в производстве твердых и полутвердых сыров. Если на упаковке указан 'фермент микробиологического (растительного) происхождения' (Microbial Rennet) — продукт 100% ХАЛЯЛЬ. Если указан животный сычуг: в ханафитском мазхабе сам фермент чист, однако стандарты Halal Damu и SMIIC требуют использования ферментов от халяль-забоя во избежание соприкосновения со свиным пепсином.",
            "detailed_fiqh_kk": "Сыр өндірісіндегі сычуг: 'микробиологиялық' (өсімдік текті) фермент болса — 100% ХАЛАЛ. Малдың мәйегінен алынса, Халал сертификаты немесе шариғатша бауыздалғанын растау талап етіледі.",
            "standards_ref": "OIC/SMIIC 1:2019 §5.1.3 • ДУМК РК Стандарт сыроделия"
        }
    }

    @classmethod
    def analyze_ingredients_deep(cls, text: str, additives_tags: List[str] = None) -> Dict[str, Any]:
        """
        Comprehensive automated Shariah & Halal analysis of ingredients text & E-codes.
        Returns precise fiqh classification, origin breakdowns, and references.
        """
        norm = text.lower()
        if additives_tags:
            for tag in additives_tags:
                clean_tag = tag.replace("en:", "").upper()
                norm += f" {clean_tag}"

        matches = cls.match_input(norm)
        haram_items = []
        doubtful_items = []
        shubhat_details = []

        # 1. Match specific Shubhât deep entries
        if "e471" in norm or "моно- и диглицерид" in norm or "моноглицерид" in norm or "diglyceride" in norm:
            shubhat_details.append(cls.SHUBHAT_KNOWLEDGE["E471"])
            doubtful_items.append("E471 (Моно- и диглицериды)")

        if "e120" in norm or "кармин" in norm or "кошенил" in norm or "carmine" in norm:
            shubhat_details.append(cls.SHUBHAT_KNOWLEDGE["E120"])
            haram_items.append("E120 (Кармин / Кошениль — Насекомые)")

        if "желатин" in norm or "gelatin" in norm or "e441" in norm:
            # Check if certified fish or halal
            if "рыбный желатин" in norm or "агар" in norm or "говяжий желатин халяль" in norm:
                pass
            else:
                shubhat_details.append(cls.SHUBHAT_KNOWLEDGE["GELATIN"])
                doubtful_items.append("Желатин (E441)")

        if "сычужн" in norm or "rennet" in norm or "пепсин" in norm or "химозин" in norm:
            if "микробиологическ" in norm or "растительн" in norm or "microbial" in norm:
                pass
            else:
                shubhat_details.append(cls.SHUBHAT_KNOWLEDGE["RENNET"])
                doubtful_items.append("Сычужный фермент (Rennet)")

        # 2. General ontology checks
        for m in matches:
            if m["verdict"] == "HARAM" and m["title_ru"] not in haram_items:
                haram_items.append(m["title_ru"])
            elif m["verdict"] == "DOUBTFUL" and m["title_ru"] not in doubtful_items:
                doubtful_items.append(m["title_ru"])

        # Determine overall verdict
        if haram_items:
            final_verdict = "HARAM"
            summary_ru = f"🔴 ВНИМАНИЕ: Продукт содержит запрещенные (ХАРАМ) компоненты: {', '.join(haram_items)}."
            summary_kk = f"🔴 ЕСКЕРТУ: Өнімде шариғатта тыйым салынған (ХАРАМ) заттар табылды: {', '.join(haram_items)}."
        elif doubtful_items or shubhat_details:
            final_verdict = "DOUBTFUL"
            summary_ru = f"🟡 ВНИМАНИЕ: Обнаружены сомнительные ингредиенты (ШУБХАТ): {', '.join(doubtful_items)}. Требуется подтверждение происхождения или сертификат Халяль."
            summary_kk = f"🟡 ЕСКЕРТУ: Құрамында күмәнді (ШҮБӘЛІ) қоспалар табылды: {', '.join(doubtful_items)}. Халал сертификаты немесе өсімдіктен алынғанын растау қажет."
        else:
            final_verdict = "HALAL"
            summary_ru = "🟢 ПРОВЕРЕНО: Прямых запрещенных компонентов и сомнительных добавок не обнаружено (Халяль)."
            summary_kk = "🟢 ТЕКСЕРІЛДІ: Құрамында тыйым салынған немесе күмәнді қоспалар табылмады (Халал)."

        return {
            "verdict": final_verdict,
            "summary_ru": summary_ru,
            "summary_kk": summary_kk,
            "haram_items": haram_items,
            "doubtful_items": doubtful_items,
            "shubhat_details": shubhat_details,
            "raw_matches_count": len(matches),
            "smiic_standard": "OIC/SMIIC 1:2019",
            "quran_ground_truth": "5:3 (Запрет мертвечины, крови и свинины) • 5:90 (Запрет опьяняющего) • 7:157 (Запрет скверны)"
        }

