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

## 🛠️ Быстрый запуск на Render.com (боевой режим)

### Шаг 1: Загрузите репозиторий на GitHub
```bash
git init
git add .
git commit -m "feat: initial release of Al-Furqan AI v2.0"
git branch -M main
git remote add origin https://github.com/ВАШ_АККАУНТ/al-furqan-ai.git
git push -u origin main
```

### Шаг 2: Blueprint-деплой (рекомендуется)
В репозитории лежит `render.yaml` — Blueprint для боевого запуска:

1. На [dashboard.render.com](https://dashboard.render.com) → **New + → Blueprint**.
2. Подключите репозиторий. Render сам создаст Web Service `al-furqan-guard`:
   - **Runtime:** Docker (`./Dockerfile`, включая Tesseract OCR rus/kaz/ara/eng)
   - **Health check:** `/api/v1/health`
   - **Disk 1GB** смонтирован в `/app/data` (переживает деплой и рестарты)
   - **План `starter` (платный)** — обязателен, т.к. только платные планы дают Disk.
3. В разделе **Environment** заполните секреты, отмеченные `sync:false`
   (значения появятся как плейсхолдеры):
   - `TELEGRAM_BOT_TOKEN` — токен бота от @BotFather
   - `TELEGRAM_WEBHOOK_SECRET` — **фиксированный** секрет вебхука
   - `TELEGRAM_ADMIN_CHAT_ID` — chat ID для уведомлений об отзывах
   - `ADMIN_API_KEY` — ключ для `GET /api/v1/feedback/list` (заголовок `X-Admin-Key`)
   - `IP_HASH_SECRET` — **фиксированная** соль анонимизации IP
4. Нажмите **Apply**. Автодеплой на каждую пуст.
   `RENDER_EXTERNAL_URL` подставляется автоматически → Telegram работает через Webhook.

> ⚠️ **Причины задавать фиксированные `TELEGRAM_WEBHOOK_SECRET` и `IP_HASH_SECRET`:**
> при пустых значениях они генерируются заново на каждый старт — деплой будет
> ротировать секрет Telegram-вебхука и «забывать» уникальные посетители в аналитике.

### Шаг 3: Локальный запуск в Docker (тем же образом, что на проде)
```bash
docker build -t al-furqan .
# персистентность runtime-состояния через volume
docker run -d -p 8000:8000 -e TELEGRAM_BOT_TOKEN=... \
  -v al-furqan-data:/app/data al-furqan
```

---

## 💻 Локальный запуск

```bash
# 1. Клонирование
git clone https://github.com/YOUR_USER/al-furqan-ai.git
cd al-furqan-ai

# 2. Установка зависимостей (Python 3.11+)
pip install -r requirements-dev.txt -c requirements.lock

# 3. Настройка окружения
copy .env.example .env   # и заполните TELEGRAM_*/ADMIN_API_KEY

# 4. Запуск веб-сервера
python server.py
```

Откройте веб-приложение: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 🌐 Переменные окружения (полный список)

| Переменная | Обязательность | Описание |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | боевой | Токен Telegram-бота |
| `TELEGRAM_WEBHOOK_SECRET` | боевой (фикс.) | Секрет вебхука Telegram |
| `ADMIN_API_KEY` | боевой | Ключ чтения отзывов (`X-Admin-Key`) |
| `IP_HASH_SECRET` | боевой (фикс.) | Соль хэширования client IP |
| `TELEGRAM_ADMIN_CHAT_ID` | опц. | Уведомления о новых отзывах |
| `RUNTIME_DATA_DIR` | опц. | Каталог runtime-состояния (SQLite, ключи B2B, отзывы). По умолчанию `<repo>/data`; на Render — путь к смонтированному диску |
| `DATABASE_URL` | опц. | PostgreSQL для аналитики (иначе SQLite в `RUNTIME_DATA_DIR`) |
| `B2B_DEMO_API_KEY` | опц. | При задании сидится демо-партнёр B2B (SHA-256 в БД). **Пусто = бэкдора нет** |
| `CORS_ORIGINS` | опц. | Разрешённые browser-origin через запятую; пусто = same-origin |
| `TRUST_PROXY_HEADERS` | опц. | `1` — доверять `X-Forwarded-For` (на Render авто) |
| `LOG_LEVEL` | опц. | `INFO` / `DEBUG` |
| `PORT` / `HOST` | опц. | Bind сервера (Render задаёт `PORT`) |

Полное описание: файл `.env.example`.

---

## 🔒 Безопасность и Стандарты

* **Криптографический хэш манифеста:** SHA-256 Verified.
* **Соответствие стандартам:** ISO/IEC 42001 (AI Management), ISO/IEC 27001, SMIIC OIC/SMIIC 1:2019, AAOIFI Shariah Standards (No. 8, 9, 21).

---

## 📜 Лицензия
MIT License. Сделано с открытым исходным кодом во благо уммы.
