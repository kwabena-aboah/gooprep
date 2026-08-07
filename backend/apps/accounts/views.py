import uuid
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from .models import Notification, PasswordResetToken
from .serializers import RegisterSerializer, UserSerializer, NotificationSerializer, CustomTokenObtainPairSerializer

User = get_user_model()


class CustomTokenObtainPairView(APIView):
    """Email + password login — returns access, refresh, and user object."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ser = CustomTokenObtainPairSerializer(data=request.data, context={'request': request})
        ser.is_valid(raise_exception=True)
        return Response(ser.validated_data)


class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class   = RegisterSerializer

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'access':  str(refresh.access_token),
            'refresh': str(refresh),
            'user':    UserSerializer(user).data,
        }, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            token = RefreshToken(request.data.get('refresh'))
            token.blacklist()
        except Exception:
            pass
        return Response({'detail': 'Logged out.'})


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        ser = UserSerializer(request.user, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data)


class UserListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs    = User.objects.all()
        email = request.query_params.get('email')
        role  = request.query_params.get('role')
        if email: qs = qs.filter(email__iexact=email)
        if role:  qs = qs.filter(role=role)
        items = qs[:10]
        return Response({'count': items.count(), 'results': [
            {'id':u.id,'full_name':u.get_full_name(),'email':u.email,
             'role':u.role,'avatar_url':u.get_avatar_url()} for u in items
        ]})


class NotificationListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        notifs = Notification.objects.filter(user=request.user)[:50]
        return Response(NotificationSerializer(notifs, many=True).data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notifications_read(request):
    ids = request.data.get('ids')
    qs  = Notification.objects.filter(user=request.user)
    if ids: qs = qs.filter(id__in=ids)
    updated = qs.update(is_read=True)
    return Response({'marked': updated})


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def request_password_reset(request):
    email = request.data.get('email', '').lower().strip()
    user  = User.objects.filter(email=email).first()
    if user:
        tok = str(uuid.uuid4()).replace('-', '')
        PasswordResetToken.objects.create(user=user, token=tok)
        reset_url = f"{settings.FRONTEND_URL}/reset-password?email={email}&token={tok}"
        send_mail(
            'Reset your Gooprep password',
            f'Hi {user.first_name or "there"},\n\nReset your password here:\n{reset_url}\n\nExpires in 24 hours.',
            settings.DEFAULT_FROM_EMAIL, [email], fail_silently=True,
        )
    return Response({'detail': 'If that email is registered, a reset link has been sent.'})


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def confirm_password_reset(request):
    email = request.data.get('email', '').lower()
    tok   = request.data.get('token', '')
    pw1   = request.data.get('new_password1', '')
    pw2   = request.data.get('new_password2', '')
    if pw1 != pw2:
        return Response({'new_password2': ['Passwords do not match.']}, status=400)
    if len(pw1) < 8:
        return Response({'new_password1': ['Min 8 characters.']}, status=400)
    try:
        obj = PasswordResetToken.objects.get(token=tok, user__email=email)
        if not obj.is_valid():
            return Response({'detail': 'Token expired.'}, status=400)
        obj.user.set_password(pw1); obj.user.save()
        obj.used = True; obj.save()
        return Response({'detail': 'Password reset successfully.'})
    except PasswordResetToken.DoesNotExist:
        return Response({'detail': 'Invalid token.'}, status=400)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    user   = request.user
    old_pw = request.data.get('old_password', '')
    pw1    = request.data.get('new_password1', '')
    pw2    = request.data.get('new_password2', '')
    if not user.check_password(old_pw):
        return Response({'old_password': ['Current password is incorrect.']}, status=400)
    if pw1 != pw2:
        return Response({'new_password2': ['Passwords do not match.']}, status=400)
    if len(pw1) < 8:
        return Response({'new_password1': ['Min 8 characters.']}, status=400)
    user.set_password(pw1); user.save()
    return Response({'detail': 'Password changed successfully.'})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def save_referral(request):
    u = request.user
    u.was_referred   = request.data.get('was_referred', False)
    u.referrer_name  = request.data.get('referrer_name', '')
    u.referrer_notes = request.data.get('referrer_notes', '')
    u.save(update_fields=['was_referred', 'referrer_name', 'referrer_notes'])
    return Response({'saved': True})