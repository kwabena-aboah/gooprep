from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from django.db.models import Q, Sum
from django.conf import settings
from django.utils import timezone
from datetime import timedelta, date
import logging

logger = logging.getLogger(__name__)
IsAdmin = permissions.IsAdminUser


def _date_filter(qs, field, period):
    now = timezone.now()
    mapping = {
        'today':   now.replace(hour=0, minute=0, second=0),
        'week':    now - timedelta(days=7),
        'month':   now - timedelta(days=30),
        'quarter': now - timedelta(days=90),
        'year':    now - timedelta(days=365),
    }
    start = mapping.get(period)
    if start:
        return qs.filter(**{f'{field}__gte': start})
    return qs


class AdminStatsView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        from django.contrib.auth import get_user_model
        from apps.scheduling.models import Lesson
        from apps.institutions.models import Institution
        from apps.payments.models import Transaction
        from apps.tutors.models import TutorProfile
        from apps.admin_panel.models import ModerationItem
        from apps.payments.models import Dispute

        User   = get_user_model()
        period = request.query_params.get('period', 'month')
        qs_u   = _date_filter(User.objects.all(), 'date_joined', period)
        qs_l   = _date_filter(Lesson.objects.all(), 'created_at', period)
        qs_t   = _date_filter(Transaction.objects.filter(status='success'), 'created_at', period)

        now   = timezone.now()
        daily = []
        for i in range(30):
            d   = (now - timedelta(days=29-i)).date()
            amt = Transaction.objects.filter(
                status='success', created_at__date=d
            ).aggregate(s=Sum('amount'))['s'] or 0
            daily.append({'date': str(d), 'amount': float(amt)})

        return Response({
            'users':              User.objects.count(),
            'tutors':             TutorProfile.objects.filter(approval_status='approved').count(),
            'students':           User.objects.filter(role='student').count(),
            'lessons':            qs_l.count(),
            'revenue':            f"{float(qs_t.aggregate(s=Sum('amount'))['s'] or 0):.2f}",
            'pending_tutor_approvals':   TutorProfile.objects.filter(approval_status='pending').count(),
            'pending_student_approvals': User.objects.filter(role='student', student_profile__is_approved=False).count(),
            'pending_institution_approvals': Institution.objects.filter(approval_status='pending').count(),
            'open_disputes':      Dispute.objects.filter(status='open').count(),
            'pending_moderation': ModerationItem.objects.filter(status='pending').count(),
            'daily_revenue':      daily,
            'new_users_period':   qs_u.count(),
            'new_lessons_period': qs_l.count(),
        })


class AdminReferralListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        from django.contrib.auth import get_user_model
        from .serializers import ReferralSerializer

        User = get_user_model()
        queryset = User.objects.filter(was_referred=True).order_by('-date_joined')
        search = request.query_params.get('search', '').strip()
        role = request.query_params.get('role', '').strip()

        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
                | Q(referrer_name__icontains=search)
            )
        if role:
            queryset = queryset.filter(role=role)

        try:
            page_size = min(max(int(request.query_params.get('page_size', 20)), 1), 100)
        except (TypeError, ValueError):
            page_size = 20
        try:
            page = max(int(request.query_params.get('page', 1)), 1)
        except (TypeError, ValueError):
            page = 1

        total = queryset.count()
        start = (page - 1) * page_size
        results = queryset[start:start + page_size]
        return Response({
            'count': total,
            'results': ReferralSerializer(results, many=True).data,
        })


class AdminUserListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        qs   = User.objects.all().order_by('-date_joined')
        s    = request.query_params.get('search')
        role = request.query_params.get('role')
        if s:    qs = qs.filter(Q(first_name__icontains=s)|Q(last_name__icontains=s)|Q(email__icontains=s))
        if role: qs = qs.filter(role=role)
        page_size = int(request.query_params.get('page_size', 20))
        page      = int(request.query_params.get('page', 1))
        total     = qs.count()
        items = list(qs[(page-1)*page_size : page*page_size].values(
            'id','email','first_name','last_name','role','subscription_plan',
            'city','phone','date_joined','last_login','is_active','total_points','level',
            'was_referred','referrer_name','email_verified'))
        for it in items:
            it['full_name'] = f"{it['first_name']} {it['last_name']}".strip()
            if it['date_joined']: it['date_joined'] = it['date_joined'].isoformat()
            if it['last_login']:  it['last_login']  = it['last_login'].isoformat()
        return Response({'count': total, 'results': items})

