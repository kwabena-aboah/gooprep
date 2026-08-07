from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailOrUsernameBackend(ModelBackend):
    """
    Authenticate by email or username.
    Works regardless of USERNAME_FIELD setting.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        user = None
        if username:
            # Try email first
            if '@' in str(username):
                user = User.objects.filter(email__iexact=username).first()
            if user is None:
                user = User.objects.filter(username=username).first()
        if user is None:
            # Try kwargs email directly
            email = kwargs.get('email')
            if email:
                user = User.objects.filter(email__iexact=email).first()
        if user is not None and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None