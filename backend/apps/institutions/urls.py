from django.urls import path
from .views import InstitutionView, InstitutionMemberView

urlpatterns = [
    path('',                            InstitutionView.as_view(),             name='institution'),
    path('members/',                    InstitutionMemberView.as_view(),        name='members'),
    path('members/<int:user_id>/',      InstitutionMemberView.as_view(),        name='remove_member'),
]