from pathlib import Path
from decouple import config, Csv
from datetime import timedelta
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = config("SECRET_KEY", default="gooprep-dev-secret-2024-change-in-prod")
DEBUG = config("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="*", cast=Csv())
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "django_filters",
    "channels",
    "apps.accounts",
    "apps.tutors",
    "apps.students",
    "apps.scheduling",
    "apps.payments",
    "apps.messaging",
    "apps.reviews",
    "apps.gamification",
    "apps.ai_features",
    "apps.courses",
    "apps.admin_panel",
    "apps.settings_app",
    "apps.institutions",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"
TEMPLATES = [{"BACKEND":"django.template.backends.django.DjangoTemplates","DIRS":[BASE_DIR/"templates"],"APP_DIRS":True,"OPTIONS":{"context_processors":["django.template.context_processors.debug","django.template.context_processors.request","django.contrib.auth.context_processors.auth","django.contrib.messages.context_processors.messages"]}}]
DATABASES = {"default":{"ENGINE":"django.db.backends.sqlite3","NAME":BASE_DIR/"db.sqlite3"}}
AUTH_USER_MODEL = "accounts.User"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME":"django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME":"django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME":"django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME":"django.contrib.auth.password_validation.NumericPasswordValidator"},
]
AUTHENTICATION_BACKENDS = [
    'apps.accounts.backends.EmailOrUsernameBackend',
    'django.contrib.auth.backends.ModelBackend',
]
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Accra"
USE_I18N = True
USE_TZ = True
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/" 
MEDIA_ROOT = BASE_DIR / "media"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES":["rest_framework_simplejwt.authentication.JWTAuthentication"],
    "DEFAULT_PERMISSION_CLASSES":["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_FILTER_BACKENDS":["django_filters.rest_framework.DjangoFilterBackend","rest_framework.filters.SearchFilter","rest_framework.filters.OrderingFilter"],
    "DEFAULT_PAGINATION_CLASS":"rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE":20,
}
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME":timedelta(hours=2),
    "REFRESH_TOKEN_LIFETIME":timedelta(days=30),
    "ROTATE_REFRESH_TOKENS":True,
    "BLACKLIST_AFTER_ROTATION":True,
}
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='http://localhost:5173,http://localhost:3000', cast=lambda v:[s.strip() for s in v.split(',')])
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CHANNEL_LAYERS = {"default":{"BACKEND":"channels.layers.InMemoryChannelLayer"}}
CELERY_BROKER_URL = config("CELERY_BROKER_URL", default="redis://localhost:6379/0")
EMAIL_BACKEND = config("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@gooprep.com")
FRONTEND_URL = config("FRONTEND_URL", default="http://localhost:5173")
PAYSTACK_PUBLIC_KEY = config("PAYSTACK_PUBLIC_KEY", default="")
PAYSTACK_SECRET_KEY = config("PAYSTACK_SECRET_KEY", default="")
BBB_URL              = config("BBB_URL", default="")
BBB_SECRET           = config("BBB_SECRET", default="")
GUPPY_ENABLED        = config("GUPPY_ENABLED", default=False, cast=bool)
GUPPY_API_URL        = config("GUPPY_API_URL", default="https://api.guppymessenger.com/v1")
GUPPY_APP_ID         = config("GUPPY_APP_ID", default="")
GUPPY_API_KEY        = config("GUPPY_API_KEY", default="")
GUPPY_WEBHOOK_SECRET = config("GUPPY_WEBHOOK_SECRET", default="")
OPENAI_API_KEY       = config("OPENAI_API_KEY", default="")
WHATSAPP_API_TOKEN   = config("WHATSAPP_API_TOKEN", default="")
WHATSAPP_PHONE_ID    = config("WHATSAPP_PHONE_ID", default="")
PLATFORM_COMMISSION  = config("PLATFORM_COMMISSION", default=0.20, cast=float)
MIN_PAYOUT           = config("MIN_PAYOUT", default=50.0, cast=float)