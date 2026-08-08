import hashlib
import hmac
from django.test import SimpleTestCase, override_settings
from apps.messaging.guppy import verify_webhook, get_guppy_status


class GuppyIntegrationTests(SimpleTestCase):
    @override_settings(GUPPY_WEBHOOK_SECRET='secret')
    def test_verifies_webhook_signature(self):
        payload = b'{"type":"message.received"}'
        signature = hmac.new(b'secret', payload, hashlib.sha256).hexdigest()
        self.assertTrue(verify_webhook(payload, f'sha256={signature}'))
        self.assertFalse(verify_webhook(payload, 'sha256=bad'))

    @override_settings(GUPPY_ENABLED=False)
    def test_disabled_status_is_safe(self):
        self.assertEqual(get_guppy_status(), {'enabled': False, 'online': False})
