from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display  = ('id','tutor','reviewer','rating','is_approved','created_at')
    list_filter   = ('is_approved','rating')
    search_fields = ('tutor__email','reviewer__email','content')
    raw_id_fields = ('tutor','reviewer','lesson')
    actions       = ['approve_reviews','reject_reviews']

    @admin.action(description='Approve selected reviews')
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)

    @admin.action(description='Reject selected reviews')
    def reject_reviews(self, request, queryset):
        queryset.update(is_approved=False)