from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (CustomTokenObtainPairView, RegisterView, MeView, LogoutView,
                    NotificationListView, mark_notifications_read, UserListView,
                    request_password_reset, confirm_password_reset, change_password, save_referral,
                    verify_email, resend_verification_email)
urlpatterns = [
    path('token/',                    CustomTokenObtainPairView.as_view(), name='token_obtain'),
    path('token/refresh/',            TokenRefreshView.as_view(),          name='token_refresh'),
    path('register/',                 RegisterView.as_view(),              name='register'),
    path('logout/',                   LogoutView.as_view(),                name='logout'),
    path('users/me/',                 MeView.as_view(),                   name='me'),
    path('users/',                    UserListView.as_view(),              name='user_list'),
    path('notifications/',            NotificationListView.as_view(),     name='notifications'),
    path('notifications/mark-read/',  mark_notifications_read,            name='mark_read'),
    path('password/reset/',           request_password_reset,             name='pw_reset'),
    path('password/reset/confirm/',   confirm_password_reset,             name='pw_reset_confirm'),
    path('password/change/',          change_password,                    name='pw_change'),
    path('referral/',                 save_referral,                      name='referral'),
    path('verify-email/',              verify_email,                   name='verify_email'),
    path('verify-email/resend/',       resend_verification_email,      name='resend_verification_email'),
]