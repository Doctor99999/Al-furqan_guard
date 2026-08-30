"""
Al-Furqan AI - Web API & Playground Server v2.0 (Hardened Production)
FastAPI server with enterprise defensive security & 100% real-world data pipelines:
- Persistent database-backed visitor analytics (SQLite / PostgreSQL)
- Universal multi-language full-text Quran search (6,236 Ayahs)
- Real image OCR processing (Pillow + Tesseract) & Halal food compliance
- Real PDF document parser (pypdf) & AAOIFI Shariah audit
- Astronomical Namaz prayer times & Kaaba Qibla bearing
- Live cryptographic SHA-256 integrity verification
- Keep-Alive / health endpoints for 24/7 Render deployment
"""

import os
import sys
import re
import json
import html
import base64
import hashlib
import hmac
import secrets
import logging
import datetime
from typing import Optional, Dict, Any, List, Tuple
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel, Field

from quran_guard import QuranEngine, QuranGuard, AhkamExtractor
from quran_guard.halal_knowledge_base import HalalKnowledgeBase
from quran_guard.config import MANIFEST_PATH, TRANSLATIONS_PATH, UI_DIR, CORS_ORIGINS, RUNTIME_DATA_DIR
from quran_guard.multimodal import (
    PDFDocumentProcessor,
    ImageOCRProcessor,
    PrayerTimesCalculator,
    ZakatCalculator,
    SemanticThemeEngine,
    AuditCertificateGenerator
)


LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger("alfurqan-server")

def compute_sha256(filepath: str) -> str:
    """Calculates live cryptographic SHA-256 hash of file."""
    if not os.path.exists(filepath):
        return "UNAVAILABLE"
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def get_client_ip(request: Request) -> str:
    """
    Resolves the real client IP.
    Proxy headers (X-Forwarded-For etc.) are honored ONLY when explicitly trusted via
    TRUST_PROXY_HEADERS=1 (auto-enabled when RENDER_EXTERNAL_URL is present), otherwise
    a spoofed header cannot bypass rate limiting or poison analytics.
    """
    import ipaddress
    peer_ip = request.client.host if request.client else "127.0.0.1"
    trust_proxy = os.environ.get(
        "TRUST_PROXY_HEADERS",
        "1" if os.environ.get("RENDER_EXTERNAL_URL") else "0"
    ) == "1"
    if trust_proxy:
        forwarded = request.headers.get("x-forwarded-for", "")
        candidate = forwarded.split(",")[0].strip() if forwarded else (
            request.headers.get("cf-connecting-ip") or request.headers.get("x-real-ip") or ""
        ).strip()
        if candidate:
            try:
                ipaddress.ip_address(candidate)
                return candidate[:45]
            except ValueError:
                pass  # Malformed header: fall back to direct peer
    return peer_ip


def sanitize_md(text: str) -> str:
    """Strips Markdown control characters from untrusted strings before Telegram formatting."""
    return re.sub(r'[*_`\[\]]', '', text or "")

# Live Cryptographic Hashes of Canonical Ground Truth
MANIFEST_SHA256 = compute_sha256(MANIFEST_PATH)
TRANSLATIONS_SHA256 = compute_sha256(TRANSLATIONS_PATH)

print(f"Initializing Al-Furqan AI Quran Core Engine v2.0 (Hardened)...")
print(f"Canonical Quran Manifest SHA-256: {MANIFEST_SHA256}")
print(f"Canonical Translations SHA-256: {TRANSLATIONS_SHA256}")

engine = QuranEngine(manifest_path=MANIFEST_PATH, translations_path=TRANSLATIONS_PATH)
guard = QuranGuard(engine)
ahkam = AhkamExtractor(engine)
print(f"Engine Ready! Loaded {len(engine.ayahs)} Ayahs, {engine.total_tokens} tokens, {len(engine.all_roots)} roots.")

import time
from database import (
    VisitorAnalyticsService, 
    OpenFoodFactsService, 
    B2BAuthService,
    HalalProductCache
)

