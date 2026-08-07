from django.contrib import admin
from .models import Institution, InstitutionMember

@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display  = ('name','owner','type','is_verified','created_at')
    list_filter   = ('type','is_verified')
    search_fields = ('name','owner__email')
    raw_id_fields = ('owner',)

@admin.register(InstitutionMember)
class InstitutionMemberAdmin(admin.ModelAdmin):
    list_display  = ('institution','user','role','added_at')
    raw_id_fields = ('institution','user')