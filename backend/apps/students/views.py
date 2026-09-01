from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from apps.tutors.models import UserDocument
from django.db.models import Sum
from django.contrib.auth import get_user_model
from .models import StudentProfile
from .serializers import StudentOnboardingSerializer

User = get_user_model()


class StudentProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        from apps.scheduling.models import Lesson
        profile, _ = StudentProfile.objects.get_or_create(user=request.user)
        lessons = Lesson.objects.filter(student=request.user)
        completed = lessons.filter(status='completed')
        minutes = completed.aggregate(total=Sum('duration_minutes'))['total'] or 0
        return Response({
            'id': request.user.id,
            'full_name': request.user.get_full_name(),
            'phone': request.user.phone,
            'address': request.user.address,
            'date_of_birth': request.user.date_of_birth,
            'gender': request.user.gender,
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
            'identity_document_type': profile.identity_document_type,
            'has_identity_document': UserDocument.objects.filter(
                user=request.user,
                doc_type__in=['ghana_passport_card', 'voters_id_card', 'drivers_license', 'other_id'],
            ).exists(),
            'is_approved': profile.is_approved,
        })

    def patch(self, request):
        profile, _ = StudentProfile.objects.get_or_create(user=request.user)
        user_fields = ['city', 'address', 'country', 'bio', 'timezone', 'language', 'date_of_birth', 'gender']
        changed_fields = []
        for field in user_fields:
            if field in request.data:
                value = request.data[field]
                # Nullable date fields must receive None, not an empty string.
                if field == 'date_of_birth' and value == '':
                    value = None
                setattr(request.user, field, value)
                changed_fields.append(field)
        if changed_fields:
            request.user.save(update_fields=changed_fields)

        serializer = StudentOnboardingSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

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
        return Response({'saved': True, 'profile': serializer.data})
