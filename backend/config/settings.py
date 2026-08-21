from pathlib import Path
from decouple import config, Csv
from datetime import timedelta
from urllib.parse import urlparse
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = config("SECRET_KEY", default="gooprep-dev-secret-2024-change-in-prod")
DEBUG = config("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="127.0.0.1", cast=Csv())
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
DATABASE_URL = config('DATABASE_URL', default='sqlite:///db.sqlite3')
_database_url = urlparse(DATABASE_URL)
if _database_url.scheme in {'postgres', 'postgresql'}:
    DATABASES = {'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': _database_url.path.lstrip('/'),
        'USER': _database_url.username or '',
        'PASSWORD': _database_url.password or '',
        'HOST': _database_url.hostname or 'localhost',
        'PORT': str(_database_url.port or 5432),
    }}
else:
    sqlite_name = _database_url.path.lstrip('/') or 'db.sqlite3'
    DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / sqlite_name}}
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'gooprep_new_db',      # Replace with your actual DB Name
#         'USER': 'gooprep_new_db_user',      # Replace with your actual DB User
#         'PASSWORD': '@g00prep26',   # Replace with your actual DB Password
#         'HOST': '127.0.0.1',              # Keep localhost for shared hosting
#         'PORT': '3306',                   # Default MySQL port
#     }
# }

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
# Set FORCE_SCRIPT_NAME only when the application is served from a subfolder.
FORCE_SCRIPT_NAME = config('FORCE_SCRIPT_NAME', default='') or None
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
STATIC_URL = "/static/"

# Static files remain local in development. Production can use S3 by setting
# AWS_STORAGE_BUCKET_NAME and running collectstatic after deployment.
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='')
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='')
AWS_S3_CUSTOM_DOMAIN = config('AWS_S3_CUSTOM_DOMAIN', default='')
AWS_S3_ENDPOINT_URL = config('AWS_S3_ENDPOINT_URL', default='') or None
AWS_LOCATION = config('AWS_LOCATION', default='static').strip('/')
AWS_MEDIA_LOCATION = config('AWS_MEDIA_LOCATION', default='media').strip('/')
AWS_QUERYSTRING_AUTH = config('AWS_QUERYSTRING_AUTH', default=False, cast=bool)
AWS_S3_FILE_OVERWRITE = True
AWS_DEFAULT_ACL = None
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=31536000, immutable'}

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

if not DEBUG and AWS_STORAGE_BUCKET_NAME:
    STORAGES = {
        'default': {
            'BACKEND': 'config.storage_backends.MediaStorage',
        },
        'staticfiles': {
            'BACKEND': 'config.storage_backends.StaticStorage',
        },
    }
    _aws_base_url = (
        f'https://{AWS_S3_CUSTOM_DOMAIN}'
        if AWS_S3_CUSTOM_DOMAIN
        else f'https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com'
    )
    STATIC_URL = f'{_aws_base_url}/{AWS_LOCATION}/'
    MEDIA_URL = f'{_aws_base_url}/{AWS_MEDIA_LOCATION}/'
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
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:5173,http://localhost:3000',
    cast=lambda value: [origin.strip().rstrip('/') for origin in value.split(',') if origin.strip()],
)
CORS_ALLOW_ALL_ORIGINS = config('CORS_ALLOW_ALL_ORIGINS', default=False, cast=bool)
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='http://localhost:5173,http://localhost:3000',
    cast=lambda value: [origin.strip().rstrip('/') for origin in value.split(',') if origin.strip()],
)
CORS_ALLOW_CREDENTIALS = True
CHANNEL_LAYERS = {"default":{"BACKEND":"channels.layers.InMemoryChannelLayer"}}
CELERY_BROKER_URL = config("CELERY_BROKER_URL", default="redis://localhost:6379/0")
EMAIL_BACKEND = config(
    'EMAIL_BACKEND',
    default='django.core.mail.backends.console.EmailBackend' if DEBUG else 'django.core.mail.backends.smtp.EmailBackend',
)
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@gooprep.com')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.sendgrid.net')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='apikey')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default=config('SENDGRID_API_KEY', default=''))
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
FRONTEND_URL = config("FRONTEND_URL", default="http://localhost:5173")
PAYSTACK_PUBLIC_KEY = config("PAYSTACK_PUBLIC_KEY", default="")
PAYSTACK_SECRET_KEY = config("PAYSTACK_SECRET_KEY", default="")
BBB_URL              = config("BBB_URL", default="")
# BBB_KEY is the shared secret used to sign BigBlueButton API requests.
# BBB_SECRET remains supported for existing deployments.
BBB_KEY              = config("BBB_KEY", default=config("BBB_SECRET", default=""))
BBB_SECRET           = BBB_KEY
GUPPY_ENABLED        = config("GUPPY_ENABLED", default=False, cast=bool)
GUPPY_API_URL        = config("GUPPY_API_URL", default="https://api.guppymessenger.com/v1")
GUPPY_APP_ID         = config("GUPPY_APP_ID", default="")
GUPPY_API_KEY        = config("GUPPY_API_KEY", default="")
GUPPY_WEBHOOK_SECRET = config("GUPPY_WEBHOOK_SECRET", default="")
OPENAI_API_KEY       = config("OPENAI_API_KEY", default="")
WHATSAPP_API_TOKEN   = config("WHATSAPP_API_TOKEN", default="")
WHATSAPP_PHONE_ID    = config("WHATSAPP_PHONE_ID", default="")
# Commission is a fraction of the gross lesson amount retained by the platform.
PLATFORM_COMMISSION = config(
    'PLATFORM_COMMISSION',
    default=config('PLATFORM_COMMISSION_RATE', default=0.20),
    cast=float,
)
MIN_PAYOUT = config(
    'MIN_PAYOUT',
    default=config('MIN_TUTOR_PAYOUT', default=50.0),
    cast=float,
)

if not DEBUG:
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=31536000, cast=int)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True