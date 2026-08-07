from django.urls import path
from .views import ReviewListView, TutorReviewResponseView
urlpatterns = [
    path('',             ReviewListView.as_view(),        name='reviews'),
    path('<int:pk>/respond/', TutorReviewResponseView.as_view(), name='review_respond'),
]