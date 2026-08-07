"""Guppy Messenger integration service."""
import hashlib, hmac, logging
from typing import Optional
import httpx
from django.conf import settings

logger = logging.getLogger(__name__)

def _enabled(): return bool(settings.GUPPY_ENABLED and settings.GUPPY_API_KEY and settings.GUPPY_APP_ID)
def _headers(): return {'Authorization':f'Bearer {settings.GUPPY_API_KEY}','X-App-ID':settings.GUPPY_APP_ID,'Content-Type':'application/json'}
BASE = lambda: settings.GUPPY_API_URL

def register_user(user) -> Optional[str]:
    if not _enabled(): return None
    try:
        with httpx.Client(timeout=10) as c:
            r = c.post(f'{BASE()}/users', headers=_headers(), json={
                'external_id':str(user.id),'name':user.get_full_name() or user.email,
                'email':user.email,'phone':user.phone or '',
                'avatar_url':user.get_avatar_url(),'metadata':{'role':user.role},
            })
            r.raise_for_status()
            gid = r.json().get('id')
            if gid: type(user).objects.filter(pk=user.pk).update(guppy_user_id=gid)
            return gid
    except Exception as e:
        logger.warning(f'[Guppy] register_user failed for {user.email}: {e}')
        return None

def get_or_create_guppy_user(user) -> Optional[str]:
    if not _enabled(): return None
    return user.guppy_user_id or register_user(user)

def create_conversation(participant_ids: list, metadata: dict = None) -> Optional[dict]:
    if not _enabled(): return None
    try:
        with httpx.Client(timeout=10) as c:
            r = c.post(f'{BASE()}/conversations', headers=_headers(), json={'participant_ids':participant_ids,'metadata':metadata or {}})
            r.raise_for_status(); return r.json()
    except Exception as e: logger.warning(f'[Guppy] create_conversation: {e}'); return None

def send_message(guppy_conv_id: str, sender_guppy_id: str, content: str) -> Optional[dict]:
    if not _enabled(): return None
    try:
        with httpx.Client(timeout=10) as c:
            r = c.post(f'{BASE()}/conversations/{guppy_conv_id}/messages', headers=_headers(),
                       json={'sender_id':sender_guppy_id,'type':'text','content':content})
            r.raise_for_status(); return r.json()
    except Exception as e: logger.warning(f'[Guppy] send_message: {e}'); return None

def send_system_message(guppy_conv_id: str, content: str) -> Optional[dict]:
    if not _enabled(): return None
    try:
        with httpx.Client(timeout=10) as c:
            r = c.post(f'{BASE()}/conversations/{guppy_conv_id}/system-messages', headers=_headers(), json={'content':content})
            r.raise_for_status(); return r.json()
    except Exception as e: logger.warning(f'[Guppy] send_system_message: {e}'); return None

def send_push_notification(guppy_user_id: str, title: str, body: str, data: dict = None) -> Optional[dict]:
    if not _enabled(): return None
    try:
        with httpx.Client(timeout=10) as c:
            r = c.post(f'{BASE()}/notifications/push', headers=_headers(),
                       json={'user_id':guppy_user_id,'title':title,'body':body,'data':data or {}})
            r.raise_for_status(); return r.json()
    except Exception as e: logger.warning(f'[Guppy] push: {e}'); return None

def broadcast_notification(user_ids: list, title: str, body: str) -> Optional[dict]:
    if not _enabled(): return None
    try:
        with httpx.Client(timeout=10) as c:
            r = c.post(f'{BASE()}/notifications/broadcast', headers=_headers(), json={'user_ids':user_ids,'title':title,'body':body})
            r.raise_for_status(); return r.json()
    except Exception as e: logger.warning(f'[Guppy] broadcast: {e}'); return None

def verify_webhook(payload: bytes, signature: str) -> bool:
    secret = settings.GUPPY_WEBHOOK_SECRET
    if not secret: return True
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(f'sha256={expected}', signature)

