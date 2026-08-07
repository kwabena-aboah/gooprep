from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import StudentProfile

User = get_user_model()


class StudentProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from scheduling.models import Lesson
        from django.db.models import Sum
        sp, _  = StudentProfile.objects.get_or_create(user=request.user)
        lessons = Lesson.objects.filter(student=request.user)
        completed = lessons.filter(status='completed')
        hours = float((completed.aggregate(h=Sum('duration_minutes'))['h'] or 0) / 60)
        return Response({
            'id':            request.user.id,
            'full_name':     request.user.get_full_name(),
            'email':         request.user.email,
            'avatar_url':    request.user.get_avatar_url(),
            'city':          request.user.city,
            'timezone':      request.user.timezone,
            'total_lessons': lessons.count(),
            'completed':     completed.count(),
            'hours_learned': round(hours, 1),
            'streak_days':   request.user.streak_days,
            'total_points':  request.user.total_points,
            'level':         request.user.level,
            'education_level': sp.education_level,
            'school':          sp.school,
            'learning_goals':  sp.learning_goals,
            'is_approved':     sp.is_approved,
        })

    def patch(self, request):
        sp, _ = StudentProfile.objects.get_or_create(user=request.user)
        u = request.user
        for field in ['city','country','bio','timezone','language']:
            if field in request.data:
                setattr(u, field, request.data[field])
        u.save()
        for field in ['education_level','school','subjects_interest','learning_goals']:
            if field in request.data:
                setattr(sp, field, request.data[field])
        sp.save()
        return Response({'saved': True})