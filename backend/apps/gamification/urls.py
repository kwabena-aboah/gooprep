from django.urls import path

from .views import BadgeListView, PointsView, DailyActivityView, LeaderboardView


urlpatterns = [
    path('badges/', BadgeListView.as_view(), name='badges'),
    path('points/', PointsView.as_view(), name='points'),
    path('activity/', DailyActivityView.as_view(), name='daily_activity'),
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
]