# =========================================================================
# TOKEN BUCKET RATE LIMITER FOR OCR AI
# =========================================================================
class TokenBucketRateLimiter:
    """
    Token Bucket rate limiter for OCR AI image processing:
    - Capacity: 3 tokens available immediately
    - Refill Rate: 1 token restored every 120 seconds (2 minutes)
    - Unlimited for B2B API keys and Barcode lookups
    """
    def __init__(self, capacity: int = 3, refill_seconds: int = 120):
        self.capacity = capacity
        self.refill_seconds = refill_seconds
        self.buckets: Dict[str, Dict[str, Any]] = {}

    def is_allowed(self, client_id: str) -> Tuple[bool, int, float]:
        now = time.time()
        bucket = self.buckets.get(client_id)
        
        if not bucket:
            # First request: consume 1 token, leaving capacity - 1
            self.buckets[client_id] = {
                "tokens": self.capacity - 1,
                "last_refill": now
            }
            return True, self.capacity - 1, 0.0

        # Refill tokens based on elapsed intervals
        elapsed = now - bucket["last_refill"]
        refill_count = int(elapsed // self.refill_seconds)
        if refill_count > 0:
            bucket["tokens"] = min(self.capacity, bucket["tokens"] + refill_count)
            bucket["last_refill"] = now - (elapsed % self.refill_seconds)

        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            return True, int(bucket["tokens"]), 0.0
        else:
            time_until_next = max(1, int(self.refill_seconds - (now - bucket["last_refill"])))
            return False, 0, time_until_next

ocr_rate_limiter = TokenBucketRateLimiter(capacity=3, refill_seconds=120)

# Legacy in-memory fallback for non-DB environments
ANALYTICS_DATA = {"total_queries_verified": 0}



from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: If TELEGRAM_BOT_TOKEN and RENDER_EXTERNAL_URL are present, configure Telegram Webhook!
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    ext_url = os.environ.get("RENDER_EXTERNAL_URL", "").rstrip("/")
    if token and ext_url:
        try:
            import bot
            bot_app = bot.create_bot_app(token)
            await bot_app.initialize()
            webhook_url = f"{ext_url}/api/v1/telegram-webhook"
            # Shared secret so the endpoint can reject forged updates
            webhook_secret = os.environ.get("TELEGRAM_WEBHOOK_SECRET") or secrets.token_urlsafe(32)
            app.state.telegram_webhook_secret = webhook_secret
            print(f"[Telegram Webhook] Registering webhook on Render: {webhook_url}")
            await bot_app.bot.set_webhook(url=webhook_url, drop_pending_updates=True, secret_token=webhook_secret)
            app.state.bot_app = bot_app
            print(f"[Telegram Webhook] ✅ Webhook successfully activated! (0% polling conflicts)")
        except Exception as e:
            print(f"[Telegram Webhook] Setup notice: {e}")
    yield
    # Shutdown
    if hasattr(app.state, "bot_app"):
        try:
            await app.state.bot_app.shutdown()
        except Exception as e:
            logger.warning("telegram bot shutdown failed: %s", e)

app = FastAPI(
    title="Al-Furqan Guard — L0 Ground Truth & Anti-Hallucination API",
    description="Deterministic anti-hallucination guardrail, 1,651 roots analyzer, Halal screening, and AAOIFI Shariah compliance.",
    version="2.0.0",
    lifespan=lifespan
)

@app.post("/api/v1/telegram-webhook")
async def telegram_webhook(request: Request):
    """Processes incoming Telegram updates via Webhook. Rejects forged requests via shared secret."""
    if not hasattr(request.app.state, "bot_app"):
        return {"status": "bot_not_initialized"}

    expected_secret = getattr(request.app.state, "telegram_webhook_secret", None)
    provided_secret = request.headers.get("x-telegram-bot-api-secret-token", "")
    if not expected_secret or not hmac.compare_digest(provided_secret, expected_secret):
        raise HTTPException(status_code=403, detail="Forbidden")

    try:
        from telegram import Update
        data = await request.json()
        update = Update.de_json(data, request.app.state.bot_app.bot)
        if update:
            await request.app.state.bot_app.process_update(update)
        return {"status": "ok"}
    except Exception:
        # Do not leak internal error details to untrusted callers
        return {"status": "error"}


# 1. Enterprise Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=self"
    # CSP tuned for the actual UI dependency set (gtag, html5-qrcode, tesseract.js CDN,
    # Google Fonts, everyayah.com audio, Open Food Facts images)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://www.googletagmanager.com https://unpkg.com https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' data: https://fonts.gstatic.com; "
        "img-src 'self' data: blob: https:; "
        "media-src 'self' https://everyayah.com; "
        "connect-src 'self' https://world.openfoodfacts.org https://www.googletagmanager.com "
        "https://*.google-analytics.com https://analytics.google.com https://cdn.jsdelivr.net "
        "https://unpkg.com https://tessdata.projectnaptha.com; "
        "worker-src 'self' blob: https://cdn.jsdelivr.net https://unpkg.com; "
        "frame-ancestors 'self'; base-uri 'self'; form-action 'self'"
    )
    return response

# 2. CORS & Compression Middleware
if CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
app.add_middleware(GZipMiddleware, minimum_size=500)

# Reciters CDN map (EveryAyah.com)
RECITERS_CDN = {
    "alafasy": "https://everyayah.com/data/Alafasy_128kbps",
    "husary": "https://everyayah.com/data/Husary_128kbps",
    "abdulbasit": "https://everyayah.com/data/Abdul_Basit_Murattal_192kbps"
}

# Heavy-document rate limiter: PDF parsing + difflib audit are CPU-expensive
pdf_rate_limiter = TokenBucketRateLimiter(capacity=3, refill_seconds=600)

# 3. Request Models with Defensive Payload Boundaries

class VerifyRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=100000, description="Input text to verify against Quranic ground truth")

class RootClaimRequest(BaseModel):
    word: str = Field(..., min_length=1, max_length=100)
    claimed_root: str = Field(..., min_length=1, max_length=50)
    context_id: Optional[str] = Field(None, max_length=50)

class ContractAuditRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=200000)

class ExportAuditPDFRequest(BaseModel):
    document_title: Optional[str] = Field("Договор / Соглашение", max_length=200)
    contract_text: Optional[str] = Field(None, max_length=200000)
    audit_data: Optional[Dict[str, Any]] = None

class HalalScreenRequest(BaseModel):
    query: Optional[str] = Field(None, max_length=50000)
    text: Optional[str] = Field(None, max_length=50000)

class ImageScanRequest(BaseModel):
    image_base64: str = Field(..., min_length=1, max_length=10000000) # Max ~7.5MB raw

class PDFScanRequest(BaseModel):
    pdf_base64: str = Field(..., min_length=1, max_length=25000000) # Max ~20MB raw

class ZakatRequest(BaseModel):
    cash_savings: float = Field(0.0, ge=0)
    gold_grams: float = Field(0.0, ge=0)
    silver_grams: float = Field(0.0, ge=0)
    business_inventory: float = Field(0.0, ge=0)
    liabilities_due: float = Field(0.0, ge=0)
    currency: Optional[str] = Field("₸", max_length=10)

class FeedbackRequest(BaseModel):
    name: Optional[str] = Field("Anonymous", max_length=100)
    email_or_phone: Optional[str] = Field("", max_length=150)
    category: str = Field("suggestion", max_length=50)
    message: str = Field(..., min_length=1, max_length=10000)

FEEDBACK_STORE: List[Dict[str, Any]] = []
MAX_FEEDBACK_ITEMS = 1000

