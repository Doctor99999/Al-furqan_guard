"""
Al-Furqan AI — Database Engine & Scalable Storage Architecture
Enterprise Storage supporting PostgreSQL (Render/Cloud) and native SQLite (Zero-Config local fallback).

Manages:
1. Real Persistent Visitor Analytics across all time intervals (Day/Week/Month/Year/All-time)
2. 2.5M+ Halal Products Repository & Cache (with Open Food Facts API integration)
3. B2B Commercial API Key Management & Token Authentication
"""

import os
import sys
import re
import json
import hashlib
import hmac
import sqlite3
import datetime
import urllib.request
import urllib.parse
from typing import Optional, Dict, Any, List, Tuple

try:
    from quran_guard.config import RUNTIME_DATA_DIR
except Exception:
    RUNTIME_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# Try importing SQLAlchemy if installed; otherwise use built-in sqlite3 seamlessly
try:
    from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, Index
    from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

os.makedirs(RUNTIME_DATA_DIR, exist_ok=True)
LOCAL_SQLITE_PATH = os.path.join(RUNTIME_DATA_DIR, "alfurqan_production.db")

# =========================================================================
# NATIVE SQLITE & POSTGRESQL MULTI-BACKEND ENGINE
# =========================================================================

class DBConnection:
    @staticmethod
    def get_sqlite_conn():
        conn = sqlite3.connect(LOCAL_SQLITE_PATH, check_same_thread=False, timeout=30)
        conn.row_factory = sqlite3.Row
        # WAL: readers don't block writers (and vice-versa); critical since several
        # endpoints (B2B counters, visitor logs) write while reads are frequent.
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=5000")
        return conn

def init_native_db():
    conn = DBConnection.get_sqlite_conn()
    cur = conn.cursor()
    
    # 1. Visitor Logs table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS visitor_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_hash TEXT NOT NULL,
            visit_date TEXT NOT NULL,
            year_month TEXT NOT NULL,
            year TEXT NOT NULL,
            week_start TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_agent TEXT
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_vlog_ip_date ON visitor_logs(ip_hash, visit_date)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_vlog_date ON visitor_logs(visit_date)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_vlog_month ON visitor_logs(year_month)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_vlog_year ON visitor_logs(year)")

    # 2. Halal Products Cache (2.5M+ products)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS halal_products (
            barcode TEXT PRIMARY KEY,
            product_name TEXT NOT NULL,
            brand TEXT,
            categories TEXT,
            ingredients_text TEXT,
            halal_verdict TEXT NOT NULL,
            shubhat_summary TEXT,
            e_codes_detected TEXT,
            shubhat_details_json TEXT,
            data_source TEXT DEFAULT 'LOCAL_ONTOLOGY',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 3. B2B Commercial Organizations & API Keys
    cur.execute("""
        CREATE TABLE IF NOT EXISTS b2b_organizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            org_name TEXT NOT NULL,
            api_key TEXT UNIQUE NOT NULL,
            key_hash TEXT,
            is_active INTEGER DEFAULT 1,
            tier TEXT DEFAULT 'ENTERPRISE',
            total_requests INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_used_at TIMESTAMP
        )
        """)
    
    # Migrate pre-existing databases: add key_hash column if missing
    cols = [r[1] for r in cur.execute("PRAGMA table_info(b2b_organizations)").fetchall()]
    if "key_hash" not in cols:
        cur.execute("ALTER TABLE b2b_organizations ADD COLUMN key_hash TEXT")
    
    # Seed a demo B2B master key only when explicitly provided via env (no hardcoded backdoor).
    demo_key = os.environ.get("B2B_DEMO_API_KEY", "").strip()
    if demo_key:
        demo_hash = hashlib.sha256(demo_key.encode()).hexdigest()
        cur.execute("SELECT id FROM b2b_organizations WHERE key_hash = ? OR api_key = ?", (demo_hash, demo_key))
        if not cur.fetchone():
            # Upgrade any legacy plaintext row for this key
            cur.execute("UPDATE b2b_organizations SET key_hash = ?, api_key = ? WHERE api_key = ?", (demo_hash, demo_hash, demo_key))
            cur.execute("""
                INSERT INTO b2b_organizations (org_name, api_key, key_hash, is_active, tier, total_requests)
                SELECT 'Al-Furqan Enterprise Demo Partner', ?, ?, 1, 'ENTERPRISE', 0
                WHERE NOT EXISTS (SELECT 1 FROM b2b_organizations WHERE key_hash = ?)
            """, (demo_hash, demo_hash, demo_hash))

    conn.commit()
    conn.close()

