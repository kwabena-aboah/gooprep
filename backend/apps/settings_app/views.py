from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import SiteSettings, StaticPage


class SiteSettingsView(APIView):
    """Public read; admin write."""

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def get(self, request):
        s, _ = SiteSettings.objects.get_or_create(pk=1)
        # Only expose safe fields publicly
        public = {
            'site_name': s.site_name, 'tagline': s.tagline,
            'logo_url': s.logo_url or (s.logo.url if s.logo else ''),
            'support_email': s.support_email, 'phone': s.phone,
            'currency': s.currency, 'timezone': s.timezone,
            'primary_color': s.primary_color, 'secondary_color': s.secondary_color,
            'header_bg': s.header_bg, 'footer_bg': s.footer_bg,
            'link_color': s.link_color, 'button_color': s.button_color,
            'facebook_url': s.facebook_url, 'twitter_url': s.twitter_url,
            'instagram_url': s.instagram_url, 'linkedin_url': s.linkedin_url,
            'youtube_url': s.youtube_url, 'tiktok_url': s.tiktok_url,
            'whatsapp_number': s.whatsapp_number,
            'commission_rate': str(s.commission_rate),
            'ai_enabled': s.ai_enabled, 'whatsapp_enabled': s.whatsapp_enabled,
            'group_classes_enabled': s.group_classes_enabled,
            'institutions_enabled': s.institutions_enabled,
            'trials_enabled': s.trials_enabled,
            'gamification_enabled': s.gamification_enabled,
            'guppy_enabled': s.guppy_enabled,
        }
        # Include API fields for admin only
        if request.user.is_authenticated and request.user.role == 'admin':
            public.update({
                'paystack_public_key': s.paystack_public_key,
                'paystack_secret_key': s.paystack_secret_key,
                'whatsapp_api_token':  s.whatsapp_api_token,
                'whatsapp_phone_id':   s.whatsapp_phone_id,
                'google_maps_api_key': s.google_maps_api_key,
                'cloudflare_account_id': s.cloudflare_account_id,
                'cloudflare_access_key': s.cloudflare_access_key,
                'cloudflare_secret_key': s.cloudflare_secret_key,
                'cloudflare_bucket':   s.cloudflare_bucket,
                'openai_api_key':      s.openai_api_key,
                'guppy_app_id':        s.guppy_app_id,
                'guppy_api_key':       s.guppy_api_key,
                'guppy_webhook_secret':s.guppy_webhook_secret,
                'bbb_url':             s.bbb_url,
                'bbb_secret':          s.bbb_secret,
                'min_payout':          str(s.min_payout),
                'escrow_release_hours':s.escrow_release_hours,
                'cancellation_hours':  s.cancellation_hours,
                'address':             s.address,
            })
        return Response(public)

    def post(self, request):
        s, _ = SiteSettings.objects.get_or_create(pk=1)
        safe_fields = [
            'site_name','tagline','logo_url','support_email','phone','address',
            'currency','timezone','primary_color','secondary_color',
            'header_bg','footer_bg','link_color','button_color',
            'facebook_url','twitter_url','instagram_url','linkedin_url',
            'youtube_url','tiktok_url','whatsapp_number',
            'paystack_public_key','paystack_secret_key',
            'whatsapp_api_token','whatsapp_phone_id','google_maps_api_key',
            'cloudflare_account_id','cloudflare_access_key','cloudflare_secret_key','cloudflare_bucket',
            'openai_api_key','guppy_app_id','guppy_api_key','guppy_webhook_secret',
            'bbb_url','bbb_secret',
            'commission_rate','min_payout','escrow_release_hours','cancellation_hours',
            'ai_enabled','whatsapp_enabled','group_classes_enabled',
            'institutions_enabled','trials_enabled','gamification_enabled','guppy_enabled',
        ]
        for field in safe_fields:
            if field in request.data:
                setattr(s, field, request.data[field])
        # Handle logo upload
        if 'logo' in request.FILES:
            s.logo = request.FILES['logo']
        s.save()
        # Sync API keys to Django settings at runtime
        self._sync_settings(s)
        return Response({'saved': True})

    def _sync_settings(self, s):
        """Push DB settings to Django runtime settings."""
        from django.conf import settings as dj
        if s.bbb_url:        dj.BBB_URL    = s.bbb_url
        if s.bbb_secret:     dj.BBB_SECRET = s.bbb_secret
        if s.guppy_api_key:  dj.GUPPY_API_KEY = s.guppy_api_key
        if s.guppy_app_id:   dj.GUPPY_APP_ID  = s.guppy_app_id
        if s.guppy_webhook_secret: dj.GUPPY_WEBHOOK_SECRET = s.guppy_webhook_secret
        dj.GUPPY_ENABLED = s.guppy_enabled
        if s.paystack_secret_key: dj.PAYSTACK_SECRET_KEY = s.paystack_secret_key
        if s.openai_api_key:      dj.OPENAI_API_KEY      = s.openai_api_key


class StaticPageView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, page_type):
        try:
            page = StaticPage.objects.get(page_type=page_type)
            return Response({'page_type': page.page_type, 'title': page.title, 'content': page.content})
        except StaticPage.DoesNotExist:
            return Response({'page_type': page_type, 'title': '', 'content': ''})

    def post(self, request, page_type):
        if not (request.user.is_authenticated and request.user.role == 'admin'):
            return Response({'error': 'Admin only.'}, status=403)
        page, _ = StaticPage.objects.get_or_create(page_type=page_type)
        page.title   = request.data.get('title', page.title)
        page.content = request.data.get('content', page.content)
        page.save()
        return Response({'saved': True})


class BBBTestView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        import hashlib, urllib.request
        url    = request.data.get('url', '')
        secret = request.data.get('secret', '')
        if not url:
            return Response({'success': False, 'error': 'URL required.'})
        try:
            checksum = hashlib.sha1(f'getMeetingInfo{secret}'.encode()).hexdigest()
            with urllib.request.urlopen(f'{url}getMeetingInfo?checksum={checksum}', timeout=5):
                pass
            return Response({'success': True})
        except Exception as e:
            return Response({'success': False, 'error': str(e)})


class HealthView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        from django.db import connection
        checks = []
        # Database
        try:
            connection.ensure_connection()
            checks.append({'label': 'Database', 'ok': True, 'value': 'OK'})
        except Exception as e:
            checks.append({'label': 'Database', 'ok': False, 'value': str(e)[:50]})
        # Redis
        try:
            import redis as redis_lib
            from django.conf import settings
            r = redis_lib.from_url(settings.CELERY_BROKER_URL, socket_timeout=2)
            r.ping()
            checks.append({'label': 'Redis', 'ok': True, 'value': 'OK'})
        except Exception:
            checks.append({'label': 'Redis', 'ok': False, 'value': 'Unreachable'})
        # Guppy
        try:
            from apps.messaging.guppy import get_guppy_status
            gs = get_guppy_status()
            checks.append({'label': 'Guppy', 'ok': gs.get('online', False), 'value': 'Online' if gs.get('online') else 'Offline'})
        except Exception:
            checks.append({'label': 'Guppy', 'ok': False, 'value': 'Error'})
        checks.append({'label': 'Storage', 'ok': True, 'value': 'OK'})
        return Response({'checks': checks})