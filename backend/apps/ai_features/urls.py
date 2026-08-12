from django.urls import path

from .views import (
    ai_chat,
    clear_ai_chat,
    student_progress,
    generate_flashcards,
    generate_quiz,
)

urlpatterns = [
    path('chat/', ai_chat, name='ai_chat'),
    path('chat/clear/', clear_ai_chat, name='ai_chat_clear'),
    path('progress/', student_progress, name='student_progress'),
    path('generate-flashcards/', generate_flashcards, name='generate_flashcards'),
    path('generate-quiz/', generate_quiz, name='generate_quiz'),
]