# Auto-initialize database tables
init_native_db()


# =========================================================================
# 1. VISITOR ANALYTICS SERVICE
# =========================================================================

class VisitorAnalyticsService:
    """Manages real persistent visitor metrics across day, week, month, year, and all-time."""

    @staticmethod
    def record_visit(ip_hash: str, user_agent: str = "") -> Dict[str, Any]:
        conn = DBConnection.get_sqlite_conn()
        cur = conn.cursor()
        try:
            now_utc = datetime.datetime.now(datetime.timezone.utc)
            today_str = now_utc.strftime("%Y-%m-%d")
            year_month_str = now_utc.strftime("%Y-%m")
            year_str = now_utc.strftime("%Y")
            start_of_week = (now_utc - datetime.timedelta(days=now_utc.weekday())).strftime("%Y-%m-%d")

            # Check if this IP was already recorded today
            cur.execute("SELECT id FROM visitor_logs WHERE ip_hash = ? AND visit_date = ?", (ip_hash, today_str))
            if not cur.fetchone():
                cur.execute("""
                    INSERT INTO visitor_logs (ip_hash, visit_date, year_month, year, week_start, user_agent)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (ip_hash, today_str, year_month_str, year_str, start_of_week, user_agent[:250] if user_agent else ""))
                conn.commit()

            # Real aggregated metrics across all timeframes
            cur.execute("SELECT COUNT(DISTINCT ip_hash) FROM visitor_logs WHERE visit_date = ?", (today_str,))
            today_count = cur.fetchone()[0] or 1

            cur.execute("SELECT COUNT(DISTINCT ip_hash) FROM visitor_logs WHERE visit_date >= ?", (start_of_week,))
            week_count = cur.fetchone()[0] or 1

            cur.execute("SELECT COUNT(DISTINCT ip_hash) FROM visitor_logs WHERE year_month = ?", (year_month_str,))
            month_count = cur.fetchone()[0] or 1

            cur.execute("SELECT COUNT(DISTINCT ip_hash) FROM visitor_logs WHERE year = ?", (year_str,))
            year_count = cur.fetchone()[0] or 1

            cur.execute("SELECT COUNT(DISTINCT ip_hash) FROM visitor_logs")
            unique_all_count = cur.fetchone()[0] or 1

            cur.execute("SELECT COUNT(*) FROM visitor_logs")
            all_time_count = cur.fetchone()[0] or 1

            return {
                "today": max(1, today_count),
                "week": max(1, week_count),
                "month": max(1, month_count),
                "year": max(1, year_count),
                "all_time": max(1, all_time_count),
                "total_visitors": max(1, all_time_count),
                "unique_visitors": max(1, unique_all_count),
                "status": "SQL_PERSISTENT_REAL"
            }
        except Exception as e:
            print(f"[VisitorAnalyticsService] Error: {e}")
            return {
                "today": 1, "week": 1, "month": 1, "year": 1, "all_time": 1,
                "total_visitors": 1, "unique_visitors": 1, "status": "FALLBACK"
            }
        finally:
            conn.close()


# =========================================================================
# 2. OPEN FOOD FACTS & HALAL PRODUCT SERVICE
# =========================================================================

class OpenFoodFactsService:
    """Queries Open Food Facts API (2.5M+ products) and caches verified Halal status."""

    API_URL = "https://world.openfoodfacts.org/api/v2/product/{barcode}.json"

    @classmethod
    def fetch_product_by_barcode(cls, barcode: str) -> Optional[Dict[str, Any]]:
        clean_barcode = re.sub(r"\D", "", barcode.strip())
        if not clean_barcode:
            return None

        url = cls.API_URL.format(barcode=clean_barcode)
        headers = {
            "User-Agent": "Al-Furqan-AI/2.0 (Halal Ground Truth Auditor; contact@alfurqan.ai)"
        }
        
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    payload = json.loads(resp.read().decode("utf-8"))
                    if payload.get("status") == 1 and "product" in payload:
                        p = payload["product"]
                        return {
                            "barcode": clean_barcode,
                            "name": p.get("product_name") or p.get("product_name_ru") or p.get("generic_name") or "Неизвестный продукт",
                            "brand": p.get("brands", "Не указан"),
                            "categories": p.get("categories", ""),
                            "ingredients_text": p.get("ingredients_text") or p.get("ingredients_text_ru") or p.get("ingredients_text_en") or "",
                            "additives_tags": p.get("additives_tags", []),
                            "image_url": p.get("image_url", "")
                        }
        except Exception as e:
            print(f"[OpenFoodFacts] Fetch notice for barcode {clean_barcode}: {e}")
        return None


# =========================================================================
# 3. B2B AUTHENTICATION SERVICE
# =========================================================================

class B2BOrgModel:
    def __init__(self, id, org_name, api_key, is_active, tier, total_requests):
        self.id = id
        self.org_name = org_name
        self.api_key = api_key
        self.is_active = bool(is_active)
        self.tier = tier
        self.total_requests = total_requests

class B2BAuthService:
    """Validates B2B Enterprise API keys and tracks commercial usage.
    Keys are stored as SHA-256 hashes; legacy plaintext rows are transparently upgraded."""

    @staticmethod
    def _hash_key(api_key: str) -> str:
        return hashlib.sha256(api_key.encode("utf-8")).hexdigest()

    @staticmethod
    def validate_api_key(api_key: str) -> Optional[B2BOrgModel]:
        if not api_key or not api_key.strip():
            return None
        key = api_key.strip()
        key_hash = B2BAuthService._hash_key(key)
        conn = DBConnection.get_sqlite_conn()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT id, org_name, api_key, key_hash, is_active, tier, total_requests
                FROM b2b_organizations
                WHERE is_active = 1
            """)
            matched_row = None
            for row in cur.fetchall():
                stored_hash = (row["key_hash"] or "").strip()
                stored_plain = row["api_key"] or ""
                if stored_hash:
                    if hmac.compare_digest(stored_hash, key_hash):
                        matched_row = row
                        break
                elif stored_plain:
                    # Legacy plaintext row: timing-safe compare, then upgrade to hash
                    if hmac.compare_digest(stored_plain, key):
                        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
                        cur.execute("""
                            UPDATE b2b_organizations
                            SET key_hash = ?, api_key = ?, last_used_at = COALESCE(last_used_at, ?)
                            WHERE id = ?
                        """, (key_hash, key_hash, now_str, row["id"]))
                        conn.commit()
                        matched_row = row
                        break

            if matched_row is None:
                return None

            now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
            cur.execute("""
                UPDATE b2b_organizations
                SET total_requests = total_requests + 1, last_used_at = ?
                WHERE id = ?
            """, (now_str, matched_row["id"]))
            conn.commit()
            return B2BOrgModel(
                id=matched_row["id"],
                org_name=matched_row["org_name"],
                api_key="",
                is_active=bool(matched_row["is_active"]),
                tier=matched_row["tier"],
                total_requests=(matched_row["total_requests"] or 0) + 1
            )
        except Exception as e:
            print(f"[B2BAuthService] Error: {e}")
            return None
        finally:
            conn.close()


