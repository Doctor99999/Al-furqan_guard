"""
Al-Furqan Guard — Мультимодальный Telegram-бот v2.0 (Hardened Enterprise)
Детерминированный L0 Ground Truth фильтр Корана, PDF-аудитор, распознавание фото (OCR),
Халяль-комплаенс, время намаза, Кибла и расчет Закята.

Возможности:
1. 📖 Чтение и прослушивание 114 Сур и 6 236 Аятов (/fatiha, /ayah, /surah)
2. 🛡️ Защита от галлюцинаций ИИ (проверка достоверности цитат в текстах)
3. 📄 Аудит PDF-документов (финансовые договоры, книги, статьи)
4. 📷 Распознавание фото и этикеток продуктов (OCR + Халяль-анализ)
5. 📍 Точное астрономическое время 5 намазов и компас Киблы по геолокации
6. 💰 Шариатский калькулятор Закята и Нисаба
7. 🔍 Семантический поиск по темам Корана (/search <тема>)
8. 📜 Тафсир аятов (Ибн Касир, Ас-Саади) (/tafsir <сура> <аят>)
9. 🌐 Мультиязычность (Русский, Қазақша, English)
"""

import io
import os
import sys
import re
import json
import logging
from typing import Optional

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# Подключение ядра Al-Furqan
from quran_guard import QuranEngine, QuranGuard, AhkamExtractor
from quran_guard.halal_knowledge_base import HalalKnowledgeBase
from quran_guard.config import MANIFEST_PATH, TRANSLATIONS_PATH
from quran_guard.multimodal import (
    PDFDocumentProcessor,
    ImageOCRProcessor,
    PrayerTimesCalculator,
    ZakatCalculator,
    SemanticThemeEngine
)

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("AlFurqanBot")

# Инициализация ядра
print("Загрузка Al-Furqan Guard Core Engine v2.0...")
engine = QuranEngine(manifest_path=MANIFEST_PATH, translations_path=TRANSLATIONS_PATH)
guard = QuranGuard(engine)
ahkam = AhkamExtractor(engine)
print("Ядро Al-Furqan Guard успешно загружено!")

# Хранилище языковых настроек пользователей (user_id -> lang)
USER_LANGS = {}
USER_RECITERS = {} # user_id -> reciter ('alafasy', 'husary', 'abdulbasit')

# CDN чтецов
RECITERS_CDN = {
    "alafasy": "https://everyayah.com/data/Alafasy_128kbps",
    "husary": "https://everyayah.com/data/Husary_128kbps",
    "abdulbasit": "https://everyayah.com/data/Abdul_Basit_Murattal_192kbps"
}

def get_user_lang(user_id: int) -> str:
    return USER_LANGS.get(user_id, "ru")

def get_user_reciter(user_id: int) -> str:
    return USER_RECITERS.get(user_id, "alafasy")

# =========================================================================
# ТЕКСТЫ И ИНТЕРФЕЙС
# =========================================================================