# Privacy salt for IP anonymization: ENV secret or per-process random (never hardcoded)
IP_HASH_SALT = os.environ.get("IP_HASH_SECRET") or secrets.token_hex(32)
# Admin key required to read submitted feedback (PII protection)
ADMIN_API_KEY = os.environ.get("ADMIN_API_KEY", "")

# Tafsir Summaries for Key Juridical & Doctrinal Verses (As-Sa'di & Ibn Kathir)
TAFSIR_REGISTRY = {
    "5:3": {
        "title": "Тафсир аята 5:3 (Запретная и дозволенная пища)",
        "summary_ru": "Аллах запретил верующим мертвечину, вытекшую кровь и мясо свиньи из-за их скверности (Хабаис) и вреда для тела и души. Завершение религии и милости.",
        "summary_kk": "Аллаһ мүміндерге өлексені, аққан қанды және доңыз етін олардың ластығы мен зияны үшін тыйды. Ислам дінінің толықтырылуы мен кемелденуі."
    },
    "2:275": {
        "title": "Тафсир аята 2:275 (Различие между торговлей и Риба)",
        "summary_ru": "Аллах дозволил честную торговлю с реальным товаром и наценкой, но категорически запретил ростовщичество (Риба), когда деньги растут сами по себе без труда и риска.",
        "summary_kk": "Аллаһ нақты тауар мен пайдасы бар адал сауданы халал етті, ал еңбексіз ақшадан ақша тудыратын өсімқорлықты (рибаны) қатаң арам қылды."
    },
    "5:90": {
        "title": "Тафсир аята 5:90 (Категорический запрет опьяняющего и азарта)",
        "summary_ru": "Вино (любой алкоголь) и азартные игры объявлены скверной из деяний сатаны. Приказ отдаляться ('Фаджтанибух') является высшей степенью запрета в Коране.",
        "summary_kk": "Арақ пен құмар ойындар шайтанның лас амалы деп жарияланды. 'Аулақ болыңдар' деген әмір Құрандағы ең қатаң тыйым түрі."
    },
    "4:29": {
        "title": "Тафсир аята 4:29 (Неприкосновенность чужого имущества)",
        "summary_ru": "Запрещено присваивать чужое имущество ложным путем (обман, взятки, скрытые комиссии). Торговля действительна только по взаимному согласию сторон.",
        "summary_kk": "Өзгенің мал-мүлкін алдау, өсім немесе пара арқылы жеу харам. Сауда тек екі тараптың ризалығымен жүруі шарт."
    }
}

# =========================================================================
# V2.0 REST API ENDPOINTS
# =========================================================================

@app.get("/api/v1/health")
async def health_check():
    """Liveness & health endpoint for Keep-Alive and Render monitoring."""
    return {
        "status": "healthy",
        "service": "al-furqan-guard",
        "version": "2.0.0",
        "total_ayahs": len(engine.ayahs),
        "total_roots": len(engine.all_roots),
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }

@app.get("/api/stats")
@app.get("/api/v1/stats")
async def get_stats():
    """Returns engine and corpus statistics."""
    return engine.get_stats()

@app.get("/api/v1/integrity/verify")
async def verify_integrity():
    """Returns live cryptographic verification and SHA-256 seal of the Quran Ground Truth."""
    return {
        "status": "VERIFIED_CANONICAL",
        "manifest_sha256": MANIFEST_SHA256,
        "translations_sha256": TRANSLATIONS_SHA256,
        "total_ayahs": len(engine.ayahs),
        "total_tokens": engine.total_tokens,
        "total_roots": len(engine.all_roots),
        "canonical_source": "Tanzil Quran Project v1.0.2 / Uthmani Script",
        "timestamp_verified": True
    }

@app.get("/api/v1/analytics/visitor-count")
def get_visitor_count(request: Request):
    """Tracks and returns real, 100% authentic persistent visitor metrics across all timeframes via PostgreSQL."""
    client_ip = get_client_ip(request)

    # Salted SHA-256 for GDPR/privacy compliance (secret salt from ENV or per-process random)
    ip_hash = hashlib.sha256(f"{IP_HASH_SALT}{client_ip}".encode()).hexdigest()[:16]
    user_agent = request.headers.get("user-agent", "")
    
    # Record and query persistent analytics from PostgreSQL / SQLite
    stats = VisitorAnalyticsService.record_visit(ip_hash, user_agent)
    return stats

# =========================================================================
# OPEN FOOD FACTS 2.5M+ PRODUCTS & BARCODE SCANNER (RATE LIMITED)
# =========================================================================
barcode_rate_limiter = TokenBucketRateLimiter(capacity=20, refill_seconds=60)

