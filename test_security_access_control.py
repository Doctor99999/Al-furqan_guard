"""
Al-Furqan AI - Access Control Regression Tests
Locks in the hardened, unauthenticated entry points:
- Telegram webhook must reject requests lacking the shared secret (403)
- Telegram webhook must accept requests carrying the correct secret
- /api/v1/feedback/list must require a valid X-Admin-Key (403 otherwise)
"""

import unittest
from fastapi.testclient import TestClient
import server
from server import app

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


if __name__ == "__main__":
    unittest.main()
