# import hashlib
# from rest_framework import permissions
# from rest_framework.decorators import api_view, permission_classes

# from datetime import timedelta
# from django.utils import timezone

# from django.contrib.auth import get_user_model
# from django.utils import timezone
# from django.utils.dateparse import parse_datetime
# from django.db import transaction
# from django.db.models import Q

# from rest_framework import permissions, status
# from rest_framework.response import Response
# from rest_framework.views import APIView

# from .models import Lesson
# from .serializers import LessonSerializer


# User = get_user_model()


# class LessonListView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request):
#         user = request.user

#         # -----------------------------------------
#         # Base queryset based on user role
#         # -----------------------------------------
#         if user.role == "tutor":
#             qs = Lesson.objects.filter(tutor=user)

#         elif user.role in ("admin", "staff"):
#             qs = Lesson.objects.all()

#         else:
#             qs = Lesson.objects.filter(student=user)

#         # -----------------------------------------
#         # Filters
#         # -----------------------------------------
#         status_filter = request.query_params.get("status")
#         month = request.query_params.get("month")
#         student_id = request.query_params.get("student")

#         if status_filter:
#             qs = qs.filter(status=status_filter)

#         if month:
#             try:
#                 year, month_number = month.split("-")

#                 qs = qs.filter(
#                     start_time__year=int(year),
#                     start_time__month=int(month_number),
#                 )

#             except (ValueError, TypeError):
#                 pass

#         if student_id and user.role == "tutor":
#             qs = qs.filter(student_id=student_id)

#         # -----------------------------------------
#         # Ordering
#         # -----------------------------------------
#         ordering = request.query_params.get(
#             "ordering",
#             "-start_time"
#         )

#         allowed_ordering = {
#             "start_time",
#             "-start_time",
#             "created_at",
#             "-created_at",
#             "status",
#             "-status",
#         }

#         if ordering not in allowed_ordering:
#             ordering = "-start_time"

#         qs = (
#             qs
#             .select_related("tutor", "student", "subject")
#             .order_by(ordering)
#         )

#         # -----------------------------------------
#         # Pagination
#         # -----------------------------------------
#         try:
#             page_size = int(
#                 request.query_params.get("page_size", 15)
#             )
#         except (ValueError, TypeError):
#             page_size = 15

#         try:
#             page = int(
#                 request.query_params.get("page", 1)
#             )
#         except (ValueError, TypeError):
#             page = 1

#         page_size = max(1, min(page_size, 100))
#         page = max(1, page)

#         total = qs.count()

#         start_index = (page - 1) * page_size
#         end_index = start_index + page_size

#         lessons = qs[start_index:end_index]

#         # -----------------------------------------
#         # Serialize
#         # -----------------------------------------
#         data = LessonSerializer(
#             lessons,
#             many=True
#         ).data

#         # -----------------------------------------
#         # Can join calculation
#         # -----------------------------------------
#         now = timezone.now()

#         for i, lesson in enumerate(lessons):

#             if lesson.start_time:
#                 join_window = lesson.start_time - timedelta(
#                     minutes=10
#                 )

#                 data[i]["can_join"] = (
#                     now >= join_window
#                     and lesson.status in (
#                         "confirmed",
#                         "in_progress",
#                     )
#                     and lesson.payment_status == "paid"
#                 )
#             else:
#                 data[i]["can_join"] = False

#         return Response({
#             "count": total,
#             "results": data,
#         })

#     def post(self, request):
#         """
#         Create a new lesson booking.
#         """

#         try:
#             # -----------------------------------------
#             # Get tutor
#             # -----------------------------------------
#             tutor_id = request.data.get("tutor")

#             if not tutor_id:
#                 return Response(
#                     {
#                         "error": "Tutor is required.",
#                         "field": "tutor",
#                     },
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )

#             tutor = (
#                 User.objects
#                 .filter(
#                     id=tutor_id,
#                     role="tutor",
#                 )
#                 .first()
#             )

#             if not tutor:
#                 return Response(
#                     {
#                         "error": "Tutor account was not found.",
#                         "field": "tutor",
#                     },
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )

#             # -----------------------------------------
#             # Determine student
#             # -----------------------------------------
#             student = request.user

#             booked_on_behalf = self._to_bool(
#                 request.data.get(
#                     "booked_on_behalf",
#                     False
#                 )
#             )

#             if booked_on_behalf:

#                 learner_email = (
#                     request.data.get(
#                         "learner_email",
#                         ""
#                     )
#                     .strip()
#                     .lower()
#                 )

#                 if not learner_email:
#                     return Response(
#                         {
#                             "error": (
#                                 "Learner email is required "
#                                 "when booking on behalf."
#                             ),
#                             "field": "learner_email",
#                         },
#                         status=status.HTTP_400_BAD_REQUEST,
#                     )

#                 learner = (
#                     User.objects
#                     .filter(
#                         email__iexact=learner_email,
#                         role="student",
#                     )
#                     .first()
#                 )

