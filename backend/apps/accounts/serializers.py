from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from .models import Notification

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    full_name  = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = [
            'id','email','first_name','last_name','full_name','role','phone','bio',
            'avatar','avatar_url','city','address','country','date_of_birth','gender','timezone','language',
            'total_points','level','streak_days','notify_email','notify_sms',
            'notify_push','notify_whatsapp','date_joined','last_login','is_active',
            'was_referred','referrer_name','referrer_notes','email_verified',
        ]
        read_only_fields = ['id','email','role','avatar_url','date_joined','last_login',
                            'total_points','level','streak_days']

    def get_full_name(self, obj):  return obj.get_full_name() or obj.email
    def get_avatar_url(self, obj): return obj.get_avatar_url()


class RegisterSerializer(serializers.ModelSerializer):
    password        = serializers.CharField(write_only=True, min_length=8)
    password2       = serializers.CharField(write_only=True)
    was_referred    = serializers.BooleanField(required=False, default=False)
    referrer_name   = serializers.CharField(required=False, allow_blank=True, max_length=200, default='')
    referrer_notes  = serializers.CharField(required=False, allow_blank=True, max_length=500, default='')
    institution_name = serializers.CharField(required=False, allow_blank=True, max_length=200)
    phone = serializers.CharField(required=True, allow_blank=False, max_length=30)

    class Meta:
        model  = User
        fields = ['email','first_name','last_name','phone','role','username',
                  'password','password2','was_referred','referrer_name','referrer_notes','institution_name']

    def validate_phone(self, value):
        normalized = (value or '').strip()
        if not normalized:
            raise serializers.ValidationError('Phone number is required.')
        return normalized

    def validate_email(self, v):
        if User.objects.filter(email=v.lower()).exists():
            raise serializers.ValidationError('An account with this email already exists.')
        return v.lower()

    def validate(self, data):
        if data.get('password') != data.pop('password2', ''):
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        if data.get('was_referred') and not data.get('referrer_name', '').strip():
            raise serializers.ValidationError({'referrer_name': "Please enter the referrer's name."})
        if data.get('role') == 'institution' and not data.get('institution_name', '').strip():
            raise serializers.ValidationError({'institution_name': 'Institution name is required.'})
        return data

    def create(self, validated_data):
        pw = validated_data.pop('password')
        institution_name = validated_data.pop('institution_name', '').strip()
        user = User(**validated_data)
        user.set_password(pw)
        user.save()

        if user.role == 'institution':
            from apps.institutions.models import Institution
            Institution.objects.create(owner=user, name=institution_name)
        elif user.role == 'student':
            from apps.students.models import StudentProfile
            StudentProfile.objects.get_or_create(
                user=user,
                defaults={'needs_approval': True, 'is_approved': False},
            )
        return user


class CustomTokenObtainPairSerializer(serializers.Serializer):
    """
    Email + password login — bypasses simplejwt's username requirement entirely.
    """
    email    = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        from rest_framework_simplejwt.tokens import RefreshToken
        email    = attrs['email'].lower().strip()
        password = attrs['password']
        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {'detail': 'No active account found with the given credentials'}
            )
        if not user_obj.is_active:
            raise serializers.ValidationError(
                {'detail': 'No active account found with the given credentials'}
            )
        user = authenticate(
            request=self.context.get('request'),
            username=user_obj.username,
            password=password,
        )
        if not user:
            raise serializers.ValidationError(
                {'detail': 'No active account found with the given credentials'}
            )
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access':  str(refresh.access_token),
            'user':    UserSerializer(user).data,
        }


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Notification
        fields = ['id','notification_type','title','message','is_read','link','created_at']