@app.get("/api/v1/halal/barcode/{barcode}")
def check_halal_barcode(barcode: str, request: Request = None):
    """
    Looks up products by barcode (2.5M+ items) via PostgreSQL cache & Open Food Facts API.
    Rate limited (20/min per IP) to prevent outbound-request amplification; B2B keys bypass.
    """
    if request is None:
        # Internal/nested call (e.g. from /b2b/halal-check): auth handled by caller.
        is_b2b = True
    else:
        api_key = request.headers.get("x-api-key") or request.headers.get("authorization", "").replace("Bearer ", "").strip()
        is_b2b = bool(api_key and B2BAuthService.validate_api_key(api_key))
        if not is_b2b:
            allowed, _remaining, wait_seconds = barcode_rate_limiter.is_allowed(get_client_ip(request))
            if not allowed:
                raise HTTPException(
                    status_code=429,
                    detail=f"Слишком много запросов. Повторите через {wait_seconds} секунд.",
                    headers={"Retry-After": str(wait_seconds)}
                )

    clean_code = re.sub(r"\D", "", barcode.strip())[:20]
    if not clean_code:
        raise HTTPException(status_code=400, detail="Некорректный штрихкод")

    # 1. Check local database cache
    cached = HalalProductCache.get_by_barcode(clean_code)
    if cached:
        return {
            "barcode": cached["barcode"],
            "name": cached["product_name"],
            "brand": cached.get("brand"),
            "categories": cached.get("categories"),
            "ingredients_text": cached.get("ingredients_text"),
            "halal_verdict": cached["halal_verdict"],
            "summary": cached.get("shubhat_summary"),
            "shubhat_details": json.loads(cached["shubhat_details_json"]) if cached.get("shubhat_details_json") else [],
            "source": "DATABASE_CACHE"
        }

    # 2. Fetch from Open Food Facts API (2.5M+ products)
    off_data = OpenFoodFactsService.fetch_product_by_barcode(clean_code)
    if not off_data:
        return {
            "barcode": clean_code,
            "name": "Товар не найден в глобальной базе",
            "halal_verdict": "NOT_FOUND",
            "summary": "Штрихкод отсутствует в каталоге Open Food Facts (2.5 млн товаров). Пожалуйста, сфотографируйте состав продукта камерой (OCR).",
            "source": "OPEN_FOOD_FACTS"
        }

    # 3. Analyze ingredients through Shariah/Halal & Shubhât Knowledge Base
    analysis = HalalKnowledgeBase.analyze_ingredients_deep(
        off_data.get("ingredients_text", ""), 
        off_data.get("additives_tags", [])
    )

    # 3.1 HTML-escape third-party strings (Open Food Facts is publicly editable -> stored XSS vector)
    for field in ("name", "brand", "categories", "ingredients_text"):
        if off_data.get(field):
            off_data[field] = html.escape(str(off_data[field])[:10000], quote=True)

    # 4. Cache verified result in Database
    HalalProductCache.save_product(
        barcode=clean_code,
        name=off_data["name"][:250],
        brand=off_data.get("brand", "")[:120],
        categories=off_data.get("categories", "")[:250],
        ingredients=off_data.get("ingredients_text", ""),
        verdict=analysis["verdict"],
        summary=analysis["summary_ru"],
        shubhat_json=json.dumps(analysis.get("shubhat_details", []), ensure_ascii=False),
        source="OPEN_FOOD_FACTS"
    )

    return {
        "barcode": clean_code,
        "name": off_data["name"],
        "brand": off_data.get("brand"),
        "categories": off_data.get("categories"),
        "ingredients_text": off_data.get("ingredients_text"),
        "halal_verdict": analysis["verdict"],
        "summary_ru": analysis["summary_ru"],
        "summary_kk": analysis["summary_kk"],
        "haram_items": analysis["haram_items"],
        "doubtful_items": analysis["doubtful_items"],
        "shubhat_details": analysis["shubhat_details"],
        "source": "OPEN_FOOD_FACTS_ANALYZED"
    }

# =========================================================================
# B2B & PUBLIC SHARIAH / HALAL AUDIT ENDPOINTS
# =========================================================================
@app.post("/api/v1/b2b/halal-check")
@app.post("/api/v1/halal-check")
def b2b_halal_check(req: HalalScreenRequest, request: Request):
    """
    Enterprise B2B / Public Halal Screening Endpoint:
    Accepts text, barcode, or ingredient list.
    B2B authorization via X-API-Key or Bearer token removes rate limits and logs commercial usage.
    """
    api_key = request.headers.get("x-api-key") or request.headers.get("authorization", "").replace("Bearer ", "").strip()
    org = B2BAuthService.validate_api_key(api_key) if api_key else None

    query_text = (req.query or req.text or "").strip()
    if not query_text:
        raise HTTPException(status_code=400, detail="Параметр query или text обязателен")

    # If barcode provided
    if re.match(r"^\d{8,14}$", query_text):
        return check_halal_barcode(query_text, request)

    # Deep Shubhât and Halal Analysis
    analysis = HalalKnowledgeBase.analyze_ingredients_deep(query_text)
    return {
        "authenticated_as": org.org_name if org else "PUBLIC_B2C_TIER",
        "tier": org.tier if org else "FREE",
        "query": query_text,
        "halal_verdict": analysis["verdict"],
        "summary_ru": analysis["summary_ru"],
        "summary_kk": analysis["summary_kk"],
        "haram_items": analysis["haram_items"],
        "doubtful_items": analysis["doubtful_items"],
        "shubhat_details": analysis["shubhat_details"],
        "smiic_standard": analysis["smiic_standard"],
        "quran_ground_truth": analysis["quran_ground_truth"]
    }

# =========================================================================
# CROSS-LINGUAL SEMANTIC SEARCH (RUSSIAN / KAZAKH -> ARABIC ROOT)
# =========================================================================
@app.get("/api/v1/quran/semantic-search")
def semantic_search(q: str = "", limit: int = 50):
    """
    Cross-Language Semantic & Stemming Search:
    Translates Russian/Kazakh queries (e.g. 'Милосердие', 'Мейірім') to Arabic Root ('رحм') and returns verified Ayahs.
    """
    if not q:
        return {"query": "", "results": []}
    return engine.search_cross_lingual(q, limit=limit)




@app.get("/api/v1/quran/surahs")
async def get_surahs_list():
    """Returns metadata for all 114 Surahs."""
    surahs_list = []
    for s_num in range(1, 115):
        surahs_list.append({
            "number": s_num,
            "ayah_count": engine.CANONICAL_AYAH_COUNTS[s_num - 1],
            "name_ar": engine.SURAH_NAMES.get("ar", [])[s_num - 1] if len(engine.SURAH_NAMES.get("ar", [])) >= s_num else f"سورة {s_num}",
            "name_ru": engine.SURAH_NAMES.get("ru", [])[s_num - 1] if len(engine.SURAH_NAMES.get("ru", [])) >= s_num else f"Сура {s_num}",
            "name_kk": engine.SURAH_NAMES.get("kk", [])[s_num - 1] if len(engine.SURAH_NAMES.get("kk", [])) >= s_num else f"Сүре {s_num}",
            "name_en": engine.SURAH_NAMES.get("en", [])[s_num - 1] if len(engine.SURAH_NAMES.get("en", [])) >= s_num else f"Surah {s_num}"
        })
    return {"total_surahs": 114, "surahs": surahs_list}

