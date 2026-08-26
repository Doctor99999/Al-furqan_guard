"""
Al-Furqan AI - Access Control Regression Tests
Locks in the hardened, unauthenticated entry points:
- Telegram webhook must reject requests lacking the shared secret (403)
- Telegram webhook must accept requests carrying the correct secret
- /api/v1/feedback/list must require a valid X-Admin-Key (403 otherwise)
"""

import hashlib
import unittest
from fastapi.testclient import TestClient
import server
from server import app
from database import B2BAuthService, DBConnection

client = TestClient(app)


class TestAccessControl(unittest.TestCase):

    def test_webhook_rejects_without_secret(self):
        """Forged webhook posts without the secret token must be refused."""
        app.state.bot_app = object()
        app.state.telegram_webhook_secret = "unit-test-secret"
        resp = client.post("/api/v1/telegram-webhook", json={"update_id": 1})
        self.assertEqual(resp.status_code, 403,
                         "Webhook must reject requests without X-Telegram-Bot-Api-Secret-Token")

    def test_webhook_accepts_with_secret(self):
        """A request carrying the correct secret must pass the gate (not 403)."""
        app.state.bot_app = object()
        app.state.telegram_webhook_secret = "unit-test-secret"
        resp = client.post(
            "/api/v1/telegram-webhook",
            json={"update_id": 1},
            headers={"X-Telegram-Bot-Api-Secret-Token": "unit-test-secret"},
        )
        self.assertNotEqual(resp.status_code, 403,
                            "Webhook must accept requests with the correct secret token")

    def test_feedback_list_requires_admin_key(self):
        """Feedback PII must stay private without a valid X-Admin-Key."""
        original = server.ADMIN_API_KEY
        try:
            server.ADMIN_API_KEY = "unit-test-admin"
            # No header -> 403
            resp = client.get("/api/v1/feedback/list")
            self.assertEqual(resp.status_code, 403,
                             "Feedback list must reject requests without X-Admin-Key")
            # Wrong header -> 403
            resp = client.get("/api/v1/feedback/list", headers={"X-Admin-Key": "wrong"})
            self.assertEqual(resp.status_code, 403,
                             "Feedback list must reject a wrong X-Admin-Key")
            # Correct header -> 200 and returns a feedback collection
            resp = client.get("/api/v1/feedback/list",
                              headers={"X-Admin-Key": "unit-test-admin"})
            self.assertEqual(resp.status_code, 200)
            self.assertIn("feedback", resp.json())
        finally:
            server.ADMIN_API_KEY = original


class TestB2BApiKeyHashing(unittest.TestCase):
    """Locks in the SHA-256 + constant-time B2B key storage (no plaintext at rest)."""

    def _insert_org(self, org_name, api_key=None, key_hash=None, is_active=1):
        conn = DBConnection.get_sqlite_conn()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO b2b_organizations
               (org_name, api_key, key_hash, is_active, tier, total_requests)
               VALUES (?, ?, ?, ?, 'free', 0)""",
            (org_name, api_key or "", key_hash or "", is_active),
        )
        conn.commit()
        oid = cur.lastrowid
        conn.close()
        return oid

    def _delete_org(self, oid):
        conn = DBConnection.get_sqlite_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM b2b_organizations WHERE id = ?", (oid,))
        conn.commit()
        conn.close()

    def test_hashed_key_validates(self):
        key = "b2b-secret-key-123"
        oid = self._insert_org("Hashed Test Org",
                               key_hash=hashlib.sha256(key.encode()).hexdigest())
        try:
            model = B2BAuthService.validate_api_key(key)
            self.assertIsNotNone(model, "Valid hashed API key must authenticate")
            self.assertEqual(model.org_name, "Hashed Test Org")
            self.assertEqual(model.api_key, "",
                             "Returned model must never carry the raw key")
            self.assertIsNone(B2BAuthService.validate_api_key("definitely-wrong"),
                              "Wrong key must not authenticate")
        finally:
            self._delete_org(oid)

    def test_legacy_plaintext_key_is_upgraded(self):
        legacy = "legacy-plaintext-key"
        oid = self._insert_org("Legacy Test Org", api_key=legacy, key_hash="")
        try:
            model = B2BAuthService.validate_api_key(legacy)
            self.assertIsNotNone(model, "Legacy plaintext key must still authenticate")
            conn = DBConnection.get_sqlite_conn()
            cur = conn.cursor()
            cur.execute("SELECT api_key, key_hash FROM b2b_organizations WHERE id = ?", (oid,))
            row = cur.fetchone()
            conn.close()
            self.assertEqual(row["key_hash"], hashlib.sha256(legacy.encode()).hexdigest(),
                             "Legacy row must be upgraded to SHA-256 hash")
            self.assertNotEqual(row["api_key"], legacy,
                                "Plaintext key must be replaced after upgrade")
        finally:
            self._delete_org(oid)


if __name__ == "__main__":
    unittest.main()
