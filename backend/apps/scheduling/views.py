import hashlib
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes

from datetime import timedelta
from django.utils import timezone

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.db import transaction
from django.db.models import Q

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Lesson
from .serializers import LessonSerializer


User = get_user_model()


class LessonListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        # -----------------------------------------
        # Base queryset based on user role
        # -----------------------------------------
        if user.role == "tutor":
            qs = Lesson.objects.filter(tutor=user)

        elif user.role in ("admin", "staff"):
            qs = Lesson.objects.all()

        else:
            qs = Lesson.objects.filter(student=user)

        # -----------------------------------------
        # Filters
        # -----------------------------------------
        status_filter = request.query_params.get("status")
        month = request.query_params.get("month")
        student_id = request.query_params.get("student")

        if status_filter:
            qs = qs.filter(status=status_filter)

        if month:
            try:
                year, month_number = month.split("-")

                qs = qs.filter(
                    start_time__year=int(year),
                    start_time__month=int(month_number),
                )

            except (ValueError, TypeError):
                pass

        if student_id and user.role == "tutor":
            qs = qs.filter(student_id=student_id)

        # -----------------------------------------
        # Ordering
        # -----------------------------------------
        ordering = request.query_params.get(
            "ordering",
            "-start_time"
        )

        allowed_ordering = {
            "start_time",
            "-start_time",
            "created_at",
            "-created_at",
            "status",
            "-status",
        }

        if ordering not in allowed_ordering:
            ordering = "-start_time"

        qs = (
            qs
            .select_related("tutor", "student", "subject")
            .order_by(ordering)
        )

        # -----------------------------------------
        # Pagination
        # -----------------------------------------
        try:
            page_size = int(
                request.query_params.get("page_size", 15)
            )
        except (ValueError, TypeError):
            page_size = 15

        try:
            page = int(
                request.query_params.get("page", 1)
            )
        except (ValueError, TypeError):
            page = 1

        page_size = max(1, min(page_size, 100))
        page = max(1, page)

        total = qs.count()

        start_index = (page - 1) * page_size
        end_index = start_index + page_size

        lessons = qs[start_index:end_index]

        # -----------------------------------------
        # Serialize
        # -----------------------------------------
        data = LessonSerializer(
            lessons,
            many=True
        ).data

        # -----------------------------------------
        # Can join calculation
        # -----------------------------------------
        now = timezone.now()

        for i, lesson in enumerate(lessons):

            if lesson.start_time:
                join_window = lesson.start_time - timedelta(
                    minutes=10
                )

                data[i]["can_join"] = (
                    now >= join_window
                    and lesson.status in (
                        "confirmed",
                        "in_progress",
                    )
                    and lesson.payment_status == "paid"
                )
            else:
                data[i]["can_join"] = False

        return Response({
            "count": total,
            "results": data,
        })

    def post(self, request):
        """
        Create a new lesson booking.
        """

        try:
            # -----------------------------------------
            # Get tutor
            # -----------------------------------------
            tutor_id = request.data.get("tutor")

            if not tutor_id:
                return Response(
                    {
                        "error": "Tutor is required.",
                        "field": "tutor",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            tutor = (
                User.objects
                .filter(
                    id=tutor_id,
                    role="tutor",
                )
                .first()
            )

            if not tutor:
                return Response(
                    {
                        "error": "Tutor account was not found.",
                        "field": "tutor",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # -----------------------------------------
            # Determine student
            # -----------------------------------------
            student = request.user

            booked_on_behalf = self._to_bool(
                request.data.get(
                    "booked_on_behalf",
                    False
                )
            )

            if booked_on_behalf:

                learner_email = (
                    request.data.get(
                        "learner_email",
                        ""
                    )
                    .strip()
                    .lower()
                )

                if not learner_email:
                    return Response(
                        {
                            "error": (
                                "Learner email is required "
                                "when booking on behalf."
                            ),
                            "field": "learner_email",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                learner = (
                    User.objects
                    .filter(
                        email__iexact=learner_email,
                        role="student",
                    )
                    .first()
                )

                if not learner:
                    return Response(
                        {
                            "error": (
                                "Learner student account "
                                "was not found."
                            ),
                            "field": "learner_email",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                student = learner

            # -----------------------------------------
            # Dates
            # -----------------------------------------
            start_time = request.data.get("start_time")
            end_time = request.data.get("end_time")

            if not start_time:
                return Response(
                    {
                        "error": "Start time is required.",
                        "field": "start_time",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not end_time:
                return Response(
                    {
                        "error": "End time is required.",
                        "field": "end_time",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            start = parse_datetime(start_time)
            end = parse_datetime(end_time)

            if start is None:
                return Response(
                    {
                        "error": "Invalid start_time format.",
                        "field": "start_time",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if end is None:
                return Response(
                    {
                        "error": "Invalid end_time format.",
                        "field": "end_time",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Make naive datetimes timezone-aware
            if timezone.is_naive(start):
                start = timezone.make_aware(start)

            if timezone.is_naive(end):
                end = timezone.make_aware(end)

            if end <= start:
                return Response(
                    {
                        "error": (
                            "End time must be later "
                            "than start time."
                        ),
                        "field": "end_time",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            duration = int(
                (end - start).total_seconds() / 60
            )

            if duration <= 0:
                return Response(
                    {
                        "error": "Lesson duration must be greater than zero."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Tutor booking rules are enforced here, not only in the UI.
            tutor_profile = tutor.tutor_profile
            now = timezone.now()
            if start < now + timedelta(hours=tutor_profile.min_notice_hours):
                return Response({'error': f'Please book at least {tutor_profile.min_notice_hours} hours in advance.', 'field': 'start_time'}, status=400)

            blocked_dates = {str(item.get('date', item))[:10] for item in (tutor_profile.blocked_dates or [])}
            if start.date().isoformat() in blocked_dates:
                return Response({'error': 'The tutor is unavailable on that date.', 'field': 'start_time'}, status=400)

            weekday_slots = [slot for slot in (tutor_profile.availability or []) if int(slot.get('day_of_week', -1)) == start.weekday()]
            start_minutes = start.hour * 60 + start.minute
            end_minutes = end.hour * 60 + end.minute
            if not weekday_slots or not any(
                int(str(slot.get('start_time', '00:00'))[:2]) * 60 + int(str(slot.get('start_time', '00:00'))[3:5]) <= start_minutes
                and int(str(slot.get('end_time', '23:59'))[:2]) * 60 + int(str(slot.get('end_time', '23:59'))[3:5]) >= end_minutes
                for slot in weekday_slots
            ):
                return Response({'error': 'The selected time is outside the tutor availability.', 'field': 'start_time'}, status=400)

            day_lessons = Lesson.objects.filter(tutor=tutor, start_time__date=start.date()).exclude(status='cancelled')
            if day_lessons.count() >= tutor_profile.max_daily_bookings:
                return Response({'error': 'The tutor has reached the booking limit for that day.', 'field': 'start_time'}, status=400)
            buffer_delta = timedelta(minutes=tutor_profile.booking_buffer_minutes)
            if day_lessons.filter(start_time__lt=end + buffer_delta, end_time__gt=start - buffer_delta).exists():
                return Response({'error': 'Please choose a time with enough buffer from another lesson.', 'field': 'start_time'}, status=400)

            # -----------------------------------------
            # Subject
            # -----------------------------------------
            subject_id = request.data.get("subject")

            if subject_id in ("", None, "null"):
                subject_id = None
            else:
                try:
                    subject_id = int(subject_id)
                except (TypeError, ValueError):
                    return Response(
                        {"error": "Invalid subject.", "field": "subject"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if not tutor.tutor_profile.subjects.filter(pk=subject_id).exists():
                    return Response(
                        {
                            "error": "The selected subject is not offered by this tutor.",
                            "field": "subject",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # -----------------------------------------
            # Price
            # -----------------------------------------
            price = request.data.get("price", 0)

            if price in ("", None):
                price = 0

            # -----------------------------------------
            # Create lesson
            # -----------------------------------------
            lesson = Lesson.objects.create(
                tutor=tutor,
                student=student,

                subject_id=subject_id,

                lesson_type=request.data.get(
                    "lesson_type",
                    "regular",
                ),

                start_time=start,
                end_time=end,
                duration_minutes=duration,

                topic=request.data.get(
                    "topic",
                    "",
                ),

                price=price,

                currency=request.data.get(
                    "currency",
                    "GHS",
                ),

                record_session=self._to_bool(
                    request.data.get(
                        "record_session",
                        True,
                    )
                ),

                status="pending",
                payment_status="pending",

                booked_on_behalf=booked_on_behalf,

                booker_name=request.data.get(
                    "booker_name",
                    "",
                ),

                booker_relationship=request.data.get(
                    "booker_relationship",
                    "",
                ),

                booker_phone=request.data.get(
                    "booker_phone",
                    "",
                ),

                booker_email=request.data.get(
                    "booker_email",
                    "",
                ),

                notes=request.data.get(
                    "notes",
                    "",
                ),
            )

            # -----------------------------------------
            # Notifications
            # -----------------------------------------
            try:
                from apps.messaging.guppy import (
                    notify_lesson_booked
                )

                notify_lesson_booked(lesson)

            except Exception as notification_error:
                print(
                    "Lesson notification failed:",
                    notification_error
                )

            # -----------------------------------------
            # Response
            # -----------------------------------------
            lesson = (
                Lesson.objects
                .select_related(
                    "tutor",
                    "student",
                    "subject",
                )
                .get(pk=lesson.pk)
            )

            data = LessonSerializer(lesson).data

            data["can_join"] = False

            return Response(
                data,
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            # Print the real error in development
            import traceback

            traceback.print_exc()

            return Response(
                {
                    "error": str(e),
                    "type": e.__class__.__name__,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    @staticmethod
    def _to_bool(value):
        """
        Safely convert frontend boolean values.
        """

        if isinstance(value, bool):
            return value

        if value is None:
            return False

        if isinstance(value, str):
            return value.strip().lower() in (
                "true",
                "1",
                "yes",
                "on",
            )

        if isinstance(value, int):
            return value == 1

        return bool(value)

class LessonDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, pk):
        try:
            l = Lesson.objects.select_related('tutor','student','subject').get(pk=pk)
            if request.user not in [l.tutor, l.student] and request.user.role not in ('admin','staff'):
                return Response({'error':'Forbidden.'}, status=403)
            d = LessonSerializer(l).data
            now = timezone.now()
            d['can_join'] = (
                now >= (l.start_time - timedelta(minutes=10))
                and l.status in ('confirmed', 'in_progress')
                and l.payment_status == 'paid'
            )
            return Response(d)
        except Lesson.DoesNotExist:
            return Response({'error':'Not found.'}, status=404)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def join_lesson(request, pk):
    from django.conf import settings as dj_settings
    try:
        l = Lesson.objects.get(pk=pk)
        if request.user not in [l.tutor, l.student]:
            return Response({'error':'Not your lesson.'}, status=403)
        if l.payment_status != 'paid':
            return Response({'error': 'Payment is required before joining this lesson.'}, status=402)
        if l.status not in ('confirmed', 'in_progress'):
            return Response({'error': 'This lesson is not ready to join.'}, status=400)
        bbb_url    = dj_settings.BBB_URL
        bbb_secret = dj_settings.BBB_SECRET
        if not bbb_url or not bbb_secret:
            return Response({'join_url': None, 'error': 'Virtual classroom not configured. Contact admin.'}, status=503)
        meeting_id = l.bbb_meeting_id or f'gooprep-lesson-{l.id}'
        is_mod     = request.user == l.tutor
        pw         = hashlib.sha1(f'{meeting_id}-{"mod" if is_mod else "att"}{bbb_secret}'.encode()).hexdigest()[:8]
        join_str   = f'fullName={request.user.get_full_name()}&meetingID={meeting_id}&password={pw}&redirect=true'
        checksum   = hashlib.sha1(f'join{join_str}{bbb_secret}'.encode()).hexdigest()
        join_url   = f'{bbb_url}join?{join_str}&checksum={checksum}'
        if l.status == 'confirmed':
            l.status = 'in_progress'; l.bbb_meeting_id = meeting_id
            l.save(update_fields=['status','bbb_meeting_id'])
        return Response({'join_url': join_url, 'meeting_id': meeting_id})
    except Lesson.DoesNotExist:
        return Response({'error':'Not found.'}, status=404)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def end_lesson(request, pk):
    try:
        l = Lesson.objects.get(pk=pk)
        if request.user != l.tutor and request.user.role not in ('admin','staff'):
            return Response({'error':'Only the tutor can end the lesson.'}, status=403)
        l.status = 'completed'; l.save(update_fields=['status'])
        try:
            from apps.gamification.services import record_completed_lesson
            record_completed_lesson(l)
        except Exception:
            pass
        try:
            from apps.scheduling.tasks import generate_ai_summary
            generate_ai_summary.delay(l.id)
        except Exception: pass
        return Response({'ended':True})
    except Lesson.DoesNotExist:
        return Response({'error':'Not found.'}, status=404)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def reschedule_lesson(request, pk):
    try:
        l = Lesson.objects.get(pk=pk)
        if request.user not in [l.tutor, l.student]:
            return Response({'error':'Forbidden.'}, status=403)
        from django.utils.dateparse import parse_datetime
        l.start_time = parse_datetime(request.data.get('new_start_time')) or l.start_time
        l.end_time   = parse_datetime(request.data.get('new_end_time'))   or l.end_time
        l.status = 'rescheduled'; l.save()
        return Response({'rescheduled':True})
    except Lesson.DoesNotExist:
        return Response({'error':'Not found.'}, status=404)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def lesson_recordings(request, pk):
    try:
        l = Lesson.objects.get(pk=pk)
        recs = []
        if l.recording_url: recs.append({'playback_url':l.recording_url,'duration':l.duration_minutes})
        return Response({'recordings':recs})
    except Lesson.DoesNotExist:
        return Response({'error': 'Not found.'}, status=404)