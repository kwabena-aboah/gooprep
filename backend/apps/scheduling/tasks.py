import logging
from django.utils import timezone
from datetime import timedelta
logger = logging.getLogger(__name__)

def generate_ai_summary_sync(lesson_id):
    """Synchronous version — called directly when Celery not available."""
    try:
        from .models import Lesson
        from django.conf import settings
        lesson = Lesson.objects.get(pk=lesson_id)
        api_key = settings.OPENAI_API_KEY
        if not api_key: return
        import openai
        client = openai.OpenAI(api_key=api_key)
        subject = lesson.subject.name if lesson.subject else 'General'
        topic   = lesson.topic or subject
        resp = client.chat.completions.create(model='gpt-3.5-turbo',messages=[{'role':'user','content':f'Write a concise 3-sentence study summary for a {subject} lesson on: {topic}.'}],max_tokens=200)
        lesson.ai_summary = resp.choices[0].message.content
        fc = client.chat.completions.create(model='gpt-3.5-turbo',messages=[{'role':'user','content':f'Generate 5 flashcards for {subject}: {topic}. Return only a JSON array with "q" and "a" keys.'}],max_tokens=400)
        import json
        try: lesson.ai_flashcards = json.loads(fc.choices[0].message.content)
        except: lesson.ai_flashcards = []
        lesson.save(update_fields=['ai_summary','ai_flashcards'])
    except Exception as e:
        logger.warning(f'AI summary failed for lesson {lesson_id}: {e}')

try:
    from config.celery import app as celery_app
    @celery_app.task(bind=True, max_retries=3)
    def generate_ai_summary(self, lesson_id):
        generate_ai_summary_sync(lesson_id)

    @celery_app.task
    def send_lesson_reminders():
        from .models import Lesson
        window_start = timezone.now() + timedelta(minutes=25)
        window_end   = timezone.now() + timedelta(minutes=35)
        lessons = Lesson.objects.filter(start_time__gte=window_start,start_time__lte=window_end,status='confirmed').select_related('tutor','student','subject')
        for l in lessons:
            try:
                from apps.messaging.guppy import notify_lesson_reminder
                notify_lesson_reminder(l)
            except Exception: pass

    @celery_app.task
    def check_no_shows():
        from .models import Lesson
        cutoff = timezone.now() - timedelta(hours=1)
        Lesson.objects.filter(status='confirmed',start_time__lt=cutoff).update(status='no_show')
except ImportError:
    def generate_ai_summary(lesson_id):
        generate_ai_summary_sync(lesson_id)