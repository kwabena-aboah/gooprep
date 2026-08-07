from django.contrib import admin
from .models import GroupClass, GroupClassEnrollment

@admin.register(GroupClass)
class GroupClassAdmin(admin.ModelAdmin):
    list_display  = ('title','tutor','subject','level','max_students','price','is_active','start_time')
    list_filter   = ('level','is_active')
    search_fields = ('title','tutor__email')
    raw_id_fields = ('tutor','subject')

@admin.register(GroupClassEnrollment)
class GroupClassEnrollmentAdmin(admin.ModelAdmin):
    list_display  = ('group_class','student','enrolled_at')
    raw_id_fields = ('group_class','student')