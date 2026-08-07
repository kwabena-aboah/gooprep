from django.urls import path
from .views import (SubjectListView, TutorListView, TutorDetailView, TutorSlugView,
                    MyTutorProfileView, TutorAvailabilityView, MyStudentsView,
                    FavouritesView, toggle_favourite, tutor_onboarding)
urlpatterns = [
    path('',                      TutorListView.as_view(),       name='tutor_list'),
    path('subjects/',             SubjectListView.as_view(),     name='subjects'),
    path('my-profile/',           MyTutorProfileView.as_view(),  name='my_profile'),
    path('my-students/',          MyStudentsView.as_view(),      name='my_students'),
    path('favourites/',           FavouritesView.as_view(),      name='favourites'),
    path('onboarding/',           tutor_onboarding,              name='onboarding'),
    path('<int:pk>/',             TutorDetailView.as_view(),     name='tutor_detail'),
    path('<int:pk>/favourite/',   toggle_favourite,              name='toggle_fav'),
    path('<int:pk>/availability/',TutorAvailabilityView.as_view(),name='tutor_avail'),
    path('slug/<slug:slug>/',     TutorSlugView.as_view(),       name='tutor_slug'),
    path('my-availability/',      TutorAvailabilityView.as_view(),name='my_avail'),
]