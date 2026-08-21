"""
Al-Furqan Guard — Master Halal/Haram Knowledge Base Builder v2.0
Compiles comprehensive datasets from:
- OIC/SMIIC 1:2019 (General Requirements for Halal Food)
- JAKIM (Malaysia Halal Standards MS 1500:2009)
- MUI / BPJPH (Indonesia Halal Assurance System HAS 23000)
- ДУМК («Халал Даму» - Казахстан)
- Совет Муфтиев РФ (МЦСиС «Халяль»)
- IFANCA (Islamic Food and Nutrition Council of America)
- SANHA (South African National Halal Authority)
"""

import json
import os
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "halal_master_database.json")

# 1. CORE E-CODES DATABASE (Comprehensive E100 to E1520)
# Statuses: HALAL, HARAM, DOUBTFUL (MUSHBOOH)
E_CODES_DATA = {
    # ------------------ E100–E199: COLOURS ------------------
    "E100": {"name_en": "Curcumin", "name_ru": "Куркумин", "name_kk": "Куркумин", "status": "HALAL", "origin": "Растительное (Куркума)", "standard": "SMIIC 1:2019"},
    "E101": {"name_en": "Riboflavin (Vitamin B2)", "name_ru": "Рибофлавин (Витамин B2)", "name_kk": "Рибофлавин", "status": "DOUBTFUL", "origin": "Растительное / Микробиологическое / Животное", "standard": "SMIIC 1:2019 §5.1.2"},
    "E102": {"name_en": "Tartrazine", "name_ru": "Тартразин", "name_kk": "Тартразин", "status": "HALAL", "origin": "Синтетическое", "standard": "SMIIC 1:2019"},
    "E104": {"name_en": "Quinoline Yellow", "name_ru": "Желтый хинолиновый", "name_kk": "Хинолинді сары", "status": "HALAL", "origin": "Синтетическое", "standard": "SMIIC 1:2019"},
    "E110": {"name_en": "Sunset Yellow FCF", "name_ru": "Желтый «солнечный закат»", "name_kk": "Күн батуы сары", "status": "HALAL", "origin": "Синтетическое", "standard": "SMIIC 1:2019"},
    "E120": {"name_en": "Carmine / Cochineal", "name_ru": "Кармин / Кошениль", "name_kk": "Кармин / Кошениль", "status": "HARAM", "origin": "Насекомые (Кошениль)", "standard": "ДУМК / SMIIC 1:2019 (Харам по Ханафи/Шафии)"},
    "E122": {"name_en": "Azorubine / Carmoisine", "name_ru": "Азорубин / Кармуазин", "name_kk": "Азорубин", "status": "HALAL", "origin": "Синтетическое", "standard": "SMIIC 1:2019"},
    "E123": {"name_en": "Amaranth", "name_ru": "Амарант", "name_kk": "Амарант", "status": "HALAL", "origin": "Синтетическое", "standard": "SMIIC 1:2019"},
    "E124": {"name_en": "Ponceau 4R", "name_ru": "Понсо 4R", "name_kk": "Понсо 4R", "status": "HALAL", "origin": "Синтетическое", "standard": "SMIIC 1:2019"},
    "E127": {"name_en": "Erythrosine", "name_ru": "Эритрозин", "name_kk": "Эритрозин", "status": "HALAL", "origin": "Синтетическое", "standard": "SMIIC 1:2019"},
    "E129": {"name_en": "Allura Red AC", "name_ru": "Красный очаровательный АС", "name_kk": "Аллюра қызыл", "status": "HALAL", "origin": "Синтетическое", "standard": "SMIIC 1:2019"},
    "E131": {"name_en": "Patent Blue V", "name_ru": "Синий патентованный V", "name_kk": "Патенттелген көк V", "status": "HALAL", "origin": "Синтетическое", "standard": "SMIIC 1:2019"},
    "E132": {"name_en": "Indigotine / Indigo carmine", "name_ru": "Индигокармин", "name_kk": "Индигокармин", "status": "HALAL", "origin": "Синтетическое", "standard": "SMIIC 1:2019"},
    "E133": {"name_en": "Brilliant Blue FCF", "name_ru": "Бриллиантовый синий FCF", "name_kk": "Бриллиантты көк", "status": "HALAL", "origin": "Синтетическое", "standard": "SMIIC 1:2019"},
    "E140": {"name_en": "Chlorophylls", "name_ru": "Хлорофиллы", "name_kk": "Хлорофиллдар", "status": "HALAL", "origin": "Растительное (Люцерна, крапива)", "standard": "SMIIC 1:2019"},
    "E141": {"name_en": "Copper complexes of chlorophylls", "name_ru": "Медные комплексы хлорофиллов", "name_kk": "Хлорофиллдің мыс кешендері", "status": "HALAL", "origin": "Растительное", "standard": "SMIIC 1:2019"},
    "E150a": {"name_en": "Plain Caramel", "name_ru": "Сахарный колер I простой", "name_kk": "Қарапайым карамель", "status": "HALAL", "origin": "Растительное (Сахар)", "standard": "SMIIC 1:2019"},
    "E150b": {"name_en": "Caustic sulfite caramel", "name_ru": "Сахарный колер II", "name_kk": "Карамель түсі II", "status": "HALAL", "origin": "Растительное", "standard": "SMIIC 1:2019"},
    "E150c": {"name_en": "Ammonia caramel", "name_ru": "Сахарный колер III", "name_kk": "Карамель түсі III", "status": "HALAL", "origin": "Растительное", "standard": "SMIIC 1:2019"},
    "E150d": {"name_en": "Sulfite ammonia caramel", "name_ru": "Сахарный колер IV", "name_kk": "Карамель түсі IV", "status": "HALAL", "origin": "Растительное", "standard": "SMIIC 1:2019"},
    "E153": {"name_en": "Vegetable carbon", "name_ru": "Уголь растительный", "name_kk": "Өсімдік көмірі", "status": "DOUBTFUL", "origin": "Растительное / Животное (Костный уголь)", "standard": "SMIIC 1:2019 (Халяль при растительном угле)"},
    "E160a": {"name_en": "Beta-carotene", "name_ru": "Бета-каротин", "name_kk": "Бета-каротин", "status": "DOUBTFUL", "origin": "Растительное / Синтетическое (Носитель может содержать желатин)", "standard": "SMIIC 1:2019"},
    "E160b": {"name_en": "Annatto", "name_ru": "Аннато экстракт", "name_kk": "Аннато сығындысы", "status": "HALAL", "origin": "Растительное (Семена бикса орельяна)", "standard": "SMIIC 1:2019"},
    "E160c": {"name_en": "Paprika extract", "name_ru": "Экстракт паприки", "name_kk": "Паприка сығындысы", "status": "HALAL", "origin": "Растительное (Красный перец)", "standard": "SMIIC 1:2019"},
    "E160d": {"name_en": "Lycopene", "name_ru": "Ликопин", "name_kk": "Ликопин", "status": "HALAL", "origin": "Растительное (Томаты)", "standard": "SMIIC 1:2019"},
    "E161b": {"name_en": "Lutein", "name_ru": "Лютеин", "name_kk": "Лютеин", "status": "HALAL", "origin": "Растительное (Бархатцы)", "standard": "SMIIC 1:2019"},
    "E162": {"name_en": "Beetroot Red / Betanin", "name_ru": "Свекольный красный / Бетанин", "name_kk": "Қызылша қызылы", "status": "HALAL", "origin": "Растительное (Свекла)", "standard": "SMIIC 1:2019"},
    "E163": {"name_en": "Anthocyanins", "name_ru": "Антоцианы", "name_kk": "Антоцианиндер", "status": "HALAL", "origin": "Растительное (Виноград, ягоды)", "standard": "SMIIC 1:2019"},
    "E170": {"name_en": "Calcium carbonate", "name_ru": "Карбонат кальция (Мел)", "name_kk": "Кальций карбонаты", "status": "HALAL", "origin": "Минеральное", "standard": "SMIIC 1:2019"},
    "E171": {"name_en": "Titanium dioxide", "name_ru": "Диоксид титана", "name_kk": "Титан диоксиді", "status": "HALAL", "origin": "Минеральное", "standard": "SMIIC 1:2019"},
    "E172": {"name_en": "Iron oxides", "name_ru": "Оксиды железа", "name_kk": "Темір оксидтері", "status": "HALAL", "origin": "Минеральное", "standard": "SMIIC 1:2019"},

    # ------------------ E200–E299: PRESERVATIVES ------------------
    "E200": {"name_en": "Sorbic acid", "name_ru": "Сорбиновая кислота", "name_kk": "Сорбин қышқылы", "status": "HALAL", "origin": "Растительное / Синтетическое", "standard": "SMIIC 1:2019"},
    "E202": {"name_en": "Potassium sorbate", "name_ru": "Сорбат калия", "name_kk": "Калий сорбаты", "status": "HALAL", "origin": "Синтетическое", "standard": "SMIIC 1:2019"},
    "E211": {"name_en": "Sodium benzoate", "name_ru": "Бензоат натрия", "name_kk": "Натрий бензоаты", "status": "HALAL", "origin": "Синтетическое", "standard": "SMIIC 1:2019"},
    "E220": {"name_en": "Sulfur dioxide", "name_ru": "Диоксид серы", "name_kk": "Күкірт диоксиді", "status": "HALAL", "origin": "Химическое", "standard": "SMIIC 1:2019"},
    "E250": {"name_en": "Sodium nitrite", "name_ru": "Нитрит натрия", "name_kk": "Натрий нитриті", "status": "HALAL", "origin": "Минеральное / Синтетическое", "standard": "SMIIC 1:2019"},
    "E252": {"name_en": "Potassium nitrate", "name_ru": "Нитрат калия (Селитра)", "name_kk": "Калий нитраты", "status": "DOUBTFUL", "origin": "Минеральное / Животное происхождение", "standard": "SMIIC 1:2019"},
    "E260": {"name_en": "Acetic acid", "name_ru": "Уксусная кислота", "name_kk": "Сірке қышқылы", "status": "HALAL", "origin": "Синтетическое / Натуральное брожение", "standard": "SMIIC 1:2019"},
    "E270": {"name_en": "Lactic acid", "name_ru": "Молочная кислота", "name_kk": "Сүт қышқылы", "status": "HALAL", "origin": "Бактериальная ферментация углеводов (Сахар/Кукуруза)", "standard": "SMIIC 1:2019"},

    # ------------------ E300–E399: ANTIOXIDANTS & ACIDITY ------------------
    "E300": {"name_en": "Ascorbic acid (Vitamin C)", "name_ru": "Аскорбиновая кислота (Витамин C)", "name_kk": "Аскорбин қышқылы", "status": "HALAL", "origin": "Растительное (Глюкоза)", "standard": "SMIIC 1:2019"},
    "E304": {"name_en": "Ascorbyl palmitate", "name_ru": "Аскорбилпальмитат", "name_kk": "Аскорбилпальмитат", "status": "DOUBTFUL", "origin": "Пальмитиновая кислота (Растительное или Животное)", "standard": "SMIIC 1:2019 §5.1.2"},
    "E306": {"name_en": "Tocopherol-rich extract (Vit E)", "name_ru": "Экстракт токоферолов (Витамин E)", "name_kk": "Токоферолдар (Е дәрумені)", "status": "HALAL", "origin": "Растительное (Растительные масла)", "standard": "SMIIC 1:2019"},
    "E322": {"name_en": "Lecithins", "name_ru": "Лецитины (Соевый, подсолнечный)", "name_kk": "Лецитиндер (Соя, күнбағыс)", "status": "HALAL", "origin": "Растительное (Соя, подсолнечник) / Яичный", "standard": "SMIIC 1:2019 (Халяль при растительном соевом лецитине)"},
    "E330": {"name_en": "Citric acid", "name_ru": "Лимонная кислота", "name_kk": "Лимон қышқылы", "status": "HALAL", "origin": "Ферментация Aspergillus niger (Глюкоза/Меласса)", "standard": "SMIIC 1:2019"},
    "E334": {"name_en": "Tartaric acid", "name_ru": "Винная кислота (L(+)-)", "name_kk": "Шарап қышқылы", "status": "HALAL", "origin": "Побочный продукт виноделия (полное химическое преображение / Тахаввуль)", "standard": "SMIIC / ДУМК (Разрешено)"},

    # ------------------ E400–E499: EMULSIFIERS, STABILIZERS, THICKENERS ------------------
    "E406": {"name_en": "Agar", "name_ru": "Агар-агар", "name_kk": "Агар-агар", "status": "HALAL", "origin": "Растительное (Морские красные водоросли)", "standard": "SMIIC 1:2019 (100% Халяль замена желатина)"},
    "E407": {"name_en": "Carrageenan", "name_ru": "Каррагинан", "name_kk": "Каррагинан", "status": "HALAL", "origin": "Растительное (Морские водоросли)", "standard": "SMIIC 1:2019"},
    "E410": {"name_en": "Locust bean gum", "name_ru": "Камедь рожкового дерева", "name_kk": "Рожков ағашы шайыры", "status": "HALAL", "origin": "Растительное", "standard": "SMIIC 1:2019"},
    "E412": {"name_en": "Guar gum", "name_ru": "Гуаровая камедь", "name_kk": "Гуар шайыры", "status": "HALAL", "origin": "Растительное (Гуаровые бобы)", "standard": "SMIIC 1:2019"},
    "E414": {"name_en": "Acacia gum / Gum arabic", "name_ru": "Гуммиарабик", "name_kk": "Гуммиарабик", "status": "HALAL", "origin": "Растительное (Смола акации)", "standard": "SMIIC 1:2019"},
    "E415": {"name_en": "Xanthan gum", "name_ru": "Ксантановая камедь", "name_kk": "Ксантан шайыры", "status": "HALAL", "origin": "Бактериальная ферментация (Xanthomonas campestris)", "standard": "SMIIC 1:2019"},
    "E420": {"name_en": "Sorbitol", "name_ru": "Сорбит / Сорбитол", "name_kk": "Сорбит", "status": "HALAL", "origin": "Растительное (Кукурузный крахмал / Глюкоза)", "standard": "SMIIC 1:2019"},
    "E422": {"name_en": "Glycerol / Glycerine", "name_ru": "Глицерин", "name_kk": "Глицерин", "status": "DOUBTFUL", "origin": "Растительное / Синтетическое / Животный жир", "standard": "SMIIC 1:2019 §5.1.2 • JAKIM"},
    "E440": {"name_en": "Pectins", "name_ru": "Пектин", "name_kk": "Пектин", "status": "HALAL", "origin": "Растительное (Яблочные выжимки, цитрусовая корка)", "standard": "SMIIC 1:2019"},
    "E441": {"name_en": "Gelatine", "name_ru": "Желатин", "name_kk": "Желатин", "status": "DOUBTFUL", "origin": "Свиная шкура (80% в ЕС - ХАРАМ) / Говяжьи кости / Рыба (ХАЛЯЛЬ)", "standard": "ДУМК / SMIIC 1:2019 (Халяль только при наличии сертификата)"},
    "E470a": {"name_en": "Sodium, potassium and calcium salts of fatty acids", "name_ru": "Соли жирных кислот", "name_kk": "Май қышқылдарының тұздары", "status": "DOUBTFUL", "origin": "Растительные или животные жиры", "standard": "SMIIC 1:2019 §5.1.2"},
    "E471": {"name_en": "Mono- and diglycerides of fatty acids", "name_ru": "Моно- и диглицериды жирных кислот", "name_kk": "Май қышқылдарының моно- және диглицеридтері", "status": "DOUBTFUL", "origin": "Растительные масла (ХАЛЯЛЬ) или Животные жиры (ХАРАМ)", "standard": "SMIIC 1:2019 §5.1.2 • ДУМК (Халал Даму)"},
    "E472a": {"name_en": "Acetic acid esters of mono- and diglycerides", "name_ru": "Эфиры уксусной кислоты и моно-диглицеридов", "name_kk": "Сірке қышқылы эфирлері", "status": "DOUBTFUL", "origin": "Животное или растительное сырье", "standard": "SMIIC 1:2019 §5.1.2"},
    "E472b": {"name_en": "Lactic acid esters of mono- and diglycerides", "name_ru": "Эфиры молочной кислоты и моно-диглицеридов", "name_kk": "Сүт қышқылы эфирлері", "status": "DOUBTFUL", "origin": "Животное или растительное сырье", "standard": "SMIIC 1:2019 §5.1.2"},
    "E472c": {"name_en": "Citric acid esters of mono- and diglycerides", "name_ru": "Эфиры лимонной кислоты и моно-диглицеридов", "name_kk": "Лимон қышқылы эфирлері", "status": "DOUBTFUL", "origin": "Животное или растительное сырье", "standard": "SMIIC 1:2019 §5.1.2"},
    "E472e": {"name_en": "Diacetyltartaric acid esters of mono- and diglycerides", "name_ru": "Эфиры диацетилвинной кислоты (DATEM)", "name_kk": "Диацетилшарап қышқылы эфирлері", "status": "DOUBTFUL", "origin": "Растительное или животное сырье", "standard": "SMIIC 1:2019 §5.1.2"},
    "E476": {"name_en": "Polyglycerol polyricinoleate (PGPR)", "name_ru": "Полиглицерин полирицинолеат", "name_kk": "Полиглицерин полирицинолеат", "status": "DOUBTFUL", "origin": "Касторовое масло (Растительное) + Глицерин (Может быть животным)", "standard": "SMIIC 1:2019"},
    "E481": {"name_en": "Sodium stearoyl-2-lactylate", "name_ru": "Стеароил-2-лактилат натрия", "name_kk": "Натрий стеароиллактилаты", "status": "DOUBTFUL", "origin": "Стеариновая кислота (Растительная или Животная)", "standard": "SMIIC 1:2019 §5.1.2"},
    "E482": {"name_en": "Calcium stearoyl-2-lactylate", "name_ru": "Стеароил-2-лактилат кальция", "name_kk": "Кальций стеароиллактилаты", "status": "DOUBTFUL", "origin": "Стеариновая кислота (Растительная или Животная)", "standard": "SMIIC 1:2019 §5.1.2"},
    "E491": {"name_en": "Sorbitan monostearate", "name_ru": "Сорбитан моностеарат", "name_kk": "Сорбитан моностеараты", "status": "DOUBTFUL", "origin": "Стеариновая кислота (Животная или Растительная)", "standard": "SMIIC 1:2019 §5.1.2"},
    "E492": {"name_en": "Sorbitan tristearate", "name_ru": "Сорбитан тристеарат", "name_kk": "Сорбитан тристеараты", "status": "DOUBTFUL", "origin": "Стеариновая кислота (Животная или Растительная)", "standard": "SMIIC 1:2019 §5.1.2"},

    # ------------------ E500–E599: SALTS & ACIDITY REGULATORS ------------------
    "E500": {"name_en": "Sodium carbonates (Baking soda)", "name_ru": "Карбонаты натрия (Пищевая сода)", "name_kk": "Натрий карбонаттары (Ас содасы)", "status": "HALAL", "origin": "Минеральное", "standard": "SMIIC 1:2019"},
    "E503": {"name_en": "Ammonium carbonates", "name_ru": "Карбонаты аммония", "name_kk": "Аммоний карбонаттары", "status": "HALAL", "origin": "Синтетическое", "standard": "SMIIC 1:2019"},
    "E542": {"name_en": "Bone phosphate", "name_ru": "Костный фосфат", "name_kk": "Сүйек фосфаты", "status": "HARAM", "origin": "Животные кости (Свиньи или нехаляльный скот)", "standard": "ДУМК / JAKIM (Харам)"},
    "E570": {"name_en": "Fatty acids (Stearic acid)", "name_ru": "Жирные кислоты (Стеариновая кислота)", "name_kk": "Май қышқылдары", "status": "DOUBTFUL", "origin": "Животный жир (Свиной/говяжий) или пальмовое масло", "standard": "SMIIC 1:2019 §5.1.2"},

    # ------------------ E600–E699: FLAVOUR ENHANCERS ------------------
    "E621": {"name_en": "Monosodium glutamate (MSG)", "name_ru": "Глутамат натрия", "name_kk": "Натрий глутаматы", "status": "HALAL", "origin": "Бактериальная ферментация сахарного тростника/маниоки", "standard": "SMIIC 1:2019 (Халяль при растительном субстрате)"},
    "E627": {"name_en": "Disodium guanylate", "name_ru": "Гуанилат натрия", "name_kk": "Натрий гуанилаты", "status": "DOUBTFUL", "origin": "Дрожжевой экстракт / Рыба / Мясной экстракт", "standard": "SMIIC 1:2019"},
    "E631": {"name_en": "Disodium inosinate", "name_ru": "Инозинат натрия", "name_kk": "Натрий инозинаты", "status": "DOUBTFUL", "origin": "Мясной экстракт (Свинина/говядина) / Дрожжи / Тапиока", "standard": "SMIIC 1:2019 §5.1.2 • JAKIM"},
    "E635": {"name_en": "Disodium 5'-ribonucleotides", "name_ru": "5'-рибонуклеотиды натрия", "name_kk": "5'-рибонуклеотидтер", "status": "DOUBTFUL", "origin": "Смесь E627 и E631", "standard": "SMIIC 1:2019 §5.1.2"},

    # ------------------ E900–E999: GLAZING AGENTS & SWEETENERS ------------------
    "E901": {"name_en": "Beeswax", "name_ru": "Пчелиный воск", "name_kk": "Ара балауызы", "status": "HALAL", "origin": "Продукт пчеловодства (Халяль)", "standard": "SMIIC 1:2019"},
    "E904": {"name_en": "Shellac", "name_ru": "Шеллак", "name_kk": "Шеллак", "status": "DOUBTFUL", "origin": "Смола лаковых червецов (Керия лакка)", "standard": "ДУМК / SMIIC (Запрещено в ряде мазхабов как продукт насекомых)"},
    "E920": {"name_en": "L-cysteine", "name_ru": "L-цистеин", "name_kk": "L-цистеин", "status": "HARAM", "origin": "Человеческий волос / Свиная щетина / Перья птиц", "standard": "SMIIC 1:2019 §5.1.4 (Человеческие волосы и свиная щетина категорически ХАРАМ)"},
    "E950": {"name_en": "Acesulfame K", "name_ru": "Ацесульфам калия", "name_kk": "Ацесульфам К", "status": "HALAL", "origin": "Синтетическое", "standard": "SMIIC 1:2019"},
    "E951": {"name_en": "Aspartame", "name_ru": "Аспартам", "name_kk": "Аспартам", "status": "HALAL", "origin": "Синтетическое (Аминокислоты)", "standard": "SMIIC 1:2019"},
    "E955": {"name_en": "Sucralose", "name_ru": "Сукралоза", "name_kk": "Сукралоза", "status": "HALAL", "origin": "Синтетическое (Производное сахарозы)", "standard": "SMIIC 1:2019"},
    "E965": {"name_en": "Maltitol", "name_ru": "Мальтит / Мальтитол", "name_kk": "Мальтитол", "status": "HALAL", "origin": "Растительное (Кукурузный крахмал)", "standard": "SMIIC 1:2019"},
    "E967": {"name_en": "Xylitol", "name_ru": "Ксилит / Ксилитол", "name_kk": "Ксилит", "status": "HALAL", "origin": "Растительное (Древесина березы, кукурузные кочерыжки)", "standard": "SMIIC 1:2019"},

    # ------------------ E1000–E1520: MISCELLANEOUS ------------------
    "E1105": {"name_en": "Lysozyme", "name_ru": "Лизоцим", "name_kk": "Лизоцим", "status": "HALAL", "origin": "Белок куриных яиц", "standard": "SMIIC 1:2019"},
    "E1422": {"name_en": "Acetylated distarch adipate", "name_ru": "Дикрахмаладипат ацетилированный (Крахмал E1422)", "name_kk": "Модификацияланған крахмал", "status": "HALAL", "origin": "Растительное (Модифицированный кукурузный крахмал)", "standard": "SMIIC 1:2019"},
    "E1520": {"name_en": "Propylene glycol", "name_ru": "Пропиленгликоль", "name_kk": "Пропиленгликоль", "status": "HALAL", "origin": "Синтетическое (Не является пьянящим этиловым спиртом)", "standard": "SMIIC 1:2019"}
}