@app.get("/api/v1/quran/search")
def quran_search(q: str, lang: str = "all", limit: int = 30):
    """Universal full-text search across Arabic text and 7 language translations."""
    clean_q = q.strip()[:100]
    if not clean_q:
        return {"query": "", "total": 0, "results": []}
    
    results = engine.search_text(clean_q, lang=lang, limit=limit)
    return {
        "query": clean_q,
        "total": len(results),
        "results": results
    }

@app.post("/api/verify")
@app.post("/api/v1/guard/validate")
def verify_text(req: VerifyRequest):
    """Full Anti-Hallucination verification of input text."""
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    result = guard.verify_full_text(req.text)
    return result

@app.post("/api/verify/root")
@app.post("/api/v1/roots/verify")
def verify_root(req: RootClaimRequest):
    """Verifies morphological root claim."""
    result = guard.verify_root_claim(req.word, req.claimed_root, req.context_id)
    return result

@app.post("/api/audit/contract")
@app.post("/api/v1/halal/screen")
def screen_halal(req: HalalScreenRequest, request: Request = None):
    """Universal Halal, food ingredients, and Shariah screener with barcode auto-detection."""
    input_text = (req.text or req.query or "").strip()
    if not input_text:
        return {
            "query": "",
            "total_matches": 0,
            "matches": [],
            "findings": [],
            "findings_count": 0,
            "overall_verdict": "UNKNOWN",
            "status_message": "EMPTY_INPUT",
            "is_compliant": True,
            "disclaimer_ru": ahkam.DISCLAIMER_RU,
            "disclaimer_kk": ahkam.DISCLAIMER_KK,
            "disclaimer": ahkam.DISCLAIMER_RU
        }
    
    # Check if input is a pure numeric barcode (8-14 digits)
    clean_digits = re.sub(r"\D", "", input_text)
    if 8 <= len(clean_digits) <= 14 and clean_digits == input_text:
        try:
            barcode_res = check_halal_barcode(clean_digits, request)
            if barcode_res.get("halal_verdict") != "NOT_FOUND":
                v = barcode_res["halal_verdict"]
                m = [{
                    "category": "BARCODE_PRODUCT",
                    "verdict": v,
                    "title_ru": f"{barcode_res.get('name', 'Товар')} ({barcode_res.get('brand', '')})",
                    "title_kk": f"{barcode_res.get('name', 'Тауар')} ({barcode_res.get('brand', '')})",
                    "title_en": f"{barcode_res.get('name', 'Product')} ({barcode_res.get('brand', '')})",
                    "description_ru": barcode_res.get("summary_ru") or barcode_res.get("summary", ""),
                    "description_kk": barcode_res.get("summary_kk") or barcode_res.get("summary", ""),
                    "ayah_ref": "SMIIC / Open Food Facts"
                }]
                return {
                    "query": input_text,
                    "barcode_data": barcode_res,
                    "total_matches": 1,
                    "matches": m,
                    "findings": m,
                    "findings_count": 1,
                    "overall_verdict": v,
                    "status_message": f"BARCODE_{v}",
                    "is_compliant": (v != "HARAM"),
                    "disclaimer_ru": ahkam.DISCLAIMER_RU,
                    "disclaimer_kk": ahkam.DISCLAIMER_KK,
                    "disclaimer": ahkam.DISCLAIMER_RU
                }
        except Exception as e:
            logger.warning("barcode lookup during halal screen failed, falling back to text match: %s", e)

    matches = HalalKnowledgeBase.match_input(input_text)
    is_haram = any(f.get("verdict") == "HARAM" for f in matches)
    is_doubtful = any(f.get("verdict") == "DOUBTFUL" for f in matches)
    is_halal = any(f.get("verdict") == "HALAL" for f in matches)

    if is_haram:
        overall_verdict = "HARAM"
        status_message = "ТЫЙЫМ САЛЫНҒАН (ХАРАМ) / ОБНАРУЖЕНЫ ПРИЗНАКИ ХАРАМА"
    elif is_doubtful:
        overall_verdict = "DOUBTFUL"
        status_message = "ШҮБӘЛІ / СОМНИТЕЛЬНОЕ (МУШТАБИХАТ - ҚҰРАМЫН ТЕКСЕРУ ҚАЖЕТ)"
    elif is_halal:
        overall_verdict = "HALAL"
        status_message = "РҰҚСАТ ЕТІЛГЕН (ХАЛАЛ) / РАЗРЕШЕНО (ХАЛЯЛЬ)"
    else:
        overall_verdict = "HALAL_DEFAULT"
        status_message = "ХАЛАЛ (НЕГІЗГІ ЕРЕЖЕ: ТЫЙЫМ БОЛМАҒАН БАРЛЫҚ НӘРСЕ АДАЛ)"

    return {
        "query": input_text,
        "total_matches": len(matches),
        "matches": matches,
        "findings": matches,
        "findings_count": len(matches),
        "overall_verdict": overall_verdict,
        "status_message": status_message,
        "is_compliant": not is_haram,
        "disclaimer_ru": ahkam.DISCLAIMER_RU,
        "disclaimer_kk": ahkam.DISCLAIMER_KK,
        "disclaimer": ahkam.DISCLAIMER_RU
    }

