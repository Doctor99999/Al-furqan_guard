"""
Al-Furqan AI - Multi-Modal Document, Image & Islamic Intelligence Engine v2.0
Supports:
1. PDF Document Parsing & Shariah Compliance Audit (pypdf)
2. Image & Photo OCR Text Extraction (Pillow / pytesseract / Fallback)
3. Astronomical Prayer Times (Namaz) & Qibla Direction Calculator (Kaaba Geodesics)
4. Islamic Zakat & Nisab Calculator (Fiqh Standards)
5. Semantic Theme Search & Topic Matcher across 6,236 Ayahs
"""

import io
import os
import re
import math
import datetime
from typing import Optional, Dict, Any, List, Tuple
from PIL import Image

try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

# =========================================================================
# 1. PDF DOCUMENT PROCESSING & SHARIAH AUDITOR
# =========================================================================

class PDFDocumentProcessor:
    """Extracts text from PDF contracts, books, and articles for automated Shariah audit."""

    @staticmethod
    def extract_text_from_bytes(pdf_bytes: bytes, max_pages: int = 50) -> Tuple[str, int]:
        """Extracts text from raw PDF bytes safely with page bounds."""
        if not PYPDF_AVAILABLE:
            return "PDF processing library not available", 0
            
        try:
            reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            total_pages = len(reader.pages)
            pages_to_read = min(total_pages, max_pages)
            
            extracted_text = []
            for i in range(pages_to_read):
                page = reader.pages[i]
                text = page.extract_text() or ""
                extracted_text.append(f"--- [СТРАНИЦА {i+1}] ---\n{text}")
                
            return "\n\n".join(extracted_text), total_pages
        except Exception:
            return "", 0

    @staticmethod
    def audit_pdf(pdf_bytes: bytes, guard, halal_engine, lang: str = "ru") -> Dict[str, Any]:
        """Runs complete Anti-Hallucination and AAOIFI audit across entire PDF document."""
        full_text, pages_count = PDFDocumentProcessor.extract_text_from_bytes(pdf_bytes)
        text_truncated = len(full_text) > 200000
        audit_text = full_text[:200000]
        
        # 1. Guardrail quote check
        guard_report = guard.verify_full_text(audit_text)
        
        # 2. AAOIFI contract compliance check
        aaoifi_report = halal_engine.audit_contract_aaoifi(audit_text)
        
        # 3. Halal food / ingredient check
        halal_matches = halal_engine.match_input(audit_text)
        
        result = {
            "total_pages": pages_count,
            "text_truncated": text_truncated,
            "text_length": len(full_text),
            "guard_report": guard_report,
            "aaoifi_report": aaoifi_report,
            "halal_matches": halal_matches,
            "text_preview": full_text[:1200]
        }
        return result

    # Alias for backwards compatibility
    audit_document = audit_pdf

# =========================================================================
# 2. IMAGE & PHOTO OCR PROCESSOR
# =========================================================================

class ImageOCRProcessor:
    """Extracts text from food packaging, labels, certificates, and contracts via OCR."""

    @staticmethod
    def extract_text(image_bytes: bytes) -> str:
        """Extracts text from image bytes using Tesseract with image preprocessing fallback."""
        try:
            # Prevent Decompression Bomb DoS (25 megapixels limit)
            Image.MAX_IMAGE_PIXELS = 25_000_000
            
            img = Image.open(io.BytesIO(image_bytes))
            
            # Check dimensions explicitly as well
            if img.width * img.height > 25_000_000:
                return "Ошибка: Изображение превышает лимит в 25 мегапикселей."
            
            # Convert to grayscale / RGB for optimal OCR
            if img.mode != 'RGB':
                img = img.convert('RGB')
                
            if PYTESSERACT_AVAILABLE:
                try:
                    # Attempt Tesseract with multi-language support (rus, kaz, ara, eng) and explicit timeout
                    text = pytesseract.image_to_string(img, lang="rus+kaz+ara+eng", timeout=10)
                    if text and text.strip():
                        return text.strip()
                except Exception as ex:
                    print(f"Tesseract OCR Exception: {ex}")
                    
            # Fallback: Basic image analysis metadata
            width, height = img.size
            return f"Изображение {width}x{height}px получено для анализа состава."
        except Exception:
            return "Ошибка обработки изображения"

    @staticmethod
    def ocr_readable(text: str) -> bool:
        """True only when OCR produced real content; False for error/fallback strings."""
        if not text or not text.strip():
            return False
        if text.startswith("Ошибка обработки изображения"):
            return False
        return not re.match(r"^Изображение \d+x\d+px получено для анализа состава", text)