#                 if not learner:
#                     return Response(
#                         {
#                             "error": (
#                                 "Learner student account "
#                                 "was not found."
#                             ),
#                             "field": "learner_email",
#                         },
#                         status=status.HTTP_400_BAD_REQUEST,
#                     )

#                 student = learner

#             # -----------------------------------------
#             # Dates
#             # -----------------------------------------
#             start_time = request.data.get("start_time")
#             end_time = request.data.get("end_time")

#             if not start_time:
#                 return Response(
#                     {
#                         "error": "Start time is required.",
#                         "field": "start_time",
#                     },
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )

#             if not end_time:
#                 return Response(
#                     {
#                         "error": "End time is required.",
#                         "field": "end_time",
#                     },
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )

#             start = parse_datetime(start_time)
#             end = parse_datetime(end_time)

#             if start is None:
#                 return Response(
#                     {
#                         "error": "Invalid start_time format.",
#                         "field": "start_time",
#                     },
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )

#             if end is None:
#                 return Response(
#                     {
#                         "error": "Invalid end_time format.",
#                         "field": "end_time",
#                     },
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )

#             # Make naive datetimes timezone-aware
#             if timezone.is_naive(start):
#                 start = timezone.make_aware(start)

#             if timezone.is_naive(end):
#                 end = timezone.make_aware(end)

#             if end <= start:
#                 return Response(
#                     {
#                         "error": (
#                             "End time must be later "
#                             "than start time."
#                         ),
#                         "field": "end_time",
#                     },
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )

#             duration = int(
#                 (end - start).total_seconds() / 60
#             )

#             if duration <= 0:
#                 return Response(
#                     {
#                         "error": "Lesson duration must be greater than zero."
#                     },
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )

#             # Tutor booking rules are enforced here, not only in the UI.
#             tutor_profile = tutor.tutor_profile
#             now = timezone.now()
#             if start < now + timedelta(hours=tutor_profile.min_notice_hours):
#                 return Response({'error': f'Please book at least {tutor_profile.min_notice_hours} hours in advance.', 'field': 'start_time'}, status=400)

#             blocked_dates = {str(item.get('date', item))[:10] for item in (tutor_profile.blocked_dates or [])}
#             if start.date().isoformat() in blocked_dates:
#                 return Response({'error': 'The tutor is unavailable on that date.', 'field': 'start_time'}, status=400)

#             weekday_slots = [slot for slot in (tutor_profile.availability or []) if int(slot.get('day_of_week', -1)) == start.weekday()]
#             start_minutes = start.hour * 60 + start.minute
#             end_minutes = end.hour * 60 + end.minute
#             if not weekday_slots or not any(
#                 int(str(slot.get('start_time', '00:00'))[:2]) * 60 + int(str(slot.get('start_time', '00:00'))[3:5]) <= start_minutes
#                 and int(str(slot.get('end_time', '23:59'))[:2]) * 60 + int(str(slot.get('end_time', '23:59'))[3:5]) >= end_minutes
#                 for slot in weekday_slots
#             ):
#                 return Response({'error': 'The selected time is outside the tutor availability.', 'field': 'start_time'}, status=400)

#             day_lessons = Lesson.objects.filter(tutor=tutor, start_time__date=start.date()).exclude(status='cancelled')
#             if day_lessons.count() >= tutor_profile.max_daily_bookings:
#                 return Response({'error': 'The tutor has reached the booking limit for that day.', 'field': 'start_time'}, status=400)
#             buffer_delta = timedelta(minutes=tutor_profile.booking_buffer_minutes)
#             if day_lessons.filter(start_time__lt=end + buffer_delta, end_time__gt=start - buffer_delta).exists():
#                 return Response({'error': 'Please choose a time with enough buffer from another lesson.', 'field': 'start_time'}, status=400)

#             # -----------------------------------------
#             # Subject
#             # -----------------------------------------
#             subject_id = request.data.get("subject")

#             if subject_id in ("", None, "null"):
#                 subject_id = None
#             else:
#                 try:
#                     subject_id = int(subject_id)
#                 except (TypeError, ValueError):
#                     return Response(
#                         {"error": "Invalid subject.", "field": "subject"},
#                         status=status.HTTP_400_BAD_REQUEST,
#                     )

#                 if not tutor.tutor_profile.subjects.filter(pk=subject_id).exists():
#                     return Response(
#                         {
#                             "error": "The selected subject is not offered by this tutor.",
#                             "field": "subject",
#                         },
#                         status=status.HTTP_400_BAD_REQUEST,
#                     )

#             # -----------------------------------------
#             # Price
#             # -----------------------------------------
#             price = request.data.get("price", 0)

#             if price in ("", None):
#                 price = 0

#             # -----------------------------------------
#             # Create lesson
#             # -----------------------------------------
#             lesson = Lesson.objects.create(
#                 tutor=tutor,
#                 student=student,

#                 subject_id=subject_id,

#                 lesson_type=request.data.get(
#                     "lesson_type",
#                     "regular",
#                 ),