# 2. COMPREHENSIVE INGREDIENTS ONTOLOGY & STEM REGISTRY
INGREDIENTS_REGISTRY = {
    "PORK_AND_SWINE": {
        "status": "HARAM",
        "category_ru": "Свинина и производные свиного происхождения",
        "category_kk": "Доңыз еті және шошқадан алынған өнімдер",
        "quran_ayah": "2:173, 5:3, 6:145, 16:115",
        "standards": ["OIC/SMIIC 1:2019 §5.1.1", "ДУМК Халал Даму", "JAKIM MS 1500:2009"],
        "stems": [
            "свинина", "свиной", "свиное", "свинной", "поросенок", "хряк", "шпик", "бекон",
            "карбонад", "буженина", "грудинка свиная", "сало", "смалец", "лярд", "шошқа",
            "доңыз", "шошқа майы", "pork", "swine", "pig", "bacon", "lard", "pork fat",
            "porcine", "porcine gelatin", "porcine collagen", "porcine pepsin", "свиной желатин",
            "пепсин свиной", "пепсин свиней", "панкреатин свиной"
        ]
    },
    "CARRION_AND_BLOOD": {
        "status": "HARAM",
        "category_ru": "Мертвечина, кровь и нехаляльный убой",
        "category_kk": "Өлексе, қан және шариғатқа сай сойылмаған мал өнімдері",
        "quran_ayah": "2:173, 5:3, 6:145",
        "standards": ["OIC/SMIIC 1:2019 §5.1.1", "ДУМК Халал Даму"],
        "stems": [
            "мертвечина", "падаль", "кровь", "кровяная", "гемоглобин", "плазма крови",
            "альбумин крови", "гематоген", "өлексе", "қан", "қан плазмасы", "гематоген",
            "blood", "plasma", "hemoglobin", "carrion", "non-dhabihah", "нехаляльный убой"
        ]
    },
    "ALCOHOL_AND_INTOXICANTS": {
        "status": "HARAM",
        "category_ru": "Алкоголь, спиртные напитки и опьяняющие вещества",
        "category_kk": "Алкоголь, арақ-шарап және мас қылатын заттар",
        "quran_ayah": "5:90, 2:219",
        "standards": ["OIC/SMIIC 1:2019 §5.1.3", "ДУМК Халал Даму", "JAKIM"],
        "stems": [
            "спирт", "алкоголь", "этанол", "этиловый спирт", "вино", "винный", "винный уксус",
            "коньяк", "коньячный", "ром", "ромовый", "пиво", "пивные дрожжи", "ликёр",
            "бренди", "виски", "водка", "шампанское", "арақ", "шарап", "спирт", "сыра",
            "сыра ашытқысы", "wine", "alcohol", "ethanol", "beer", "rum", "cognac", "liqueur",
            "whisky", "brandy", "wine extract", "beer yeast extract"
        ]
    },
    "INSECT_DERIVATIVES": {
        "status": "HARAM",
        "category_ru": "Насекомые и красители на их основе (Кармин, Шеллак)",
        "category_kk": "Жәндіктер және олардан алынатын бояғыштар",
        "quran_ayah": "7:157 (Хабаис / Скверна)",
        "standards": ["ДУМК РК Постановление", "Ханафи/Шафии Мазхаб", "SMIIC 1:2019 §5.1.1"],
        "stems": [
            "кармин", "кармины", "кошениль", "карминовая кислота", "e120", "е120", "шеллак",
            "e904", "е904", "carmine", "cochineal", "carminic acid", "shellac", "жәндіктер",
            "кошениль сығындысы"
        ]
    },
    "ANIMAL_FAT_AND_EMULSIFIERS": {
        "status": "DOUBTFUL",
        "category_ru": "Эмульгаторы и жирные кислоты (Требуется сертификат Халяль)",
        "category_kk": "Эмульгаторлар мен май қышқылдары (Халал сертификаты талап етіледі)",
        "quran_ayah": "Хадис: Оставь то, что внушает сомнение (Тирмизи)",
        "standards": ["OIC/SMIIC 1:2019 §5.1.2", "JAKIM MS 1500:2009", "ДУМК Халал Даму"],
        "stems": [
            "животный жир", "говяжий жир", "жир животного происхождения", "мал майы",
            "моно- и диглицериды", "моноглицериды", "диглицериды", "e471", "е471", "e472",
            "е472", "e472a", "e472b", "e472c", "e472e", "e476", "е476", "e481", "е481",
            "e482", "е482", "глицерин", "e422", "е422", "стеариновая кислота", "стеарат",
            "e570", "е570", "animal fat", "glycerol", "mono- and diglycerides", "pgpr"
        ]
    },
    "ENZYMES_AND_RENNET": {
        "status": "DOUBTFUL",
        "category_ru": "Ферменты и сычужный фермент сыра (Сычуг)",
        "category_kk": "Ферменттер және ірімшік мәйегі",
        "quran_ayah": "Фикх стандарты",
        "standards": ["OIC/SMIIC 1:2019 §5.1.2", "ДУМК Халал Даму"],
        "stems": [
            "сычужный фермент", "сычуг", "пепсин", "сычужный сыр", "животный сычуг",
            "липаза животная", "мәйек", "ірімшік мәйегі", "rennet", "animal rennet",
            "pepsin", "animal lipase"
        ]
    },
    "PLANT_AND_SYNTHETIC_HALAL": {
        "status": "HALAL",
        "category_ru": "Разрешенные растительные и микробиологические ингредиенты",
        "category_kk": "Рұқсат етілген өсімдік және микробиологиялық қоспалар",
        "quran_ayah": "2:168, 5:4",
        "standards": ["OIC/SMIIC 1:2019", "ДУМК Халал Даму"],
        "stems": [
            "растительное масло", "подсолнечное масло", "пальмовое масло", "соевое масло",
            "оливковое масло", "агар-агар", "пектин", "гуаровая камедь", "ксантановая камедь",
            "соевый лецитин", "подсолнечный лецитин", "микробиальный фермент", "микробиологический ренин",
            "химозин микробиальный", "өсімдік майы", "агар-агар", "пектин", "соя лецитині",
            "plant oil", "soy lecithin", "agar", "pectin", "guar gum", "xanthan gum", "microbial rennet"
        ]
    }
}

