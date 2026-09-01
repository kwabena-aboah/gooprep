from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Institution, InstitutionMember
from .serializers import InstitutionSerializer

User = get_user_model()


class InstitutionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_owned(self, request):
        return Institution.objects.prefetch_related('members__user').get(owner=request.user)

    def get(self, request):
        try:
            institution = self.get_owned(request)
        except Institution.DoesNotExist:
            return Response({'detail': 'No institution found.'}, status=404)
        data = InstitutionSerializer(institution, context={'request': request}).data
        data['members'] = [
            {'id': member.user_id, 'name': member.user.get_full_name(),
             'email': member.user.email, 'role': member.role}
            for member in institution.members.all()[:100]
        ]
        return Response(data)

    def post(self, request):
        if Institution.objects.filter(owner=request.user).exists():
            return Response({'error': 'You already have an institution.'}, status=400)
        serializer = InstitutionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        institution = serializer.save(owner=request.user)
        # New institutions must complete admin review before verification.
        request.user.role = 'institution'
        request.user.save(update_fields=['role'])
        return Response(InstitutionSerializer(institution).data, status=201)

    def patch(self, request):
        try:
            institution = self.get_owned(request)
        except Institution.DoesNotExist:
            return Response({'error': 'No institution found.'}, status=404)
        serializer = InstitutionSerializer(institution, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'saved': True, 'institution': serializer.data})


class InstitutionMemberView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_owned(self, request):
        return Institution.objects.get(owner=request.user)

    def post(self, request):
        try:
            institution = self.get_owned(request)
        except Institution.DoesNotExist:
            return Response({'error': 'No institution found.'}, status=404)
        email = request.data.get('email', '').strip().lower()
        if not email:
            return Response({'error': 'Member email is required.'}, status=400)
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            return Response({'error': 'No user found with that email.'}, status=404)
        role = request.data.get('role', 'student')
        if role not in {'student', 'tutor', 'staff'}:
            return Response({'error': 'Invalid member role.'}, status=400)
        member, created = InstitutionMember.objects.get_or_create(
            institution=institution, user=user, defaults={'role': role}
        )
        if not created:
            return Response({'error': 'User is already a member.'}, status=400)
        return Response({'added': True, 'name': user.get_full_name(), 'role': member.role}, status=201)

    def delete(self, request, user_id):
        try:
            institution = self.get_owned(request)
        except Institution.DoesNotExist:
            return Response({'error': 'No institution found.'}, status=404)
        deleted, _ = InstitutionMember.objects.filter(institution=institution, user_id=user_id).delete()
        return Response({'removed': bool(deleted)})