#                 start_time=start,
#                 end_time=end,
#                 duration_minutes=duration,

#                 topic=request.data.get(
#                     "topic",
#                     "",
#                 ),

#                 price=price,

#                 currency=request.data.get(
#                     "currency",
#                     "GHS",
#                 ),

#                 record_session=self._to_bool(
#                     request.data.get(
#                         "record_session",
#                         True,
#                     )
#                 ),

#                 status="pending",
#                 payment_status="pending",

#                 booked_on_behalf=booked_on_behalf,

#                 booker_name=request.data.get(
#                     "booker_name",
#                     "",
#                 ),

#                 booker_relationship=request.data.get(
#                     "booker_relationship",
#                     "",
#                 ),

#                 booker_phone=request.data.get(
#                     "booker_phone",
#                     "",
#                 ),

#                 booker_email=request.data.get(
#                     "booker_email",
#                     "",
#                 ),

#                 notes=request.data.get(
#                     "notes",
#                     "",
#                 ),
#             )

#             # -----------------------------------------
#             # Notifications
#             # -----------------------------------------
#             try:
#                 from apps.messaging.guppy import (
#                     notify_lesson_booked
#                 )

#                 notify_lesson_booked(lesson)

#             except Exception as notification_error:
#                 print(
#                     "Lesson notification failed:",
#                     notification_error
#                 )

#             # -----------------------------------------
#             # Response
#             # -----------------------------------------
#             lesson = (
#                 Lesson.objects
#                 .select_related(
#                     "tutor",
#                     "student",
#                     "subject",
#                 )
#                 .get(pk=lesson.pk)
#             )

#             data = LessonSerializer(lesson).data

#             data["can_join"] = False

#             return Response(
#                 data,
#                 status=status.HTTP_201_CREATED,
#             )

#         except Exception as e:
#             # Print the real error in development
#             import traceback

#             traceback.print_exc()

#             return Response(
#                 {
#                     "error": str(e),
#                     "type": e.__class__.__name__,
#                 },
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#     @staticmethod
#     def _to_bool(value):
#         """
#         Safely convert frontend boolean values.
#         """

#         if isinstance(value, bool):
#             return value

#         if value is None:
#             return False

#         if isinstance(value, str):
#             return value.strip().lower() in (
#                 "true",
#                 "1",
#                 "yes",
#                 "on",
#             )

#         if isinstance(value, int):
#             return value == 1

#         return bool(value)

# class LessonDetailView(APIView):
#     permission_classes = [permissions.IsAuthenticated]
#     def get(self, request, pk):
#         try:
#             l = Lesson.objects.select_related('tutor','student','subject').get(pk=pk)
#             if request.user not in [l.tutor, l.student] and request.user.role not in ('admin','staff'):
#                 return Response({'error':'Forbidden.'}, status=403)
#             d = LessonSerializer(l).data
#             now = timezone.now()
#             d['can_join'] = (
#                 now >= (l.start_time - timedelta(minutes=10))
#                 and l.status in ('confirmed', 'in_progress')
#                 and l.payment_status == 'paid'
#             )
#             return Response(d)
#         except Lesson.DoesNotExist:
#             return Response({'error':'Not found.'}, status=404)

# @api_view(['POST'])
# @permission_classes([permissions.IsAuthenticated])
# def join_lesson(request, pk):
#     from django.conf import settings as dj_settings
#     try:
#         l = Lesson.objects.get(pk=pk)
#         if request.user not in [l.tutor, l.student]:
#             return Response({'error':'Not your lesson.'}, status=403)
#         if l.payment_status != 'paid':
#             return Response({'error': 'Payment is required before joining this lesson.'}, status=402)
#         if l.status not in ('confirmed', 'in_progress'):
#             return Response({'error': 'This lesson is not ready to join.'}, status=400)
#         bbb_url    = dj_settings.BBB_URL
#         bbb_secret = dj_settings.BBB_SECRET
#         if not bbb_url or not bbb_secret:
#             return Response({'join_url': None, 'error': 'Virtual classroom not configured. Contact admin.'}, status=503)
#         meeting_id = l.bbb_meeting_id or f'gooprep-lesson-{l.id}'
#         is_mod     = request.user == l.tutor
#         pw         = hashlib.sha1(f'{meeting_id}-{"mod" if is_mod else "att"}{bbb_secret}'.encode()).hexdigest()[:8]
#         join_str   = f'fullName={request.user.get_full_name()}&meetingID={meeting_id}&password={pw}&redirect=true'
#         checksum   = hashlib.sha1(f'join{join_str}{bbb_secret}'.encode()).hexdigest()
#         join_url   = f'{bbb_url}join?{join_str}&checksum={checksum}'
#         if l.status == 'confirmed':
#             l.status = 'in_progress'; l.bbb_meeting_id = meeting_id
#             l.save(update_fields=['status','bbb_meeting_id'])
#         return Response({'join_url': join_url, 'meeting_id': meeting_id})
#     except Lesson.DoesNotExist:
#         return Response({'error':'Not found.'}, status=404)

