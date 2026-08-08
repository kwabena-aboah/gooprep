from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Review
from .serializers import ReviewSerializer

class ReviewListView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    def get(self, request):
        tutor_id = request.query_params.get('tutor_id')
        qs = Review.objects.filter(is_approved=True)
        if tutor_id: qs = qs.filter(tutor_id=tutor_id)
        page_size = int(request.query_params.get('page_size',20))
        page = int(request.query_params.get('page',1))
        total = qs.count()
        return Response({'count':total,'results':ReviewSerializer(qs[(page-1)*page_size:page*page_size],many=True).data})

    def post(self, request):
        from apps.scheduling.models import Lesson
        try: lesson = Lesson.objects.get(id=request.data.get('lesson'), student=request.user, status='completed')
        except: return Response({'error':'Lesson not found or not completed.'}, status=400)
        if Review.objects.filter(lesson=lesson).exists():
            return Response({'error':'Review already submitted.'}, status=400)
        r = Review.objects.create(
            lesson=lesson, tutor=lesson.tutor, reviewer=request.user,
            rating=request.data.get('rating',5), content=request.data.get('content',''),
            would_recommend=request.data.get('would_recommend',True),
            communication_rating=request.data.get('communication_rating'),
            expertise_rating=request.data.get('expertise_rating'),
            punctuality_rating=request.data.get('punctuality_rating'),
        )
        lesson.has_review = True; lesson.save(update_fields=['has_review'])
        # Update tutor average rating
        from django.db.models import Avg, Count
        from apps.tutors.models import TutorProfile
        try:
            tp = TutorProfile.objects.get(user=lesson.tutor)
            agg = Review.objects.filter(tutor=lesson.tutor, is_approved=True).aggregate(avg=Avg('rating'), cnt=Count('id'))
            tp.average_rating = round(agg['avg'] or 0, 2)
            tp.total_reviews  = agg['cnt']
            tp.save(update_fields=['average_rating','total_reviews'])
        except: pass
        try:
            from apps.messaging.guppy import get_or_create_guppy_user, send_push_notification
            gid = get_or_create_guppy_user(lesson.tutor)
            if gid: send_push_notification(gid,'⭐ New Review!',f'{request.user.get_full_name()} gave you {r.rating} stars.')
        except: pass
        return Response(ReviewSerializer(r).data, status=201)

class TutorReviewResponseView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, pk):
        try:
            r = Review.objects.get(pk=pk, tutor=request.user)
            r.tutor_response = request.data.get('response','')
            r.save(update_fields=['tutor_response'])
            return Response({'saved':True})
        except Review.DoesNotExist:
            return Response({'error':'Review not found.'}, status=404)