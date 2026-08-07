# Create webhook-only URL files
from django.urls import path
from .views import GuppyWebhookView
urlpatterns = [
    path('', GuppyWebhookView.as_view(), name='guppy_webhook_root'),
]