def build_master_database():
    database = {
        "version": "2.0.0",
        "title": "Al-Furqan Guard — Master Halal/Haram Knowledge Base",
        "description": "Deterministic canonical food additives, E-codes, chemical substances, and Shariah rulings registry.",
        "standards_aligned": [
            "OIC/SMIIC 1:2019 (General Requirements for Halal Food)",
            "JAKIM (MS 1500:2009 Halal Food Standards, Malaysia)",
            "BPJPH / MUI (HAS 23000 Halal Assurance System, Indonesia)",
            "ДУМК («Халал Даму» стандарттары, Қазақстан)",
            "МЦСиС «Халяль» (Совет Муфтиев России)"
        ],
        "stats": {
            "total_e_codes": len(E_CODES_DATA),
            "total_categories": len(INGREDIENTS_REGISTRY),
            "total_stems": sum(len(c["stems"]) for c in INGREDIENTS_REGISTRY.values())
        },
        "e_codes": E_CODES_DATA,
        "ingredient_categories": INGREDIENTS_REGISTRY
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(database, f, ensure_ascii=False, indent=2)

    print(f"✅ Successfully generated Halal Master Database at: {OUTPUT_PATH}")
    print(f"📊 Total E-Codes: {database['stats']['total_e_codes']}")
    print(f"📊 Total Categories: {database['stats']['total_categories']}")
    print(f"📊 Total Ingredient Stems: {database['stats']['total_stems']}")
    print(f"📦 File Size: {os.path.getsize(OUTPUT_PATH) / 1024:.2f} KB")

if __name__ == "__main__":
    build_master_database()