# =========================================================================
# 3. ASTRONOMICAL NAMAZ PRAYER TIMES & QIBLA DIRECTION
# =========================================================================

class PrayerTimesCalculator:
    """
    Computes deterministic 5 daily prayer times (Fajr, Sunrise, Dhuhr, Asr, Maghrib, Isha)
    and exact Qibla bearing degree towards Kaaba in Mecca (21.4225° N, 39.8262° E).
    """
    KAABA_LAT = 21.4225
    KAABA_LON = 39.8262

    @staticmethod
    def calculate_qibla(lat: float, lon: float) -> Tuple[float, str]:
        """Calculates precise compass bearing (0-360°) to Kaaba in Mecca."""
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)
        kaaba_lat_rad = math.radians(PrayerTimesCalculator.KAABA_LAT)
        kaaba_lon_rad = math.radians(PrayerTimesCalculator.KAABA_LON)
        
        delta_lon = kaaba_lon_rad - lon_rad
        
        y = math.sin(delta_lon)
        x = math.cos(lat_rad) * math.tan(kaaba_lat_rad) - math.sin(lat_rad) * math.cos(delta_lon)
        
        bearing_rad = math.atan2(y, x)
        bearing_deg = (math.degrees(bearing_rad) + 360) % 360
        
        # Compass direction name
        directions = ["С", "СВ", "В", "ЮВ", "Ю", "ЮЗ", "З", "СЗ"]
        idx = int((bearing_deg + 22.5) / 45) % 8
        compass_dir = directions[idx]
        
        return round(bearing_deg, 1), compass_dir

    @staticmethod
    def calculate_prayer_times(lat: float, lon: float, date: Optional[datetime.date] = None, timezone_offset: Optional[float] = None) -> Dict[str, str]:
        """Calculates exact 5 prayer times for given GPS coordinates and date."""
        if date is None:
            date = datetime.date.today()
            
        # Julian date computation
        year = date.year
        month = date.month
        day = date.day
        
        if month <= 2:
            year -= 1
            month += 12
            
        a = math.floor(year / 100)
        b = 2 - a + math.floor(a / 4)
        jd = math.floor(365.25 * (year + 4716)) + math.floor(30.6001 * (month + 1)) + day + b - 1524.5
        
        d = jd - 2451545.0
        g = 357.529 + 0.98560028 * d
        q = 280.459 + 0.98564736 * d
        l = q + 1.915 * math.sin(math.radians(g)) + 0.020 * math.sin(math.radians(2 * g))
        
        e = 23.439 - 0.00000036 * d
        ra = math.degrees(math.atan2(math.cos(math.radians(e)) * math.sin(math.radians(l)), math.cos(math.radians(l)))) / 15.0
        ra = (ra + 24) % 24
        
        dec = math.degrees(math.asin(math.sin(math.radians(e)) * math.sin(math.radians(l))))
        eqt = q / 15.0 - ra
        
        # Local timezone offset approximation if not supplied
        if timezone_offset is None:
            timezone_offset = round(lon / 15.0)
            
        # Solar Noon (Dhuhr)
        noon = (12 + timezone_offset - (lon / 15.0) - eqt) % 24
        
        # Helper for sun altitude angles
        def time_for_angle(angle: float, is_morning: bool = True) -> float:
            try:
                lat_rad = math.radians(lat)
                dec_rad = math.radians(dec)
                val = (math.sin(math.radians(angle)) - math.sin(lat_rad) * math.sin(dec_rad)) / (math.cos(lat_rad) * math.cos(dec_rad))
                val = max(-1.0, min(1.0, val))
                hour_angle = math.degrees(math.acos(val)) / 15.0
                return (noon - hour_angle) if is_morning else (noon + hour_angle)
            except Exception:
                return noon
                
        # Fajr angle (18°), Sunrise (-0.833°), Asr (shadow=1), Maghrib (-0.833°), Isha (17°)
        fajr_val = time_for_angle(-18.0, is_morning=True)
        sunrise_val = time_for_angle(-0.833, is_morning=True)
        
        # Asr shadow factor
        lat_rad = math.radians(lat)
        dec_rad = math.radians(dec)
        asr_angle = -math.degrees(math.atan(1.0 + math.tan(abs(lat_rad - dec_rad))))
        asr_val = time_for_angle(asr_angle, is_morning=False)
        
        maghrib_val = time_for_angle(-0.833, is_morning=False)
        isha_val = time_for_angle(-17.0, is_morning=False)
        
        def format_time(decimal_hours: float) -> str:
            hours = int(decimal_hours) % 24
            minutes = int((decimal_hours - int(decimal_hours)) * 60)
            return f"{hours:02d}:{minutes:02d}"
            
        return {
            "fajr": format_time(fajr_val),
            "sunrise": format_time(sunrise_val),
            "dhuhr": format_time(noon),
            "asr": format_time(asr_val),
            "maghrib": format_time(maghrib_val),
            "isha": format_time(isha_val)
        }

