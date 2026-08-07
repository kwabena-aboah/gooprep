from django.urls import path
from .views import paystack_webhook
urlpatterns = [
    path('', paystack_webhook, name='paystack_webhook_root'),
]