from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.request import Request
from .views import ExportReportView


def export_report(request):
    """Serve authenticated admin report downloads through the Django URL layer."""
    drf_request = Request(request, authenticators=[JWTAuthentication()])
    user = drf_request.user
    if not user or not user.is_authenticated:
        return JsonResponse({'detail': 'Authentication credentials were not provided.'}, status=401)
    if not user.is_staff:
        return JsonResponse({'detail': 'You do not have permission to perform this action.'}, status=403)
    return ExportReportView().get(drf_request)