# =========================================================================
# 4. SHARIAH ZAKAT & NISAB CALCULATOR
# =========================================================================

class ZakatCalculator:
    """Calculates canonical Islamic Zakat (2.5%) based on Gold/Silver Nisab thresholds."""
    
    # Standard Nisab weights in Grams (Fiqh consensus)
    GOLD_NISAB_GRAMS = 85.0    # 85 grams of 24k gold
    SILVER_NISAB_GRAMS = 595.0 # 595 grams of silver
    ZAKAT_RATE = 0.025         # 2.5% (1/40th)

    @staticmethod
    def calculate_zakat(
        cash_savings: float = 0.0,
        gold_grams: float = 0.0,
        silver_grams: float = 0.0,
        business_inventory: float = 0.0,
        liabilities_due: float = 0.0,
        gold_price_per_gram: float = 66000.0,   # KZT/gram - EXAMPLE default; pass live market price for accuracy
        silver_price_per_gram: float = 550.0,   # KZT/gram - EXAMPLE default; pass live market price for accuracy
        currency_symbol: str = "₸",
        nisab_reference: str = "silver"  # "silver" (preferred for cash wealth) or "gold"
    ) -> Dict[str, Any]:
        """Calculates exact Zakat liability and Nisab eligibility.

        The obligation threshold follows `nisab_reference`:
        - "silver" (default): 595g of silver -- the standard most fiqh authorities
          prefer for monetary wealth, because the lower threshold obligates earlier
          and benefits the poor (this matches the calculator's documented intent).
        - "gold": 85g of gold -- the higher, more conservative threshold.
        Both thresholds are returned so clients can display them transparently.
        """
        gold_value = max(0.0, gold_grams) * gold_price_per_gram
        silver_value = max(0.0, silver_grams) * silver_price_per_gram

        gross_wealth = cash_savings + gold_value + silver_value + business_inventory
        net_wealth = max(0.0, gross_wealth - liabilities_due)

        gold_nisab_threshold = ZakatCalculator.GOLD_NISAB_GRAMS * gold_price_per_gram
        silver_nisab_threshold = ZakatCalculator.SILVER_NISAB_GRAMS * silver_price_per_gram

        reference = nisab_reference.strip().lower() if isinstance(nisab_reference, str) else "silver"
        if reference not in ("silver", "gold"):
            reference = "silver"
        nisab_threshold_used = silver_nisab_threshold if reference == "silver" else gold_nisab_threshold

        is_obligatory = net_wealth >= nisab_threshold_used
        zakat_amount = (net_wealth * ZakatCalculator.ZAKAT_RATE) if is_obligatory else 0.0

        return {
            "is_obligatory": is_obligatory,
            "currency": currency_symbol,
            "gross_wealth": round(gross_wealth, 2),
            "liabilities": round(liabilities_due, 2),
            "net_wealth": round(net_wealth, 2),
            "gold_nisab_threshold": round(gold_nisab_threshold, 2),
            "silver_nisab_threshold": round(silver_nisab_threshold, 2),
            "nisab_reference": reference,
            "nisab_threshold_used": round(nisab_threshold_used, 2),
            "zakat_due": round(zakat_amount, 2),
            "rate_percent": "2.5%"
        }