I18N_MESSAGES = {
    "ru": {
        "welcome": (
            "🌟 *Добро пожаловать в Al-Furqan Guard!* 🌟\n\n"
            "Мультимодальная платформа верификации Корана, исламских финансов и стандартов Халяль на базе *L0 Ground Truth* (6 236 аятов, 130 030 токенов, 1 651 корень).\n\n"
            "📌 *Что умеет этот бот:*\n"
            "• 📖 *Коран и Чтение:* Аудио любого аята и суры с переводом и транслитерацией\n"
            "• 🛡️ *Анти-Галлюцинация:* Проверка любых текстов на выдуманные цитаты\n"
            "• 📄 *PDF-Аудитор:* Отправьте PDF-файл (договор/книгу) для проверки соответствия стандартам AAOIFI и Корану\n"
            "• 📷 *Фото OCR:* Сфотографируйте состав продукта или документ для мгновенного анализа\n"
            "• 📍 *Намаз и Кибла:* Отправьте геолокацию для расчета времени намаза и направления на Каабу\n"
            "• 💰 *Калькулятор Закята:* Точный расчет нисаба (2.5%) по золоту и сбережениям\n"
            "• 🔍 *ИИ-Поиск:* Поиск по темам (терпение, родители, торговля, пост)\n\n"
            "👇 *Используйте интерактивное меню ниже или просто отправьте текст/фото/PDF:*"
        ),
        "btn_fatiha": "📖 114 Сур Корана",
        "btn_halal": "🥗 Халяль Скринер",
        "btn_roots": "🧬 Корни Корана (1 651)",
        "btn_namaz": "📍 Намаз & Кибла",
        "btn_zakat": "💰 Калькулятор Закята",
        "btn_search": "🔍 Поиск по темам",
        "btn_reciter": "🎙️ Выбрать чтеца",
        "btn_lang": "🌐 Сменить язык",
        "help": (
            "📖 *Команды и возможности Al-Furqan Guard:*\n\n"
            "• `/fatiha` — Сура Аль-Фатиха с транслитерацией и аудио\n"
            "• `/ayah 2 255` — Получить Аят аль-Курси (или `<сура> <аят>`)\n"
            "• `/surah 112` — Получить суру целиком\n"
            "• `/halal свинина` или `/halal E120` — Проверка на Халяль\n"
            "• `/root صبر` — Анализ корня в Коране\n"
            "• `/search родители` — Поиск аятов по теме\n"
            "• `/zakat` — Калькулятор Закята\n"
            "• `/tafsir 5 3` — Тафсир к аяту\n\n"
            "📸 *Мультимодальность:* Отправьте **фото состава** или **PDF-документ**, бот автоматически распознает текст и выполнит аудит!"
        )
    },
    "kk": {
        "welcome": (
            "🌟 *Al-Furqan Guard мультимодальды ботына қош келдіңіз!* 🌟\n\n"
            "Қасиетті Құранның *L0 Ground Truth* эталоны, исламдық қаржы және Халал комплаенс сүзгісі (6 236 аят, 130 030 таңба, 1 651 түбір).\n\n"
            "📌 *Боттың барлық мүмкіндіктері:*\n"
            "• 📖 *Құранды оқу & тыңдау:* Кез келген аят пен сүренің аудиосы, транскрипциясы мен аудармасы\n"
            "• 🛡️ *ЖИ галлюцинациясына қарсы:* Мәтіндегі бұрмаланған аяттарды анықтау\n"
            "• 📄 *PDF құжат аудиті:* Келісімшарт немесе кітапты PDF түрінде жіберіп, AAOIFI мен Құран бойынша тексеріңіз\n"
            "• 📷 *Фото OCR тану:* Тағам құрамы немесе мәтінді фотоға түсіріп жіберіңіз\n"
            "• 📍 *Намаз уақыты & Құбыла:* Геолокация жіберіп, 5 уақыт намаз бен Қағба бағытын біліңіз\n"
            "• 💰 *Зекет есептегіші:* Нисаб пен 2.5% зекетті дәл есептеу\n"
            "• 🔍 *Тақырыптық іздеу:* Сабыр, ата-ана, адал сауда, ораза туралы аяттар\n\n"
            "👇 *Төмендегі батырмаларды қолданыңыз немесе мәтін/фото/PDF жіберіңіз:*"
        ),
        "btn_fatiha": "📖 114 Сүре каталогы",
        "btn_halal": "🥗 Халал сүзгісі",
        "btn_roots": "🧬 1 651 Түбір",
        "btn_namaz": "📍 Намаз & Құбыла",
        "btn_zakat": "💰 Зекет калькуляторы",
        "btn_search": "🔍 Тақырыптық іздеу",
        "btn_reciter": "🎙️ Құран оқушысын таңдау",
        "btn_lang": "🌐 Тілді ауыстыру",
        "help": (
            "📖 *Бот пәрмендері:*\n\n"
            "• `/fatiha` — Әл-Фатиха сүресі (транскрипциясы мен аудиосы)\n"
            "• `/ayah 2 255` — Аятул-Күрси (немесе `<сүре> <аят>`)\n"
            "• `/surah 112` — Сүрені толық тыңдау\n"
            "• `/halal доңыз` немесе `/halal E120` — Халал сүзгісі\n"
            "• `/root صبر` — Түбір бойынша аяттар\n"
            "• `/search ата-ана` — Тақырыптық іздеу\n"
            "• `/zakat` — Зекет есептеу\n"
            "• `/tafsir 5 3` — Аяттың тафсирі\n\n"
            "📸 *Мультимодальдылық:* **Фото** немесе **PDF файл** жіберіңіз, бот автоматты түрде мәтінді оқып, аудит жасайды!"
        )
    },
    "en": {
        "welcome": (
            "🌟 *Welcome to Al-Furqan Guard Multi-Modal Bot!* 🌟\n\n"
            "Deterministic Quran Ground Truth, Islamic Finance & Halal Compliance (6,236 Ayahs, 130,030 Tokens, 1,651 Roots).\n\n"
            "📌 *Key Capabilities:*\n"
            "• 📖 *Quran Audio & Text:* Read & Listen to any Ayah with verified translations\n"
            "• 🛡️ *Anti-Hallucination:* Verifies Quranic quotes against false attributions\n"
            "• 📄 *PDF Auditor:* Upload PDF contracts/books for AAOIFI & Shariah compliance audit\n"
            "• 📷 *Photo OCR:* Snap food labels or contracts for instant verification\n"
            "• 📍 *Prayer Times & Qibla:* Send location for 5 daily prayer times and Kaaba compass\n"
            "• 💰 *Zakat Calculator:* Accurate Nisab & 2.5% Zakat computation\n"
            "• 🔍 *Semantic Search:* Natural theme search (patience, parents, finance, fasting)\n\n"
            "👇 *Use the menu below or simply upload text/photo/PDF:*"
        ),
        "btn_fatiha": "📖 114 Surahs Catalog",
        "btn_halal": "🥗 Halal Screener",
        "btn_roots": "🧬 1,651 Roots",
        "btn_namaz": "📍 Prayer Times & Qibla",
        "btn_zakat": "💰 Zakat Calculator",
        "btn_search": "🔍 Thematic Search",
        "btn_reciter": "🎙️ Select Reciter",
        "btn_lang": "🌐 Change Language",
        "help": (
            "📖 *Commands & Features:*\n\n"
            "• `/fatiha` — Surah Al-Fatiha with audio and transliteration\n"
            "• `/ayah 2 255` — Ayat al-Kursi (or `<sura> <ayah>`)\n"
            "• `/surah 112` — Listen to full Surah\n"
            "• `/halal pork` or `/halal E120` — Halal verification\n"
            "• `/root sbr` — Search verses by root\n"
            "• `/search patience` — Semantic theme search\n"
            "• `/zakat` — Zakat calculation\n\n"
            "📸 *Multi-Modal:* Send a **Photo** or **PDF document** for automated text extraction & audit!"
        )
    }
}

