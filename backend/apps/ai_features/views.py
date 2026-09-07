from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import AIConversation, StudentProgress
import logging
logger = logging.getLogger(__name__)

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def ai_chat(request):
    conv = AIConversation.objects.filter(user=request.user).first()
    if request.method == 'GET':
        return Response({'messages': conv.messages if conv else []})

    message = str(request.data.get('message', '')).strip()
    if not message:
        return Response({'error': 'Message required.'}, status=400)

    from django.conf import settings
    api_key = str(getattr(settings, 'OPENAI_API_KEY', '') or '').strip()
    if not api_key:
        return Response({'error': 'AI assistant is not configured.'}, status=503)

    conv, _ = AIConversation.objects.get_or_create(user=request.user)
    history = [
        item for item in (conv.messages or [])[-10:]
        if isinstance(item, dict) and item.get('role') in {'user', 'assistant'}
    ]
    history.append({'role': 'user', 'content': message})
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=getattr(settings, 'OPENAI_MODEL', 'gpt-4o-mini'),
            messages=[
                {'role': 'system', 'content': (
                    "You are a helpful study assistant for Gooprep, Ghana's tutoring "
                    "platform. Help with homework, exam preparation, and learning "
                    "questions. Be concise, educational, and use Ghana context when relevant."
                )},
                *history,
            ],
            max_tokens=600,
        )
        ai_reply = (response.choices[0].message.content or '').strip()
        if not ai_reply:
            raise RuntimeError('OpenAI returned an empty response.')
    except Exception:
        logger.exception('AI chat request failed for user %s', request.user.pk)
        return Response({'error': 'The AI assistant is temporarily unavailable.'}, status=503)

    history.append({'role': 'assistant', 'content': ai_reply})
    conv.messages = history[-20:]
    conv.save(update_fields=['messages', 'updated_at'])
    return Response({'response': ai_reply, 'messages': conv.messages})

@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def clear_ai_chat(request):
    AIConversation.objects.filter(user=request.user).update(messages=[])
    return Response({'cleared':True})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def student_progress(request):
    from apps.scheduling.models import Lesson
    from django.db.models import Count

    completed = Lesson.objects.filter(
        student=request.user,
        status='completed',
        subject__isnull=False,
    ).values('subject_id', 'subject__name').annotate(lessons_completed=Count('id'))
    results = []
    for row in completed:
        progress, _ = StudentProgress.objects.get_or_create(
            student=request.user,
            subject_id=row['subject_id'],
        )
        if progress.lessons_completed != row['lessons_completed']:
            progress.lessons_completed = row['lessons_completed']
            progress.save(update_fields=['lessons_completed', 'last_updated'])
        results.append({
            'subject_id': row['subject_id'],
            'subject_name': row['subject__name'],
            'score_before': progress.score_before,
            'score_after': progress.score_after,
            'lessons_completed': progress.lessons_completed,
        })
    return Response({'results': results})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_flashcards(request):
    topic = request.data.get('topic', '').strip()
    subject = request.data.get('subject', '').strip()
    if not topic:
        return Response({'error': 'Topic required.'}, status=400)
    from django.conf import settings
    if not settings.OPENAI_API_KEY:
        return Response({'cards': [], 'error': 'AI not configured.'})
    try:
        import json
        import openai
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=getattr(settings, 'OPENAI_MODEL', 'gpt-4o-mini'),
            messages=[{'role': 'user', 'content': (
                f'Generate 5 concise flashcards for {subject or "General"}: {topic}. '
                'Return only JSON array objects with q and a keys. No markdown.'
            )}],
            max_tokens=500,
        )
        cards = json.loads(response.choices[0].message.content)
        return Response({'cards': cards})
    except Exception as exc:
        logger.warning('Flashcard generation failed: %s', exc)
        return Response({'cards': [], 'error': 'Could not generate flashcards.'}, status=502)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_quiz(request):
    topic   = request.data.get('topic','')
    subject = request.data.get('subject','')
    if not topic: return Response({'error':'Topic required.'}, status=400)
    from django.conf import settings
    if not settings.OPENAI_API_KEY: return Response({'questions':[],'error':'AI not configured.'})
    try:
        import openai, json
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        resp = client.chat.completions.create(
            model=getattr(settings, 'OPENAI_MODEL', 'gpt-4o-mini'),
            messages=[{'role':'user','content':f'Generate 5 multiple-choice questions for {subject or "General"}: {topic}. Return only a JSON array with "question", "options" (array of 4), "answer" (index 0-3). No markdown.'}],
            max_tokens=600)
        questions = json.loads(resp.choices[0].message.content)
        return Response({'questions':questions})
    except Exception as e:
        return Response({'questions':[],'error':str(e)})
