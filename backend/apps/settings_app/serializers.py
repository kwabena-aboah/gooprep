from rest_framework import serializers
from .models import SiteSettings, StaticPage, FAQItem

class SiteSettingsSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    class Meta:
        model = SiteSettings
        fields = '__all__'

    def get_logo_url(self, obj):
        if obj.logo:
            try:
                return obj.logo.url
            except Exception:
                pass
        return '/static/img/gooprep_logo.png'

class StaticPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaticPage
        fields = ['id','page_type','title','content','meta_description','is_published','updated_at']

class FAQItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQItem
        fields = ['id','category','question','answer','target_audience','sort_order']
