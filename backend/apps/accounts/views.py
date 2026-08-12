import uuid
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from .models import Notification, PasswordResetToken
from .serializers import RegisterSerializer, UserSerializer, NotificationSerializer, CustomTokenObtainPairSerializer

User = get_user_model()


class CustomTokenObtainPairView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = CustomTokenObtainPairSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.validated_data)


class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({'access': str(refresh.access_token), 'refresh': str(refresh), 'user': UserSerializer(user).data}, status=201)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            RefreshToken(request.data.get('refresh')).blacklist()
        except Exception:
            pass
        return Response({'detail': 'Logged out.'})


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UserListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = User.objects.all()
        if request.query_params.get('email'):
            queryset = queryset.filter(email__iexact=request.query_params['email'])
        if request.query_params.get('role'):
            queryset = queryset.filter(role=request.query_params['role'])
        items = queryset[:10]
        return Response({'count': items.count(), 'results': [
            {'id': user.id, 'full_name': user.get_full_name(), 'email': user.email,
             'role': user.role, 'avatar_url': user.get_avatar_url()}
            for user in items
        ]})


class NotificationListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user)[:50]
        return Response(NotificationSerializer(notifications, many=True).data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notifications_read(request):
    queryset = Notification.objects.filter(user=request.user)
    if request.data.get('ids'):
        queryset = queryset.filter(id__in=request.data['ids'])
    return Response({'marked': queryset.update(is_read=True)})


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def request_password_reset(request):
    email = request.data.get('email', '').lower().strip()
    user = User.objects.filter(email=email).first()
    if user:
        token = PasswordResetToken.objects.create(user=user, token=uuid.uuid4().hex)
        reset_url = f'{settings.FRONTEND_URL}/reset-password?email={email}&token={token.token}'
        send_mail('Reset your Gooprep password', f'Reset your password here: {reset_url}', settings.DEFAULT_FROM_EMAIL, [email], fail_silently=True)
    return Response({'detail': 'If that email is registered, a reset link has been sent.'})


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def confirm_password_reset(request):
    email = request.data.get('email', '').lower()
    token = request.data.get('token', '')
    password1 = request.data.get('new_password1', '')
    password2 = request.data.get('new_password2', '')
    if password1 != password2:
        return Response({'new_password2': ['Passwords do not match.']}, status=400)
    if len(password1) < 8:
        return Response({'new_password1': ['Min 8 characters.']}, status=400)
    try:
        reset = PasswordResetToken.objects.get(token=token, user__email=email)
        if not reset.is_valid():
            return Response({'detail': 'Token expired.'}, status=400)
        reset.user.set_password(password1); reset.user.save()
        reset.used = True; reset.save(update_fields=['used'])
        return Response({'detail': 'Password reset successfully.'})
    except PasswordResetToken.DoesNotExist:
        return Response({'detail': 'Invalid token.'}, status=400)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    user = request.user
    if not user.check_password(request.data.get('old_password', '')):
        return Response({'old_password': ['Current password is incorrect.']}, status=400)
    password1 = request.data.get('new_password1', '')
    if password1 != request.data.get('new_password2', ''):
        return Response({'new_password2': ['Passwords do not match.']}, status=400)
    if len(password1) < 8:
        return Response({'new_password1': ['Min 8 characters.']}, status=400)
    user.set_password(password1); user.save()
    return Response({'detail': 'Password changed successfully.'})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def save_referral(request):
    user = request.user
    user.was_referred = request.data.get('was_referred', False)
    user.referrer_name = request.data.get('referrer_name', '')
    user.referrer_notes = request.data.get('referrer_notes', '')
    user.save(update_fields=['was_referred', 'referrer_name', 'referrer_notes'])
    return Response({'saved': True})