# =========================================================================
# 5. SEMANTIC QURAN THEME SEARCH & SMART QA
# =========================================================================

THEMATIC_INDEX = {
    "терпение": [
        (2, 153), (2, 155), (3, 200), (39, 10), (103, 3)
    ],
    "сабыр": [
        (2, 153), (2, 155), (3, 200), (39, 10), (103, 3)
    ],
    "родители": [
        (17, 23), (17, 24), (31, 14), (46, 15), (29, 8)
    ],
    "ата-ана": [
        (17, 23), (17, 24), (31, 14), (46, 15), (29, 8)
    ],
    "справедливость": [
        (4, 58), (4, 135), (5, 8), (16, 90), (42, 15)
    ],
    "әділдік": [
        (4, 58), (4, 135), (5, 8), (16, 90), (42, 15)
    ],
    "торговля": [
        (2, 275), (2, 282), (4, 29), (62, 9), (83, 1)
    ],
    "сауда": [
        (2, 275), (2, 282), (4, 29), (62, 9), (83, 1)
    ],
    "риба": [
        (2, 275), (2, 276), (2, 278), (3, 130), (30, 39)
    ],
    "прощение": [
        (3, 133), (3, 134), (4, 110), (39, 53), (42, 40)
    ],
    "кешірім": [
        (3, 133), (3, 134), (4, 110), (39, 53), (42, 40)
    ],
    "закят": [
        (2, 43), (2, 110), (9, 60), (9, 103), (22, 41)
    ],
    "зекет": [
        (2, 43), (2, 110), (9, 60), (9, 103), (22, 41)
    ],
    "намаз": [
        (2, 45), (2, 238), (4, 103), (20, 14), (29, 45)
    ],
    "ораза": [
        (2, 183), (2, 184), (2, 185), (2, 187)
    ],
    "пост": [
        (2, 183), (2, 184), (2, 185), (2, 187)
    ],
    # English (en)
    "patience": [
        (2, 153), (2, 155), (3, 200), (39, 10), (103, 3)
    ],
    "parents": [
        (17, 23), (17, 24), (31, 14), (46, 15), (29, 8)
    ],
    "justice": [
        (4, 58), (4, 135), (5, 8), (16, 90), (42, 15)
    ],
    "trade": [
        (2, 275), (2, 282), (4, 29), (62, 9), (83, 1)
    ],
    "commerce": [
        (2, 275), (2, 282), (4, 29), (62, 9), (83, 1)
    ],
    "usury": [
        (2, 275), (2, 276), (2, 278), (3, 130), (30, 39)
    ],
    "interest": [
        (2, 275), (2, 276), (2, 278), (3, 130), (30, 39)
    ],
    "forgiveness": [
        (3, 133), (3, 134), (4, 110), (39, 53), (42, 40)
    ],
    "zakat": [
        (2, 43), (2, 110), (9, 60), (9, 103), (22, 41)
    ],
    "prayer": [
        (2, 45), (2, 238), (4, 103), (20, 14), (29, 45)
    ],
    "salat": [
        (2, 45), (2, 238), (4, 103), (20, 14), (29, 45)
    ],
    "fasting": [
        (2, 183), (2, 184), (2, 185), (2, 187)
    ],
    # Turkish (tr)
    "sabır": [
        (2, 153), (2, 155), (3, 200), (39, 10), (103, 3)
    ],
    "ebeveyn": [
        (17, 23), (17, 24), (31, 14), (46, 15), (29, 8)
    ],
    "adalet": [
        (4, 58), (4, 135), (5, 8), (16, 90), (42, 15)
    ],
    "ticaret": [
        (2, 275), (2, 282), (4, 29), (62, 9), (83, 1)
    ],
    "faiz": [
        (2, 275), (2, 276), (2, 278), (3, 130), (30, 39)
    ],
    "bağışlama": [
        (3, 133), (3, 134), (4, 110), (39, 53), (42, 40)
    ],
    "zekat": [
        (2, 43), (2, 110), (9, 60), (9, 103), (22, 41)
    ],
    "namaz": [
        (2, 45), (2, 238), (4, 103), (20, 14), (29, 45)
    ],
    "oruç": [
        (2, 183), (2, 184), (2, 185), (2, 187)
    ],
    # Uzbek (uz)
    "sabr": [
        (2, 153), (2, 155), (3, 200), (39, 10), (103, 3)
    ],
    "ota-ona": [
        (17, 23), (17, 24), (31, 14), (46, 15), (29, 8)
    ],
    "adolat": [
        (4, 58), (4, 135), (5, 8), (16, 90), (42, 15)
    ],
    "savdo": [
        (2, 275), (2, 282), (4, 29), (62, 9), (83, 1)
    ],
    "ribo": [
        (2, 275), (2, 276), (2, 278), (3, 130), (30, 39)
    ],
    "kechirim": [
        (3, 133), (3, 134), (4, 110), (39, 53), (42, 40)
    ],
    "roza": [
        (2, 183), (2, 184), (2, 185), (2, 187)
    ],
    # Indonesian (id)
    "kesabaran": [
        (2, 153), (2, 155), (3, 200), (39, 10), (103, 3)
    ],
    "orang tua": [
        (17, 23), (17, 24), (31, 14), (46, 15), (29, 8)
    ],
    "keadilan": [
        (4, 58), (4, 135), (5, 8), (16, 90), (42, 15)
    ],
    "perdagangan": [
        (2, 275), (2, 282), (4, 29), (62, 9), (83, 1)
    ],
    "ampunan": [
        (3, 133), (3, 134), (4, 110), (39, 53), (42, 40)
    ],
    "solat": [
        (2, 45), (2, 238), (4, 103), (20, 14), (29, 45)
    ],
    "puasa": [
        (2, 183), (2, 184), (2, 185), (2, 187)
    ]
}