@api_view(['POST'])
@permission_classes([IsAdmin])
def toggle_user_active(request, user_id):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        u = User.objects.get(id=user_id)
        u.is_active = not u.is_active
        u.save(update_fields=['is_active'])
        return Response({'active': u.is_active})
    except User.DoesNotExist:
        return Response({'error': 'Not found.'}, status=404)


class AdminTutorListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        from apps.tutors.models import TutorProfile
        from apps.tutors.serializers import TutorProfileSerializer
        qs = TutorProfile.objects.select_related('user').prefetch_related('subjects', 'user__verification_documents')
        approval = request.query_params.get('approval_status')
        search   = request.query_params.get('search')
        if approval: qs = qs.filter(approval_status=approval)
        if search:   qs = qs.filter(Q(user__first_name__icontains=search)|Q(user__last_name__icontains=search))
        page_size = int(request.query_params.get('page_size', 12))
        page      = int(request.query_params.get('page', 1))
        total     = qs.count()
        return Response({'count': total, 'results': TutorProfileSerializer(
            qs[(page-1)*page_size:page*page_size], many=True, context={'request': request}
        ).data})


@api_view(['POST'])
@permission_classes([IsAdmin])
def approve_tutor(request, tutor_id):
    from apps.tutors.models import TutorProfile
    try:
        tp         = TutorProfile.objects.get(id=tutor_id)
        new_status = request.data.get('status', 'approved')
        tp.approval_status = new_status
        tp.save(update_fields=['approval_status'])
        try:
            from apps.messaging.guppy import notify_tutor_approved
            notify_tutor_approved(tp.user, new_status == 'approved')
        except Exception: pass
        from apps.accounts.models import Notification
        Notification.objects.create(user=tp.user, notification_type='tutor_approved',
            title='Application Update',
            message=f'Your tutor application has been {new_status}.',
            link='/dashboard')
        return Response({'status': new_status})
    except TutorProfile.DoesNotExist:
        return Response({'error': 'Not found.'}, status=404)


# ── Student Approvals ──────────────────────────────────────────────
class StudentApprovalListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        from apps.students.models import StudentProfile
        User = __import__('django.contrib.auth', fromlist=['get_user_model']).get_user_model()
        for student in User.objects.filter(role='student').iterator():
            StudentProfile.objects.get_or_create(
                user=student,
                defaults={'needs_approval': True, 'is_approved': False},
            )
        approval_status = request.query_params.get('approval_status', 'pending')
        search          = request.query_params.get('search','')

        if approval_status == 'pending':
            profiles = StudentProfile.objects.filter(is_approved=False).select_related('user')
        elif approval_status == 'approved':
            profiles = StudentProfile.objects.filter(is_approved=True).select_related('user')
        else:
            profiles = StudentProfile.objects.all().select_related('user')

        if search:
            profiles = profiles.filter(
                Q(user__first_name__icontains=search)|
                Q(user__last_name__icontains=search)|
                Q(user__email__icontains=search)
            )
        page_size = int(request.query_params.get('page_size', 20))
        page      = int(request.query_params.get('page', 1))
        total     = profiles.count()
        items = [{
            'id':               p.user.id,
            'full_name':        p.user.get_full_name(),
            'email':            p.user.email,
            'phone':            p.user.phone,
            'city':             p.user.city,
            'subscription_plan':p.user.subscription_plan,
            'date_joined':      p.user.date_joined.isoformat() if p.user.date_joined else '',
            'is_active':        p.user.is_active,
            'is_approved':      p.is_approved,
            'education_level':  p.education_level,
            'school':           p.school,
            'identity_document_type': p.identity_document_type,
            'verification_documents': [
                {'id': d.id, 'doc_type': d.doc_type, 'doc_label': d.get_doc_type_display(),
                 'file_url': request.build_absolute_uri(d.file.url),
                 'file_name': d.file.name.rsplit('/', 1)[-1], 'is_verified': d.is_verified,
                 'uploaded_at': d.uploaded_at.isoformat()}
                for d in p.user.verification_documents.all()
            ],
            'was_referred':     p.user.was_referred,
            'referrer_name':    p.user.referrer_name,
        } for p in profiles[(page-1)*page_size:page*page_size]]
        return Response({'count': total, 'results': items})

    def post(self, request):
        """Bulk approve or suspend students."""
        from apps.students.models import StudentProfile
        user_ids = request.data.get('user_ids', [])
        action   = request.data.get('action', 'approve')
        approve  = (action == 'approve')

        updated = StudentProfile.objects.filter(user_id__in=user_ids).update(is_approved=approve)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        for user in User.objects.filter(id__in=user_ids):
            user.is_active = approve
            user.save(update_fields=['is_active'])
            from apps.accounts.models import Notification
            Notification.objects.create(
                user=user, notification_type='student_approved',
                title='Account ' + ('Approved' if approve else 'Suspended'),
                message='Welcome to Gooprep!' if approve else 'Your account has been suspended.',
                link='/dashboard'
            )
            try:
                from apps.messaging.guppy import notify_student_approved
                notify_student_approved(user, approve)
            except Exception: pass
        return Response({'updated': updated, 'action': action})


