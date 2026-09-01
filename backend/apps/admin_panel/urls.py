from django.urls import path

from .views import (
    AdminStatsView, AdminUserListView, AdminReferralListView, toggle_user_active,
    AdminTutorListView, approve_tutor, StudentApprovalListView, approve_student,
    InstitutionApprovalListView, approve_institution, AdminRevenueView,
    AdminTransactionListView, AdminDisputeListView, resolve_dispute,
    AdminModerationListView, moderation_action, BBBStatusView, AdminBBBView,
    bbb_rooms, bbb_recordings, bbb_end_meeting, bbb_delete_recording,
)
from .export_routes import export_report

urlpatterns = [
    path('stats/', AdminStatsView.as_view(), name='admin_stats'),
    path('users/', AdminUserListView.as_view(), name='admin_users'),
    path('referrals/', AdminReferralListView.as_view(), name='admin_referrals'),
    path('users/<int:user_id>/toggle-active/', toggle_user_active, name='toggle_user'),
    path('tutors/', AdminTutorListView.as_view(), name='admin_tutors'),
    path('tutors/<int:tutor_id>/approve/', approve_tutor, name='approve_tutor'),
    path('students/', StudentApprovalListView.as_view(), name='admin_students'),
    path('students/<int:student_id>/approve/', approve_student, name='approve_student'),
    path('institutions/', InstitutionApprovalListView.as_view(), name='admin_institutions'),
    path('institutions/<int:institution_id>/approve/', approve_institution, name='approve_institution'),
    path('revenue/', AdminRevenueView.as_view(), name='admin_revenue'),
    path('transactions/', AdminTransactionListView.as_view(), name='admin_txns'),
    path('disputes/', AdminDisputeListView.as_view(), name='admin_disputes'),
    path('disputes/<int:dispute_id>/resolve/', resolve_dispute, name='resolve_dispute'),
    path('moderation/', AdminModerationListView.as_view(), name='admin_mod'),
    path('moderation/<int:item_id>/action/', moderation_action, name='mod_action'),
    path('bbb/', AdminBBBView.as_view(), name='admin-bbb'),
    path('bbb/status/', BBBStatusView.as_view(), name='bbb_status'),
    path('bbb/rooms/', bbb_rooms, name='bbb_rooms'),
    path('bbb/recordings/', bbb_recordings, name='bbb_recordings'),
    path('bbb/end-meeting/', bbb_end_meeting, name='bbb_end_meeting'),
    path('bbb/delete-recording/', bbb_delete_recording, name='bbb_delete_recording'),
    path('export/', export_report, name='export_report'),
]