# @api_view(['POST'])
# @permission_classes([permissions.IsAuthenticated])
# def end_lesson(request, pk):
#     try:
#         l = Lesson.objects.get(pk=pk)
#         if request.user != l.tutor and request.user.role not in ('admin','staff'):
#             return Response({'error':'Only the tutor can end the lesson.'}, status=403)
#         l.status = 'completed'; l.save(update_fields=['status'])
#         try:
#             from apps.gamification.services import record_completed_lesson
#             record_completed_lesson(l)
#         except Exception:
#             pass
#         try:
#             from apps.scheduling.tasks import generate_ai_summary
#             generate_ai_summary.delay(l.id)
#         except Exception: pass
#         return Response({'ended':True})
#     except Lesson.DoesNotExist:
#         return Response({'error':'Not found.'}, status=404)

# @api_view(['POST'])
# @permission_classes([permissions.IsAuthenticated])
# def reschedule_lesson(request, pk):
#     try:
#         l = Lesson.objects.get(pk=pk)
#         if request.user not in [l.tutor, l.student]:
#             return Response({'error':'Forbidden.'}, status=403)
#         from django.utils.dateparse import parse_datetime
#         l.start_time = parse_datetime(request.data.get('new_start_time')) or l.start_time
#         l.end_time   = parse_datetime(request.data.get('new_end_time'))   or l.end_time
#         l.status = 'rescheduled'; l.save()
#         return Response({'rescheduled':True})
#     except Lesson.DoesNotExist:
#         return Response({'error':'Not found.'}, status=404)

# @api_view(['GET'])
# @permission_classes([permissions.IsAuthenticated])
# def lesson_recordings(request, pk):
#     try:
#         l = Lesson.objects.get(pk=pk)
#         recs = []
#         if l.recording_url: recs.append({'playback_url':l.recording_url,'duration':l.duration_minutes})
#         return Response({'recordings':recs})
#     except Lesson.DoesNotExist:
#         return Response({'error': 'Not found.'}, status=404)

import hashlib
import logging

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Lesson
from .serializers import (
    LessonListSerializer,
    LessonSerializer,
)
from .bbb_service import bbb


logger = logging.getLogger(__name__)


# ============================================================================
# BBB PASSWORD HELPERS
# ============================================================================

def _generate_bbb_password(kind: str, lesson_id) -> str:
    """
    Generate the same deterministic BBB password used for a lesson.

    The BBBService creates passwords using:

        gooprep-attendee-{lesson.id}
        gooprep-moderator-{lesson.id}

    Keep this logic synchronized with bbb_service.py.
    """

    if kind == "moderator":
        prefix = "gooprep-moderator"
    elif kind == "attendee":
        prefix = "gooprep-attendee"
    else:
        raise ValueError(
            "BBB password kind must be 'moderator' or 'attendee'."
        )

    return hashlib.sha256(
        f"{prefix}-{lesson_id}".encode("utf-8")
    ).hexdigest()[:12]


def _get_user_name(user) -> str:
    """
    Safely determine the display name for a user.
    """

    full_name = ""

    try:
        full_name = user.get_full_name()
    except Exception:
        pass

    if full_name:
        return full_name

    username = getattr(user, "username", "")

    if username:
        return username

    email = getattr(user, "email", "")

    if email:
        return email

    return str(user)


def _get_avatar_url(user):
    """
    Safely obtain a user's avatar URL if the user model provides it.
    """

    if not hasattr(user, "get_avatar_url"):
        return None

    try:
        return user.get_avatar_url()
    except Exception:
        return None


def _user_has_lesson_access(user, lesson) -> bool:
    """
    Return True when the authenticated user is either
    the tutor or student assigned to the lesson.
    """

    return (
        user.id == lesson.tutor_id
        or user.id == lesson.student_id
    )


# ============================================================================
# LESSON LIST / CREATE
# ============================================================================