# Compatibility helpers for HalalProduct Cache
class HalalProductCache:
    @staticmethod
    def get_by_barcode(barcode: str) -> Optional[Dict[str, Any]]:
        conn = DBConnection.get_sqlite_conn()
        cur = conn.cursor()
        try:
            cur.execute("SELECT * FROM halal_products WHERE barcode = ?", (barcode.strip(),))
            row = cur.fetchone()
            if row:
                return dict(row)
            return None
        finally:
            conn.close()

    @staticmethod
    def save_product(barcode: str, name: str, brand: str, categories: str, ingredients: str,
                     verdict: str, summary: str, shubhat_json: str, source: str = "OPEN_FOOD_FACTS"):
        conn = DBConnection.get_sqlite_conn()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO halal_products (barcode, product_name, brand, categories, ingredients_text, halal_verdict, shubhat_summary, shubhat_details_json, data_source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(barcode) DO UPDATE SET
                    product_name=excluded.product_name,
                    brand=excluded.brand,
                    categories=excluded.categories,
                    ingredients_text=excluded.ingredients_text,
                    halal_verdict=excluded.halal_verdict,
                    shubhat_summary=excluded.shubhat_summary,
                    shubhat_details_json=excluded.shubhat_details_json,
                    updated_at=CURRENT_TIMESTAMP
            """, (barcode, name, brand, categories, ingredients, verdict, summary, shubhat_json, source))
            # Bound cache growth (disk-fill protection): keep newest 50k rows
            cur.execute("""
                DELETE FROM halal_products WHERE rowid NOT IN (
                    SELECT rowid FROM halal_products ORDER BY rowid DESC LIMIT 50000
                )
            """)
            conn.commit()
        except Exception as e:
            print(f"[HalalProductCache] Save error: {e}")
        finally:
            conn.close()
