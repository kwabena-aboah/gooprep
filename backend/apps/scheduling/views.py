import hashlib
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from datetime import timedelta
from .models import Lesson
from .serializers import LessonSerializer

class LessonListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        u = request.user
        if u.role == 'tutor':         qs = Lesson.objects.filter(tutor=u)
        elif u.role in ('admin','staff'): qs = Lesson.objects.all()
        else:                          qs = Lesson.objects.filter(student=u)
        s  = request.query_params.get('status')
        m  = request.query_params.get('month')
        sid = request.query_params.get('student')
        if s:   qs = qs.filter(status=s)
        if m:
            try: y,mo = m.split('-'); qs = qs.filter(start_time__year=y, start_time__month=mo)
            except: pass
        if sid and u.role=='tutor': qs = qs.filter(student_id=sid)
        order = request.query_params.get('ordering','-start_time')
        qs = qs.select_related('tutor','student','subject').order_by(order)
        page_size = int(request.query_params.get('page_size',15))
        page = int(request.query_params.get('page',1))
        total = qs.count()
        now = timezone.now()
        data = LessonSerializer(qs[(page-1)*page_size:page*page_size], many=True).data
        for i, lesson in enumerate(qs[(page-1)*page_size:page*page_size]):
            win = lesson.start_time - timedelta(minutes=10)
            data[i]['can_join'] = now >= win and lesson.status in ('confirmed','in_progress')
        return Response({'count':total,'results':data})

    def post(self, request):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            tutor = User.objects.get(id=request.data.get('tutor'))
            # Determine the actual student
            student = request.user
            if request.data.get('booked_on_behalf') and request.data.get('learner_email'):
                learner = User.objects.filter(email=request.data['learner_email']).first()
                if learner: student = learner
            from django.utils.dateparse import parse_datetime
            start = parse_datetime(request.data['start_time'])
            end   = parse_datetime(request.data['end_time'])
            duration = int((end - start).total_seconds() / 60)
            lesson = Lesson.objects.create(
                tutor=tutor, student=student,
                subject_id=request.data.get('subject') or None,
                lesson_type=request.data.get('lesson_type','regular'),
                start_time=start, end_time=end, duration_minutes=duration,
                price=request.data.get('price',0), currency=request.data.get('currency','GHS'),
                record_session=request.data.get('record_session',True),
                topic=request.data.get('topic',''), status='confirmed', payment_status='paid',
                booked_on_behalf=request.data.get('booked_on_behalf',False),
                booker_name=request.data.get('booker_name',''),
                booker_relationship=request.data.get('booker_relationship',''),
                booker_phone=request.data.get('booker_phone',''),
                booker_email=request.data.get('booker_email',''),
                notes=request.data.get('notes',''),
            )
            try:
                from apps.messaging.guppy import notify_lesson_booked
                notify_lesson_booked(lesson)
            except Exception: pass
            d = LessonSerializer(lesson).data
            d['can_join'] = False
            return Response(d, status=201)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

class LessonDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, pk):
        try:
            l = Lesson.objects.select_related('tutor','student','subject').get(pk=pk)
            if request.user not in [l.tutor, l.student] and request.user.role not in ('admin','staff'):
                return Response({'error':'Forbidden.'}, status=403)
            d = LessonSerializer(l).data
            now = timezone.now()
            d['can_join'] = now >= (l.start_time - timedelta(minutes=10)) and l.status in ('confirmed','in_progress')
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
        bbb_url    = dj_settings.BBB_URL
        bbb_secret = dj_settings.BBB_SECRET
        if not bbb_url:
            return Response({'join_url':None,'error':'Virtual classroom not configured. Contact admin.'})
        meeting_id = l.bbb_meeting_id or f'gooprep-lesson-{l.id}'
        is_mod     = request.user == l.tutor
        pw         = hashlib.sha1(f'{meeting_id}-{"mod" if is_mod else "att"}{bbb_secret}'.encode()).hexdigest()[:8]
        join_str   = f'fullName={request.user.get_full_name()}&meetingID={meeting_id}&password={pw}&redirect=true'
        checksum   = hashlib.sha1(f'join{join_str}{bbb_secret}'.encode()).hexdigest()
        join_url   = f'{bbb_url}join?{join_str}&checksum={checksum}'
        if l.status == 'confirmed':
            l.status = 'in_progress'; l.bbb_meeting_id = meeting_id
            l.save(update_fields=['status','bbb_meeting_id'])
        return Response({'join_url':join_url,'meeting_id':meeting_id})
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
            from scheduling.tasks import generate_ai_summary
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
        return Response({'error':'Not found.'}, status=404)