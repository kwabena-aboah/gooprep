from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import IntegrityError
from django.db.models import Q
import json
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import TutorProfile, Subject, TutorFavourite, UserDocument
from .serializers import TutorProfileSerializer, SubjectSerializer

class AnyOrAuth(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in ('GET','HEAD','OPTIONS'): return True
        return bool(request.user and request.user.is_authenticated)

class SubjectListView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        return Response(SubjectSerializer(Subject.objects.all(), many=True).data)

class TutorListView(APIView):
    permission_classes = [AnyOrAuth]
    def get(self, request):
        qs = TutorProfile.objects.filter(
            approval_status='approved',
            user__role='tutor',
        ).exclude(
            user__role__in=['admin', 'student'],
        ).select_related('user').prefetch_related('subjects')
        s = request.query_params.get('search')
        subj = request.query_params.get('subject')
        min_p = request.query_params.get('min_price')
        max_p = request.query_params.get('max_price')
        min_r = request.query_params.get('min_rating')
        ib    = request.query_params.get('instant_book')
        feat  = request.query_params.get('is_featured')
        order = request.query_params.get('ordering','-average_rating')
        if s:   qs = qs.filter(Q(user__first_name__icontains=s)|Q(user__last_name__icontains=s)|Q(headline__icontains=s))
        if subj: qs = qs.filter(subjects__slug=subj)
        if min_p: qs = qs.filter(hourly_rate__gte=min_p)
        if max_p: qs = qs.filter(hourly_rate__lte=max_p)
        if min_r: qs = qs.filter(average_rating__gte=min_r)
        if ib=='true': qs = qs.filter(instant_book=True)
        if feat == 'true':
            qs = qs.filter(is_featured=True)
        teaching_style = request.query_params.get('teaching_style')
        if teaching_style:
            qs = qs.filter(teaching_style=teaching_style)
        order_map = {'-average_rating':'-average_rating','hourly_rate':'hourly_rate','-hourly_rate':'-hourly_rate','-total_lessons':'-total_lessons'}
        qs = qs.order_by(order_map.get(order,'-average_rating'))
        page_size = int(request.query_params.get('page_size',12))
        page = int(request.query_params.get('page',1))
        total = qs.count()
        fav_ids = set()
        if request.user.is_authenticated:
            fav_ids = set(TutorFavourite.objects.filter(student=request.user).values_list('tutor_id',flat=True))
        items = qs[(page-1)*page_size : page*page_size]
        data  = TutorProfileSerializer(items, many=True).data
        for i, tp in enumerate(items):
            data[i]['is_favourited'] = tp.id in fav_ids
        return Response({'count':total,'results':data})

class TutorDetailView(APIView):
    permission_classes = [AnyOrAuth]
    def get(self, request, pk):
        try:
            tp = TutorProfile.objects.select_related('user').prefetch_related('subjects').get(
                pk=pk,
                approval_status='approved',
                user__role='tutor',
            )
            d  = TutorProfileSerializer(tp).data
            if request.user.is_authenticated:
                d['is_favourited'] = TutorFavourite.objects.filter(student=request.user, tutor=tp).exists()
            else:
                d['is_favourited'] = False
            return Response(d)
        except TutorProfile.DoesNotExist:
            return Response({'error':'Not found.'}, status=404)

class TutorSlugView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request, slug):
        try:
            tp = TutorProfile.objects.select_related('user').prefetch_related('subjects').get(
                slug=slug,
                approval_status='approved',
                user__role='tutor',
            )
            return Response(TutorProfileSerializer(tp).data)
        except TutorProfile.DoesNotExist:
            return Response({'error':'Not found.'}, status=404)

class MyTutorProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        tp, _ = TutorProfile.objects.get_or_create(user=request.user)
        return Response(TutorProfileSerializer(tp).data)
    def patch(self, request):
        tp, _ = TutorProfile.objects.get_or_create(user=request.user)
        for f in ['headline','bio','years_experience','hourly_rate','teaching_style',
                  'instant_book','trial_lesson_enabled','trial_lesson_price',
                  'intro_video_url','slug','record_by_default','education','certifications','packages','identity_document_type',
                  'response_time']:
            if f in request.data: setattr(tp, f, request.data[f])
        if 'subjects' in request.data:
            tp.subjects.set(Subject.objects.filter(id__in=request.data['subjects']))

        requested_slug = request.data.get('slug')
        if requested_slug:
            requested_slug = str(requested_slug).strip().lower()
            tp.slug = requested_slug
            if TutorProfile.objects.filter(slug=requested_slug).exclude(pk=tp.pk).exists():
                return Response(
                    {'slug': ['This profile URL is already in use. Choose another slug.']},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        try:
            tp.save()
        except IntegrityError:
            return Response(
                {'slug': ['This profile URL is already in use. Choose another slug.']},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(TutorProfileSerializer(tp).data)

class TutorAvailabilityView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        return [permissions.AllowAny()] if self.request.method == 'GET' else [permissions.IsAuthenticated()]
    def get(self, request, pk=None):
        tp = TutorProfile.objects.filter(pk=pk).first() if pk else TutorProfile.objects.filter(user=request.user).first()
        return Response({
            'availability': tp.availability if tp else [],
            'blocked_dates': tp.blocked_dates if tp else [],
            'instant_book': tp.instant_book if tp else True,
            'min_notice_hours': tp.min_notice_hours if tp else 24,
            'max_daily_bookings': tp.max_daily_bookings if tp else 6,
            'booking_buffer_minutes': tp.booking_buffer_minutes if tp else 15,
            'response_time': tp.response_time if tp else 60,
        })
    def post(self, request):
        tp, _ = TutorProfile.objects.get_or_create(user=request.user)
        tp.availability = request.data.get('slots', tp.availability or [])
        tp.blocked_dates = request.data.get('blocked_dates', tp.blocked_dates or [])
        if 'instant_book' in request.data: tp.instant_book = request.data['instant_book']
        for key, field in [('min_notice', 'min_notice_hours'), ('max_daily', 'max_daily_bookings'), ('buffer', 'booking_buffer_minutes')]:
            if key in request.data:
                try:
                    value = max(0, int(request.data[key]))
                    if field == 'max_daily_bookings': value = max(1, value)
                    setattr(tp, field, value)
                except (TypeError, ValueError):
                    return Response({'error': f'Invalid {key}.'}, status=400)
        tp.save(update_fields=['availability','blocked_dates','instant_book','min_notice_hours','max_daily_bookings','booking_buffer_minutes'])
        return Response({'saved': True, 'availability': tp.availability, 'blocked_dates': tp.blocked_dates,
                         'instant_book': tp.instant_book, 'min_notice_hours': tp.min_notice_hours,
                         'max_daily_bookings': tp.max_daily_bookings, 'booking_buffer_minutes': tp.booking_buffer_minutes})

class MyStudentsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        from apps.scheduling.models import Lesson
        from django.contrib.auth import get_user_model
        User = get_user_model()
        search = request.query_params.get('search','')
        student_ids = Lesson.objects.filter(tutor=request.user, status='completed').values_list('student_id',flat=True).distinct()
        qs = User.objects.filter(id__in=student_ids)
        if search: qs = qs.filter(Q(first_name__icontains=search)|Q(last_name__icontains=search))
        page_size = int(request.query_params.get('page_size',12))
        page = int(request.query_params.get('page',1))
        total = qs.count()
        items = []
        for u in qs[(page-1)*page_size:page*page_size]:
            lessons = Lesson.objects.filter(tutor=request.user, student=u)
            items.append({
                'id':u.id,'full_name':u.get_full_name(),'email':u.email,
                'avatar_url':u.get_avatar_url(),'city':u.city,
                'total_lessons_with_me':lessons.count(),
                'completed':lessons.filter(status='completed').count(),
                'last_lesson_at':lessons.order_by('-start_time').values_list('start_time',flat=True).first(),
            })
        return Response({'count':total,'results':items})

class FavouritesView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        fav_ids = TutorFavourite.objects.filter(student=request.user).values_list('tutor_id',flat=True)
        profiles = TutorProfile.objects.filter(id__in=fav_ids).select_related('user').prefetch_related('subjects')
        data = TutorProfileSerializer(profiles, many=True).data
        for d in data: d['is_favourited'] = True
        return Response({'results':data})

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_favourite(request, pk):
    try:
        tp = TutorProfile.objects.get(pk=pk)
        fav, created = TutorFavourite.objects.get_or_create(student=request.user, tutor=tp)
        if not created: fav.delete(); return Response({'favourited':False})
        return Response({'favourited':True})
    except TutorProfile.DoesNotExist:
        return Response({'error':'Not found.'}, status=404)

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def tutor_onboarding(request):
    if request.method == 'GET':
        tp = TutorProfile.objects.filter(user=request.user).first()
        if not tp:
            return Response({'exists': False, 'onboarding_complete': False})
        has_identity_document = UserDocument.objects.filter(
            user=request.user, doc_type__in=['ghana_passport_card', 'voters_id_card', 'drivers_license', 'other_id']
        ).exists()
        return Response({
            'exists': True,
            'profile': TutorProfileSerializer(tp, context={'request': request}).data,
            'has_identity_document': has_identity_document,
            'onboarding_complete': tp.approval_status in ('pending', 'approved') and has_identity_document,
        })
    from django.utils.text import slugify

    tp = TutorProfile.objects.filter(user=request.user).first()
    if tp is None:
        base = slugify(request.user.get_full_name()) or f'tutor-{request.user.id}'
        slug = base
        n = 1
        while TutorProfile.objects.filter(slug=slug).exists():
            slug = f'{base}-{n}'
            n += 1
        tp = TutorProfile.objects.create(user=request.user, slug=slug)

    boolean_fields = {'instant_book', 'trial_lesson_enabled'}
    for f in ['headline','bio','years_experience','hourly_rate','teaching_style',
              'instant_book','trial_lesson_enabled','trial_lesson_price','intro_video_url','education','certifications','identity_document_type']:
        if f in request.data:
            value = request.data[f]
            if f in boolean_fields:
                normalized = str(value).strip().lower()
                value = normalized in {'true', '1', 'yes', 'on'}
            elif f in ('education', 'certifications') and isinstance(value, str):
                value = json.loads(value or '[]')
            setattr(tp, f, value)
    if 'subjects' in request.data:
        tp.subjects.set(Subject.objects.filter(id__in=request.data.getlist('subjects')))
    if not tp.slug:
        base = slugify(request.user.get_full_name()) or f'tutor-{request.user.id}'
        slug = base; n = 1
        while TutorProfile.objects.filter(slug=slug).exclude(pk=tp.pk).exists():
            slug = f'{base}-{n}'; n += 1
        tp.slug = slug
    tp.approval_status = 'pending'
    tp.save()

    identity_file = request.FILES.get('identity_document')
    identity_type = request.data.get('identity_document_type')
    if identity_file and identity_type:
        UserDocument.objects.create(user=request.user, doc_type=identity_type, file=identity_file)
    for file_obj in request.FILES.getlist('documents'):
        UserDocument.objects.create(
            user=request.user,
            doc_type=request.data.get('document_type', 'other'),
            file=file_obj,
        )
    request.user.role = 'tutor'; request.user.save(update_fields=['role'])
    # Guppy notification to admin
    try:
        from apps.messaging.guppy import notify_admin_new_tutor
        notify_admin_new_tutor(request.user)
    except Exception: pass
    return Response({'submitted': True, 'status': 'pending'})