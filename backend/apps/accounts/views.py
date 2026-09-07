import logging
import uuid
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from .models import Notification, PasswordResetToken, EmailVerificationToken
from .serializers import RegisterSerializer, UserSerializer, NotificationSerializer, CustomTokenObtainPairSerializer

logger = logging.getLogger(__name__)

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
        # Account creation must not fail because SMTP is unavailable. The
        # token is still stored so the email can be resent after configuration.
        verification_sent = self._send_verification_email(user)
        return Response({
            'verification_sent': verification_sent,
            'email': user.email,
            'detail': (
                'Verification email sent. Please check your inbox before signing in.'
                if verification_sent else
                'Your account was created, but we could not send the verification email. '
                'Please contact support or request a new verification email.'
            ),
        }, status=201)


    @staticmethod
    def _send_verification_email(user):
        token = EmailVerificationToken.objects.create(user=user, token=uuid.uuid4().hex)
        frontend_url = settings.FRONTEND_URL or 'http://localhost:5173'
        verify_url = f'{frontend_url}/verify-email?token={token.token}'
        try:
            send_mail(
                'Verify your Gooprep email address',
                f'Welcome to Gooprep! Verify your email within 24 hours: {verify_url}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        except Exception:
            # Keep registration successful; the token remains available for a resend.
            import logging
            logging.getLogger(__name__).exception(
                'Verification email delivery failed for user %s', user.pk
            )
            return False
        return True


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


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def verify_email(request):
    token_value = request.query_params.get('token', '')
    token = EmailVerificationToken.objects.filter(token=token_value).select_related('user').first()
    if not token or not token.is_valid():
        return Response({'error': 'This verification link is invalid or expired.'}, status=400)
    token.used = True
    token.save(update_fields=['used'])
    token.user.email_verified = True
    token.user.save(update_fields=['email_verified'])
    return Response({'verified': True, 'detail': 'Email verified successfully.'})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def resend_verification_email(request):
    if request.user.email_verified:
        return Response({'detail': 'Email is already verified.'})
    EmailVerificationToken.objects.filter(user=request.user, used=False).update(used=True)
    token = EmailVerificationToken.objects.create(user=request.user, token=uuid.uuid4().hex)
    frontend_url = settings.FRONTEND_URL or 'http://localhost:5173'
    verify_url = f'{frontend_url}/verify-email?token={token.token}'
    try:
        send_mail('Verify your Gooprep email address', f'Verify your email within 24 hours: {verify_url}', settings.DEFAULT_FROM_EMAIL, [request.user.email], fail_silently=False)
    except Exception:
        import logging
        logging.getLogger(__name__).exception('Verification resend failed for user %s', request.user.pk)
        return Response({'sent': False, 'detail': 'Email delivery is temporarily unavailable.'}, status=503)
    return Response({'sent': True})


@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    email = str(request.data.get('email', '')).strip().lower()

    if not email:
        return Response(
            {'email': ['Email address is required.']},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = User.objects.filter(email__iexact=email).first()

    # Always return the same response whether the account exists or not.
    # This prevents user/account enumeration.
    if not user:
        return Response({
            'detail': 'If that email is registered, a reset link has been sent.'
        })

    # Invalidate previous unused tokens
    PasswordResetToken.objects.filter(
        user=user,
        used=False
    ).update(used=True)

    # Create a new token
    token = PasswordResetToken.objects.create(
        user=user,
        token=uuid.uuid4().hex
    )

    frontend_url = (
        settings.FRONTEND_URL or
        'http://localhost:5173'
    ).rstrip('/')

    reset_url = (
        f'{frontend_url}/reset-password'
        f'?email={email}&token={token.token}'
    )

    try:
        send_mail(
            subject='Reset your Gooprep password',
            message=(
                'You requested a password reset for your Gooprep account.\n\n'
                f'Reset your password here:\n{reset_url}\n\n'
                'If you did not request this password reset, you can safely '
                'ignore this email.'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

    except Exception:
        logger.exception(
            'Password reset email failed for user %s',
            user.pk
        )

        # Invalidate the token if email delivery failed
        token.used = True
        token.save(update_fields=['used'])

        return Response(
            {
                'detail': (
                    'We could not send the password reset email. '
                    'Please try again later.'
                )
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    return Response({
        'detail': 'If that email is registered, a reset link has been sent.'
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def confirm_password_reset(request):
    email = str(request.data.get('email', '')).strip().lower()
    token_value = str(request.data.get('token', '')).strip()
    password1 = str(request.data.get('new_password1', ''))
    password2 = str(request.data.get('new_password2', ''))

    # Validate required fields
    errors = {}

    if not email:
        errors['email'] = ['Email address is required.']

    if not token_value:
        errors['token'] = ['Reset token is required.']

    if not password1:
        errors['new_password1'] = ['New password is required.']

    if not password2:
        errors['new_password2'] = ['Password confirmation is required.']

    if errors:
        return Response(
            errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    # Confirm passwords match
    if password1 != password2:
        return Response(
            {
                'new_password2': [
                    'Passwords do not match.'
                ]
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Find reset token
    try:
        reset = (
            PasswordResetToken.objects
            .select_related('user')
            .get(
                token=token_value,
                user__email__iexact=email
            )
        )
    except PasswordResetToken.DoesNotExist:
        return Response(
            {
                'token': [
                    'Invalid password reset token.'
                ]
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check token validity
    if not reset.is_valid():
        return Response(
            {
                'token': [
                    'This password reset link has expired or has already been used.'
                ]
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Use Django's password validators
    try:
        validate_password(password1, user=reset.user)
    except ValidationError as exc:
        return Response(
            {
                'new_password1': list(exc.messages)
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Change password
    reset.user.set_password(password1)
    reset.user.save(update_fields=['password'])

    # Consume token
    reset.used = True
    reset.save(update_fields=['used'])

    return Response(
        {
            'detail': 'Password reset successfully.'
        },
        status=status.HTTP_200_OK
    )


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