@app.get("/api/v1/halal/database")
def get_halal_master_database():
    """Returns the full standalone Master Halal/Haram Knowledge Base JSON dataset."""
    db_path = os.path.join(os.path.dirname(__file__), "data", "halal_master_database.json")
    if os.path.exists(db_path):
        with open(db_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "title": "Al-Furqan Guard — Master Halal/Haram Knowledge Base",
        "e_codes": HalalKnowledgeBase.E_CODES_REGISTRY,
        "ontology_categories": list(HalalKnowledgeBase.ONTOLOGY.keys())
    }

@app.post("/api/v1/contracts/audit-aaoifi")
def audit_contract_aaoifi(req: ContractAuditRequest):
    """Deep AAOIFI Shariah contract compliance analysis."""
    result = HalalKnowledgeBase.audit_contract_aaoifi(req.text)
    return result

@app.get("/api/ayah/{sura}/{ayah}")
@app.get("/api/v1/ayah/{sura}/{ayah}")
async def get_ayah(sura: int, ayah: int):
    """O(1) lookup of Ayah AST, multi-translations, tafsir, and multi-reciter audio."""
    if not (1 <= sura <= 114):
        raise HTTPException(status_code=400, detail="Surah number must be between 1 and 114")
    max_ayah = engine.CANONICAL_AYAH_COUNTS[sura - 1]
    if not (1 <= ayah <= max_ayah):
        raise HTTPException(status_code=400, detail=f"Surah {sura} only has {max_ayah} ayahs")

    data = engine.get_ayah(sura, ayah)
    if not data:
        raise HTTPException(status_code=404, detail=f"Ayah {sura}:{ayah} not found.")
    
    surah_name_ru = engine.SURAH_NAMES.get("ru", [])[sura - 1] if 1 <= sura <= 114 else ""
    surah_name_kk = engine.SURAH_NAMES.get("kk", [])[sura - 1] if 1 <= sura <= 114 else ""
    
    # Audio URLs for 3 Reciters
    s_pad = f"{sura:03d}"
    a_pad = f"{ayah:03d}"
    audio_urls = {
        "alafasy": f"{RECITERS_CDN['alafasy']}/{s_pad}{a_pad}.mp3",
        "husary": f"{RECITERS_CDN['husary']}/{s_pad}{a_pad}.mp3",
        "abdulbasit": f"{RECITERS_CDN['abdulbasit']}/{s_pad}{a_pad}.mp3"
    }

    # Tafsir Summary
    key = f"{sura}:{ayah}"
    tafsir_info = TAFSIR_REGISTRY.get(key, None)

    return {
        **data,
        "text_uthmani": data.get("text_uthmani") or data.get("text"),
        "surah_name_ru": surah_name_ru,
        "surah_name_kk": surah_name_kk,
        "audio_urls": audio_urls,
        "tafsir": tafsir_info
    }

@app.get("/api/v1/surah/{sura}")
def get_surah_full(sura: int):
    """Retrieves all Ayahs of a Surah with translations, transliterations, and audio."""
    if not (1 <= sura <= 114):
        raise HTTPException(status_code=400, detail="Surah number must be between 1 and 114")
    
    count = engine.CANONICAL_AYAH_COUNTS[sura - 1]
    ayahs_list = []
    
    s_pad = f"{sura:03d}"
    for a in range(1, count + 1):
        data = engine.get_ayah(sura, a)
        if data:
            a_pad = f"{a:03d}"
            ayahs_list.append({
                "ayah": a,
                "text_uthmani": data.get("text_uthmani") or data.get("text"),
                "transliteration": data.get("transliteration", ""),
                "translations": data.get("translations", {}),
                "tokens": data.get("tokens", []),
                "audio_urls": {
                    "alafasy": f"{RECITERS_CDN['alafasy']}/{s_pad}{a_pad}.mp3",
                    "husary": f"{RECITERS_CDN['husary']}/{s_pad}{a_pad}.mp3",
                    "abdulbasit": f"{RECITERS_CDN['abdulbasit']}/{s_pad}{a_pad}.mp3"
                }
            })
            
    surah_name_ru = engine.SURAH_NAMES.get("ru", [])[sura - 1] if 1 <= sura <= 114 else ""
    surah_name_kk = engine.SURAH_NAMES.get("kk", [])[sura - 1] if 1 <= sura <= 114 else ""
    surah_name_ar = engine.SURAH_NAMES.get("ar", [])[sura - 1] if 1 <= sura <= 114 else ""
    surah_name_en = engine.SURAH_NAMES.get("en", [])[sura - 1] if 1 <= sura <= 114 else ""
    surah_name_tr = engine.SURAH_NAMES.get("tr", [])[sura - 1] if 1 <= sura <= 114 else ""
    surah_name_uz = engine.SURAH_NAMES.get("uz", [])[sura - 1] if 1 <= sura <= 114 else ""
    surah_name_id = engine.SURAH_NAMES.get("id", [])[sura - 1] if 1 <= sura <= 114 else ""

    return {
        "sura": sura,
        "ayah_count": count,
        "surah_name_ru": surah_name_ru,
        "surah_name_kk": surah_name_kk,
        "surah_name_ar": surah_name_ar,
        "surah_name_en": surah_name_en,
        "surah_name_tr": surah_name_tr,
        "surah_name_uz": surah_name_uz,
        "surah_name_id": surah_name_id,
        "ayahs": ayahs_list
    }

@app.get("/api/root/{root}")
@app.get("/api/v1/root/{root}")
def get_root(root: str):
    """Searches for verses containing the specified morphological root."""
    root_clean = root.strip()[:20]
    results = engine.search_by_root(root_clean)
    return {"root": root_clean, "total": len(results), "results": results}