@api_view(['POST'])
@permission_classes([IsAdmin])
def approve_student(request, student_id):
    from apps.students.models import StudentProfile
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        u  = User.objects.get(id=student_id, role='student')
        sp, _ = StudentProfile.objects.get_or_create(user=u)
        action    = request.data.get('action', 'approve')
        is_active = (action == 'approve')
        sp.is_approved = is_active
        sp.save(update_fields=['is_approved'])
        u.is_active = is_active
        u.save(update_fields=['is_active'])
        from apps.accounts.models import Notification
        Notification.objects.create(user=u, notification_type='student_approved',
            title='Account ' + ('Approved' if is_active else 'Suspended'),
            message='Welcome to Gooprep! Start booking lessons now.' if is_active else 'Contact support for help.',
            link='/dashboard')
        try:
            from apps.messaging.guppy import notify_student_approved
            notify_student_approved(u, is_active)
        except Exception: pass
        return Response({'active': is_active, 'approved': is_active})
    except User.DoesNotExist:
        return Response({'error': 'Not found.'}, status=404)


class AdminRevenueView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        from apps.payments.models import Transaction, Payout
        period = request.query_params.get('period', 'month')
        qs     = _date_filter(Transaction.objects.filter(status='success'), 'created_at', period)
        gross  = float(qs.aggregate(s=Sum('amount'))['s'] or 0)
        fees   = round(gross * settings.PLATFORM_COMMISSION, 2)
        payouts_total = float(Payout.objects.filter(status='completed').aggregate(s=Sum('amount'))['s'] or 0)
        now   = timezone.now()
        days  = 7 if period == 'week' else 30
        daily = []
        for i in range(days):
            d   = (now - timedelta(days=days-1-i)).date()
            amt = Transaction.objects.filter(status='success', created_at__date=d).aggregate(s=Sum('amount'))['s'] or 0
            daily.append({'date': str(d), 'amount': float(amt)})
        return Response({
            'gross':   f'{gross:.2f}', 'fees': f'{fees:.2f}',
            'payouts': f'{payouts_total:.2f}',
            'escrow':  f'{max(gross * (1 - settings.PLATFORM_COMMISSION) - payouts_total, 0):.2f}',
            'daily':   daily,
        })


class AdminTransactionListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        from apps.payments.models import Transaction
        from apps.payments.serializers import TransactionSerializer
        qs = Transaction.objects.select_related('payer').order_by('-created_at')
        page_size = int(request.query_params.get('page_size', 30))
        page      = int(request.query_params.get('page', 1))
        return Response({'count': qs.count(),
                         'results': TransactionSerializer(qs[(page-1)*page_size:page*page_size], many=True).data})


class AdminDisputeListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        from apps.payments.models import Dispute
        from apps.payments.serializers import DisputeSerializer
        qs = Dispute.objects.select_related('filed_by', 'lesson').all()
        s  = request.query_params.get('status')
        if s: qs = qs.filter(status=s)
        qs = qs.order_by('-created_at')
        page_size = int(request.query_params.get('page_size', 15))
        page      = int(request.query_params.get('page', 1))
        return Response({'count': qs.count(), 'open_count': qs.filter(status='open').count(),
                         'results': DisputeSerializer(qs[(page-1)*page_size:page*page_size], many=True).data})


@api_view(['POST'])
@permission_classes([IsAdmin])
def resolve_dispute(request, dispute_id):
    from apps.payments.models import Dispute
    try:
        d = Dispute.objects.get(id=dispute_id)
        d.status     = request.data.get('status', 'resolved')
        d.resolution = request.data.get('resolution', '')
        d.save(update_fields=['status', 'resolution'])
        return Response({'status': d.status})
    except Dispute.DoesNotExist:
        return Response({'error': 'Not found.'}, status=404)


class AdminModerationListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        from apps.admin_panel.models import ModerationItem
        qs = ModerationItem.objects.select_related('author').all()
        ct = request.query_params.get('content_type')
        if ct: qs = qs.filter(content_type=ct)
        qs = qs.order_by('-created_at')
        page_size = int(request.query_params.get('page_size', 15))
        page      = int(request.query_params.get('page', 1))
        items = [{'id':m.id,'content_type':m.content_type,'content':m.content,
                  'author_name':m.author_name,'reasons':m.reasons,
                  'flag_count':m.flag_count,'status':m.status,'resolution':m.resolution,
                  'created_at':m.created_at.isoformat() if m.created_at else ''}
                 for m in qs[(page-1)*page_size:page*page_size]]
        return Response({'count': qs.count(), 'results': items})


@api_view(['POST'])
@permission_classes([IsAdmin])
def moderation_action(request, item_id):
    from apps.admin_panel.models import ModerationItem
    try:
        m = ModerationItem.objects.get(id=item_id)
        m.status     = 'resolved'
        m.resolution = request.data.get('action', '')
        m.save(update_fields=['status', 'resolution'])
        return Response({'status': m.status})
    except ModerationItem.DoesNotExist:
        return Response({'error': 'Not found.'}, status=404)


class BBBStatusView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        from apps.scheduling.bbb_service import bbb

        meetings = bbb.get_meetings() if bbb.configured else {}
        successful = meetings.get('returncode') == 'SUCCESS'
        raw_meetings = meetings.get('meetings', {}).get('meeting', []) if successful else []
        if isinstance(raw_meetings, dict):
            raw_meetings = [raw_meetings]
        participants = sum(int(m.get('participantCount') or 0) for m in raw_meetings)
        return Response({
            'online': successful,
            'configured': bbb.configured,
            'url': bbb.base_url,
            'version': meetings.get('version', '—') if successful else '—',
            'active_meetings': len(raw_meetings),
            'meeting_count': len(raw_meetings),
            'participant_count': participants,
            'error': '' if successful else meetings.get('message', 'BBB is unavailable.'),
        })