class LessonListCreateView(APIView):
    """
    GET:
        Return lessons belonging to the authenticated user.

    POST:
        Create a new lesson.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):
        user = request.user

        queryset = (
            Lesson.objects
            .select_related(
                "tutor",
                "student",
                "subject",
            )
            .filter(
                Q(tutor=user)
                | Q(student=user)
            )
        )

        # --------------------------------------------------------------
        # Optional role filter
        # --------------------------------------------------------------

        role = request.query_params.get("role")

        if role == "tutor":
            queryset = queryset.filter(
                tutor=user
            )

        elif role == "student":
            queryset = queryset.filter(
                student=user
            )

        elif role not in (None, "", "all"):
            return Response(
                {
                    "detail": (
                        "Invalid role. "
                        "Use 'tutor', 'student', or 'all'."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        status_filter = request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        month = request.query_params.get("month")
        if month:
            try:
                year, month_number = month.split("-", 1)
                queryset = queryset.filter(
                    start_time__year=int(year),
                    start_time__month=int(month_number),
                )
            except (TypeError, ValueError):
                return Response(
                    {"detail": "month must use YYYY-MM format."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        ordering = request.query_params.get("ordering", "-start_time")
        if ordering not in {"start_time", "-start_time", "created_at", "-created_at", "status", "-status"}:
            ordering = "-start_time"
        queryset = queryset.order_by(ordering)

        try:
            page = max(1, int(request.query_params.get("page", 1)))
            page_size = min(100, max(1, int(request.query_params.get("page_size", 15))))
        except (TypeError, ValueError):
            return Response(
                {"detail": "page and page_size must be integers."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        total = queryset.count()
        start = (page - 1) * page_size
        lessons = queryset[start:start + page_size]
        serializer = LessonListSerializer(lessons, many=True)

        return Response(
            {"count": total, "results": serializer.data},
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        """
        Create a lesson.

        The serializer is responsible for validating the incoming
        lesson data.

        We do not blindly trust client-supplied student/tutor values.
        """

        serializer = LessonSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        validated = serializer.validated_data

        tutor = validated.get("tutor")
        student = validated.get("student")

        # --------------------------------------------------------------
        # Tutor is required
        # --------------------------------------------------------------

        if not tutor:
            return Response(
                {
                    "detail": "A tutor is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------------------
        # Default student to authenticated user
        # --------------------------------------------------------------

        if not student:
            student = request.user

        # --------------------------------------------------------------
        # Prevent arbitrary user impersonation
        #
        # If the booking is being created for another student,
        # the serializer/application must explicitly permit it.
        # --------------------------------------------------------------

        booked_on_behalf = validated.get(
            "booked_on_behalf",
            False,
        )

        if (
            student.id != request.user.id
            and not booked_on_behalf
            and not request.user.is_staff
        ):
            return Response(
                {
                    "detail": (
                        "You cannot create a lesson "
                        "for another student."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # --------------------------------------------------------------
        # Save
        # --------------------------------------------------------------

        lesson = serializer.save(
            student=student
        )

        logger.info(
            "Lesson %s created by user %s.",
            lesson.id,
            request.user.id,
        )

        return Response(
            LessonSerializer(
                lesson
            ).data,
            status=status.HTTP_201_CREATED,
        )


# ============================================================================
# LESSON DETAIL
# ============================================================================

class LessonDetailView(APIView):
    """
    Retrieve a lesson belonging to the authenticated user.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def get_object(self, request, pk):
        return get_object_or_404(
            Lesson.objects.select_related(
                "tutor",
                "student",
                "subject",
            ).filter(
                Q(tutor=request.user)
                | Q(student=request.user)
            ),
            pk=pk,
        )

    def get(self, request, pk):
        lesson = self.get_object(
            request,
            pk,
        )

        return Response(
            LessonSerializer(
                lesson
            ).data,
            status=status.HTTP_200_OK,
        )


# ============================================================================
# BBB PROVISION
# ============================================================================

