"""
Gooprep Backend Unit Tests
Tests all core modules: auth, tutors, scheduling, payments, messaging, admin_panel
"""
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


def make_user(email, role='student', password='Test@1234', **kw):
    uname = email.split('@')[0]
    u = User.objects.create_user(username=uname, email=email, password=password,
                                  first_name='Test', last_name='User', role=role, **kw)
    return u


def auth_client(user, password='Test@1234'):
    c = APIClient()
    resp = c.post('/api/auth/token/', {'email': user.email, 'password': password}, format='json')
    assert resp.status_code == 200, f"Login failed: {resp.data}"
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")
    return c


# ── 1. Account Tests ──────────────────────────────────────────────
class RegisterTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_student(self):
        resp = self.client.post('/api/auth/register/', {
            'email': 'student@test.com', 'username': 'student1',
            'first_name': 'Alice', 'last_name': 'Mensah',
            'password': 'Test@1234', 'password2': 'Test@1234',
            'role': 'student',
        }, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertIn('access', resp.data)
        self.assertIn('user', resp.data)
        self.assertEqual(resp.data['user']['role'], 'student')

    def test_register_with_referral(self):
        resp = self.client.post('/api/auth/register/', {
            'email': 'referred@test.com', 'username': 'referred1',
            'first_name': 'Bob', 'last_name': 'Asante',
            'password': 'Test@1234', 'password2': 'Test@1234',
            'role': 'student', 'was_referred': True,
            'referrer_name': 'Kwame Boateng',
            'referrer_notes': 'My teacher at GIS',
        }, format='json')
        self.assertEqual(resp.status_code, 201)
        u = User.objects.get(email='referred@test.com')
        self.assertTrue(u.was_referred)
        self.assertEqual(u.referrer_name, 'Kwame Boateng')

    def test_register_missing_referrer_name(self):
        resp = self.client.post('/api/auth/register/', {
            'email': 'x@test.com', 'username': 'x1',
            'first_name': 'X', 'last_name': 'Y',
            'password': 'Test@1234', 'password2': 'Test@1234',
            'role': 'student', 'was_referred': True,
            'referrer_name': '',
        }, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_register_duplicate_email(self):
        make_user('dup@test.com')
        resp = self.client.post('/api/auth/register/', {
            'email': 'dup@test.com', 'username': 'dup2',
            'first_name': 'D', 'last_name': 'U',
            'password': 'Test@1234', 'password2': 'Test@1234', 'role': 'student',
        }, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_register_password_mismatch(self):
        resp = self.client.post('/api/auth/register/', {
            'email': 'mm@test.com', 'username': 'mm1',
            'first_name': 'M', 'last_name': 'M',
            'password': 'Test@1234', 'password2': 'Wrong@5678', 'role': 'student',
        }, format='json')
        self.assertEqual(resp.status_code, 400)


class LoginTestCase(TestCase):
    def setUp(self):
        self.user = make_user('login@test.com')
        self.client = APIClient()

    def test_login_success(self):
        resp = self.client.post('/api/auth/token/', {'email': 'login@test.com', 'password': 'Test@1234'}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('access', resp.data)
        self.assertIn('user', resp.data)

    def test_login_wrong_password(self):
        resp = self.client.post('/api/auth/token/', {'email': 'login@test.com', 'password': 'wrong'}, format='json')
        self.assertEqual(resp.status_code, 401)

    def test_me_endpoint(self):
        c = auth_client(self.user)
        resp = c.get('/api/auth/users/me/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['email'], 'login@test.com')

    def test_me_unauthenticated(self):
        resp = self.client.get('/api/auth/users/me/')
        self.assertEqual(resp.status_code, 401)

    def test_update_profile(self):
        c = auth_client(self.user)
        resp = c.patch('/api/auth/users/me/', {'city': 'Accra', 'bio': 'I love learning'}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['city'], 'Accra')

    def test_password_change(self):
        c = auth_client(self.user)
        resp = c.post('/api/auth/password/change/', {
            'old_password': 'Test@1234', 'new_password1': 'NewPass@9999', 'new_password2': 'NewPass@9999'
        }, format='json')
        self.assertEqual(resp.status_code, 200)

    def test_password_change_wrong_old(self):
        c = auth_client(self.user)
        resp = c.post('/api/auth/password/change/', {
            'old_password': 'wrong', 'new_password1': 'NewPass@9999', 'new_password2': 'NewPass@9999'
        }, format='json')
        self.assertEqual(resp.status_code, 400)


class NotificationTestCase(TestCase):
    def setUp(self):
        self.user = make_user('notif@test.com')
        self.client = auth_client(self.user)
        from apps.accounts.models import Notification
        Notification.objects.create(user=self.user, title='Test', message='Hello', notification_type='system')

    def test_list_notifications(self):
        resp = self.client.get('/api/auth/notifications/')
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(len(resp.data), 1)

    def test_mark_all_read(self):
        resp = self.client.post('/api/auth/notifications/mark-read/')
        self.assertEqual(resp.status_code, 200)


# ── 2. Tutor Tests ────────────────────────────────────────────────
class SubjectTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        from apps.tutors.models import Subject
        Subject.objects.create(name='Mathematics', slug='mathematics')
        Subject.objects.create(name='English', slug='english')

    def test_list_subjects(self):
        resp = self.client.get('/api/tutors/subjects/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 2)


class TutorProfileTestCase(TestCase):
    def setUp(self):
        from apps.tutors.models import Subject
        self.subj  = Subject.objects.create(name='Physics', slug='physics')
        self.tutor = make_user('tutor@test.com', role='tutor')
        from apps.tutors.models import TutorProfile
        self.tp = TutorProfile.objects.create(
            user=self.tutor, headline='Physics Expert',
            hourly_rate=80, approval_status='approved'
        )
        self.tp.subjects.add(self.subj)
        self.client = APIClient()

    def test_list_tutors(self):
        resp = self.client.get('/api/tutors/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 1)
        self.assertEqual(resp.data['results'][0]['headline'], 'Physics Expert')

    def test_tutor_detail(self):
        resp = self.client.get(f'/api/tutors/{self.tp.id}/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['hourly_rate'], '80.00')

    def test_my_profile_unauthenticated(self):
        resp = self.client.get('/api/tutors/my-profile/')
        self.assertEqual(resp.status_code, 401)

    def test_my_profile_authenticated(self):
        c = auth_client(self.tutor)
        resp = c.get('/api/tutors/my-profile/')
        self.assertEqual(resp.status_code, 200)

    def test_update_my_profile(self):
        c = auth_client(self.tutor)
        resp = c.patch('/api/tutors/my-profile/', {'headline': 'Updated Headline', 'hourly_rate': '120.00'}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['headline'], 'Updated Headline')

    def test_search_tutor(self):
        resp = self.client.get('/api/tutors/?search=Physics')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 1)

    def test_filter_by_subject(self):
        resp = self.client.get('/api/tutors/?subject=physics')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 1)

    def test_favourite_toggle(self):
        student = make_user('stud@test.com')
        c = auth_client(student)
        resp = c.post(f'/api/tutors/{self.tp.id}/favourite/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.data['favourited'])
        # Toggle off
        resp = c.post(f'/api/tutors/{self.tp.id}/favourite/')
        self.assertFalse(resp.data['favourited'])


class TutorOnboardingTestCase(TestCase):
    def setUp(self):
        from apps.tutors.models import Subject
        self.subj  = Subject.objects.create(name='Chemistry', slug='chemistry')
        self.tutor = make_user('onboard@test.com')
        self.client = auth_client(self.tutor)

    def test_onboarding_submit(self):
        resp = self.client.post('/api/tutors/onboarding/', {
            'headline': 'Chemistry Tutor',
            'bio': 'I teach chemistry to WAEC students.',
            'years_experience': 3,
            'hourly_rate': 70,
            'subjects': [self.subj.id],
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.data['submitted'])
        self.assertEqual(resp.data['status'], 'pending')


# ── 3. Scheduling Tests ───────────────────────────────────────────
class LessonTestCase(TestCase):
    def setUp(self):
        from apps.tutors.models import Subject, TutorProfile
        from django.utils import timezone
        self.subj    = Subject.objects.create(name='Maths', slug='maths')
        self.tutor   = make_user('tutor2@test.com', role='tutor')
        self.student = make_user('student2@test.com', role='student')
        self.tp      = TutorProfile.objects.create(user=self.tutor, hourly_rate=60, approval_status='approved')
        self.now     = timezone.now()

    def _book(self, client=None, extra=None):
        if client is None:
            client = auth_client(self.student)
        from django.utils import timezone
        start = timezone.now().replace(microsecond=0)
        from datetime import timedelta
        end   = start + timedelta(hours=1)
        data  = {
            'tutor':      self.tutor.id,
            'subject':    self.subj.id,
            'start_time': start.isoformat(),
            'end_time':   end.isoformat(),
            'price':      60,
            'currency':   'GHS',
        }
        if extra: data.update(extra)
        return client.post('/api/scheduling/lessons/', data, format='json')

    def test_book_lesson(self):
        c    = auth_client(self.student)
        resp = self._book(c)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data['status'], 'confirmed')

    def test_book_on_behalf(self):
        parent  = make_user('parent@test.com')
        c       = auth_client(parent)
        resp    = self._book(c, extra={
            'booked_on_behalf':    True,
            'booker_name':         'Ama Boateng',
            'booker_relationship': 'Parent',
            'booker_phone':        '+233244000000',
            'booker_email':        'parent@test.com',
            'learner_email':       self.student.email,
        })
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(resp.data['booked_on_behalf'])
        self.assertEqual(resp.data['booker_name'], 'Ama Boateng')
        self.assertEqual(resp.data['booker_relationship'], 'Parent')
        # Student should be the actual learner, not the parent
        from apps.scheduling.models import Lesson
        lesson = Lesson.objects.get(id=resp.data['id'])
        self.assertEqual(lesson.student.email, self.student.email)

    def test_lesson_list_as_student(self):
        c = auth_client(self.student)
        self._book(c)
        resp = c.get('/api/scheduling/lessons/')
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(resp.data['count'], 1)

    def test_lesson_list_as_tutor(self):
        c_s = auth_client(self.student)
        self._book(c_s)
        c_t = auth_client(self.tutor)
        resp = c_t.get('/api/scheduling/lessons/')
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(resp.data['count'], 1)

    def test_reschedule_lesson(self):
        c    = auth_client(self.student)
        resp = self._book(c)
        lid  = resp.data['id']
        from django.utils import timezone
        from datetime import timedelta
        new_start = (timezone.now() + timedelta(days=2)).isoformat()
        new_end   = (timezone.now() + timedelta(days=2, hours=1)).isoformat()
        resp2 = c.post(f'/api/scheduling/lessons/{lid}/reschedule/',
                       {'new_start_time': new_start, 'new_end_time': new_end}, format='json')
        self.assertEqual(resp2.status_code, 200)
        self.assertTrue(resp2.data['rescheduled'])

    @override_settings(BBB_URL='', BBB_SECRET='')
    def test_join_lesson_no_bbb(self):
        c    = auth_client(self.student)
        resp = self._book(c)
        lid  = resp.data['id']
        resp2 = c.post(f'/api/scheduling/lessons/{lid}/join/')
        # Without BBB configured, should return a friendly error
        self.assertIn(resp2.status_code, [200, 503])
        if resp2.status_code == 200:
            self.assertIsNone(resp2.data.get('join_url'))

    def test_end_lesson_as_student_forbidden(self):
        c    = auth_client(self.student)
        resp = self._book(c)
        lid  = resp.data['id']
        resp2 = c.post(f'/api/scheduling/lessons/{lid}/end/')
        self.assertEqual(resp2.status_code, 403)

    def test_end_lesson_as_tutor(self):
        c    = auth_client(self.student)
        resp = self._book(c)
        lid  = resp.data['id']
        ct   = auth_client(self.tutor)
        resp2 = ct.post(f'/api/scheduling/lessons/{lid}/end/')
        self.assertEqual(resp2.status_code, 200)
        self.assertTrue(resp2.data['ended'])


# ── 4. Payment Tests ──────────────────────────────────────────────
class TransactionTestCase(TestCase):
    def setUp(self):
        self.user = make_user('payer@test.com')
        self.client = auth_client(self.user)

    def test_list_transactions_empty(self):
        resp = self.client.get('/api/payments/transactions/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 0)

    def test_list_payouts_empty(self):
        resp = self.client.get('/api/payments/payouts/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 0)


class DisputeTestCase(TestCase):
    def setUp(self):
        from apps.tutors.models import Subject, TutorProfile
        from apps.scheduling.models import Lesson
        from django.utils import timezone
        from datetime import timedelta
        self.tutor   = make_user('dtutor@test.com', role='tutor')
        self.student = make_user('dstudent@test.com', role='student')
        TutorProfile.objects.create(user=self.tutor, hourly_rate=60, approval_status='approved')
        subj   = Subject.objects.create(name='Bio', slug='bio')
        start  = timezone.now()
        self.lesson = Lesson.objects.create(
            tutor=self.tutor, student=self.student, subject=subj,
            start_time=start, end_time=start+timedelta(hours=1),
            price=60, status='completed', payment_status='paid'
        )
        self.client = auth_client(self.student)

    def test_file_dispute(self):
        resp = self.client.post('/api/payments/disputes/', {
            'lesson': self.lesson.id,
            'reason': 'Tutor did not show up.',
        }, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data['status'], 'open')


# ── 5. Messaging Tests ────────────────────────────────────────────
class MessagingTestCase(TestCase):
    def setUp(self):
        self.user1 = make_user('msg1@test.com')
        self.user2 = make_user('msg2@test.com')
        self.c1    = auth_client(self.user1)

    def test_create_conversation(self):
        resp = self.c1.post('/api/messaging/conversations/', {'user_id': self.user2.id}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('id', resp.data)

    def test_list_conversations(self):
        self.c1.post('/api/messaging/conversations/', {'user_id': self.user2.id}, format='json')
        resp = self.c1.get('/api/messaging/conversations/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 1)

    def test_send_and_receive_message(self):
        conv_resp = self.c1.post('/api/messaging/conversations/', {'user_id': self.user2.id}, format='json')
        conv_id   = conv_resp.data['id']
        resp = self.c1.post(f'/api/messaging/conversations/{conv_id}/messages/', {'content': 'Hello!'}, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data['content'], 'Hello!')
        # Retrieve messages
        resp2 = self.c1.get(f'/api/messaging/conversations/{conv_id}/messages/')
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(len(resp2.data['results']), 1)

    def test_send_empty_message(self):
        conv_resp = self.c1.post('/api/messaging/conversations/', {'user_id': self.user2.id}, format='json')
        conv_id   = conv_resp.data['id']
        resp = self.c1.post(f'/api/messaging/conversations/{conv_id}/messages/', {'content': ''}, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_cannot_access_other_conversation(self):
        user3 = make_user('msg3@test.com')
        conv_resp = self.c1.post('/api/messaging/conversations/', {'user_id': self.user2.id}, format='json')
        conv_id   = conv_resp.data['id']
        c3 = auth_client(user3)
        resp = c3.get(f'/api/messaging/conversations/{conv_id}/messages/')
        self.assertEqual(resp.status_code, 404)


# ── 6. Reviews Tests ──────────────────────────────────────────────
class ReviewTestCase(TestCase):
    def setUp(self):
        from apps.tutors.models import Subject, TutorProfile
        from apps.scheduling.models import Lesson
        from django.utils import timezone
        from datetime import timedelta
        self.tutor   = make_user('rtutor@test.com', role='tutor')
        self.student = make_user('rstudent@test.com', role='student')
        TutorProfile.objects.create(user=self.tutor, hourly_rate=60, approval_status='approved')
        subj   = Subject.objects.create(name='Art', slug='art')
        start  = timezone.now()
        self.lesson = Lesson.objects.create(
            tutor=self.tutor, student=self.student, subject=subj,
            start_time=start, end_time=start+timedelta(hours=1),
            price=60, status='completed', payment_status='paid'
        )
        self.client = auth_client(self.student)

    def test_submit_review(self):
        resp = self.client.post('/api/reviews/', {
            'lesson': self.lesson.id,
            'rating': 5,
            'content': 'Excellent tutor, very patient!',
            'would_recommend': True,
        }, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data['rating'], 5)

    def test_duplicate_review_rejected(self):
        self.client.post('/api/reviews/', {'lesson': self.lesson.id, 'rating': 4, 'content': 'Good.'}, format='json')
        resp = self.client.post('/api/reviews/', {'lesson': self.lesson.id, 'rating': 3, 'content': 'OK.'}, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_list_tutor_reviews(self):
        self.client.post('/api/reviews/', {'lesson': self.lesson.id, 'rating': 5, 'content': 'Great!'}, format='json')
        resp = self.client.get(f'/api/reviews/?tutor_id={self.tutor.id}')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 1)


# ── 7. Gamification Tests ─────────────────────────────────────────
class GamificationTestCase(TestCase):
    def setUp(self):
        self.user   = make_user('gamer@test.com')
        self.client = auth_client(self.user)
        from apps.gamification.models import Badge
        Badge.objects.create(name='First Lesson', icon='bi bi-star', points_required=10)

    def test_list_badges_empty(self):
        resp = self.client.get('/api/gamification/badges/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 0)

    def test_award_points_and_badge(self):
        from apps.gamification.views import award_points
        award_points(self.user, 50, 'lesson_completed', 'First lesson done')
        self.user.refresh_from_db()
        self.assertEqual(self.user.total_points, 50)
        from apps.gamification.models import UserBadge
        badges = UserBadge.objects.filter(user=self.user)
        self.assertEqual(badges.count(), 1)

    def test_leaderboard(self):
        resp = self.client.get('/api/gamification/leaderboard/?role=student')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('entries', resp.data)
        self.assertIn('my_rank', resp.data)


# ── 8. Courses Tests ──────────────────────────────────────────────
class GroupClassTestCase(TestCase):
    def setUp(self):
        from apps.tutors.models import Subject
        from django.utils import timezone
        from datetime import timedelta
        self.subj    = Subject.objects.create(name='Coding', slug='coding')
        self.tutor   = make_user('gtutor@test.com', role='tutor')
        self.student = make_user('gstudent@test.com', role='student')
        from apps.courses.models import GroupClass
        self.gc = GroupClass.objects.create(
            tutor=self.tutor, subject=self.subj,
            title='Python Bootcamp', description='Learn Python fast',
            level='beginner', start_time=timezone.now()+timedelta(days=3),
            duration_minutes=90, max_students=10, price=50,
        )

    def test_list_group_classes(self):
        resp = APIClient().get('/api/courses/group-classes/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 1)

    def test_enroll_in_class(self):
        c    = auth_client(self.student)
        resp = c.post(f'/api/courses/group-classes/{self.gc.id}/enroll/')
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(resp.data['enrolled'])

    def test_double_enroll_rejected(self):
        c = auth_client(self.student)
        c.post(f'/api/courses/group-classes/{self.gc.id}/enroll/')
        resp = c.post(f'/api/courses/group-classes/{self.gc.id}/enroll/')
        self.assertEqual(resp.status_code, 400)

    def test_unenroll_from_class(self):
        c = auth_client(self.student)
        c.post(f'/api/courses/group-classes/{self.gc.id}/enroll/')
        resp = c.delete(f'/api/courses/group-classes/{self.gc.id}/unenroll/')
        self.assertEqual(resp.status_code, 200)


# ── 9. Admin Panel Tests ──────────────────────────────────────────
class AdminPanelTestCase(TestCase):
    def setUp(self):
        self.admin   = make_user('admin@test.com', role='admin', is_staff=True, is_superuser=True)
        self.student = make_user('astudent@test.com', role='student')
        self.tutor   = make_user('atutor@test.com', role='tutor')
        from apps.tutors.models import TutorProfile
        self.tp = TutorProfile.objects.create(user=self.tutor, hourly_rate=80, approval_status='pending')
        self.client = auth_client(self.admin)

    def test_admin_stats(self):
        resp = self.client.get('/api/admin-panel/stats/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('users', resp.data)
        self.assertIn('lessons', resp.data)
        self.assertIn('revenue', resp.data)
        self.assertIn('daily_revenue', resp.data)

    def test_admin_user_list(self):
        resp = self.client.get('/api/admin-panel/users/')
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(resp.data['count'], 2)

    def test_admin_user_list_filter_role(self):
        resp = self.client.get('/api/admin-panel/users/?role=student')
        self.assertEqual(resp.status_code, 200)
        for u in resp.data['results']:
            self.assertEqual(u['role'], 'student')

    def test_toggle_user_active(self):
        resp = self.client.post(f'/api/admin-panel/users/{self.student.id}/toggle-active/')
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.data['active'])
        # Toggle back
        resp2 = self.client.post(f'/api/admin-panel/users/{self.student.id}/toggle-active/')
        self.assertTrue(resp2.data['active'])

    def test_approve_tutor(self):
        resp = self.client.post(f'/api/admin-panel/tutors/{self.tp.id}/approve/', {'status': 'approved'}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.tp.refresh_from_db()
        self.assertEqual(self.tp.approval_status, 'approved')

    def test_reject_tutor(self):
        resp = self.client.post(f'/api/admin-panel/tutors/{self.tp.id}/approve/', {'status': 'rejected'}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.tp.refresh_from_db()
        self.assertEqual(self.tp.approval_status, 'rejected')

    def test_student_approval_list(self):
        from apps.students.models import StudentProfile
        StudentProfile.objects.create(user=self.student, is_approved=False)
        resp = self.client.get('/api/admin-panel/students/?approval_status=pending')
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(resp.data['count'], 1)

    def test_approve_student(self):
        from apps.students.models import StudentProfile
        StudentProfile.objects.create(user=self.student, is_approved=False)
        resp = self.client.post(f'/api/admin-panel/students/{self.student.id}/approve/', {'action': 'approve'}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.data['approved'])
        sp = StudentProfile.objects.get(user=self.student)
        self.assertTrue(sp.is_approved)

    def test_suspend_student(self):
        from apps.students.models import StudentProfile
        StudentProfile.objects.create(user=self.student, is_approved=True)
        resp = self.client.post(f'/api/admin-panel/students/{self.student.id}/approve/', {'action': 'suspend'}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.data['approved'])

    def test_bulk_approve_students(self):
        from apps.students.models import StudentProfile
        u2 = make_user('bs2@test.com', role='student')
        StudentProfile.objects.create(user=self.student, is_approved=False)
        StudentProfile.objects.create(user=u2, is_approved=False)
        resp = self.client.post('/api/admin-panel/students/', {
            'user_ids': [self.student.id, u2.id], 'action': 'approve'
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['updated'], 2)

    def test_admin_revenue(self):
        resp = self.client.get('/api/admin-panel/revenue/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('gross', resp.data)
        self.assertIn('daily', resp.data)

    def test_non_admin_blocked(self):
        c = auth_client(self.student)
        resp = c.get('/api/admin-panel/stats/')
        self.assertEqual(resp.status_code, 403)

    def test_export_users_excel(self):
        resp = self.client.get('/api/admin-panel/export/?type=users&format=excel&period=all')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'],
                         'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    def test_export_users_pdf(self):
        resp = self.client.get('/api/admin-panel/export/?type=users&format=pdf&period=all')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'application/pdf')

    def test_export_revenue_excel(self):
        resp = self.client.get('/api/admin-panel/export/?type=revenue&format=excel&period=month')
        self.assertEqual(resp.status_code, 200)

    def test_export_referrals(self):
        resp = self.client.get('/api/admin-panel/export/?type=referrals&format=excel')
        self.assertEqual(resp.status_code, 200)


# ── 10. Settings Tests ────────────────────────────────────────────
class SiteSettingsTestCase(TestCase):
    def setUp(self):
        self.admin  = make_user('sadmin@test.com', role='admin', is_staff=True, is_superuser=True)
        self.client_a = auth_client(self.admin)
        self.anon   = APIClient()

    def test_public_settings_readable(self):
        resp = self.anon.get('/api/settings/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('site_name', resp.data)
        self.assertNotIn('paystack_secret_key', resp.data)

    def test_admin_sees_api_keys(self):
        resp = self.client_a.get('/api/settings/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('paystack_secret_key', resp.data)
        self.assertIn('bbb_url', resp.data)

    def test_update_settings(self):
        resp = self.client_a.post('/api/settings/', {
            'site_name': 'Gooprep GH', 'primary_color': '#ff0000'
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.data['saved'])

    def test_static_page_read(self):
        resp = self.anon.get('/api/settings/pages/privacy/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['page_type'], 'privacy')

    def test_static_page_write_admin_only(self):
        resp = self.anon.post('/api/settings/pages/terms/', {'title': 'Terms', 'content': 'Our terms.'}, format='json')
        self.assertEqual(resp.status_code, 403)

    def test_static_page_write_admin(self):
        resp = self.client_a.post('/api/settings/pages/about/', {
            'title': 'About Gooprep', 'content': 'We are Ghana\'s best tutoring platform.'
        }, format='json')
        self.assertEqual(resp.status_code, 200)


# ── 11. Institutions Tests ────────────────────────────────────────
class InstitutionTestCase(TestCase):
    def setUp(self):
        self.owner   = make_user('inst@test.com', role='institution')
        self.member  = make_user('imember@test.com', role='student')
        self.client  = auth_client(self.owner)

    def test_create_institution(self):
        resp = self.client.post('/api/institutions/', {
            'name': 'Accra Academy', 'type': 'school', 'description': 'Top school in Accra'
        }, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data['name'], 'Accra Academy')

    def test_add_member(self):
        self.client.post('/api/institutions/', {'name': 'Test School', 'type': 'school'}, format='json')
        resp = self.client.post('/api/institutions/members/', {
            'email': self.member.email, 'role': 'student'
        }, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(resp.data['added'])

    def test_get_institution(self):
        self.client.post('/api/institutions/', {'name': 'My School', 'type': 'school'}, format='json')
        resp = self.client.get('/api/institutions/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['name'], 'My School')


# ── 12. Password Reset Tests ──────────────────────────────────────
class PasswordResetTestCase(TestCase):
    def setUp(self):
        self.user   = make_user('reset@test.com')
        self.client = APIClient()

    def test_request_reset_registered_email(self):
        resp = self.client.post('/api/auth/password/reset/', {'email': 'reset@test.com'}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('detail', resp.data)

    def test_request_reset_unregistered_email(self):
        # Should still return 200 (no enumeration)
        resp = self.client.post('/api/auth/password/reset/', {'email': 'nobody@test.com'}, format='json')
        self.assertEqual(resp.status_code, 200)

    def test_confirm_reset_with_token(self):
        from apps.accounts.models import PasswordResetToken
        import uuid
        tok = PasswordResetToken.objects.create(user=self.user, token=str(uuid.uuid4()).replace('-',''))
        resp = self.client.post('/api/auth/password/reset/confirm/', {
            'email': self.user.email, 'token': tok.token,
            'new_password1': 'NewPass@9999', 'new_password2': 'NewPass@9999'
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPass@9999'))

    def test_confirm_reset_invalid_token(self):
        resp = self.client.post('/api/auth/password/reset/confirm/', {
            'email': self.user.email, 'token': 'badtoken',
            'new_password1': 'NewPass@9999', 'new_password2': 'NewPass@9999'
        }, format='json')
        self.assertEqual(resp.status_code, 400)
