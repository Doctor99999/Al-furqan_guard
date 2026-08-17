"""
Al-Furqan AI — Official Telegram Bot Guardrail
Deterministic Anti-Hallucination & Halal Knowledge Engine for Telegram.
"""

import os
import sys
import asyncio
from typing import Optional

from quran_guard import QuranEngine, QuranGuard
from quran_guard.halal_knowledge_base import HalalKnowledgeBase
from quran_guard.config import MANIFEST_PATH, TRANSLATIONS_PATH

# Initialize Core Engine
print("Initializing Al-Furqan AI for Telegram Bot...")
engine = QuranEngine(manifest_path=MANIFEST_PATH, translations_path=TRANSLATIONS_PATH)
guard = QuranGuard(engine)

HELP_TEXT = """
🤖 *Al-Furqan AI — Құран және Халал сүзгісі боты*

*Қолжетімді командалар:*
• `/verify <мәтін>` — Мәтінді Құран аяттары бойынша галлюцинацияға тексеру
• `/halal <тағам / E-код>` — Тағамды, E-қоспаны немесе келісімді Халал/Харамға тексеру
• `/root <түбір>` — 3/4-әріптік түбір бойынша барлық аяттарды іздеу (мыс: `رحم`, `علم`, `عدл`)
• `/ayah <сүре:аят>` — Аяттың каноникалық мәтіні мен тәпсірін алу (мыс: `5:3`, `2:275`)
• `/stats` — Коран манифесінің деректер статистикасы (6 236 аят, 130 030 таңба)
"""

def handle_text_message(text: str) -> str:
    """Processes incoming text and returns deterministic Shariah & Halal verdict."""
    text_clean = text.strip()
    
    if text_clean.startswith("/start") or text_clean.startswith("/help"):
        return HELP_TEXT

    if text_clean.startswith("/verify"):
        query = text_clean.replace("/verify", "").strip()
        if not query:
            return "⚠️ Тексеретін мәтінді енгізіңіз. Мысалы:\n`/verify Құранда 114-сүре 1-аятта: ...`"
        report = guard.verify_full_text(query)
        verdict = report.get("verdict", "UNKNOWN")
        icon = "🟢" if verdict == "CLEAN" else ("🔴" if verdict == "HALLUCINATION_DETECTED" else "🟠")
        
        lines = [f"{icon} *L0 Аудит нәтижесі:* `{verdict}`\n"]
        for quote in report.get("quotes", []):
            lines.append(f"📌 *Дәйексөз:* «{quote.get('raw_quote_text', '')}»")
            if quote.get("status") == "CANONICAL_MATCH":
                lines.append(f"✅ *Каноникалық сәйкестік:* {quote.get('sura')}:{quote.get('ayah')}")
                lines.append(f"📖 *Түпнұсқа:* `{quote.get('canonical_text')}`")
            elif quote.get("status") == "INVALID_COORDINATE":
                lines.append("❌ *Қате координат:* Аталған сүреде мұндай аят жоқ!")
            elif quote.get("status") == "TASHKEEL_DISTORTION":
                lines.append("⚠️ *Харакаттар бұрмаланған!* Дұрыс нұсқасы:")
                lines.append(f"`{quote.get('canonical_text')}`")
        return "\n".join(lines)

    if text_clean.startswith("/halal"):
        query = text_clean.replace("/halal", "").strip()
        if not query:
            return "⚠️ Тексеретін тағам атауын немесе E-кодты енгізіңіз. Мысалы:\n`/halal Кармин E120` немесе `/halal Семга`"
        matches = HalalKnowledgeBase.match_input(query)
        if not matches:
            return f"ℹ️ «{query}» бойынша тікелей тыйымдар табылмады (Күмәнді қоспаларды тексеру ұсынылады)."
        
        lines = [f"🥗 *Халал / Шариғат сараптамасы («{query}»):*\n"]
        for m in matches:
            icon = "🔴" if m["verdict"] == "HARAM" else ("🟡" if m["verdict"] == "DOUBTFUL" else "🟢")
            lines.append(f"{icon} *{m['title_kk']}*")
            lines.append(f"📝 {m['description_kk']}")
            lines.append(f"📖 *Құрандағы негіз:* {m['ayah_ref']} — `{m['canonical_arabic']}`\n")
        return "\n".join(lines)

    if text_clean.startswith("/ayah"):
        query = text_clean.replace("/ayah", "").strip()
        try:
            s_str, a_str = query.split(":")
            s, a = int(s_str), int(a_str)
            data = engine.get_ayah(s, a)
            if not data:
                return f"❌ Аят табылмады: {s}:{a}"
            s_pad, a_pad = f"{s:03d}", f"{a:03d}"
            audio_url = f"https://everyayah.com/data/Alafasy_128kbps/{s_pad}{a_pad}.mp3"
            return (
                f"📖 *Құран Кәрім [{s}:{a}]*\n\n"
                f"*{data['text_uthmani']}*\n\n"
                f"🔊 *Тыңдау:* {audio_url}"
            )
        except Exception:
            return "⚠️ Формат қате! Сүре мен аятты `5:3` немесе `2:275` түрінде жазыңыз."

    # Default fallback to Halal & Guard screening
    matches = HalalKnowledgeBase.match_input(text_clean)
    if matches:
        return handle_text_message(f"/halal {text_clean}")
    return HELP_TEXT

if __name__ == "__main__":
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("ℹ️ TELEGRAM_BOT_TOKEN not set in environment. Running offline demo loop...")
        print("Type a message to test bot responses (e.g. '/halal E120' or '/verify 114:1'):")
        while True:
            try:
                user_msg = input("\nUser: ")
                if not user_msg:
                    break
                print("\nBot Response:\n" + handle_text_message(user_msg))
            except (KeyboardInterrupt, EOFError):
                break
    else:
        print(f"🚀 Starting Al-Furqan AI Telegram Bot with token {token[:6]}...")
        # Production aiogram / telebot runner can be attached here
