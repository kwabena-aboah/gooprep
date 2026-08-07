from django.urls import path
from .views import ConversationListView, MessageListView, GuppyWebhookView, guppy_status, sync_guppy_user
urlpatterns = [
    path('conversations/',                          ConversationListView.as_view(),      name='conversations'),
    path('conversations/<int:conv_id>/messages/',   MessageListView.as_view(),           name='messages'),
    path('guppy/webhook/',                          GuppyWebhookView.as_view(),          name='guppy_webhook'),
    path('guppy/status/',                           guppy_status,                        name='guppy_status'),
    path('guppy/sync-user/',                        sync_guppy_user,                     name='guppy_sync'),
]
