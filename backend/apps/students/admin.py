from django.contrib import admin
from .models import StudentProfile

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display  = ('user','education_level','school','is_approved','needs_approval','created_at')
    list_filter   = ('is_approved','needs_approval')
    search_fields = ('user__email','user__first_name','user__last_name','school')
    raw_id_fields = ('user','approved_by')
    actions       = ['approve_selected','suspend_selected']

    @admin.action(description='Approve selected students')
    def approve_selected(self, request, queryset):
        queryset.update(is_approved=True)
        for sp in queryset:
            sp.user.is_active = True
            sp.user.save(update_fields=['is_active'])

    @admin.action(description='Suspend selected students')
    def suspend_selected(self, request, queryset):
        queryset.update(is_approved=False)
        for sp in queryset:
            sp.user.is_active = False
            sp.user.save(update_fields=['is_active'])