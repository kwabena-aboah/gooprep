from django.contrib import admin
from .models import Lesson

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display   = ('id','tutor','student','subject','status','start_time','price','payment_status','booked_on_behalf')
    list_filter    = ('status','lesson_type','payment_status','booked_on_behalf')
    search_fields  = ('tutor__email','student__email','topic','booker_name')
    raw_id_fields  = ('tutor','student','subject')
    ordering       = ('-start_time',)
    date_hierarchy = 'start_time'
    readonly_fields = ('ai_summary','ai_flashcards','ai_quiz','bbb_meeting_id','bbb_join_url')
    fieldsets = (
        ('Core', {'fields': ('tutor','student','subject','lesson_type','status','start_time','end_time','duration_minutes','topic')}),
        ('Pricing', {'fields': ('price','currency','payment_status')}),
        ('Virtual Classroom', {'fields': ('bbb_meeting_id','bbb_join_url','record_session','recording_available','recording_url')}),
        ('AI Output', {'fields': ('ai_summary','ai_flashcards','ai_quiz')}),
        ('Book on Behalf', {'fields': ('booked_on_behalf','booker_name','booker_relationship','booker_phone','booker_email')}),
        ('Other', {'fields': ('notes','has_review')}),
    )