from unittest.mock import patch
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from apps.accounts.models import User
from apps.payments.models import Subscription


class PaymentFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student', email='student@example.com', password='Test@1234')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    @override_settings(PAYSTACK_SECRET_KEY='test-secret')
    @patch('apps.payments.paystack.initialize')
    def test_subscription_initialization(self, initialize):
        initialize.return_value = {'authorization_url': 'https://paystack.test/pay'}
        response = self.client.post('/api/payments/subscriptions/', {'plan': 'pro', 'billing_cycle': 'monthly'}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['authorization_url'], 'https://paystack.test/pay')
        self.assertTrue(Subscription.objects.filter(user=self.user, status='pending').exists())

    @patch('apps.payments.paystack.verify')
    def test_verify_subscription_activates_plan(self, verify):
        subscription = Subscription.objects.create(user=self.user, plan='pro', billing_cycle='monthly', amount=89, paystack_ref='sub-ref')
        verify.return_value = {'status': 'success'}
        response = self.client.get('/api/payments/verify/?reference=sub-ref')
        self.assertEqual(response.status_code, 200)
        subscription.refresh_from_db()
        self.assertEqual(subscription.status, 'active')
        self.user.refresh_from_db()
        self.assertEqual(self.user.subscription_plan, 'pro')

    @override_settings(PAYSTACK_SECRET_KEY='test-secret')
    @patch('apps.payments.paystack.initialize')
    def test_lesson_payment_initialization(self, initialize):
        from apps.tutors.models import TutorProfile, Subject
        from apps.scheduling.models import Lesson
        from django.utils import timezone
        from datetime import timedelta
        tutor = User.objects.create_user(username='tutor', email='tutor@example.com', password='Test@1234', role='tutor')
        TutorProfile.objects.create(user=tutor, hourly_rate=80, approval_status='approved')
        subject = Subject.objects.create(name='Maths', slug='maths')
        lesson = Lesson.objects.create(tutor=tutor, student=self.user, subject=subject,
            start_time=timezone.now() + timedelta(days=1), end_time=timezone.now() + timedelta(days=1, hours=1), price=80)
        initialize.return_value = {'authorization_url': 'https://paystack.test/lesson'}
        response = self.client.post('/api/payments/initiate/', {'lesson_id': lesson.id}, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data['authorization_url'], 'https://paystack.test/lesson')

    @override_settings(PAYSTACK_SECRET_KEY='test-secret')
    @patch('apps.payments.paystack.create_transfer')
    @patch('apps.payments.paystack.create_transfer_recipient')
    def test_admin_can_process_payout(self, recipient, transfer):
        from apps.tutors.models import TutorProfile
        tutor = User.objects.create_user(username='tutor2', email='tutor2@example.com', password='Test@1234', role='tutor')
        TutorProfile.objects.create(user=tutor, pending_payout=100)
        from apps.payments.models import Payout
        payout = Payout.objects.create(tutor=tutor, amount=50, details={'number': '0240000000'})
        admin = User.objects.create_user(username='admin', email='admin@example.com', password='Test@1234', role='admin', is_staff=True, is_superuser=True)
        self.client.force_authenticate(admin)
        recipient.return_value = 'RCP_test'
        transfer.return_value = {'transfer_code': 'TRF_test'}
        response = self.client.post(f'/api/payments/payouts/{payout.id}/process/')
        self.assertEqual(response.status_code, 200)
        payout.refresh_from_db()
        self.assertEqual(payout.status, 'processing')