def get_persistent_reply_keyboard(lang: str = "ru") -> ReplyKeyboardMarkup:
    """Returns persistent ReplyKeyboardMarkup with 4 main bot actions."""
    if lang == "kk":
        keyboard = [
            [KeyboardButton("📖 Құран оқу"), KeyboardButton("🥗 Халал сүзгісі")],
            [KeyboardButton("🕋 Намаз және Құбыла"), KeyboardButton("ℹ️ Қалай қолдану керек")]
        ]
    elif lang == "en":
        keyboard = [
            [KeyboardButton("📖 Read Quran"), KeyboardButton("🥗 Halal Scanner")],
            [KeyboardButton("🕋 Prayer & Qibla"), KeyboardButton("ℹ️ How to Use")]
        ]
    else:
        keyboard = [
            [KeyboardButton("📖 Читать Коран"), KeyboardButton("🥗 Халяль сканер")],
            [KeyboardButton("🕋 Намаз и Кибла"), KeyboardButton("ℹ️ Как пользоваться")]
        ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_main_keyboard(lang: str) -> InlineKeyboardMarkup:
    t = I18N_MESSAGES.get(lang, I18N_MESSAGES["ru"])
    keyboard = [
        [
            InlineKeyboardButton(t.get("btn_fatiha", "📖 114 Сур Корана"), callback_data="cmd_surah_catalog_1"),
            InlineKeyboardButton(t["btn_halal"], callback_data="cmd_halal_menu")
        ],
        [
            InlineKeyboardButton(t["btn_namaz"], callback_data="cmd_namaz_prompt"),
            InlineKeyboardButton(t["btn_zakat"], callback_data="cmd_zakat_calc")
        ],
        [
            InlineKeyboardButton(t["btn_roots"], callback_data="cmd_roots_menu"),
            InlineKeyboardButton(t["btn_search"], callback_data="cmd_search_menu")
        ],
        [
            InlineKeyboardButton(t["btn_reciter"], callback_data="cmd_reciter_menu"),
            InlineKeyboardButton(t["btn_lang"], callback_data="cmd_lang_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# =========================================================================
# КОМАНДЫ БОТА
# =========================================================================


async def send_surah_catalog(
    update: Update, 
    context: ContextTypes.DEFAULT_TYPE, 
    page: int = 1, 
    page_size: int = 12,
    edit: bool = False
):
    """Отправляет интерактивный каталог всех 114 Сур Корана с пагинацией."""
    user = update.effective_user
    user_id = user.id if user else 0
    lang = get_user_lang(user_id)
    total_surahs = 114
    total_pages = (total_surahs + page_size - 1) // page_size
    page = max(1, min(page, total_pages))

    start_sura = (page - 1) * page_size + 1
    end_sura = min(page * page_size, total_surahs)

    surah_names = engine.SURAH_NAMES.get(lang, engine.SURAH_NAMES["ru"])

    keyboard = []
    
    # Быстрые популярные суры на первой странице
    if page == 1:
        keyboard.append([
            InlineKeyboardButton("🌟 1. Фатиха", callback_data="open_surah_1"),
            InlineKeyboardButton("👑 36. Йа Син", callback_data="open_surah_36"),
        ])
        keyboard.append([
            InlineKeyboardButton("🛡️ 67. Мульк", callback_data="open_surah_67"),
            InlineKeyboardButton("💎 112. Ихлас", callback_data="open_surah_112")
        ])

    # Список сур по 2 в ряд
    current_row = []
    for s in range(start_sura, end_sura + 1):
        s_name = surah_names[s - 1]
        if len(s_name) > 20:
            s_name = s_name[:18] + "…"
        btn_text = f"{s}. {s_name}"
        current_row.append(InlineKeyboardButton(btn_text, callback_data=f"open_surah_{s}"))
        if len(current_row) == 2:
            keyboard.append(current_row)
            current_row = []
    if current_row:
        keyboard.append(current_row)

    # Навигация по страницам каталога
    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"cmd_surah_catalog_{page - 1}"))
    nav_row.append(InlineKeyboardButton(f"📄 {page}/{total_pages}", callback_data="noop"))
    if page < total_pages:
        nav_row.append(InlineKeyboardButton("Далее ➡️", callback_data=f"cmd_surah_catalog_{page + 1}"))
    keyboard.append(nav_row)

    title_text = (
        f"📖 *Каталог Священного Корана (Все 114 Сур)*\n"
        f"_Страница {page} из {total_pages} (Суры {start_sura}–{end_sura})_\n\n"
        f"Нажмите на любую суру для чтения с переводом, транслитерацией и аудио, либо отправьте номер суры числом (например, `36` или `/surah 36`):"
    )
    reply_markup = InlineKeyboardMarkup(keyboard)

    if edit and update.callback_query:
        try:
            await update.callback_query.edit_message_text(
                text=title_text,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        except Exception:
            await update.callback_query.message.reply_markdown(title_text, reply_markup=reply_markup)
    elif update.message:
        await update.message.reply_markdown(title_text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_markdown(title_text, reply_markup=reply_markup)

async def send_surah_paginated(
    update: Update, 
    context: ContextTypes.DEFAULT_TYPE, 
    sura: int, 
    page: int = 1, 
    page_size: int = 10,
    edit: bool = False
):
    """
    Sends or edits a paginated view of a surah in chunks of 10-15 ayahs.
    Prevents Telegram 4096-character limit errors and provides smooth navigation.
    """
    if not (1 <= sura <= 114):
        sura = 1
    
    total_ayahs = engine.CANONICAL_AYAH_COUNTS[sura - 1]
    total_pages = max(1, (total_ayahs + page_size - 1) // page_size)
    page = max(1, min(page, total_pages))

    start_ayah = (page - 1) * page_size + 1
    end_ayah = min(page * page_size, total_ayahs)

    lang = get_user_lang(update.effective_user.id)
    sura_name = engine.SURAH_NAMES.get(lang, engine.SURAH_NAMES["ru"])[sura - 1]

    msg_lines = [
        f"📖 *{sura_name} (Сура {sura})* • _Стр. {page}/{total_pages} (Аяты {start_ayah}–{end_ayah} из {total_ayahs})_\n"
    ]

    for a in range(start_ayah, end_ayah + 1):
        data = engine.get_ayah(sura, a)
        if data:
            ar_text = data.get("text_uthmani") or data.get("text")
            tr_text = data.get("transliteration", "")
            translations = data.get("translations", {})
            trans = translations.get(lang) or translations.get("ru") or translations.get("kk") or ""

            msg_lines.append(f"*{a}.* `{ar_text}`")
            if tr_text:
                msg_lines.append(f"   _{tr_text}_")
            if trans:
                msg_lines.append(f"   💬 {trans}")
            msg_lines.append("")

    full_text = "\n".join(msg_lines)

    # Navigation buttons
    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"surah_page_{sura}_{page - 1}"))
    nav_row.append(InlineKeyboardButton(f"📄 {page}/{total_pages}", callback_data="noop"))
    if page < total_pages:
        nav_row.append(InlineKeyboardButton("Далее ➡️", callback_data=f"surah_page_{sura}_{page + 1}"))

    keyboard = [nav_row]
    
    # Audio link & Surah catalog return button
    s_pad = f"{sura:03d}"
    cat_page = (sura - 1) // 12 + 1
    keyboard.append([
        InlineKeyboardButton("🎧 Аудио суры (MP3)", url=f"https://server8.mp3quran.net/afs/{s_pad}.mp3"),
        InlineKeyboardButton("📚 Все 114 Сур", callback_data=f"cmd_surah_catalog_{cat_page}")
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    if edit and update.callback_query:
        await update.callback_query.edit_message_text(
            text=full_text,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    elif update.message:
        await update.message.reply_markdown(full_text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_markdown(full_text, reply_markup=reply_markup)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветственное сообщение с логотипом, ReplyKeyboardMarkup и Inline меню."""
    user = update.effective_user
    lang = get_user_lang(user.id)
    t = I18N_MESSAGES.get(lang, I18N_MESSAGES["ru"])
    
    logo_path = None
    for p in ["ui/logo.png", "ui/logo.jpg", "logo.png"]:
        if os.path.exists(p):
            logo_path = p
            break
            
    # 1. Send greeting with logo if available
    if logo_path:
        try:
            with open(logo_path, "rb") as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=t["welcome"],
                    parse_mode="Markdown",
                    reply_markup=get_persistent_reply_keyboard(lang)
                )
        except Exception:
            await update.message.reply_markdown(t["welcome"], reply_markup=get_persistent_reply_keyboard(lang))
    else:
        await update.message.reply_markdown(
            t["welcome"],
            reply_markup=get_persistent_reply_keyboard(lang)
        )
        
    # 2. Provide inline quick actions
    await update.message.reply_markdown(
        "⚡ *Быстрый доступ к разделам Al-Furqan Guard:*",
        reply_markup=get_main_keyboard(lang)
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Справка по доступным командам и мультимодальным функциям."""
    lang = get_user_lang(update.effective_user.id)
    t = I18N_MESSAGES.get(lang, I18N_MESSAGES["ru"])
    await update.message.reply_markdown(t["help"], reply_markup=get_persistent_reply_keyboard(lang))


async def fatiha_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправка суры Аль-Фатиха с арабским текстом, транслитерацией, переводом и аудио."""
    lang = get_user_lang(update.effective_user.id)
    
    msg_lines = [
        "📖 *СУРА 1: АЛЬ-ФАТИХА (ОТКРЫВАЮЩАЯ)* • 7 АЯТОВ\n"
        "_Uthmani Script • Transliteration • Translation_\n"
    ]
    
    for a in range(1, 8):
        data = engine.get_ayah(1, a)
        if data:
            ar_text = data.get("text_uthmani") or data.get("text")
            tr_text = data.get("transliteration", "")
            translations = data.get("translations", {})
            trans = translations.get(lang) or translations.get("ru") or translations.get("kk") or ""
            
            msg_lines.append(f"*{a}.* `{ar_text}`")
            if tr_text:
                msg_lines.append(f"   _Латиница:_ `{tr_text}`")
            if trans:
                msg_lines.append(f"   _Перевод:_ {trans}")
            msg_lines.append("")

    full_text = "\n".join(msg_lines)
    
    # Отправка текста
    if update.message:
        await update.message.reply_markdown(full_text)
    elif update.callback_query:
        await update.callback_query.message.reply_markdown(full_text)
        
    # Отправка аудио чтения Аль-Фатихи
    chat_id = update.effective_chat.id
    try:
        await context.bot.send_audio(
            chat_id=chat_id,
            audio="https://server8.mp3quran.net/afs/001.mp3",
            title="Сура Аль-Фатиха (The Opening)",
            performer="Шейх Мишари Рашид Аль-Афаси"
        )
    except Exception as e:
        logger.warning(f"Audio send notice: {e}")

async def ayah_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Поиск аята: /ayah <сура> <аят> (например, /ayah 2 255)"""
    args = context.args
    lang = get_user_lang(update.effective_user.id)
    reciter = get_user_reciter(update.effective_user.id)
    
    if not args or len(args) < 2:
        await update.message.reply_markdown(
            "⚠️ *Формат команды:* `/ayah <номер_суры> <номер_аята>`\n"
            "Например: `/ayah 2 255` (Аят аль-Курси) или `/ayah 112 1`"
        )
        return

    try:
        sura = int(args[0])
        ayah = int(args[1])
    except ValueError:
        await update.message.reply_markdown("❌ Номера суры и аята должны быть числами.")
        return

    if not (1 <= sura <= 114):
        await update.message.reply_markdown("❌ Номер суры должен быть от 1 до 114.")
        return
        
    max_ayah = engine.CANONICAL_AYAH_COUNTS[sura - 1]
    if not (1 <= ayah <= max_ayah):
        await update.message.reply_markdown(f"❌ В суре {sura} всего {max_ayah} аятов.")
        return

    data = engine.get_ayah(sura, ayah)
    if not data:
        await update.message.reply_markdown("❌ Аят не найден.")
        return

    ar_text = data.get("text_uthmani") or data.get("text")
    tr_text = data.get("transliteration", "")
    translations = data.get("translations", {})
    trans = translations.get(lang) or translations.get("ru") or translations.get("kk") or ""
    
    sura_name = engine.SURAH_NAMES.get(lang, engine.SURAH_NAMES["ru"])[sura - 1]
    
    msg = (
        f"📖 *{sura_name} [{sura}:{ayah}]*\n\n"
        f"*{ar_text}*\n\n"
        f"🗣️ *Произношение (латиница):*\n`{tr_text}`\n\n"
        f"🌍 *Смысловой перевод:*\n{trans}"
    )
    
    await update.message.reply_markdown(msg)
    
    # Отправка аудио аята
    s_pad = f"{sura:03d}"
    a_pad = f"{ayah:03d}"
    audio_url = f"{RECITERS_CDN.get(reciter, RECITERS_CDN['alafasy'])}/{s_pad}{a_pad}.mp3"
    
    try:
        await context.bot.send_audio(
            chat_id=update.effective_chat.id,
            audio=audio_url,
            title=f"{sura_name} [{sura}:{ayah}]",
            performer="Al-Furqan Audio"
        )
    except Exception as e:
        logger.warning(f"Ayah audio send notice: {e}")

async def surah_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Чтение суры с пагинацией: /surah <номер_суры> (например, /surah 2)"""
    args = context.args
    if not args:
        await send_surah_paginated(update, context, sura=1, page=1)
        return
    try:
        sura_num = int(args[0])
        if not (1 <= sura_num <= 114):
            await update.message.reply_markdown("❌ Номер суры должен быть от 1 до 114.")
            return
        await send_surah_paginated(update, context, sura=sura_num, page=1)
    except ValueError:
        await update.message.reply_markdown("⚠️ Укажите номер суры числом, например: `/surah 36` (Сура Йа Син)")

async def halal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверка продукта или E-кода на Халяль: /halal <название/E-код>"""
    query = " ".join(context.args).strip()
    if not query:
        await update.message.reply_markdown(
            "🥗 *Халяль / Харам Скринер*\n\n"
            "Отправьте название продукта, ингредиента или E-код:\n"
            "Например:\n"
            "• `/halal свинина`\n"
            "• `/halal кармин E120`\n"
            "• `/halal желатин E441`\n"
            "• `/halal семга и морепродукты`\n"
            "• `/halal кредит под 18%`"
        )
        return

    matches = HalalKnowledgeBase.match_input(query)
    lang = get_user_lang(update.effective_user.id)
    
    if not matches:
        await update.message.reply_markdown(
            f"🟢 *Прямых запретов не обнаружено (Халяль / Дозволено)*\n\n"
            f"По запросу `«{query}»` в канонической базе Корана и стандартах Халяль признаков Харама не обнаружено."
        )
        return

    for m in matches:
        is_haram = m["verdict"] == "HARAM"
        is_doubt = m["verdict"] == "DOUBTFUL"
        
        icon = "🔴" if is_haram else ("🟡" if is_doubt else "🟢")
        title = m.get(f"title_{lang}") or m.get("title_ru")
        desc = m.get(f"description_{lang}") or m.get("description_ru")
        ar_text = m.get("canonical_arabic", "")
        ayah_ref = m.get("ayah_ref", "")
        arabic_line = f"📖 *{ar_text}*\n\n" if ar_text else ""
        msg = (
            f"{icon} *{title}*\n\n"
            f"📝 {desc}\n\n"
            f"{arabic_line}"
            f"📌 *Основа в Коране:* {ayah_ref}"
        )
        await update.message.reply_markdown(msg)

async def root_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Поиск по семантическому корню: /root <корень>"""
    if not context.args:
        await update.message.reply_markdown(
            "🧬 *Анализатор 1 651 корня Корана*\n\n"
            "Введите арабский корень после команды:\n"
            "Например: `/root صبر` (терпение) или `/root رحم` (милость)"
        )
        return

    root = " ".join(context.args).strip()
    results = engine.search_by_root(root)
    
    if not results:
        await update.message.reply_markdown(f"❌ По корню `«{root}»` аятов не найдено.")
        return

    canonical_root = results[0].get("root", root)
    total = len(results)
    msg_lines = [
        f"🧬 *Корень:* `{canonical_root}` (запрос: {root})\n"
        f"📊 *Найдено аятов:* {total} (показаны первые 5)\n"
    ]
    
    lang = get_user_lang(update.effective_user.id)
    for res in results[:5]:
        sura = res["sura"]
        ayah = res["ayah"]
        ar = res["text_uthmani"]
        trans = res.get("translations", {}).get(lang) or res.get("translations", {}).get("ru") or ""
        sura_name = engine.SURAH_NAMES.get(lang, engine.SURAH_NAMES["ru"])[sura - 1]
        
        msg_lines.append(f"• 📖 *{sura_name} [{sura}:{ayah}]*")
        msg_lines.append(f"  `{ar}`")
        if trans:
            msg_lines.append(f"  _{trans}_")
        msg_lines.append("")

    await update.message.reply_markdown("\n".join(msg_lines))

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Семантический поиск по темам: /search <тема>"""
    query = " ".join(context.args).strip()
    if not query:
        await update.message.reply_markdown(
            "🔍 *Семантический поиск по темам Корана*\n\n"
            "Примеры запросов:\n"
            "• `/search терпение`\n"
            "• `/search родители`\n"
            "• `/search справедливость`\n"
            "• `/search торговля`\n"
            "• `/search пост`\n"
            "• `/search прощение`"
        )
        return

    results = SemanticThemeEngine.find_ayahs_by_topic(query, engine)
    if not results:
        await update.message.reply_markdown(f"❌ По теме `«{query}»` аяты не найдены. Попробуйте синоним.")
        return

    lang = get_user_lang(update.effective_user.id)
    msg_lines = [f"🔍 *Аяты Корана по теме «{query}»:*\n"]
    
    for r in results:
        sura = r["sura"]
        ayah = r["ayah"]
        ar = r["text_uthmani"]
        trans = r.get("translations", {}).get(lang) or r.get("translations", {}).get("ru") or ""
        sura_name = engine.SURAH_NAMES.get(lang, engine.SURAH_NAMES["ru"])[sura - 1]
        
        msg_lines.append(f"📖 *{sura_name} [{sura}:{ayah}]*")
        msg_lines.append(f"*{ar}*")
        if trans:
            msg_lines.append(f"_{trans}_")
        msg_lines.append("")

    await update.message.reply_markdown("\n".join(msg_lines))

async def zakat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Калькулятор Закята: /zakat <сумма_сбережений> [грамм_золота]"""
    args = context.args
    if not args:
        # Расчет по умолчанию с подсказкой
        res = ZakatCalculator.calculate_zakat(cash_savings=1000000)
        await update.message.reply_markdown(
            "💰 *Шариатский калькулятор Закята*\n\n"
            "📌 *Пример использования:*\n"
            "• `/zakat 1000000` (Закят с 1 000 000 тенге/рублей)\n"
            "• `/zakat 500000 100` (500 000 сбережений + 100 грамм золота)\n\n"
            f"📊 *Текущий порог Нисаба (85г золота):* ~{res['gold_nisab_threshold']:,.0f} ₸\n"
            f"⚖️ *Ставка Закята:* 2.5% (1/40 часть)"
        )
        return

    try:
        cash = float(args[0])
        gold = float(args[1]) if len(args) > 1 else 0.0
        res = ZakatCalculator.calculate_zakat(cash_savings=cash, gold_grams=gold)
        
        if res["is_obligatory"]:
            verdict = "✅ *Закят обязателен к выплате (Ваджиб)*"
            amount_text = f"💵 *Сумма Закята к выплате (2.5%):* `{res['zakat_due']:,.2f}`"
        else:
            verdict = "ℹ️ *Сумма меньше Нисаба (Закят не обязателен)*"
            amount_text = "Закят не начисляется, так как имущество не достигло порога Нисаба."

        msg = (
            f"💰 *РЕЗУЛЬТАТ РАСЧЕТА ЗАКЯТА*\n\n"
            f"{verdict}\n\n"
            f"• *Общее имущество:* `{res['gross_wealth']:,.2f}`\n"
            f"• *Порог Нисаба:* `{res['gold_nisab_threshold']:,.2f}`\n\n"
            f"{amount_text}\n\n"
            f"📖 _«Выстаивайте молитву и выплачивайте закят...» (Коран 2:43)_"
        )
        await update.message.reply_markdown(msg)
    except Exception as e:
        await update.message.reply_markdown(f"❌ Ошибка ввода: {str(e)}")

# =========================================================================
# МУЛЬТИМОДАЛЬНЫЕ ОБРАБОТЧИКИ (ФОТО, PDF, ГЕОЛОКАЦИЯ)
# =========================================================================

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка фото: OCR распознавание текста и проверка на Халяль/Коран."""
    photo = update.message.photo[-1] # Самое высокое разрешение
    await update.message.reply_markdown("📷 *Фото получено! Выполняется OCR-распознавание текста и анализ...*")
    
    try:
        file = await context.bot.get_file(photo.file_id)
        photo_bytes = await file.download_as_bytearray()
        
        extracted_text = ImageOCRProcessor.extract_text(bytes(photo_bytes))
        
        # Проверка на Халяль
        matches = HalalKnowledgeBase.match_input(extracted_text)
        lang = get_user_lang(update.effective_user.id)
        
        report_lines = [
            "📋 *РЕЗУЛЬТАТ OCR-АНАЛИЗА ФОТО:*\n",
            f"📝 *Распознанный фрагмент:*\n`{extracted_text[:300]}`\n"
        ]
        
        if matches:
            report_lines.append("🚨 *ОБНАРУЖЕНЫ ШАРИАТСКИЕ МАРКЕРЫ:*\n")
            for m in matches:
                is_h = m["verdict"] == "HARAM"
                icon = "🔴" if is_h else "🟡"
                report_lines.append(f"{icon} *{m.get(f'title_{lang}', m.get('title_ru'))}*")
                report_lines.append(f"   {m.get(f'description_{lang}', m.get('description_ru'))}")
                report_lines.append(f"   📖 _Основа: {m.get('ayah_ref', '')}_\n")
        else:
            report_lines.append("🟢 *Прямых запретов / Харама на изображении не обнаружено.*")

        await update.message.reply_markdown("\n".join(report_lines))
    except Exception as e:
        await update.message.reply_markdown(f"❌ Ошибка обработки фото: {str(e)}")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка PDF-документов: извлечение текста, проверка цитат и аудит договоров AAOIFI."""
    doc = update.message.document
    if not doc.file_name.lower().endswith(".pdf"):
        await update.message.reply_markdown("ℹ️ Пожалуйста, отправьте документ в формате **PDF** для проведения аудита.")
        return

    await update.message.reply_markdown("📄 *PDF-документ получен! Запущен аудит по стандартам AAOIFI и Корана...*")
    
    try:
        file = await context.bot.get_file(doc.file_id)
        pdf_bytes = await file.download_as_bytearray()
        
        audit = PDFDocumentProcessor.audit_document(bytes(pdf_bytes), guard, HalalKnowledgeBase)
        
        g_rep = audit["guard_report"]
        a_rep = audit["aaoifi_report"]
        
        msg_lines = [
            f"📑 *ОФИЦИАЛЬНЫЙ АУДИТОРСКИЙ ОТЧЕТ AL-FURQAN AI*\n",
            f"• *Файл:* `{doc.file_name}`",
            f"• *Количество страниц:* {audit['total_pages']}",
            f"• *Символов проанализировано:* {audit['text_length']:,}\n"
        ]
        
        # 1. Результат проверки цитат Корана
        if g_rep["claims_detected"]:
            if g_rep["is_valid"]:
                msg_lines.append("✅ *Цитаты Корана:* 100% достоверны (Канонический Tanzil L0).")
            else:
                msg_lines.append(f"🚨 *Цитаты Корана:* ОБНАРУЖЕНО {len(g_rep['violations'])} ИСКАЖЕНИЙ/ОШИБОК!")
        else:
            msg_lines.append("ℹ️ *Цитаты Корана:* Прямых аятов в документе не обнаружено.")

        # 2. Результат аудита AAOIFI
        if a_rep["is_compliant"]:
            msg_lines.append("✅ *Финансовый аудит AAOIFI:* Соответствует исламским стандартам.")
        else:
            msg_lines.append("❌ *Финансовый аудит AAOIFI:* Обнаружены несоответствия (Риба/Штрафы)!")
            if a_rep.get("findings"):
                for f in a_rep["findings"][:3]:
                    msg_lines.append(f"  • ⚠️ _{f['standard']}: {f.get('issue_ru')}_")

        msg_lines.append("\n🛡️ _Детерминированный аудит Al-Furqan Guard с криптографической верификацией._")
        await update.message.reply_markdown("\n".join(msg_lines))
    except Exception as e:
        await update.message.reply_markdown(f"❌ Ошибка аудита PDF: {str(e)}")

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Расчет точного времени 5 намазов и Киблы по геолокации."""
    loc = update.message.location
    lat = loc.latitude
    lon = loc.longitude
    
    # 1. Время намаза
    times = PrayerTimesCalculator.calculate_prayer_times(lat, lon)
    
    # 2. Направление Киблы
    qibla_deg, compass = PrayerTimesCalculator.calculate_qibla(lat, lon)
    
    msg = (
        f"🕌 *РАСПИСАНИЕ НАМАЗА И НАПРАВЛЕНИЕ КИБЛЫ*\n"
        f"📍 Координаты: `{lat:.4f}° N, {lon:.4f}° E`\n\n"
        f"• 🌅 *Фаджр (Таң):* `{times['fajr']}`\n"
        f"• ☀️ *Восход (Күн):* `{times['sunrise']}`\n"
        f"• 🏙️ *Зухр (Бесін):* `{times['dhuhr']}`\n"
        f"• 🌇 *Аср (Екінті):* `{times['asr']}`\n"
        f"• 🌆 *Магриб (Ақшам):* `{times['maghrib']}`\n"
        f"• 🌌 *Иша (Құптан):* `{times['isha']}`\n\n"
        f"🧭 *Направление на Каабу (Кибла):* `{qibla_deg}°` ({compass})\n"
        f"🕋 _Повернитесь на угол {qibla_deg}° по компасу._"
    )
    await update.message.reply_markdown(msg)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка голосовых сообщений."""
    await update.message.reply_markdown(
        "🎙️ *Голосовое сообщение получено!*\n\n"
        "Вы можете назвать голосом или написать тему (например: *терпение*, *родители*, *торговля*, *пост*), номер суры (например: *36*) или прислать фото этикетки товара 📸!"
    )

# =========================================================================
# УМНЫЙ АВТО-АНАЛИЗ ТЕКСТОВ
# =========================================================================

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Автоматическая проверка любого входящего текста на галлюцинации, темы и халяль, а также обработка кнопок главного меню."""
    text = update.message.text.strip()
    if not text:
        return

    lang = get_user_lang(update.effective_user.id)

    # 0. Обработка кнопок постоянного меню (ReplyKeyboardMarkup)
    if text in ["📖 Читать Коран", "📖 Құран оқу", "📖 Read Quran"]:
        await send_surah_catalog(update, context, page=1)
        return

    # 0.1 Автоматическое распознавание номера суры (например: 36, 112, 1, 114, "сура 36", "сүре 2")
    cleaned_num_text = text.lower().replace("сура", "").replace("сүре", "").replace("surah", "").replace("sura", "").strip()
    if cleaned_num_text.isdigit():
        val = int(cleaned_num_text)
        if 1 <= val <= 114:
            await send_surah_paginated(update, context, sura=val, page=1)
            return

    # 0.2 Автоматическое распознавание штрихкода товара (8–14 цифр)
    clean_digits = re.sub(r"\D", "", text)
    if 8 <= len(clean_digits) <= 14 and clean_digits == text:
        await update.message.reply_markdown(f"🔍 *Поиск товара по штрихкоду:* `{clean_digits}`...")
        try:
            from database import OpenFoodFactsService, HalalProductCache
            cached = HalalProductCache.get_by_barcode(clean_digits)
            if not cached:
                cached = await OpenFoodFactsService.fetch_product_by_barcode(clean_digits)
                if cached:
                    HalalProductCache.save_product(cached)
            
            if cached and cached.get("name"):
                analysis = HalalKnowledgeBase.analyze_ingredients_deep(
                    cached.get("ingredients_text", ""),
                    cached.get("additives_tags", [])
                )
                v = analysis["verdict"]
                badge = "🟢 *ХАЛЯЛЬ (ДОЗВОЛЕНО)*" if v == "HALAL" else ("🔴 *ХАРАМ (ЗАПРЕТНО)*" if v == "HARAM" else "🟡 *КҮМӘНДІ / ТРЕБУЕТ ПРОВЕРКИ*")
                brand_str = f" ({cached.get('brand')})" if cached.get('brand') else ""
                ing_str = f"\n\n📝 *Состав:* {cached.get('ingredients_text', '')[:350]}" if cached.get('ingredients_text') else ""
                msg = (
                    f"{badge}\n\n"
                    f"📦 *Товар:* {cached.get('name')}{brand_str}\n"
                    f"🔢 *Штрихкод:* `{clean_digits}`{ing_str}\n\n"
                    f"ℹ️ *Заключение:* {analysis['summary_ru']}\n\n"
                    f"🛡️ _База Open Food Facts (2,5 млн товаров) • Al-Furqan Guard_"
                )
                await update.message.reply_markdown(msg)
                return
            else:
                await update.message.reply_markdown(f"📦 *Штрихкод:* `{clean_digits}` не найден в базе Open Food Facts. Отправьте фото состава товара на этикетке 📸!")
                return
        except Exception as e:
            await update.message.reply_markdown(f"❌ Ошибка проверки штрихкода: {str(e)}")
            return

    elif text in ["🥗 Халяль сканер", "🥗 Халал сүзгісі", "🥗 Halal Scanner"]:
        await update.message.reply_markdown(
            "🥗 *Халяль / Харам Скринер состава продуктов*\n\n"
            "• Напишите название продукта или E-код (например, `E471`, `Кармин`, `Желатин`, `Свинина`)\n"
            "• Или сфотографируйте этикетку/состав камерой и отправьте фото в чат 📸!"
        )
        return
    elif text in ["🕋 Намаз и Кибла", "🕋 Намаз және Құбыла", "🕋 Prayer & Qibla"]:
        await update.message.reply_markdown(
            "🕋 *Астрономическое расписание Намаза и компас Киблы*\n\n"
            "Нажмите на иконку скрепки 📎 в Telegram → выберите **Геопозиция (Location)** и отправьте боту для расчета точного времени 5 намазов и азимута на Каабу!"
        )
        return
    elif text in ["ℹ️ Как пользоваться", "ℹ️ Қалай қолдану керек", "ℹ️ How to Use"]:
        await help_command(update, context)
        return

    # 1. Проверка цитат Корана через Anti-Hallucination Guardrail
    audit_report = guard.verify_full_text(text)
    
    if audit_report["claims_detected"]:
        if not audit_report["is_valid"]:
            err_msg = (
                "🚨 *ВНИМАНИЕ: ОБНАРУЖЕНА ОШИБКА / ГАЛЛЮЦИНАЦИЯ В ЦИТАТЕ!*\n\n"
                f"❌ *Количество нарушений:* {len(audit_report['violations'])}\n\n"
            )
            for v in audit_report["violations"]:
                err_msg += f"• ⚠️ *{v.get('type')}:* {v.get('details')}\n"
            err_msg += "\n🛡️ _Al-Furqan Guard предотвратил распространение искаженного текста Корана._"
            await update.message.reply_markdown(err_msg)
            return
        else:
            ok_msg = (
                "✅ *ЦИТАТА ИЗ КОРАНА УСПЕШНО ВЕРИФИЦИРОВАНА (100% CANONICAL)*\n\n"
                "Все номера аятов, канонический текст и огласовки (ташкиль) полностью соответствуют Ground Truth Tanzil."
            )
            await update.message.reply_markdown(ok_msg)
            return

    # 2. Проверка на Халяль-ингредиенты
    halal_matches = HalalKnowledgeBase.match_input(text)
    if halal_matches:
        for m in halal_matches:
            is_haram = m["verdict"] == "HARAM"
            icon = "🔴" if is_haram else "🟡"
            title = m.get(f"title_{lang}") or m.get("title_ru")
            desc = m.get(f"description_{lang}") or m.get("description_ru")
            await update.message.reply_markdown(
                f"{icon} *{title}*\n\n{desc}\n\n📖 *Основа:* {m.get('ayah_ref', '')}"
            )
        return

    # 3. Тематический поиск, если текст похож на вопрос
    theme_results = SemanticThemeEngine.find_ayahs_by_topic(text, engine)
    if theme_results:
        msg_lines = [f"🔍 *Аяты Корана по вашему запросу:*\n"]
        for r in theme_results[:3]:
            sura_name = engine.SURAH_NAMES.get(lang, engine.SURAH_NAMES["ru"])[r["sura"] - 1]
            trans = r.get("translations", {}).get(lang) or r.get("translations", {}).get("ru") or ""
            msg_lines.append(f"📖 *{sura_name} [{r['sura']}:{r['ayah']}]*")
            msg_lines.append(f"*{r['text_uthmani']}*")
            if trans:
                msg_lines.append(f"_{trans}_")
            msg_lines.append("")
        await update.message.reply_markdown("\n".join(msg_lines))
        return

    # 4. Общая подсказка
    await update.message.reply_markdown(
        "💡 *Сообщение получено.*\n\n"
        "Отправьте цитату из Корана для проверки, фото состава продукта, PDF-документ или воспользуйтесь меню `/help`."
    )

# =========================================================================
# ОБРАБОТЧИК КНОПОК
# =========================================================================

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = update.effective_user.id

    if data == "noop":
        return
    elif data.startswith("surah_page_"):
        parts = data.split("_")
        sura_num = int(parts[2])
        page_num = int(parts[3])
        await send_surah_paginated(update, context, sura=sura_num, page=page_num, edit=True)
    elif data.startswith("open_surah_"):
        sura_num = int(data.split("_")[2])
        await send_surah_paginated(update, context, sura=sura_num, page=1, edit=True)
    elif data.startswith("cmd_surah_catalog_"):
        cat_page = int(data.split("_")[3])
        await send_surah_catalog(update, context, page=cat_page, edit=True)
    elif data in ["cmd_fatiha", "cmd_quran_catalog"]:
        await send_surah_catalog(update, context, page=1, edit=False)
    elif data == "cmd_halal_menu":
        await query.message.reply_markdown(
            "🥗 *Халяль / Харам Скринер*\n\n"
            "Напишите `/halal <продукт>` или сфотографируйте этикетку/состав и отправьте в чат!"
        )
    elif data == "cmd_namaz_prompt":
        await query.message.reply_markdown(
            "📍 *Расписание Намаза и Кибла*\n\n"
            "Нажмите на иконку скрепки 📎 в Telegram $\\rightarrow$ выберите **Геопозиция (Location)** и отправьте боту!"
        )
    elif data == "cmd_zakat_calc":
        res = ZakatCalculator.calculate_zakat(cash_savings=1000000)
        await query.message.reply_markdown(
            "💰 *Калькулятор Закята*\n\n"
            "Напишите команду `/zakat <сумма>`, например:\n"
            "• `/zakat 1000000` (Закят с 1 млн сбережений)\n\n"
            f"Порог Нисаба: ~{res['gold_nisab_threshold']:,.0f} ₸"
        )
    elif data == "cmd_roots_menu":
        await query.message.reply_markdown(
            "🧬 *Анализатор 1 651 корня*\n\n"
            "Напишите команду `/root <корень>`, например:\n"
            "• `/root صبر` (терпение)\n"
            "• `/root رحم` (милость)"
        )
    elif data == "cmd_search_menu":
        await query.message.reply_markdown(
            "🔍 *Поиск по темам Корана*\n\n"
            "Напишите `/search <тема>`, например:\n"
            "• `/search родители`\n"
            "• `/search торговля`\n"
            "• `/search терпение`"
        )
    elif data == "cmd_reciter_menu":
        keyboard = [
            [
                InlineKeyboardButton("🎙️ Мишари Рашид Аль-Афаси", callback_data="set_reciter_alafasy"),
            ],
            [
                InlineKeyboardButton("🎙️ Махмуд Халиль Аль-Хусари", callback_data="set_reciter_husary"),
            ],
            [
                InlineKeyboardButton("🎙️ Абдульбасит Абдуссамад", callback_data="set_reciter_abdulbasit")
            ]
        ]
        await query.message.reply_markdown(
            "🎙️ *Выберите чтеца Корана по умолчанию:*",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif data.startswith("set_reciter_"):
        new_reciter = data.replace("set_reciter_", "")
        USER_RECITERS[user_id] = new_reciter
        names = {
            "alafasy": "Мишари Рашид Аль-Афаси",
            "husary": "Махмуд Халиль Аль-Хусари",
            "abdulbasit": "Абдульбасит Абдуссамад"
        }
        await query.message.reply_markdown(f"✅ Чтец изменен на *{names.get(new_reciter)}*!")
    elif data == "cmd_lang_menu":
        keyboard = [
            [
                InlineKeyboardButton("🇰🇿 Қазақша", callback_data="set_lang_kk"),
                InlineKeyboardButton("🇷🇺 Русский", callback_data="set_lang_ru"),
                InlineKeyboardButton("🇬🇧 English", callback_data="set_lang_en")
            ]
        ]
        await query.message.reply_markdown(
            "🌐 *Выберите язык интерфейса:*",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif data.startswith("set_lang_"):
        new_lang = data.replace("set_lang_", "")
        USER_LANGS[user_id] = new_lang
        lang_names = {"kk": "Қазақша", "ru": "Русский", "en": "English"}
        await query.message.reply_markdown(
            f"✅ Язык изменен на *{lang_names.get(new_lang, new_lang)}*!",
            reply_markup=get_main_keyboard(new_lang)
        )

# =========================================================================
# ТОЧКА ВХОДА
# =========================================================================

def create_bot_app(token: str):
    """Factory to build configured Telegram Application instance."""
    app = ApplicationBuilder().token(token).build()

    # Регистрация команд
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("fatiha", fatiha_command))
    app.add_handler(CommandHandler(["quran", "surahs"], lambda u, c: send_surah_catalog(u, c, page=1)))
    app.add_handler(CommandHandler("ayah", ayah_command))
    app.add_handler(CommandHandler("surah", surah_command))
    app.add_handler(CommandHandler("halal", halal_command))
    app.add_handler(CommandHandler("root", root_command))
    app.add_handler(CommandHandler("search", search_command))
    app.add_handler(CommandHandler("zakat", zakat_command))

    
    # Мультимодальные обработчики: Фото, Документы (PDF), Геолокация, Голос
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    
    # Кнопки
    app.add_handler(CallbackQueryHandler(handle_callback_query))
    
    # Текстовые сообщения
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

    return app

def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token and os.path.exists("bot_config.json"):
        try:
            with open("bot_config.json", "r", encoding="utf-8") as f:
                cfg = json.load(f)
                token = cfg.get("telegram_bot_token")
        except Exception:
            pass

    if not token:
        print("\n" + "="*70)
        print("⚠️  TELEGRAM_BOT_TOKEN НЕ НАЙДЕН!")
        print("="*70)
        print("1. Получите токен у @BotFather в Telegram")
        print('2. Сохраните в bot_config.json: {"telegram_bot_token": "ВАШ_ТОКЕН"}')
        print("="*70 + "\n")
        return

    import asyncio
    import time
    from telegram.error import Conflict, NetworkError, TelegramError

    retry_delay = 5
    while True:
        try:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            print("🚀 Запуск Al-Furqan Guard Multi-Modal Telegram Bot (Polling mode)...")
            app = create_bot_app(token)

            print("✅ Мультимодальный бот Al-Furqan Guard успешно запущен и слушает события Telegram!")
            # drop_pending_updates=True drops stale updates / webhook remnants
            app.run_polling(drop_pending_updates=True, stop_signals=None, close_loop=False)
            break
        except Conflict as e:
            print(f"[Telegram Bot] ⚠️ Conflict detected (another instance/deploy is running): {e}")
            print(f"[Telegram Bot] Waiting {retry_delay}s before taking over polling...")
            time.sleep(retry_delay)
            retry_delay = min(retry_delay + 5, 30)
        except (NetworkError, TelegramError) as e:
            print(f"[Telegram Bot] ⚠️ Network / Telegram error: {e}. Reconnecting in 5s...")
            time.sleep(5)
        except Exception as e:
            print(f"[Telegram Bot] ⚠️ Unexpected bot error: {e}. Reconnecting in 10s...")
            time.sleep(10)

if __name__ == "__main__":
    main()



