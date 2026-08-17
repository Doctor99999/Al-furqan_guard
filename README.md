# 🌟 Al-Furqan AI (الفُرقَان) v2.0
> **Deterministic L0 Ground Truth, Anti-Hallucination Guardrail & Multi-Modal Islamic Intelligence Platform**

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Quran Ground Truth](https://img.shields.io/badge/Quran%20Verses-6%2C236%20Ayahs-10B981.svg)](#)
[![Roots Coverage](https://img.shields.io/badge/Morphological%20Roots-1%2C651%20Roots-F59E0B.svg)](#)
[![AAOIFI Standard](https://img.shields.io/badge/Islamic%20Finance-AAOIFI%20Compliant-38BDF8.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 Обзор проекта

**Al-Furqan AI** — это детерминированная система канонической верификации священного текста Корана, защиты больших языковых моделей (LLM) от галлюцинаций, шариатского аудита исламских финансовых договоров (AAOIFI) и скрининга продуктов на Халяль/Харам.

Система работает по принципу **O(1) Ground Truth**, используя хэш-индексированный манифест Tanzil Uthmani (6 236 аятов, 130 030 токенов и 1 651 семантический корень).

---

## 🚀 Ключевые возможности

1. **📖 Чтение и прослушивание Корана (114 Сур • 6 236 Аятов):**
   - Канонический шрифт Uthmani с полным ташхилем.
   - Фонетическая латинская транслитерация каждого аята.
   - Параллельные смысловые переводы на 7 языках (*Қазақша, Русский, English, العربية, Türkçe, O‘zbekcha, Bahasa Indonesia*).
   - Аудио-потоковое воспроизведение 3 всемирно известных чтецов (*Мишари Рашид Аль-Афаси, Махмуд Халиль Аль-Хусари, Абдульбасит Абдуссамад*).

2. **🛡️ L0 Anti-Hallucination Guardrail:**
   - Выявление выдуманных аятов и ложных номеров сур в ответах ChatGPT, Claude, Gemini.
   - Проверка огласовок (ташкиль) и канонической орфографии.

3. **🥗 Халяль / Харам Скринер & OCR:**
   - Автоматический скрининг пищевых добавок (E-коды: *E120, E441, E471* и др.).
   - Распознавание состава продуктов по фотографии (OCR).

4. **📄 PDF-Аудитор договоров (AAOIFI):**
   - Загрузка PDF-файлов (кредиты, ипотеки, Мурабаха, Иджара).
   - Выявление запрещенных процентов (*Риба*), скрытых комиссий и штрафов за просрочку.

5. **📍 Время намаза и компас Киблы:**
   - Астрономический расчет 5 обязательных молитв и угла Киблы на Каабу.

6. **💰 Шариатский калькулятор Закята:**
   - Автоматический расчет Нисаба (85г золота) и 2.5% обязательного закята.

7. **✈️ Telegram-бот [@alfurqan_quran_bot](https://t.me/alfurqan_quran_bot):**
   - Доступ ко всем функциям через Telegram.

---

## 🛠️ Быстрый запуск на Render.com

### Шаг 1: Загрузите репозиторий на GitHub
```bash
git init
git add .
git commit -m "feat: initial release of Al-Furqan AI v2.0"
git branch -M main
git remote add origin https://github.com/ВАШ_АККАУНТ/al-furqan-ai.git
git push -u origin main
```

### Шаг 2: Создайте Web Service на Render
1. Перейдите на [dashboard.render.com](https://dashboard.render.com) и нажмите **New + $\rightarrow$ Web Service**.
2. Подключите ваш GitHub-репозиторий `al-furqan-ai`.
3. Настройки сервиса:
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python start_all.py`
4. В разделе **Environment Variables** добавьте:
   - `TELEGRAM_BOT_TOKEN` = `ВАШ_ТОКЕН_ОТ_BOTFATHER` (для работы бота)
   - `PORT` = `8000`
5. Нажмите **Create Web Service**. Сервис автоматически соберется и запустится!

---

## 💻 Локальный запуск

```bash
# 1. Клонирование
git clone https://github.com/YOUR_USER/al-furqan-ai.git
cd al-furqan-ai

# 2. Установка зависимостей
pip install -r requirements.txt

# 3. Запуск веб-сервера
python server.py

# 4. Запуск Telegram-бота (в отдельном окне)
$env:TELEGRAM_BOT_TOKEN="ВАШ_ТОКЕН" ; python bot.py
```

Откройте веб-приложение: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 🔒 Безопасность и Стандарты

* **Криптографический хэш манифеста:** SHA-256 Verified.
* **Соответствие стандартам:** ISO/IEC 42001 (AI Management), ISO/IEC 27001, SMIIC OIC/SMIIC 1:2019, AAOIFI Shariah Standards (No. 8, 9, 21).

---

## 📜 Лицензия
MIT License. Сделано с открытым исходным кодом во благо уммы.
