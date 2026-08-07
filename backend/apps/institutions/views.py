from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Institution, InstitutionMember

User = get_user_model()


class InstitutionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            inst = Institution.objects.get(owner=request.user)
            members = inst.members.select_related('user').all()
            return Response({
                'id':          inst.id,
                'name':        inst.name,
                'type':        inst.type,
                'description': inst.description,
                'website':     inst.website,
                'is_verified': inst.is_verified,
                'member_count': members.count(),
                'members': [
                    {'id':m.user.id,'name':m.user.get_full_name(),'email':m.user.email,'role':m.role}
                    for m in members[:50]
                ],
            })
        except Institution.DoesNotExist:
            return Response({'detail': 'No institution found.'}, status=404)

    def post(self, request):
        if Institution.objects.filter(owner=request.user).exists():
            return Response({'error': 'You already have an institution.'}, status=400)
        inst = Institution.objects.create(
            owner=request.user,
            name=request.data.get('name',''),
            type=request.data.get('type','school'),
            description=request.data.get('description',''),
            website=request.data.get('website',''),
        )
        request.user.role = 'institution'
        request.user.save(update_fields=['role'])
        return Response({'id': inst.id, 'name': inst.name}, status=201)

    def patch(self, request):
        try:
            inst = Institution.objects.get(owner=request.user)
            for f in ['name','type','description','website']:
                if f in request.data:
                    setattr(inst, f, request.data[f])
            inst.save()
            return Response({'saved': True})
        except Institution.DoesNotExist:
            return Response({'error': 'Not found.'}, status=404)


class InstitutionMemberView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Add a member to the institution by email."""
        try:
            inst = Institution.objects.get(owner=request.user)
        except Institution.DoesNotExist:
            return Response({'error': 'No institution found.'}, status=404)
        email = request.data.get('email','').lower()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': f'No user found with email {email}.'}, status=404)
        member, created = InstitutionMember.objects.get_or_create(
            institution=inst, user=user,
            defaults={'role': request.data.get('role','student')}
        )
        if not created:
            return Response({'error': 'User is already a member.'}, status=400)
        return Response({'added': True, 'name': user.get_full_name()}, status=201)

    def delete(self, request, user_id):
        try:
            inst = Institution.objects.get(owner=request.user)
            InstitutionMember.objects.filter(institution=inst, user_id=user_id).delete()
            return Response({'removed': True})
        except Institution.DoesNotExist:
            return Response({'error': 'Not found.'}, status=404)