class ProvisionBBBView(APIView):
    """
    Provision a BigBlueButton classroom for a lesson.

    POST:
        /api/scheduling/lessons/<id>/bbb/provision/
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, pk):

        lesson = get_object_or_404(
            Lesson.objects.select_related(
                "tutor",
                "student",
                "subject",
            ),
            pk=pk,
        )

        # --------------------------------------------------------------
        # Access control
        # --------------------------------------------------------------

        if not _user_has_lesson_access(
            request.user,
            lesson,
        ):
            return Response(
                {
                    "detail": (
                        "You do not have access to this lesson."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # --------------------------------------------------------------
        # Only tutor can provision
        # --------------------------------------------------------------

        if request.user.id != lesson.tutor_id:
            return Response(
                {
                    "detail": (
                        "Only the tutor can provision "
                        "the virtual classroom."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # --------------------------------------------------------------
        # Do not provision completed/cancelled lessons
        # --------------------------------------------------------------

        if lesson.status in {
            "completed",
            "cancelled",
            "no_show",
        }:
            return Response(
                {
                    "detail": (
                        "A virtual classroom cannot be "
                        "created for this lesson."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------------------
        # If already provisioned, return the existing information
        # --------------------------------------------------------------

        if lesson.bbb_meeting_id:
            return Response(
                {
                    "detail": (
                        "The virtual classroom has already "
                        "been provisioned."
                    ),
                    "meeting_id": lesson.bbb_meeting_id,
                    "join_url": lesson.bbb_join_url,
                },
                status=status.HTTP_200_OK,
            )

        # --------------------------------------------------------------
        # Provision BBB
        # --------------------------------------------------------------

        try:
            result = bbb.provision_lesson_room(
                lesson
            )

            meeting_id = result.get(
                "meeting_id"
            )

            if not meeting_id:
                logger.error(
                    "BBB provisioning returned no meeting ID "
                    "for lesson %s: %s",
                    lesson.id,
                    result,
                )

                return Response(
                    {
                        "detail": (
                            "BBB did not return a valid "
                            "meeting ID."
                        ),
                        "bbb_response": result,
                    },
                    status=status.HTTP_502_BAD_GATEWAY,
                )

            # ----------------------------------------------------------
            # Store BBB meeting information.
            #
            # The current Lesson model only has ONE bbb_join_url.
            # We store the tutor URL here because the tutor is the
            # owner/creator of the virtual classroom.
            #
            # Fresh student/tutor URLs are generated by JoinBBBView.
            # ----------------------------------------------------------

            lesson.bbb_meeting_id = meeting_id
            lesson.bbb_status = "created"
            lesson.bbb_created_at = timezone.now()

            lesson.bbb_join_url = (
                result.get(
                    "join_url_tutor",
                    "",
                )
                or ""
            )

            lesson.save(
                update_fields=[
                    "bbb_meeting_id",
                    "bbb_join_url",
                    "bbb_status",
                    "bbb_created_at",
                    "updated_at",
                ]
            )

            logger.info(
                "BBB meeting %s provisioned for lesson %s.",
                meeting_id,
                lesson.id,
            )

            return Response(
                {
                    **result,
                    "lesson_id": lesson.id,
                },
                status=status.HTTP_201_CREATED,
            )

        except RuntimeError as exc:
            logger.error(
                "BBB provisioning error for lesson %s: %s",
                lesson.id,
                exc,
            )

            return Response(
                {
                    "detail": str(exc)
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        except Exception as exc:
            logger.exception(
                "Unexpected BBB provisioning failure "
                "for lesson %s.",
                lesson.id,
            )

            return Response(
                {
                    "detail": (
                        "Failed to provision the "
                        "virtual classroom."
                    ),
                    "error": str(exc),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# ============================================================================
# BBB JOIN
# ============================================================================

class JoinBBBView(APIView):
    """
    Generate a fresh BigBlueButton join URL.

    POST:
        /api/scheduling/lessons/<id>/bbb/join/
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, pk):

        lesson = get_object_or_404(
            Lesson.objects.select_related(
                "tutor",
                "student",
            ),
            pk=pk,
        )

        # --------------------------------------------------------------
        # Access control
        # --------------------------------------------------------------

        if not _user_has_lesson_access(
            request.user,
            lesson,
        ):
            return Response(
                {
                    "detail": (
                        "You do not have access "
                        "to this lesson."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # --------------------------------------------------------------
        # BBB must exist
        # --------------------------------------------------------------

        if not lesson.bbb_meeting_id:
            return Response(
                {
                    "detail": (
                        "The virtual classroom has "
                        "not been created yet."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------------------
        # Prevent joining invalid lessons
        # --------------------------------------------------------------

        if lesson.status in {
            "cancelled",
            "completed",
            "no_show",
        }:
            return Response(
                {
                    "detail": (
                        "This lesson cannot be joined."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------------------
        # Determine role
        # --------------------------------------------------------------

        is_tutor = (
            request.user.id == lesson.tutor_id
        )

        role = (
            "moderator"
            if is_tutor
            else "attendee"
        )

        password = _generate_bbb_password(
            role,
            lesson.id,
        )

        name = _get_user_name(
            request.user
        )

        avatar_url = _get_avatar_url(
            request.user
        )

        # --------------------------------------------------------------
        # Generate join URL
        # --------------------------------------------------------------

        try:
            join_url = bbb.join_url(
                meeting_id=lesson.bbb_meeting_id,
                full_name=name,
                password=password,
                user_id=str(
                    request.user.id
                ),
                role=(
                    "MODERATOR"
                    if is_tutor
                    else "VIEWER"
                ),
                avatar_url=avatar_url,
            )

            if not join_url:
                return Response(
                    {
                        "detail": (
                            "BBB did not return "
                            "a join URL."
                        )
                    },
                    status=status.HTTP_502_BAD_GATEWAY,
                )

            # ----------------------------------------------------------
            # Check whether meeting is already running.
            # ----------------------------------------------------------

            running = False

            try:
                running = bbb.is_meeting_running(
                    lesson.bbb_meeting_id
                )
            except Exception:
                logger.warning(
                    "Unable to determine BBB running "
                    "status for lesson %s.",
                    lesson.id,
                    exc_info=True,
                )

            # ----------------------------------------------------------
            # Automatically move pending/confirmed lesson to
            # in_progress when BBB is running.
            #
            # We do NOT use bbb_status because that field does not
            # exist in the current Lesson model.
            # ----------------------------------------------------------

            if running and lesson.status in {
                "pending",
                "confirmed",
            }:
                lesson.status = "in_progress"

                lesson.save(
                    update_fields=[
                        "status",
                        "updated_at",
                    ]
                )

            logger.info(
                "User %s generated BBB join URL for lesson %s "
                "(role=%s, running=%s).",
                request.user.id,
                lesson.id,
                role,
                running,
            )

            return Response(
                {
                    "join_url": join_url,
                    "meeting_id": (
                        lesson.bbb_meeting_id
                    ),
                    "role": role,
                    "running": running,
                    "lesson_status": lesson.status,
                },
                status=status.HTTP_200_OK,
            )

        except RuntimeError as exc:
            logger.error(
                "BBB join configuration error "
                "for lesson %s: %s",
                lesson.id,
                exc,
            )

            return Response(
                {
                    "detail": str(exc)
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        except Exception as exc:
            logger.exception(
                "BBB join failed for lesson %s.",
                lesson.id,
            )

            return Response(
                {
                    "detail": (
                        "Failed to generate the "
                        "virtual classroom URL."
                    ),
                    "error": str(exc),
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )


# ============================================================================
# BBB STATUS
# ============================================================================

class BBBStatusView(APIView):
    """
    Check whether the BBB classroom for a lesson is running.

    GET:
        /api/scheduling/lessons/<id>/bbb/status/
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request, pk):

        lesson = get_object_or_404(
            Lesson.objects.select_related(
                "tutor",
                "student",
            ),
            pk=pk,
        )

        # --------------------------------------------------------------
        # Access control
        # --------------------------------------------------------------

        if not _user_has_lesson_access(
            request.user,
            lesson,
        ):
            return Response(
                {
                    "detail": "Access denied."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # --------------------------------------------------------------
        # Meeting not created
        # --------------------------------------------------------------

        if not lesson.bbb_meeting_id:
            return Response(
                {
                    "meeting_id": None,
                    "running": False,
                    "lesson_status": lesson.status,
                    "bbb_status": "not_created",
                },
                status=status.HTTP_200_OK,
            )

        # --------------------------------------------------------------
        # Check BBB
        # --------------------------------------------------------------

        try:
            running = bbb.is_meeting_running(
                lesson.bbb_meeting_id
            )

            # ----------------------------------------------------------
            # Update lesson status if appropriate.
            # ----------------------------------------------------------

            if running:
                if lesson.status in {
                    "pending",
                    "confirmed",
                }:
                    lesson.status = "in_progress"

                    lesson.save(
                        update_fields=[
                            "status",
                            "updated_at",
                        ]
                    )

                bbb_status = "running"

            else:
                if lesson.status == "in_progress":
                    bbb_status = "ended"
                else:
                    bbb_status = "not_running"

            return Response(
                {
                    "meeting_id": (
                        lesson.bbb_meeting_id
                    ),
                    "running": running,
                    "bbb_status": bbb_status,
                    "lesson_status": lesson.status,
                },
                status=status.HTTP_200_OK,
            )

        except RuntimeError as exc:
            logger.error(
                "BBB status configuration error "
                "for lesson %s: %s",
                lesson.id,
                exc,
            )

            return Response(
                {
                    "detail": str(exc)
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        except Exception as exc:
            logger.exception(
                "BBB status check failed "
                "for lesson %s.",
                lesson.id,
            )

            return Response(
                {
                    "detail": (
                        "Unable to determine "
                        "BBB meeting status."
                    ),
                    "error": str(exc),
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )


# ============================================================================
# END BBB MEETING
# ============================================================================

class EndBBBView(APIView):
    """
    End an active BigBlueButton meeting.

    POST:
        /api/scheduling/lessons/<id>/bbb/end/

    Only the tutor can end the classroom.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, pk):

        lesson = get_object_or_404(
            Lesson.objects.select_related(
                "tutor",
                "student",
            ),
            pk=pk,
        )

        # --------------------------------------------------------------
        # Only tutor can end meeting
        # --------------------------------------------------------------

        if request.user.id != lesson.tutor_id:
            return Response(
                {
                    "detail": (
                        "Only the tutor can end "
                        "the virtual classroom."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # --------------------------------------------------------------
        # Meeting must exist
        # --------------------------------------------------------------

        if not lesson.bbb_meeting_id:
            return Response(
                {
                    "detail": (
                        "No BBB meeting exists "
                        "for this lesson."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------------------
        # Generate moderator password
        # --------------------------------------------------------------

        moderator_password = _generate_bbb_password(
            "moderator",
            lesson.id,
        )

        try:
            response = bbb.end_meeting(
                meeting_id=lesson.bbb_meeting_id,
                moderator_pw=moderator_password,
            )

            if not bbb._success(response):
                logger.error(
                    "BBB failed to end meeting "
                    "for lesson %s: %s",
                    lesson.id,
                    response,
                )

                return Response(
                    {
                        "detail": (
                            response.get(
                                "message",
                                "BBB failed to end the meeting.",
                            )
                        ),
                        "bbb_response": response,
                    },
                    status=status.HTTP_502_BAD_GATEWAY,
                )

            # ----------------------------------------------------------
            # Mark lesson as completed if it was in progress.
            #
            # We do not automatically mark every lesson completed,
            # because a tutor may manually end a lesson early.
            # ----------------------------------------------------------

            if lesson.status == "in_progress":
                lesson.status = "completed"

                lesson.save(
                    update_fields=[
                        "status",
                        "updated_at",
                    ]
                )

            logger.info(
                "BBB meeting ended for lesson %s.",
                lesson.id,
            )

            return Response(
                {
                    "detail": (
                        "Virtual classroom ended successfully."
                    ),
                    "meeting_id": (
                        lesson.bbb_meeting_id
                    ),
                    "lesson_status": lesson.status,
                    "bbb_response": response,
                },
                status=status.HTTP_200_OK,
            )

        except RuntimeError as exc:
            logger.error(
                "BBB end meeting configuration error "
                "for lesson %s: %s",
                lesson.id,
                exc,
            )

            return Response(
                {
                    "detail": str(exc)
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        except Exception as exc:
            logger.exception(
                "Failed to end BBB meeting "
                "for lesson %s.",
                lesson.id,
            )

            return Response(
                {
                    "detail": (
                        "Failed to end the "
                        "virtual classroom."
                    ),
                    "error": str(exc),
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )


# ============================================================================
# LESSON RECORDINGS
# ============================================================================

class LessonRecordingsView(APIView):
    """
    Retrieve BBB recordings belonging to a lesson.

    GET:
        /api/scheduling/lessons/<id>/bbb/recordings/
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request, pk):

        lesson = get_object_or_404(
            Lesson.objects.select_related(
                "tutor",
                "student",
            ),
            pk=pk,
        )

        # --------------------------------------------------------------
        # Access control
        # --------------------------------------------------------------

        if not _user_has_lesson_access(
            request.user,
            lesson,
        ):
            return Response(
                {
                    "detail": "Access denied."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # --------------------------------------------------------------
        # Meeting does not exist
        # --------------------------------------------------------------

        if not lesson.bbb_meeting_id:
            return Response(
                {
                    "recordings": [],
                    "recording_available": False,
                    "recording_url": "",
                },
                status=status.HTTP_200_OK,
            )

        # --------------------------------------------------------------
        # Retrieve recordings
        # --------------------------------------------------------------

        try:
            recordings = bbb.get_lesson_recordings(
                lesson
            )

            # ----------------------------------------------------------
            # Update Lesson recording fields.
            #
            # The model contains:
            #
            # recording_available
            # recording_url
            #
            # We use the first usable playback URL.
            # ----------------------------------------------------------

            recording_available = bool(
                recordings
            )

            recording_url = ""

            for recording in recordings:
                url = recording.get(
                    "playback_url",
                    "",
                )

                if url:
                    recording_url = url
                    break

                # Fallback to the first available format.
                for fmt in recording.get(
                    "formats",
                    [],
                ):
                    fmt_url = fmt.get(
                        "url",
                        "",
                    )

                    if fmt_url:
                        recording_url = fmt_url
                        break

                if recording_url:
                    break

            update_fields = []

            if lesson.recording_available != recording_available:
                lesson.recording_available = (
                    recording_available
                )
                update_fields.append(
                    "recording_available"
                )

            if lesson.recording_url != recording_url:
                lesson.recording_url = recording_url
                update_fields.append(
                    "recording_url"
                )

            if update_fields:
                update_fields.append(
                    "updated_at"
                )

                lesson.save(
                    update_fields=update_fields
                )

            return Response(
                {
                    "recordings": recordings,
                    "recording_available": (
                        lesson.recording_available
                    ),
                    "recording_url": (
                        lesson.recording_url
                    ),
                },
                status=status.HTTP_200_OK,
            )

        except RuntimeError as exc:
            logger.error(
                "BBB recordings configuration error "
                "for lesson %s: %s",
                lesson.id,
                exc,
            )

            return Response(
                {
                    "detail": str(exc)
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        except Exception as exc:
            logger.exception(
                "Failed retrieving recordings "
                "for lesson %s.",
                lesson.id,
            )

            return Response(
                {
                    "detail": (
                        "Failed to retrieve "
                        "lesson recordings."
                    ),
                    "error": str(exc),
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )


# ============================================================================
# BBB HEALTH
# ============================================================================

class BBBHealthView(APIView):
    """
    Check BigBlueButton connectivity.

    GET:
        /api/scheduling/bbb/health/

    Staff only.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):

        if not request.user.is_staff:
            return Response(
                {
                    "detail": "Staff access required."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        configured = bbb.configured

        if not configured:
            return Response(
                {
                    "configured": False,
                    "healthy": False,
                    "bbb_url": "",
                    "detail": (
                        "BigBlueButton is not configured."
                    ),
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:
            healthy = bbb.server_healthy()

            return Response(
                {
                    "configured": True,
                    "healthy": healthy,
                    "bbb_url": bbb.base_url,
                },
                status=(
                    status.HTTP_200_OK
                    if healthy
                    else status.HTTP_503_SERVICE_UNAVAILABLE
                ),
            )

        except Exception as exc:
            logger.exception(
                "BBB health check failed."
            )

            return Response(
                {
                    "configured": configured,
                    "healthy": False,
                    "bbb_url": (
                        bbb.base_url
                        if configured
                        else ""
                    ),
                    "detail": str(exc),
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
