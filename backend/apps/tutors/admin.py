from django.contrib import admin
from .models import TutorProfile, Subject, TutorFavourite, TutorDocument

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name','slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(TutorProfile)
class TutorProfileAdmin(admin.ModelAdmin):
    list_display  = ('user','headline','hourly_rate','average_rating','approval_status','is_featured','total_lessons')
    list_filter   = ('approval_status','is_featured','is_top_rated')
    search_fields = ('user__email','user__first_name','user__last_name','headline')
    raw_id_fields = ('user',)
    filter_horizontal = ('subjects',)
    actions       = ['approve_selected','reject_selected','feature_selected']

    @admin.action(description='Approve selected tutors')
    def approve_selected(self, request, queryset):
        queryset.update(approval_status='approved')
        for tp in queryset:
            try:
                from messaging.guppy import notify_tutor_approved
                notify_tutor_approved(tp.user, True)
            except Exception: pass

    @admin.action(description='Reject selected tutors')
    def reject_selected(self, request, queryset):
        queryset.update(approval_status='rejected')

    @admin.action(description='Mark as featured')
    def feature_selected(self, request, queryset):
        queryset.update(is_featured=True)

@admin.register(TutorFavourite)
class TutorFavouriteAdmin(admin.ModelAdmin):
    list_display  = ('student','tutor','created_at')
    raw_id_fields = ('student','tutor')

@admin.register(TutorDocument)
class TutorDocumentAdmin(admin.ModelAdmin):
    list_display  = ('tutor','doc_type','is_verified','uploaded_at')
    list_filter   = ('doc_type','is_verified')
    raw_id_fields = ('tutor',)