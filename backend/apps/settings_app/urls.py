from django.urls import path
from .views import SiteSettingsView, StaticPageView, BBBTestView, HealthView

urlpatterns = [
    path('',                     SiteSettingsView.as_view(), name='site_settings'),
    path('health/',              HealthView.as_view(),       name='health'),
    path('bbb/test/',            BBBTestView.as_view(),      name='bbb_test'),
    path('pages/<str:page_type>/', StaticPageView.as_view(), name='static_page'),
]