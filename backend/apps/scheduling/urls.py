# from django.urls import path

# from .views import (
#     LessonListView,
#     LessonDetailView,
#     join_lesson,
#     end_lesson,
#     reschedule_lesson,
#     lesson_recordings,
# )


# urlpatterns = [

#     # ---------------------------------------------------------
#     # LESSONS
#     # ---------------------------------------------------------

#     path(
#         'lessons/',
#         LessonListView.as_view(),
#         name='lesson_list'
#     ),

#     path(
#         'lessons/<int:pk>/',
#         LessonDetailView.as_view(),
#         name='lesson_detail'
#     ),

#     path(
#         'lessons/<int:pk>/join/',
#         join_lesson,
#         name='lesson_join'
#     ),

#     path(
#         'lessons/<int:pk>/end/',
#         end_lesson,
#         name='lesson_end'
#     ),

#     path(
#         'lessons/<int:pk>/reschedule/',
#         reschedule_lesson,
#         name='lesson_reschedule'
#     ),

#     path(
#         'lessons/<int:pk>/recordings/',
#         lesson_recordings,
#         name='lesson_recordings'
#     ),

# ]

from django.urls import path

from .views import (
    BBBHealthView,
    BBBStatusView,
    EndBBBView,
    JoinBBBView,
    LessonDetailView,
    LessonListCreateView,
    LessonRecordingsView,
    ProvisionBBBView,
)
from .views_bbb import bbb_webhook


app_name = "scheduling"


urlpatterns = [
    # ==============================================================
    # LESSONS
    # ==============================================================

    path(
        "lessons/",
        LessonListCreateView.as_view(),
        name="lesson-list-create",
    ),

    path(
        "lessons/<int:pk>/",
        LessonDetailView.as_view(),
        name="lesson-detail",
    ),

    # ==============================================================
    # BIGBLUEBUTTON
    # ==============================================================

    path(
        "lessons/<int:pk>/bbb/provision/",
        ProvisionBBBView.as_view(),
        name="bbb-provision",
    ),

    path(
        "lessons/<int:pk>/bbb/join/",
        JoinBBBView.as_view(),
        name="bbb-join",
    ),

    path(
        "lessons/<int:pk>/bbb/status/",
        BBBStatusView.as_view(),
        name="bbb-status",
    ),

    path(
        "lessons/<int:pk>/bbb/end/",
        EndBBBView.as_view(),
        name="bbb-end",
    ),

    path(
        "lessons/<int:pk>/bbb/recordings/",
        LessonRecordingsView.as_view(),
        name="bbb-recordings",
    ),

    # ==============================================================
    # BIGBLUEBUTTON WEBHOOK
    # ==============================================================

    path(
        "bbb/webhook/",
        bbb_webhook,
        name="bbb-webhook",
    ),

    # ==============================================================
    # BIGBLUEBUTTON ADMIN / HEALTH
    # ==============================================================

    path(
        "bbb/health/",
        BBBHealthView.as_view(),
        name="bbb-health",
    ),
]