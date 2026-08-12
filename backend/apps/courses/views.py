from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from django.db.models import Q
from .models import GroupClass, GroupClassEnrollment
from .serializers import GroupClassSerializer

class GroupClassListView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        qs = GroupClass.objects.filter(is_active=True).select_related('tutor','subject')
        subject = request.query_params.get('subject')
        level   = request.query_params.get('level')
        if subject:
            subject_filter = Q(subject__slug=subject)
            if str(subject).isdigit():
                subject_filter |= Q(subject_id=int(subject))
            qs = qs.filter(subject_filter)
        if level:   qs = qs.filter(level=level)
        page_size = int(request.query_params.get('page_size', 12))
        page      = int(request.query_params.get('page', 1))
        total     = qs.count()
        enrolled_ids = set()
        if request.user.is_authenticated:
            enrolled_ids = set(
                GroupClassEnrollment.objects.filter(student=request.user)
                .values_list('group_class_id', flat=True)
            )
        data = GroupClassSerializer(
            qs[(page-1)*page_size : page*page_size], many=True
        ).data
        for i, gc in enumerate(qs[(page-1)*page_size : page*page_size]):
            data[i]['is_enrolled'] = gc.id in enrolled_ids
            data[i]['spots_left']  = max(0, gc.max_students - gc.enrolled)
        return Response({'count': total, 'results': data})

    def post(self, request):
        """Tutors create group classes."""
        if request.user.role not in ('tutor', 'admin'):
            return Response({'error': 'Only tutors can create group classes.'}, status=403)
        from apps.tutors.models import Subject
        from django.utils.dateparse import parse_datetime
        gc = GroupClass.objects.create(
            tutor=request.user,
            subject=Subject.objects.filter(id=request.data.get('subject')).first(),
            title=request.data.get('title', ''),
            description=request.data.get('description', ''),
            level=request.data.get('level', 'beginner'),
            start_time=parse_datetime(request.data.get('start_time','')),
            duration_minutes=int(request.data.get('duration_minutes', 60)),
            max_students=int(request.data.get('max_students', 10)),
            price=request.data.get('price', 0),
        )
        return Response(GroupClassSerializer(gc).data, status=201)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def enroll_class(request, pk):
    try:
        gc = GroupClass.objects.get(pk=pk, is_active=True)
    except GroupClass.DoesNotExist:
        return Response({'error': 'Class not found.'}, status=404)
    if gc.enrolled >= gc.max_students:
        return Response({'error': 'This class is full.'}, status=400)
    enr, created = GroupClassEnrollment.objects.get_or_create(
        group_class=gc, student=request.user
    )
    if not created:
        return Response({'error': 'Already enrolled.'}, status=400)
    try:
        from apps.messaging.guppy import get_or_create_guppy_user, send_push_notification
        tutor_gid = get_or_create_guppy_user(gc.tutor)
        if tutor_gid:
            send_push_notification(
                tutor_gid, '📚 New Enrollment',
                f'{request.user.get_full_name()} enrolled in "{gc.title}".'
            )
    except Exception:
        pass
    return Response({'enrolled': True, 'class_id': gc.id}, status=201)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def bulk_enroll_classes(request):
    class_ids = request.data.get('class_ids', [])
    if not isinstance(class_ids, list) or not class_ids:
        return Response({'error': 'class_ids must be a non-empty list.'}, status=400)

    with transaction.atomic():
        classes = list(
            GroupClass.objects.select_for_update()
            .filter(id__in=class_ids, is_active=True)
        )
        if len(classes) != len(set(class_ids)):
            return Response({'error': 'One or more group classes were not found.'}, status=404)

        already = set(GroupClassEnrollment.objects.filter(
            student=request.user, group_class_id__in=class_ids
        ).values_list('group_class_id', flat=True))
        to_enroll = [gc for gc in classes if gc.id not in already]
        full = [gc.id for gc in to_enroll if gc.enrolled >= gc.max_students]
        if full:
            return Response({'error': 'Some selected classes are full.', 'full_class_ids': full}, status=400)

        GroupClassEnrollment.objects.bulk_create([
            GroupClassEnrollment(group_class=gc, student=request.user)
            for gc in to_enroll
        ])

    return Response({
        'enrolled': [gc.id for gc in to_enroll],
        'already_enrolled': sorted(already),
    }, status=201)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def unenroll_class(request, pk):
    deleted, _ = GroupClassEnrollment.objects.filter(
        group_class_id=pk, student=request.user
    ).delete()
    if deleted:
        return Response({'unenrolled': True})
    return Response({'error': 'Enrollment not found.'}, status=404)

class MyGroupClassesView(APIView):
    """Classes enrolled in (student) or created (tutor)."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role == 'tutor':
            qs = GroupClass.objects.filter(tutor=request.user).select_related('subject')
        else:
            enrolled_ids = GroupClassEnrollment.objects.filter(
                student=request.user
            ).values_list('group_class_id', flat=True)
            qs = GroupClass.objects.filter(id__in=enrolled_ids).select_related('tutor','subject')
        data = GroupClassSerializer(qs, many=True).data
        return Response({'count': len(data), 'results': data})