def get_guppy_status() -> dict:
    if not _enabled(): return {'enabled':False,'online':False}
    try:
        with httpx.Client(timeout=5) as c:
            r = c.get(f'{BASE()}/health', headers=_headers())
            return {'enabled':True,'online':r.status_code<400,'status':r.status_code,'app_id':settings.GUPPY_APP_ID[:8]+'...'}
    except Exception as e:
        return {'enabled':True,'online':False,'error':str(e)}

# ── Platform helpers ──────────────────────────────────────────
def notify_lesson_booked(lesson):
    if not _enabled(): return
    try:
        tutor_gid   = get_or_create_guppy_user(lesson.tutor)
        student_gid = get_or_create_guppy_user(lesson.student)
        if tutor_gid and student_gid:
            conv = create_conversation([tutor_gid, student_gid], {'lesson_id':lesson.id,'type':'lesson_chat'})
            if conv: send_system_message(conv['id'], f'📚 Lesson booked: {lesson.subject_name} on {lesson.start_time.strftime("%d %b %Y %H:%M")} · GHS {lesson.price}')
        if student_gid: send_push_notification(student_gid,'Lesson Booked! 🎉',f'Your {lesson.subject_name} lesson with {lesson.tutor_name} is confirmed.')
        if tutor_gid:   send_push_notification(tutor_gid,'New Booking 📅',f'{lesson.student_name} booked a {lesson.subject_name} lesson.')
    except Exception as e: logger.warning(f'[Guppy] notify_lesson_booked: {e}')

def notify_lesson_reminder(lesson):
    if not _enabled(): return
    try:
        student_gid = get_or_create_guppy_user(lesson.student)
        tutor_gid   = get_or_create_guppy_user(lesson.tutor)
        if student_gid: send_push_notification(student_gid,'⏰ Lesson in 30 min!',f'Your {lesson.subject_name} with {lesson.tutor_name} starts soon.')
        if tutor_gid:   send_push_notification(tutor_gid,'⏰ Lesson in 30 min!',f'Your lesson with {lesson.student_name} starts soon.')
    except Exception as e: logger.warning(f'[Guppy] notify_lesson_reminder: {e}')

def notify_payment_received(transaction):
    if not _enabled(): return
    try:
        if transaction.lesson:
            gid = get_or_create_guppy_user(transaction.lesson.tutor)
            if gid:
                net = float(transaction.amount) * 0.85
                send_push_notification(gid,'💰 Payment Received!',f'GHS {net:.2f} earned from {transaction.payer_name}.')
    except Exception as e: logger.warning(f'[Guppy] notify_payment_received: {e}')

def notify_admin_new_tutor(user):
    if not _enabled(): return
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        for admin in User.objects.filter(role='admin', is_active=True)[:3]:
            gid = get_or_create_guppy_user(admin)
            if gid: send_push_notification(gid,'New Tutor Application',f'{user.get_full_name()} submitted a tutor application. Review it in admin.')
    except Exception as e: logger.warning(f'[Guppy] notify_admin_new_tutor: {e}')

def notify_tutor_approved(tutor_user, approved: bool):
    if not _enabled(): return
    try:
        gid = get_or_create_guppy_user(tutor_user)
        if gid:
            if approved: send_push_notification(gid,'🎉 Application Approved!','Your Gooprep tutor application has been approved. Start teaching today!')
            else:        send_push_notification(gid,'Application Update','Your tutor application status has been updated. Check your email for details.')
    except Exception as e: logger.warning(f'[Guppy] notify_tutor_approved: {e}')

def notify_student_approved(student_user, approved: bool):
    if not _enabled(): return
    try:
        gid = get_or_create_guppy_user(student_user)
        if gid:
            if approved: send_push_notification(gid,'✅ Account Approved!','Welcome to Gooprep! You can now book lessons.')
            else:        send_push_notification(gid,'⚠️ Account Suspended','Your account has been suspended. Contact support for assistance.')
    except Exception as e: logger.warning(f'[Guppy] notify_student_approved: {e}')
