"""
Al-Furqan AI - Production Readiness Regression Tests
Locks in behavior a public release depends on:
- PDF audit route actually parses a real PDF (was previously untested)
- Token-bucket rate limiters answer 429 once exhausted
- Pydantic payload boundaries reject oversized / empty base64 bodies (422)
- OCR error responses never leak internal exception details (str(e) sanitized)
"""

import base64
import json
import os
import unittest
from fastapi.testclient import TestClient

import server
from server import app, pdf_rate_limiter, ocr_rate_limiter
from quran_guard.multimodal import AuditCertificateGenerator

client = TestClient(app)


class TestRateLimiting(unittest.TestCase):

    def test_pdf_rate_limiter_answers_429_after_exhaustion(self):
        """Exhausting the 3-token bucket must yield 429 with Retry-After on the 4th call."""
        pdf_rate_limiter.buckets.clear()
        statuses = []
        for _ in range(4):
            resp = client.post(
                "/api/v1/documents/audit-pdf",
                json={"pdf_base64": "!!!not-base64!!!"},  # decode error -> 400 (token still consumed)
            )
            statuses.append(resp.status_code)
        self.assertEqual(statuses[:3], [400, 400, 400],
                         "First three calls must pass the rate limiter")
        self.assertEqual(statuses[3], 429,
                         "Fourth call within the window must be rate-limited")
        retry = resp.headers.get("retry-after")
        self.assertIsNotNone(retry, "429 response should carry Retry-After")

    def test_pdf_rate_limiter_resets_buckets_for_other_tests(self):
        """A freshly cleared bucket admits requests again (keeps suite deterministic)."""
        pdf_rate_limiter.buckets.clear()
        resp = client.post("/api/v1/documents/audit-pdf",
                           json={"pdf_base64": "!!!not-base64!!!"})
        self.assertEqual(resp.status_code, 400, "Limiter reset must admit a new request")


class TestPayloadBoundaries(unittest.TestCase):

    def test_oversized_ocr_base64_rejected(self):
        """Payloads beyond the ImageScanRequest cap must fail validation (422)."""
        oversized = "A" * (10_000_000 + 1)
        resp = client.post("/api/v1/images/audit-ocr",
                           json={"image_base64": oversized})
        self.assertEqual(resp.status_code, 422)

    def test_empty_pdf_base64_rejected(self):
        """Empty payloads must fail validation (422), not reach business logic."""
        resp = client.post("/api/v1/documents/audit-pdf",
                           json={"pdf_base64": ""})
        self.assertEqual(resp.status_code, 422)


class TestOcrErrorSanitization(unittest.TestCase):

    def test_ocr_failure_returns_generic_message(self):
        """Internal exception details must never leak: unreadable image => success(NOT_FOUND), not an error dump."""
        ocr_rate_limiter.buckets.clear()
        resp = client.post("/api/v1/images/audit-ocr",
                           json={"image_base64": base64.b64encode(b"this-is-not-an-image").decode()})
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["status"], "success")
        self.assertEqual(body["halal_verdict"], "NOT_FOUND")
        self.assertFalse(body["ocr_text_read"])
        self.assertNotIn("Traceback", json.dumps(resp.json()))
        self.assertNotIn("File \"", json.dumps(resp.json()))
        self.assertNotIn("PIL", json.dumps(resp.json()))
        self.assertNotIn("cannot identify image file", json.dumps(resp.json()))


class TestPdfAuditRealPipeline(unittest.TestCase):

    def test_real_pdf_is_audited_end_to_end(self):
        """POST /documents/audit-pdf parses a real generated PDF and returns audit totals."""
        pdf_bytes = AuditCertificateGenerator.generate_pdf_bytes(
            audit_report={
                "is_compliant": True,
                "contract_type": "GENERAL_COMMERCIAL",
                "findings": [],
                "quran_basis": "2:275 • 4:29",
            },
            doc_title="Production Readiness Test",
        )
        pdf_rate_limiter.buckets.clear()
        resp = client.post(
            "/api/v1/documents/audit-pdf",
            json={"pdf_base64": base64.b64encode(pdf_bytes).decode()},
        )
        self.assertEqual(resp.status_code, 200, resp.text[:200])
        audit = resp.json()["audit"]
        self.assertGreaterEqual(audit["total_pages"], 1)
        self.assertIn("guard_report", audit)
        self.assertIn("aaoifi_report", audit)


class TestBodySizeLimit(unittest.TestCase):

    def test_oversized_body_rejected_before_parsing(self):
        """Middleware must return 413 (not 422) when Content-Length exceeds the limit."""
        old = os.environ.get("MAX_BODY_BYTES")
        os.environ["MAX_BODY_BYTES"] = "256"
        try:
            resp = client.post("/api/v1/guard/validate",
                               json={"text": "x" * 5000})
        finally:
            if old is None:
                os.environ.pop("MAX_BODY_BYTES", None)
            else:
                os.environ["MAX_BODY_BYTES"] = old
        self.assertEqual(resp.status_code, 413)
        self.assertIn("Payload Too Large", resp.text)

    def test_small_body_still_reaches_route(self):
        """A normal-sized body is not blocked by the size guard."""
        resp = client.post("/api/v1/guard/validate",
                           json={"text": "Проверка обычного текста без цитат."})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["verdict"], "NO_CITATIONS_FOUND")


class TestImageOcrRouteWorks(unittest.TestCase):

    def test_valid_image_runs_ocr_pipeline(self):
        """A decodable image must reach the OCR pipeline (regression: AttributeError on engine.screen_halal)."""
        from PIL import Image
        import io as _io
        buf = _io.BytesIO()
        Image.new("RGB", (64, 64), (0, 0, 0)).save(buf, format="PNG")
        payload = base64.b64encode(buf.getvalue()).decode()
        ocr_rate_limiter.buckets.clear()
        resp = client.post("/api/v1/images/audit-ocr", json={"image_base64": payload})
        self.assertEqual(resp.status_code, 200, resp.text[:300])
        body = resp.json()
        self.assertEqual(body["status"], "success")
        blob = json.dumps(body)
        self.assertNotIn("Traceback", blob)
        self.assertNotIn("AttributeError", blob)
        self.assertNotIn('File "', blob)

    def test_unreadable_image_never_claimed_halal(self):
        """Corrupt image bytes must NOT be analyzed: garbage previously produced a false 'HALAL' verdict."""
        garbage = base64.b64encode(b"\x80PNG garbage-not-a-png").decode()
        ocr_rate_limiter.buckets.clear()
        resp = client.post("/api/v1/images/audit-ocr", json={"image_base64": garbage})
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertNotEqual(body.get("halal_verdict"), "HALAL")
        self.assertTrue(body.get("ocr_text_read") is False)
        self.assertNotIn("Traceback", json.dumps(body))
        self.assertNotIn("cannot identify image file", json.dumps(body))


class TestPdfErrorNoInternalLeak(unittest.TestCase):

    def test_corrupt_pdf_returns_400_without_internal_details(self):
        """PDF parse failures must return 400 (not 200-with-leak) and never expose str(e)."""
        garbage = base64.b64encode(b"%%PDF-1.4\n% broken trailer").decode()
        pdf_rate_limiter.buckets.clear()
        resp = client.post("/api/v1/documents/audit-pdf", json={"pdf_base64": garbage})
        self.assertEqual(resp.status_code, 400, resp.text[:300])
        self.assertNotIn("Stream has ended unexpectedly", resp.text)
        self.assertNotIn("Traceback", resp.text)
        self.assertNotIn('File "', resp.text)


if __name__ == "__main__":
    unittest.main()