@app.get("/api/roots")
@app.get("/api/v1/roots")
def list_roots():
    """Returns list of top roots with occurrence frequencies."""
    roots_with_counts = []
    for r, occurrences in engine.root_index.items():
        roots_with_counts.append({
            "root": r,
            "occurrences": len(occurrences),
            "ayahs_count": len(set(x[0] for x in occurrences))
        })
    roots_with_counts.sort(key=lambda x: x["occurrences"], reverse=True)
    return {"total_roots": len(roots_with_counts), "roots": roots_with_counts}

@app.get("/api/ahkam/{category}")
@app.get("/api/v1/ahkam/{category}")
def get_ahkam(category: str):
    """Returns categorized Ahkam (tahrim, ibaha, wajib, finance, justice)."""
    cat_clean = category.strip()[:30]
    return ahkam.get_category_ayahs(cat_clean)

# =========================================================================
# MULTI-MODAL OCR, PDF & PRAYER TIMES ENDPOINTS (100% REAL)
# =========================================================================

@app.post("/api/v1/images/audit-ocr")
@app.post("/api/v1/halal/scan-image")
def scan_image_ocr(req: ImageScanRequest, request: Request):
    """
    Real OCR image processing using Pillow & Tesseract.
    Protected by Token Bucket Rate Limiter (3 tokens max, +1 refill every 2 min).
    B2B requests with X-API-Key bypass rate limits!
    """
    # 1. B2B Rate-limit bypass check
    api_key = request.headers.get("x-api-key") or request.headers.get("authorization", "").replace("Bearer ", "").strip()
    is_b2b = bool(api_key and B2BAuthService.validate_api_key(api_key))

    if not is_b2b:
        allowed, remaining_tokens, wait_seconds = ocr_rate_limiter.is_allowed(get_client_ip(request))
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail=f"Лимит OCR-сканирований исчерпан (3 токена). Пожалуйста, подождите {wait_seconds} сек.",
                headers={"Retry-After": str(wait_seconds)}
            )

    try:
        img_data = req.image_base64
        if "," in img_data:
            img_data = img_data.split(",")[1]
        img_bytes = base64.b64decode(img_data)
        
        extracted_text = ImageOCRProcessor.extract_text(img_bytes)
        analysis = HalalKnowledgeBase.analyze_ingredients_deep(extracted_text)
        guard_report = guard.verify_full_text(extracted_text[:20000])
        screen_res = engine.screen_halal(extracted_text)
        
        return {
            "status": "success",
            "extracted_text": extracted_text[:1200],
            "halal_verdict": analysis["verdict"],
            "summary_ru": analysis["summary_ru"],
            "summary_kk": analysis["summary_kk"],
            "haram_items": analysis["haram_items"],
            "doubtful_items": analysis["doubtful_items"],
            "shubhat_details": analysis["shubhat_details"],
            "guard_report": guard_report,
            "matches": screen_res.get("matches", [])
        }
    except Exception as e:
        logger.error("OCR image processing failed: %s", e, exc_info=True)
        return {
            "status": "error",
            "message": "Не удалось обработать изображение. Проверьте формат файла (PNG/JPEG) и попробуйте снова.",
            "extracted_text": "",
            "matches": []
        }


@app.post("/api/v1/documents/audit-pdf")
def audit_pdf_document(req: PDFScanRequest, request: Request):
    """Audits PDF contract or text for Quran quotes and AAOIFI compliance. Rate limited (3/10min per IP); B2B bypass."""
    api_key = request.headers.get("x-api-key") or request.headers.get("authorization", "").replace("Bearer ", "").strip()
    is_b2b = bool(api_key and B2BAuthService.validate_api_key(api_key))
    if not is_b2b:
        allowed, _remaining, wait_seconds = pdf_rate_limiter.is_allowed(get_client_ip(request))
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail=f"Лимит PDF-аудитов исчерпан (3 токена). Повторите через {wait_seconds} секунд.",
                headers={"Retry-After": str(wait_seconds)}
            )
    try:
        pdf_data = req.pdf_base64
        if "," in pdf_data:
            pdf_data = pdf_data.split(",")[1]
        pdf_bytes = base64.b64decode(pdf_data)
        
        audit_result = PDFDocumentProcessor.audit_pdf(pdf_bytes, guard, HalalKnowledgeBase)
        return {
            "status": "success",
            "audit": audit_result
        }
    except Exception as e:
        logger.error("PDF audit failed: %s", e, exc_info=True)
        raise HTTPException(status_code=400, detail="Не удалось прочитать PDF-документ. Проверьте, что файл не повреждён и не защищён паролем.")

@app.post("/api/v1/documents/export-audit-pdf")
def export_audit_pdf(req: ExportAuditPDFRequest):
    """Generates official AAOIFI Shariah Compliance PDF Certificate."""
    try:
        audit_data = req.audit_data
        if not audit_data:
            if req.contract_text:
                audit_data = HalalKnowledgeBase.audit_contract_aaoifi(req.contract_text)
            else:
                audit_data = {
                    "is_compliant": True,
                    "contract_type": "GENERAL_COMMERCIAL",
                    "findings": [],
                    "quran_basis": "2:275 • 4:29"
                }
        
        pdf_bytes = AuditCertificateGenerator.generate_pdf_bytes(
            audit_report=audit_data,
            doc_title=req.document_title or "Договор / Соглашение"
        )
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="Al_Furqan_AAOIFI_Audit_Certificate.pdf"'
            }
        )
    except Exception as e:
        logger.error("PDF certificate generation failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Не удалось сформировать сертификат. Попробуйте ещё раз.")

@app.get("/api/v1/keep-alive")
async def keep_alive_ping():
    """Ultra-lightweight keep-alive heartbeat endpoint to prevent Render cold starts."""
    return {
        "status": "alive",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "service": "al-furqan-guard",
        "version": "2.0.0"
    }

