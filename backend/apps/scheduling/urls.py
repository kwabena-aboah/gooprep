from django.urls import path

from .views import (
    LessonListView,
    LessonDetailView,
    join_lesson,
    end_lesson,
    reschedule_lesson,
    lesson_recordings,
)


urlpatterns = [

    # ---------------------------------------------------------
    # LESSONS
    # ---------------------------------------------------------

    path(
        'lessons/',
        LessonListView.as_view(),
        name='lesson_list'
    ),

    path(
        'lessons/<int:pk>/',
        LessonDetailView.as_view(),
        name='lesson_detail'
    ),

    path(
        'lessons/<int:pk>/join/',
        join_lesson,
        name='lesson_join'
    ),

    path(
        'lessons/<int:pk>/end/',
        end_lesson,
        name='lesson_end'
    ),

    path(
        'lessons/<int:pk>/reschedule/',
        reschedule_lesson,
        name='lesson_reschedule'
    ),

    path(
        'lessons/<int:pk>/recordings/',
        lesson_recordings,
        name='lesson_recordings'
    ),

]