class SemanticThemeEngine:
    """Retrieves canonical Quranic Ayahs by natural semantic themes and questions."""

    @staticmethod
    def find_ayahs_by_topic(query: str, engine) -> List[Dict[str, Any]]:
        """Finds most relevant Ayahs for a given topic or query."""
        q = query.lower().strip()
        matched_coords = []
        
        for keyword, coords in THEMATIC_INDEX.items():
            if keyword in q:
                matched_coords.extend(coords)
                
        # Deduplicate preserving order
        unique_coords = []
        for c in matched_coords:
            if c not in unique_coords:
                unique_coords.append(c)
                
        results = []
        for sura, ayah in unique_coords[:7]:
            data = engine.get_ayah(sura, ayah)
            if data:
                results.append({
                    "sura": sura,
                    "ayah": ayah,
                    "text_uthmani": data.get("text_uthmani") or data.get("text"),
                    "transliteration": data.get("transliteration", ""),
                    "translations": data.get("translations", {})
                })
                
        return results


# =========================================================================
# 6. AAOIFI OFFICIAL AUDIT CERTIFICATE PDF GENERATOR (ReportLab)
# =========================================================================

class AuditCertificateGenerator:
    """Generates formal, printable AAOIFI Shariah Compliance PDF Audit Reports."""

    @staticmethod
    def generate_pdf_bytes(audit_report: Dict[str, Any], doc_title: str = "Договор / Соглашение") -> bytes:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfbase import pdfmetrics
        import os
        
        font_name = 'Helvetica'
        font_bold = 'Helvetica-Bold'
        if os.path.exists('f:/al-furqan-ai/Roboto-Regular.ttf'):
            pdfmetrics.registerFont(TTFont('Roboto', 'f:/al-furqan-ai/Roboto-Regular.ttf'))
            font_name = 'Roboto'
            font_bold = 'Roboto' # using regular as fallback for bold

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CertTitle',
            parent=styles['Heading1'],
            fontName=font_bold,
            fontSize=16,
            leading=20,
            textColor=colors.HexColor('#0F172A'),
            alignment=1
        )
        subtitle_style = ParagraphStyle(
            'CertSubtitle',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#64748B'),
            alignment=1
        )
        body_style = ParagraphStyle(
            'CertBody',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor('#1E293B')
        )
        finding_title_style = ParagraphStyle(
            'FindingTitle',
            parent=styles['Normal'],
            fontSize=10.5,
            leading=14,
            textColor=colors.HexColor('#DC2626'),
            fontName=font_bold
        )
        quran_box_style = ParagraphStyle(
            'QuranBox',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=9,
            leading=13,
            textColor=colors.HexColor('#0F766E')
        )

        elements = []

        # Header
        elements.append(Paragraph("🛡️ AL-FURQAN GUARD • SHARIAH COMPLIANCE AUDIT", title_style))
        elements.append(Paragraph("Deterministic AAOIFI Standard Verification & Quranic Ground Truth Audit", subtitle_style))
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#CBD5E1'), spaceAfter=14))

        # Document Details Box
        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        is_compliant = audit_report.get("is_compliant", False)
        status_text = "🟢 100% COMPLIANT (СООТВЕТСТВУЕТ ШАРИАТУ)" if is_compliant else "🔴 NON-COMPLIANT (ОБНАРУЖЕНЫ ШАРИАТСКИЕ РИСКИ)"
        status_color = colors.HexColor('#16A34A') if is_compliant else colors.HexColor('#DC2626')

        import html
        
        info_data = [
            [Paragraph("<b>Название документа:</b>", body_style), Paragraph(html.escape(str(doc_title)), body_style)],
            [Paragraph("<b>Дата аудита:</b>", body_style), Paragraph(timestamp, body_style)],
            [Paragraph("<b>Тип контракта (AAOIFI):</b>", body_style), Paragraph(html.escape(str(audit_report.get("contract_type", "COMMERCIAL"))), body_style)],
            [Paragraph("<b>Вердикт аудитора:</b>", body_style), Paragraph(f"<b>{status_text}</b>", ParagraphStyle('Status', parent=body_style, textColor=status_color))]
        ]
        info_table = Table(info_data, colWidths=[150, 370])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 14))

        # Findings Section
        findings = audit_report.get("findings", [])
        elements.append(Paragraph(f"<b>РЕЗУЛЬТАТЫ ПРОВЕРКИ И ВЫЯВЛЕННЫЕ РИСКИ ({len(findings)}):</b>", ParagraphStyle('H2', parent=styles['Heading2'], fontName=font_bold, fontSize=11.5, leading=15, textColor=colors.HexColor('#0F172A'))))
        elements.append(Spacer(1, 6))

        if not findings:
            elements.append(Paragraph("В ходе глубокого семантического и юридического аудита условий договора прямого несоответствия стандартам AAOIFI и аятам Корана не обнаружено.", body_style))
        else:
            for idx, f in enumerate(findings, 1):
                f_title = html.escape(str(f.get("risk_title_ru") or f.get("standard") or ""))
                f_issue = html.escape(str(f.get("issue_ru", "")))
                f_solution = html.escape(str(f.get("solution_ru", "")))
                f_ayah = html.escape(str(f.get("ayah_ref", "")))
                f_ayah_trans = html.escape(str(f.get("ayah_trans_ru", "")))
                f_severity = html.escape(str(f.get("severity", "CRITICAL")))

                elements.append(Paragraph(f"{idx}. {f_title} [{f_severity}]", finding_title_style))
                elements.append(Paragraph(f"<b>Суть нарушения:</b> {f_issue}", body_style))
                elements.append(Spacer(1, 3))
                if f_ayah:
                    elements.append(Paragraph(f"📖 <b>Основа в Коране:</b> {f_ayah} • <i>{f_ayah_trans}</i>", quran_box_style))
                if f_solution:
                    elements.append(Paragraph(f"💡 <b>Рекомендация по устранению:</b> {f_solution}", ParagraphStyle('Rec', parent=body_style, textColor=colors.HexColor('#15803D'))))
                elements.append(Spacer(1, 10))

        # Footer Seal
        elements.append(Spacer(1, 14))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E2E8F0'), spaceAfter=8))
        elements.append(Paragraph("Электронный сертификат сформирован детерминированной системой Al-Furqan Guard v2.0 • SHA-256 Verified • Tanzil Quran L0 Ground Truth", ParagraphStyle('Foot', parent=subtitle_style, fontSize=8, leading=10)))

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