class AdminBBBView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        from apps.scheduling.bbb_service import bbb
        healthy  = bbb.server_healthy()
        meetings = {}
        version  = {}
        if healthy:
            meetings = bbb.get_meetings()
            version  = bbb.get_api_version()

        from apps.scheduling.models import Lesson, BBBWebhookEvent
        active_rooms = Lesson.objects.filter(status='in_progress').select_related('tutor', 'student', 'subject')
        recent_events = BBBWebhookEvent.objects.order_by('-received_at')[:20]

        return Response({
            'server': {
                'healthy': healthy,
                'configured': bbb.configured,
                'url': bbb.base_url,
                'version': version.get('version', ''),
            },
            'active_meetings': meetings,
            'active_lesson_rooms': [{
                'lesson_id': str(l.id),
                'meeting_id': l.bbb_meeting_id,
                'tutor_name': l.tutor.get_full_name(),
                'student_name': l.student.get_full_name(),
                'subject': l.subject_name,
                'recording': l.record_session,
            } for l in active_rooms],
            'recent_webhook_events': [{
                'event_type': e.event_type,
                'meeting_id': e.meeting_id,
                'received_at': e.received_at.isoformat(),
            } for e in recent_events],
        })

    def post(self, request):
        """Admin can force-end a BBB meeting."""
        from apps.scheduling.bbb_service import bbb
        from apps.scheduling.models import Lesson
        lesson_id = request.data.get('lesson_id')
        try:
            lesson = Lesson.objects.get(pk=lesson_id)
            if not lesson.bbb_meeting_id:
                return Response({'error': 'Lesson has no BBB meeting.'}, status=400)
            bbb.end_meeting(lesson.bbb_meeting_id, request.data.get('moderator_password', ''))
            lesson.status = 'completed'
            lesson.save(update_fields=['status'])
            return Response({'message': f'Lesson {lesson_id} ended by admin.'})
        except Lesson.DoesNotExist:
            return Response({'error': 'Lesson not found.'}, status=404)
        except Exception as exc:
            return Response({'error': str(exc)}, status=500) 


@api_view(['GET'])
@permission_classes([IsAdmin])
def bbb_rooms(request):
    from apps.scheduling.bbb_service import bbb
    response = bbb.get_meetings() if bbb.configured else {'meetings': {}}
    meetings = response.get('meetings', {}).get('meeting', [])
    if isinstance(meetings, dict):
        meetings = [meetings]
    return Response({
        'meetings': meetings,
        'configured': bbb.configured,
        'error': response.get('message', ''),
    })


@api_view(['GET'])
@permission_classes([IsAdmin])
def bbb_recordings(request):
    from apps.scheduling.bbb_service import bbb
    response = bbb.get_recordings(meeting_id='') if bbb.configured else {'recordings': {}}
    recordings = response.get('recordings', {}).get('recording', [])
    if isinstance(recordings, dict):
        recordings = [recordings]

    normalized = []
    for recording in recordings:
        formats = recording.get('playback', {}).get('format', [])
        if isinstance(formats, dict):
            formats = [formats]
        normalized.append({
            'recordID': recording.get('recordID', ''),
            'name': recording.get('name', ''),
            'duration': recording.get('duration', ''),
            'size': recording.get('size', ''),
            'startTime': recording.get('startTime', ''),
            'playbackUrl': formats[0].get('url', '') if formats else '',
        })
    return Response({
        'recordings': normalized,
        'configured': bbb.configured,
        'error': response.get('message', ''),
    })


@api_view(['POST'])
@permission_classes([IsAdmin])
def bbb_end_meeting(request):
    from apps.scheduling.bbb_service import bbb
    meeting_id = request.data.get('meeting_id')
    password = request.data.get('moderator_pw') or request.data.get('moderator_password', '')
    if not meeting_id:
        return Response({'error': 'meeting_id is required.'}, status=400)
    response = bbb.end_meeting(meeting_id, password)
    return Response(response, status=200 if response.get('returncode') == 'SUCCESS' else 502)


@api_view(['POST'])
@permission_classes([IsAdmin])
def bbb_delete_recording(request):
    from apps.scheduling.bbb_service import bbb
    record_id = request.data.get('record_id')
    if not record_id:
        return Response({'error': 'record_id is required.'}, status=400)
    response = bbb.delete_recording(record_id)
    return Response(response, status=200 if response.get('returncode') == 'SUCCESS' else 502)


class InstitutionApprovalListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        from apps.institutions.models import Institution
        from apps.institutions.serializers import InstitutionSerializer
        queryset = Institution.objects.select_related('owner').order_by('-created_at')
        approval = request.query_params.get('approval_status')
        if approval in {'pending', 'approved', 'rejected'}:
            queryset = queryset.filter(approval_status=approval)
        search = request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(owner__email__icontains=search))
        try:
            page = max(1, int(request.query_params.get('page', 1)))
            page_size = min(100, max(1, int(request.query_params.get('page_size', 20))))
        except (TypeError, ValueError):
            return Response({'error': 'page and page_size must be integers.'}, status=400)
        total = queryset.count()
        items = queryset[(page - 1) * page_size:page * page_size]
        return Response({'count': total, 'results': InstitutionSerializer(items, many=True).data})


