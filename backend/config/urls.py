from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),

    # Auth & Users
    path('api/auth/',         include('apps.accounts.urls')),

    # Core platform
    path('api/tutors/',       include('apps.tutors.urls')),
    path('api/students/',     include('apps.students.urls')),
    path('api/scheduling/',   include('apps.scheduling.urls')),
    path('api/payments/',     include('apps.payments.urls')),
    path('api/messaging/',    include('apps.messaging.urls')),
    path('api/reviews/',      include('apps.reviews.urls')),
    path('api/gamification/', include('apps.gamification.urls')),
    path('api/ai/',           include('apps.ai_features.urls')),
    path('api/courses/',      include('apps.courses.urls')),
    path('api/institutions/', include('apps.institutions.urls')),

    # Admin & Settings
    path('api/admin-panel/',  include('apps.admin_panel.urls')),
    path('api/settings/',     include('apps.settings_app.urls')),

    # External webhooks (dedicated paths, no sub-include conflict)
    path('webhooks/guppy/',      include('apps.messaging.webhook_urls')),
    path('webhooks/paystack/',   include('apps.payments.webhook_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,  document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)