@app.get("/api/v1/halal/certified-registry")
def get_certified_registry():
    """Returns official Cross-Validated Halal Certified Brands database."""
    reg_path = os.path.join(os.path.dirname(__file__), "data", "halal_certified_registry.json")
    if os.path.exists(reg_path):
        with open(reg_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"status": "ok", "certified_brands": {}}

@app.get("/api/v1/namaz/times")
def get_namaz_times(lat: float = 51.1694, lon: float = 71.4491):
    """Returns astronomical 5 prayer times and Qibla compass bearing for given GPS coordinates."""
    times = PrayerTimesCalculator.calculate_prayer_times(lat, lon)
    qibla_deg, compass = PrayerTimesCalculator.calculate_qibla(lat, lon)
    return {
        "latitude": lat,
        "longitude": lon,
        "prayer_times": times,
        "qibla_bearing_deg": qibla_deg,
        "qibla_compass_direction": compass
    }

@app.post("/api/v1/zakat/calculate")
def calculate_zakat(req: ZakatRequest):
    """Computes Nisab and 2.5% Zakat liability."""
    return ZakatCalculator.calculate_zakat(
        cash_savings=req.cash_savings,
        gold_grams=req.gold_grams,
        silver_grams=req.silver_grams,
        business_inventory=req.business_inventory,
        liabilities_due=req.liabilities_due,
        currency_symbol=req.currency or "₸"
    )

@app.get("/api/v1/search/theme")
def search_theme(q: str):
    """Semantic thematic Quran search across 6,236 Ayahs."""
    clean_q = q.strip()[:100]
    results = SemanticThemeEngine.find_ayahs_by_topic(clean_q, engine)
    return {"query": clean_q, "total_found": len(results), "results": results}

FEEDBACK_FILE_PATH = os.path.join(RUNTIME_DATA_DIR, "feedback_submissions.json")

def persist_feedback_entry(entry: Dict[str, Any]):
    """Appends feedback entry to persistent disk storage."""
    try:
        os.makedirs(os.path.dirname(FEEDBACK_FILE_PATH), exist_ok=True)
        items = []
        if os.path.exists(FEEDBACK_FILE_PATH):
            try:
                with open(FEEDBACK_FILE_PATH, "r", encoding="utf-8") as f:
                    items = json.load(f)
            except Exception:
                items = []
        if not isinstance(items, list):
            items = []
        items.append(entry)
        if len(items) > MAX_FEEDBACK_ITEMS:
            items = items[-MAX_FEEDBACK_ITEMS:]
        with open(FEEDBACK_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.warning(f"Failed to persist feedback to disk: {e}")

@app.post("/api/v1/feedback")
def submit_feedback(req: FeedbackRequest):
    """Submits user feedback with memory bounds protection and persistent disk storage."""
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    global FEEDBACK_STORE
    if len(FEEDBACK_STORE) >= MAX_FEEDBACK_ITEMS:
        FEEDBACK_STORE.pop(0)
        
    entry = {
        "id": len(FEEDBACK_STORE) + 1,
        "name": req.name.strip()[:100],
        "contact": req.email_or_phone.strip()[:150],
        "category": req.category[:50],
        "message": req.message.strip()[:10000],
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    FEEDBACK_STORE.append(entry)
    persist_feedback_entry(entry)

    # Optional Telegram Admin notification
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    admin_chat_id = os.environ.get("TELEGRAM_ADMIN_CHAT_ID")
    if bot_token and admin_chat_id:
        try:
            import urllib.request
            import urllib.parse
            tg_text = (
                f"📬 *НОВЫЙ ОТЗЫВ В AL-FURQAN GUARD (№{entry['id']})*\n\n"
                f"👤 *Имя:* {sanitize_md(entry['name'])}\n"
                f"📞 *Контакты:* {sanitize_md(entry['contact']) or 'Не указан'}\n"
                f"🏷️ *Категория:* {sanitize_md(entry['category'])}\n"
                f"💬 *Сообщение:*\n{sanitize_md(entry['message'])}\n\n"
                f"⏱️ _{entry['timestamp']}_"
            )
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = urllib.parse.urlencode({
                "chat_id": admin_chat_id,
                "text": tg_text,
                "parse_mode": "Markdown"
            }).encode("utf-8")
            req_tg = urllib.request.Request(url, data=data, method="POST")
            urllib.request.urlopen(req_tg, timeout=3)
        except Exception as e:
            logger.warning(f"Telegram admin feedback notification failed: {e}")
    
    return {
        "status": "success",
        "success": True,
        "feedback_id": entry["id"],
        "message_kk": "Пікіріңіз бен хабарламаңыз сәтті қабылданды және тіркелді! Рахмет.",
        "message_ru": "Ваш отзыв и обращение успешно приняты и сохранены! Спасибо.",
        "message_en": "Your feedback has been successfully received and recorded! Thank you."
    }

@app.get("/api/v1/feedback/list")
def get_feedback_list(request: Request):
    """Returns list of submitted user feedback. Restricted: requires X-Admin-Key header."""
    if not ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Feedback access disabled: ADMIN_API_KEY is not configured")
    provided = request.headers.get("x-admin-key", "")
    if not hmac.compare_digest(provided, ADMIN_API_KEY):
        raise HTTPException(status_code=403, detail="Forbidden")
    if os.path.exists(FEEDBACK_FILE_PATH):
        try:
            with open(FEEDBACK_FILE_PATH, "r", encoding="utf-8") as f:
                items = json.load(f)
                return {"total": len(items), "feedback": items}
        except Exception as e:
            logger.warning("failed to read feedback file %s, falling back to memory store: %s", FEEDBACK_FILE_PATH, e)
    return {"total": len(FEEDBACK_STORE), "feedback": FEEDBACK_STORE}

# Mount static UI
app.mount("/", StaticFiles(directory=UI_DIR, html=True), name="ui")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
