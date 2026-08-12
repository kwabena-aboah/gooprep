from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import AIConversation, StudentProgress
import logging
logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def ai_chat(request):
    message = request.data.get('message','').strip()
    if not message: return Response({'error':'Message required.'}, status=400)
    from django.conf import settings
    api_key = settings.OPENAI_API_KEY
    if not api_key: return Response({'response':'AI assistant is currently unavailable. Please contact support.'})
    # Get or create conversation history
    conv, _ = AIConversation.objects.get_or_create(user=request.user)
    history  = conv.messages[-10:]  # keep last 10 messages for context
    history.append({'role':'user','content':message})
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
                {'role':'system','content':"You are a helpful study assistant for Gooprep, Ghana's tutoring platform. Help students with homework, exam prep, and learning questions. Be concise and educational. Use Ghana context when relevant."},
                *history
            ], max_tokens=600
        )
        ai_reply = resp.choices[0].message.content
        history.append({'role':'assistant','content':ai_reply})
        conv.messages = history[-20:]  # keep last 20
        conv.save(update_fields=['messages','updated_at'])
        return Response({'response':ai_reply})
    except Exception as e:
        logger.warning(f'AI chat error: {e}')
        return Response({'response':'Sorry, I could not process that right now. Please try again shortly.'})

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
    stored = {
        progress.subject_id: progress
        for progress in StudentProgress.objects.filter(student=request.user)
    }
    results = []
    for row in completed:
        progress = stored.get(row['subject_id'])
        results.append({
            'subject_id': row['subject_id'],
            'subject_name': row['subject__name'],
            'score_before': progress.score_before if progress else 0,
            'score_after': progress.score_after if progress else 0,
            'lessons_completed': row['lessons_completed'],
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
            model='gpt-3.5-turbo',
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
        resp = client.chat.completions.create(model='gpt-3.5-turbo',
            messages=[{'role':'user','content':f'Generate 5 multiple-choice questions for {subject or "General"}: {topic}. Return only a JSON array with "question", "options" (array of 4), "answer" (index 0-3). No markdown.'}],
            max_tokens=600)
        questions = json.loads(resp.choices[0].message.content)
        return Response({'questions':questions})
    except Exception as e:
        return Response({'questions':[],'error':str(e)})
