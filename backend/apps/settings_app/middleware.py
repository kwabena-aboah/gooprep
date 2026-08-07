from django.http import JsonResponse
from .models import SiteSettings

class SiteSettingsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            site = SiteSettings.objects.first()
            if site and site.maintenance_mode and not request.path.startswith('/django-admin'):
                if request.path.startswith('/api/'):
                    return JsonResponse({'error': 'Platform under maintenance.', 'message': site.maintenance_message}, status=503)
        except Exception:
            pass
        return self.get_response(request)
