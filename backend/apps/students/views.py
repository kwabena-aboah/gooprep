from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from django.contrib.auth import get_user_model
from .models import StudentProfile
from .serializers import StudentOnboardingSerializer

User = get_user_model()


class StudentProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from apps.scheduling.models import Lesson
        profile, _ = StudentProfile.objects.get_or_create(user=request.user)
        lessons = Lesson.objects.filter(student=request.user)
        completed = lessons.filter(status='completed')
        minutes = completed.aggregate(total=Sum('duration_minutes'))['total'] or 0
        return Response({
            'id': request.user.id,
            'full_name': request.user.get_full_name(),
            'email': request.user.email,
            'avatar_url': request.user.get_avatar_url(),
            'city': request.user.city,
            'country': request.user.country,
            'timezone': request.user.timezone,
            'total_lessons': lessons.count(),
            'completed': completed.count(),
            'hours_learned': round(float(minutes) / 60, 1),
            'streak_days': request.user.streak_days,
            'total_points': request.user.total_points,
            'level': request.user.level,
            'education_level': profile.education_level,
            'school': profile.school,
            'learning_goals': profile.learning_goals,
            'subjects_interest': profile.subjects_interest,
            'is_approved': profile.is_approved,
        })

    def patch(self, request):
        profile, _ = StudentProfile.objects.get_or_create(user=request.user)
        user_fields = ['city', 'country', 'bio', 'timezone', 'language', 'date_of_birth']
        changed_fields = []
        for field in user_fields:
            if field in request.data:
                setattr(request.user, field, request.data[field])
                changed_fields.append(field)
        if changed_fields:
            request.user.save(update_fields=changed_fields)

        serializer = StudentOnboardingSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'saved': True, 'profile': serializer.data})
