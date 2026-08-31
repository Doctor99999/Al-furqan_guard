"""
Al-Furqan AI - Anti-Hallucination Guardrail & Validator
Interceps, verifies, diffs, and auto-corrects AI outputs against the canonical Quranic manifest.
"""

import re
import difflib
from typing import Dict, List, Optional, Any, Tuple
from .quran_engine import QuranEngine, strip_tashkeel, normalize_arabic


class QuranGuard:
    """
    4-Level Ground Truth Validator for AI-generated text:
    Level 1: Contextually Anchored Citation Gate (eliminates false positives on timestamps/scores).
    Level 2: Optimal Bipartite Multi-Quote Alignment & Precision Diff Engine.
    Level 3: Exact Morphological Token & Root Verifier (No substring heuristics).
    Level 4: Span-Safe Canonical Auto-Correction & Grounding.
    """

    # Quranic contextual anchor keywords across multilingual queries
    ANCHOR_KEYWORDS = {
        'сура', 'суре', 'суры', 'суру', 'аят', 'аяте', 'аята', 'аяты', 'коран', 'коране', 'корана',
        'surah', 'sura', 'ayah', 'ayat', 'verse', 'verses', 'quran', 'qur\'an', 'koran',
        'сүре', 'сүресі', 'сүресінде', 'аят', 'аяты', 'аятында', 'құран', 'құранда',
        'سورة', 'آية', 'ايات', 'القرآن', 'قرآن',
        'sure', 'suresi', 'ayet', 'ayeti', 'kuran', 'kur\'an',
        'suro', 'sura', 'oyat', 'oyati', 'qur\'on',
        'surat', 'ayat', 'al-qur\'an'
    }

    # Muqatta'at (isolated letters) known verses for lenient diacritic treatment
    MUQATTAAT_VERSES = {
        "2:1", "3:1", "7:1", "10:1", "11:1", "12:1", "13:1", "14:1", "15:1",
        "19:1", "20:1", "26:1", "27:1", "28:1", "29:1", "30:1", "31:1", "32:1",
        "36:1", "38:1", "40:1", "41:1", "42:1", "42:2", "43:1", "44:1", "45:1",
        "46:1", "50:1", "68:1"
    }

    def __init__(self, engine: Optional[QuranEngine] = None):
        self.engine = engine or QuranEngine()

        # Regular expressions for detecting citations
        # 1. Explicit multi-lingual phrases: "сура 2 аят 255", "surah 2:255", "2-сүре 255-аят"
        self.explicit_patterns = [
            re.compile(r'сур[аеыуі]?\s*(?P<sura>\d{1,3})[,\s\-]+аят[аеы]?\s*(?P<ayah>\d{1,3})', re.IGNORECASE),
            re.compile(r'sura[h]?\s*(?P<sura>\d{1,3})[,\s\-]+(?:ayah|verse)\s*(?P<ayah>\d{1,3})', re.IGNORECASE),
            re.compile(r'(?P<sura>\d{1,3})[\-\s]*сүре(?:сі)?[\s,]+(?P<ayah>\d{1,3})[\-\s]*аят', re.IGNORECASE),
            re.compile(r'سورة\s*(?P<sura>\d{1,3})[,\s\-]+(?:آية|اية)\s*(?P<ayah>\d{1,3})', re.IGNORECASE),
            re.compile(r'(?P<sura>\d{1,3})\.\s*sure[,\s\-]+(?P<ayah>\d{1,3})\.\s*ayet', re.IGNORECASE),
        ]

        # 2. Strict bracketed numeric: [2:255], (2:255), (2/255)
        self.bracketed_pattern = re.compile(r'(?:\[|\()(?P<sura>\d{1,3})[:/](?P<ayah>\d{1,3})(?:\]|\))')

        # 3. Bare numeric pattern (requires surrounding contextual anchor keywords)
        self.bare_numeric_pattern = re.compile(r'\b(?P<sura>\d{1,3})[:/](?P<ayah>\d{1,3})\b')

        # Arabic script detection pattern (3+ consecutive Arabic words or meaningful phrases)
        self.arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF\s]{4,}')

    def _has_contextual_anchor(self, text: str, start: int, end: int, window: int = 60) -> bool:
        """Verifies if a numeric citation has Quranic keywords in its surrounding text context."""
        left = max(0, start - window)
        right = min(len(text), end + window)
        surrounding_text = text[left:right].lower()
        words = re.findall(r'[\w\'-]+', surrounding_text)
        return any(w in self.ANCHOR_KEYWORDS for w in words)

    def detect_citations(self, text: str) -> List[Dict[str, Any]]:
        """
        Extracts all Quranic citations from text with contextual grounding.
        Eliminates false positives on timestamps (14:30), scores (3:0), or versions.
        """
        found = []
        seen_spans = set()

        # Phase 1: Explicit multi-lingual patterns (high confidence)
        for pattern in self.explicit_patterns:
            for match in pattern.finditer(text):
                sura = int(match.group('sura'))
                ayah = int(match.group('ayah'))
                span = (match.start(), match.end())
                if any(s[0] <= span[0] and span[1] <= s[1] for s in seen_spans):
                    continue
                seen_spans.add(span)

                is_valid, msg = self.engine.is_valid_coordinate(sura, ayah)
                surah_name = self.engine.SURAH_NAMES_RU[sura - 1] if 1 <= sura <= 114 else "Неизвестно"

                found.append({
                    "raw_match": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                    "sura": sura,
                    "ayah": ayah,
                    "id": f"{sura}:{ayah}",
                    "is_valid": is_valid,
                    "surah_name": surah_name,
                    "status_message": msg
                })

        # Phase 2: Strict bracketed numeric: [2:255] or (2:255)
        for match in self.bracketed_pattern.finditer(text):
            sura = int(match.group('sura'))
            ayah = int(match.group('ayah'))
            span = (match.start(), match.end())
            if any(s[0] <= span[0] and span[1] <= s[1] for s in seen_spans):
                continue
            seen_spans.add(span)

            is_valid, msg = self.engine.is_valid_coordinate(sura, ayah)
            surah_name = self.engine.SURAH_NAMES_RU[sura - 1] if 1 <= sura <= 114 else "Неизвестно"

            found.append({
                "raw_match": match.group(0),
                "start": match.start(),
                "end": match.end(),
                "sura": sura,
                "ayah": ayah,
                "id": f"{sura}:{ayah}",
                "is_valid": is_valid,
                "surah_name": surah_name,
                "status_message": msg
            })

        # Phase 3: Bare numeric pattern: requires context anchor window
        for match in self.bare_numeric_pattern.finditer(text):
            span = (match.start(), match.end())
            if any(s[0] <= span[0] and span[1] <= s[1] for s in seen_spans):
                continue

            # Only accept bare numbers if grounded in Quranic context
            if self._has_contextual_anchor(text, match.start(), match.end()):
                sura = int(match.group('sura'))
                ayah = int(match.group('ayah'))
                seen_spans.add(span)

                is_valid, msg = self.engine.is_valid_coordinate(sura, ayah)
                surah_name = self.engine.SURAH_NAMES_RU[sura - 1] if 1 <= sura <= 114 else "Неизвестно"

                found.append({
                    "raw_match": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                    "sura": sura,
                    "ayah": ayah,
                    "id": f"{sura}:{ayah}",
                    "is_valid": is_valid,
                    "surah_name": surah_name,
                    "status_message": msg
                })

        # Sort by occurrence position in text
        found.sort(key=lambda x: x['start'])
        return found

    def extract_arabic_quotes(self, text: str) -> List[Dict[str, Any]]:
        """Finds Arabic text chunks within input string."""
        quotes = []
        for match in self.arabic_pattern.finditer(text):
            chunk = match.group(0).strip()
            # Ignore isolated punctuation or tiny single letters
            if len(strip_tashkeel(chunk)) >= 3:
                quotes.append({
                    "raw_text": chunk,
                    "start": match.start(),
                    "end": match.end()
                })
        return quotes

    def compute_diff(self, generated_text: str, canonical_text: str, ayah_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculates precise visual diff and similarity metric between generated and canonical text.
        Handles special Muqatta'at verses (e.g. 42:2 عسق) with proper tolerance.
        """
        gen_clean = generated_text.strip()
        can_clean = canonical_text.strip()

        # Similarity ratio
        seq = difflib.SequenceMatcher(None, gen_clean, can_clean)
        similarity = round(seq.ratio() * 100, 2)

        # Letter-only similarity (ignoring tashkeel)
        norm_gen = normalize_arabic(gen_clean)
        norm_can = normalize_arabic(can_clean)
        seq_norm = difflib.SequenceMatcher(None, norm_gen, norm_can)
        norm_similarity = round(seq_norm.ratio() * 100, 2)

        # Token diff
        diff_chunks = []
        for tag, i1, i2, j1, j2 in seq.get_opcodes():
            diff_chunks.append({
                "tag": tag,  # 'equal', 'replace', 'delete', 'insert'
                "gen": gen_clean[i1:i2],
                "canonical": can_clean[j1:j2]
            })

        is_exact = (gen_clean == can_clean)

        # Special case: Muqatta'at isolated letters (e.g. 42:2 'عسق' vs 'عٓسٓقٓ')
        if ayah_id and ayah_id in self.MUQATTAAT_VERSES:
            if norm_gen == norm_can:
                is_exact = True

        has_tashkeel_error = (not is_exact and norm_similarity >= 95.0)

        return {
            "similarity_percent": similarity,
            "text_structure_similarity": norm_similarity,
            "is_exact_match": is_exact,
            "has_tashkeel_error": has_tashkeel_error,
            "diff_chunks": diff_chunks
        }

    def verify_root_claim(self, word: str, claimed_root: str, context_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Verifies if a word originates from a specific 3/4-letter root in the canonical manifest.
        Uses exact token/lemma comparison (==) rather than substring heuristics.
        """
        word_norm = normalize_arabic(word)
        root_norm = normalize_arabic(claimed_root).replace(" ", "")

        # Prefix peeling for exact comparison
        # e.g. 'الرحمان' -> 'رحمان'
        word_stem = re.sub(r'^(?:ال|و|ف|ب|ل|ك|س)', '', word_norm)

        # 1. If context Ayah is provided (1:1 coordinate validation)
        if context_id and context_id in self.engine.ayahs:
            ayah_data = self.engine.ayahs[context_id]
            for token in ayah_data['tokens']:
                token_form_norm = normalize_arabic(token.get('form', ''))
                token_lemma_norm = normalize_arabic(token.get('lemma', '') or '')
                token_root = token.get('root')
                token_root_norm = normalize_arabic(token_root or '')

                # Exact equality against form or lemma
                is_word_match = (
                    token_form_norm == word_norm or
                    token_form_norm == word_stem or
                    token_lemma_norm == word_norm or
                    token_lemma_norm == word_stem
                )

                if is_word_match and token_root:
                    is_root_match = (token_root_norm == root_norm or token_root == claimed_root)
                    return {
                        "is_valid": is_root_match,
                        "ayah_id": context_id,
                        "word": word,
                        "claimed_root": claimed_root,
                        "canonical_root": token_root,
                        "canonical_lemma": token.get('lemma'),
                        "flags": token.get('flags', []),
                        "message": f"Корень '{claimed_root}' подтвержден для слова '{word}'" if is_root_match else f"Галлюцинация корня: в аяте {context_id} слово '{word}' имеет канонический корень '{token_root}', а не '{claimed_root}'."
                    }

        # 2. Global search in entire manifest using exact token equality
        matching_roots = set()
        for ayah in self.engine.ayahs.values():
            for token in ayah['tokens']:
                token_form_norm = normalize_arabic(token.get('form', ''))
                token_lemma_norm = normalize_arabic(token.get('lemma', '') or '')
                if token_form_norm == word_norm or token_form_norm == word_stem or token_lemma_norm == word_norm or token_lemma_norm == word_stem:
                    if token.get('root'):
                        matching_roots.add(token.get('root'))

        if not matching_roots:
            return {
                "is_valid": False,
                "word": word,
                "claimed_root": claimed_root,
                "canonical_root": None,
                "message": f"Слово '{word}' не найдено как точная словарная форма в кораническом корпусе."
            }

        is_match = any(normalize_arabic(r) == root_norm for r in matching_roots)
        return {
            "is_valid": is_match,
            "word": word,
            "claimed_root": claimed_root,
            "canonical_roots": list(matching_roots),
            "message": f"Корень подтвержден ({claimed_root})" if is_match else f"Галлюцинация корня: слово '{word}' в корпусе связано с корнем {list(matching_roots)}, а не '{claimed_root}'."
        }

    def _align_citations_and_quotes(self, citations: List[Dict[str, Any]], quotes: List[Dict[str, Any]]) -> List[Tuple[Dict[str, Any], Optional[Dict[str, Any]]]]:
        """
        Optimal bipartite matching between citations and extracted Arabic quotes.
        Matches each citation to the closest and most structurally similar Arabic quote without cross-collisions.
        """
        if not quotes:
            return [(c, None) for c in citations]

        pairs = []
        assigned_quote_indices = set()

        for cit in citations:
            if not cit['is_valid']:
                pairs.append((cit, None))
                continue

            best_quote = None
            best_quote_idx = None
            best_score = -1.0

            ayah_data = self.engine.get_ayah(cit['sura'], cit['ayah'])
            if not ayah_data:
                continue
            canonical_text = ayah_data.get('text', '') or ayah_data.get('text_uthmani', '')
            norm_canonical = normalize_arabic(canonical_text)

            for q_idx, q in enumerate(quotes):
                if q_idx in assigned_quote_indices:
                    continue

                # Distance in characters
                char_dist = min(abs(q['start'] - cit['end']), abs(cit['start'] - q['end']))
                if char_dist > 300:
                    continue  # Too far to be related

                # Structural textual similarity
                norm_quote = normalize_arabic(q['raw_text'])
                sim = difflib.SequenceMatcher(None, norm_quote, norm_canonical).ratio()

                # Weighted matching score (combines text similarity + spatial proximity)
                proximity_score = max(0.0, 1.0 - (char_dist / 300.0))
                total_score = (sim * 0.7) + (proximity_score * 0.3)

                if total_score > best_score and (sim >= 0.25 or proximity_score >= 0.8):
                    best_score = total_score
                    best_quote = q
                    best_quote_idx = q_idx

            if best_quote and best_quote_idx is not None:
                assigned_quote_indices.add(best_quote_idx)
                pairs.append((cit, best_quote))
            else:
                pairs.append((cit, None))

        return pairs

    def verify_full_text(self, text: str) -> Dict[str, Any]:
        """
        Master Anti-Hallucination Pipeline:
        Scans complete text for quotes, citations, and Arabic verses.
        Returns detailed audit, hallucination alerts, visual diffs, and span-safe auto-corrections.
        """
        citations = self.detect_citations(text)
        arabic_quotes = self.extract_arabic_quotes(text)

        hallucinations = []
        verified_items = []

        # Replacements to apply (list of (start, end, replacement_text))
        replacements = []

        # Optimal bipartite matching
        citation_quote_pairs = self._align_citations_and_quotes(citations, arabic_quotes)

        for cit, matched_arabic in citation_quote_pairs:
            if not cit['is_valid']:
                hallucinations.append({
                    "type": "INVALID_COORDINATE",
                    "severity": "CRITICAL",
                    "match": cit['raw_match'],
                    "sura": cit['sura'],
                    "ayah": cit['ayah'],
                    "error_description": cit['status_message'],
                    "suggested_fix": f"В суре {cit['sura']} всего {self.engine.CANONICAL_AYAH_COUNTS[cit['sura']-1] if 1 <= cit['sura'] <= 114 else 0} аятов."
                })
            else:
                ayah_record = self.engine.get_ayah(cit['sura'], cit['ayah'])
                if not ayah_record:
                    continue
                canonical_text = ayah_record.get('text', '') or ayah_record.get('text_uthmani', '')
                canonical_id = cit['id']

                if matched_arabic:
                    diff_info = self.compute_diff(matched_arabic['raw_text'], canonical_text, ayah_id=canonical_id)
                    if diff_info['is_exact_match']:
                        verified_items.append({
                            "type": "EXACT_CITATION",
                            "id": canonical_id,
                            "surah_name": cit['surah_name'],
                            "text": canonical_text,
                            "transliteration": ayah_record.get('transliteration', ''),
                            "translations": ayah_record.get('translations', {}),
                            "tokens": ayah_record['tokens'],
                            "content_verified": True
                        })
                    else:
                        error_type = "TASHKEEL_DISTORTION" if diff_info['has_tashkeel_error'] else "TEXT_MUTATION"
                        hallucinations.append({
                            "type": error_type,
                            "severity": "HIGH" if error_type == "TEXT_MUTATION" else "MEDIUM",
                            "id": canonical_id,
                            "surah_name": cit['surah_name'],
                            "generated_quote": matched_arabic['raw_text'],
                            "canonical_quote": canonical_text,
                            "transliteration": ayah_record.get('transliteration', ''),
                            "translations": ayah_record.get('translations', {}),
                            "diff": diff_info,
                            "error_description": "Обнаружено искажение огласовок (ташкиля)" if error_type == "TASHKEEL_DISTORTION" else "Обнаружено искажение букв или слов в цитате аята",
                            "suggested_fix": canonical_text
                        })
                        # Schedule span replacement
                        replacements.append((matched_arabic['start'], matched_arabic['end'], canonical_text))
                else:
                    verified_items.append({
                        "type": "VALID_COORDINATE",
                        "id": canonical_id,
                        "surah_name": cit['surah_name'],
                        "canonical_text": canonical_text,
                        "transliteration": ayah_record.get('transliteration', ''),
                        "translations": ayah_record.get('translations', {}),
                        "tokens": ayah_record['tokens'],
                        "content_verified": False,
                        "note_ru": "Проверена только координата (сура:аят). Текст цитаты не сверен с каноном, т.к. арабский текст цитаты отсутствует."
                    })

        # Apply span-safe replacements from right-to-left
        corrected_text = text
        replacements.sort(key=lambda x: x[0], reverse=True)
        for start, end, rep in replacements:
            corrected_text = corrected_text[:start] + rep + corrected_text[end:]

        # Content-verification accounting:
        # EXACT_CITATION  => quote text + coordinates matched canonical Tanzil text
        # VALID_COORDINATE => coordinates are valid, but quote content was NOT verified
        #                     (no Arabic quote present to diff against the canonical text)
        content_verified_count = sum(1 for v in verified_items if v.get("content_verified"))
        coordinate_only_count = len(verified_items) - content_verified_count

        # Trust score calculation
        total_checks = len(citations)
        if total_checks == 0:
            trust_score = 100.0 if not hallucinations else 0.0
            verdict = "NO_CITATIONS_FOUND"
            verdict_ru = "Цитат и ссылок на Коран в тексте не обнаружено"
        else:
            critical_count = sum(1 for h in hallucinations if h['severity'] == 'CRITICAL')
            high_count = sum(1 for h in hallucinations if h['severity'] == 'HIGH')
            med_count = sum(1 for h in hallucinations if h['severity'] == 'MEDIUM')

            deductions = (critical_count * 50) + (high_count * 30) + (med_count * 15)
            trust_score = max(0.0, 100.0 - deductions)

            if critical_count > 0 or high_count > 0:
                verdict = "HALLUCINATION_DETECTED"
                verdict_ru = "Обнаружена галлюцинация или искажение текста Корана"
            elif med_count > 0:
                verdict = "MINOR_WARNINGS"
                verdict_ru = "Предупреждение: обнаружены неточности в огласовках (ташкиле)"
            elif coordinate_only_count == 0:
                verdict = "VERIFIED_CANONICAL"
                verdict_ru = "Текст полностью верифицирован и соответствует каноническому манифесту"
            elif content_verified_count > 0:
                verdict = "VERIFIED_CANONICAL_PARTIAL"
                verdict_ru = "Частичная сверка: часть цитат соответствует канону, остальные проверены только по номерам аятов"
            else:
                verdict = "VERIFIED_COORDINATES_ONLY"
                verdict_ru = "Номера аятов корректны, но текст цитат не сверен с каноном (арабский текст цитат отсутствует)"

        # Backwards-compatible aliases consumed by bot.py and ui/app.js:
        # claims_detected / is_valid / violations[{type, details}]
        violations = []
        for h in hallucinations:
            v = dict(h)
            v.setdefault("details", h.get("error_description", ""))
            violations.append(v)

        return {
            "trust_score": round(trust_score, 1),
            "verdict": verdict,
            "verdict_ru": verdict_ru,
            "total_citations_found": len(citations),
            "hallucinations_count": len(hallucinations),
            "hallucinations": hallucinations,
            "verified_items": verified_items,
            "corrected_text": corrected_text,
            "original_text": text,
            "claims_detected": len(citations) > 0,
            "content_verified_count": content_verified_count,
            "coordinate_only_count": coordinate_only_count,
            "contains_unverified_content": coordinate_only_count > 0,
            "is_valid": len(hallucinations) == 0,
            "violations": violations
        }
