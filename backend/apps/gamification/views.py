from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import UserBadge, PointsHistory
from .serializers import UserBadgeSerializer, PointsHistorySerializer

class BadgeListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        badges = UserBadge.objects.filter(user=request.user).select_related('badge')
        return Response(UserBadgeSerializer(badges, many=True).data)

class PointsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        history = PointsHistory.objects.filter(user=request.user)[:50]
        return Response({'total':request.user.total_points,'level':request.user.level,
                         'streak':request.user.streak_days,'history':PointsHistorySerializer(history,many=True).data})

class LeaderboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        role = request.query_params.get('role','student')
        users = User.objects.filter(role=role, is_active=True).order_by('-total_points')[:20]
        my_rank = None
        entries = []
        for i, u in enumerate(users, 1):
            is_me = u.id == request.user.id
            if is_me: my_rank = i
            entries.append({'rank':i,'name':u.get_full_name(),'avatar':u.get_avatar_url(),
                            'points':u.total_points,'level':u.level,'streak':u.streak_days,'is_me':is_me})
        if my_rank is None:
            above = User.objects.filter(role=role,is_active=True,total_points__gt=request.user.total_points).count()
            my_rank = above + 1
        return Response({'entries':entries,'my_rank':my_rank})

def award_points(user, points: int, action: str, description: str = ''):
    """Award points to a user and check for level up."""
    user.total_points += points
    # Level up every 500 points
    user.level = max(1, user.total_points // 500 + 1)
    user.save(update_fields=['total_points','level'])
    PointsHistory.objects.create(user=user, points=points, action=action, description=description)
    # Check badges
    _check_badges(user)

def _check_badges(user):
    from .models import Badge, UserBadge
    for badge in Badge.objects.all():
        if user.total_points >= badge.points_required:
            UserBadge.objects.get_or_create(user=user, badge=badge)
