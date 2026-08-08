from django.test import SimpleTestCase, override_settings
from apps.scheduling.bbb_service import BBBService


class BBBIntegrationTests(SimpleTestCase):
    @override_settings(BBB_URL='https://bbb.example.com/bigbluebutton/api/', BBB_SECRET='secret')
    def test_builds_signed_urls(self):
        service = BBBService()
        url = service.join_url('lesson-1', 'Student', 'attendee', '1')
        self.assertIn('https://bbb.example.com/bigbluebutton/api/join?', url)
        self.assertIn('checksum=', url)

    @override_settings(BBB_URL='', BBB_SECRET='')
    def test_unconfigured_service_does_not_call_server(self):
        service = BBBService()
        self.assertFalse(service.configured)
        self.assertFalse(service.server_healthy())
