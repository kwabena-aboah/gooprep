from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import UserBadge, PointsHistory
from .serializers import UserBadgeSerializer, PointsHistorySerializer
from .services import record_daily_activity


class BadgeListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        badges = UserBadge.objects.filter(user=request.user).select_related('badge')
        return Response(UserBadgeSerializer(badges, many=True).data)


class PointsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        history = PointsHistory.objects.filter(user=request.user)[:50]
        return Response({
            'total': request.user.total_points,
            'level': request.user.level,
            'streak': request.user.streak_days,
            'history': PointsHistorySerializer(history, many=True).data,
        })


class DailyActivityView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user, awarded = record_daily_activity(request.user)
        return Response({
            'awarded': awarded,
            'total': user.total_points,
            'level': user.level,
            'streak': user.streak_days,
        })


class LeaderboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        role = request.query_params.get('role', 'student')
        users = User.objects.filter(
            role=role,
            is_active=True,
        ).order_by('-total_points', 'id')[:20]

        my_rank = None
        entries = []
        for rank, user in enumerate(users, 1):
            is_me = user.id == request.user.id
            if is_me:
                my_rank = rank
            entries.append({
                'rank': rank,
                'name': user.get_full_name() or user.email,
                'avatar': user.get_avatar_url(),
                'points': user.total_points,
                'level': user.level,
                'streak': user.streak_days,
                'is_me': is_me,
            })

        if my_rank is None:
            my_rank = User.objects.filter(
                role=role,
                is_active=True,
                total_points__gt=request.user.total_points,
            ).count() + 1

        return Response({'entries': entries, 'my_rank': my_rank})