@api_view(['POST'])
@permission_classes([IsAdmin])
def approve_institution(request, institution_id):
    from apps.institutions.models import Institution
    institution = Institution.objects.filter(pk=institution_id).first()
    if not institution:
        return Response({'error': 'Institution not found.'}, status=404)
    new_status = request.data.get('status', 'approved')
    if new_status not in {'approved', 'rejected', 'pending'}:
        return Response({'error': 'Invalid approval status.'}, status=400)
    institution.approval_status = new_status
    institution.is_verified = new_status == 'approved'
    institution.rejection_reason = request.data.get('reason', '') if new_status == 'rejected' else ''
    institution.reviewed_by = request.user
    institution.reviewed_at = timezone.now()
    institution.save(update_fields=['approval_status', 'is_verified', 'rejection_reason', 'reviewed_by', 'reviewed_at'])
    return Response({'status': institution.approval_status, 'is_verified': institution.is_verified})


# ── Export Endpoint ────────────────────────────────────────────────
class ExportReportView(APIView):
    """
    GET /api/admin-panel/export/?type=users&format=excel&period=month
    Returns a streaming file download (xlsx or pdf).
    Using APIView instead of @api_view so HttpResponse passes through cleanly.
    """
    permission_classes = [IsAdmin]

    def get(self, request):
        from django.contrib.auth import get_user_model
        from apps.scheduling.models import Lesson
        from apps.payments.models import Transaction
        from apps.tutors.models import TutorProfile
        from .exports import (
            export_users_excel,   export_users_pdf,
            export_lessons_excel, export_lessons_pdf,
            export_revenue_excel, export_revenue_pdf,
            export_tutors_excel,  export_tutors_pdf,
            export_referrals_excel,
        )

        report_type = request.query_params.get('type',   'users')
        fmt         = request.query_params.get('format', 'excel')
        period      = request.query_params.get('period', 'all')
        User        = get_user_model()

        try:
            if report_type == 'users':
                qs = _date_filter(User.objects.all(), 'date_joined', period).order_by('-date_joined')
                fn = export_users_excel(qs) if fmt == 'excel' else export_users_pdf(qs)

            elif report_type == 'lessons':
                qs = _date_filter(Lesson.objects.all(), 'created_at', period).order_by('-start_time')
                fn = export_lessons_excel(qs) if fmt == 'excel' else export_lessons_pdf(qs)

            elif report_type == 'revenue':
                qs = _date_filter(
                    Transaction.objects.filter(status='success'), 'created_at', period
                ).order_by('-created_at')
                fn = export_revenue_excel(qs) if fmt == 'excel' else export_revenue_pdf(qs)

            elif report_type == 'tutors':
                qs = TutorProfile.objects.all().order_by('-created_at')
                fn = export_tutors_excel(qs) if fmt == 'excel' else export_tutors_pdf(qs)

            elif report_type == 'referrals':
                qs  = User.objects.filter(was_referred=True).order_by('-date_joined')
                fn  = export_referrals_excel(qs)
                fmt = 'excel'

            else:
                return Response({'error': 'Unknown report type.'}, status=400)

            ext      = 'xlsx' if fmt == 'excel' else 'pdf'
            ct       = (
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                if fmt == 'excel' else 'application/pdf'
            )
            filename = f'gooprep_{report_type}_{period}_{date.today()}.{ext}'
            response = HttpResponse(fn, content_type=ct)
            response['Content-Disposition']          = f'attachment; filename="{filename}"'
            response['Access-Control-Expose-Headers'] = 'Content-Disposition'
            return response

        except ImportError as e:
            return Response({'error': f'Export library not installed: {e}'}, status=500)
        except Exception as e:
            logger.error(f'Export error: {e}', exc_info=True)
            return Response({'error': str(e)}, status=500)