from django.urls import path
from .views import GroupClassListView, MyGroupClassesView, enroll_class, unenroll_class

urlpatterns = [
    path('group-classes/',                  GroupClassListView.as_view(),  name='group_classes'),
    path('group-classes/my/',               MyGroupClassesView.as_view(),  name='my_classes'),
    path('group-classes/<int:pk>/enroll/',  enroll_class,                  name='enroll'),
    path('group-classes/<int:pk>/unenroll/',unenroll_class,                name='unenroll'),
]