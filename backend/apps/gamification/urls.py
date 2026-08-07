from django.urls import path
from .views import BadgeListView, PointsView, LeaderboardView
urlpatterns = [
    path('badges/',       BadgeListView.as_view(),  name='badges'),
    path('points/',       PointsView.as_view(),     name='points'),
    path('leaderboard/',  LeaderboardView.as_view(), name='leaderboard'),
]