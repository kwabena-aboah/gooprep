from rest_framework import serializers
from .models import StudentProfile, LearningPath, KnowledgeBase

class StudentProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = StudentProfile
        fields = ['id','full_name','email','learning_goals','current_level',
                  'preferred_languages','budget_min','budget_max',
                  'preferred_teaching_style','subjects_of_interest',
                  'total_lessons','total_hours','total_spent','created_at']

class LearningPathSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningPath
        fields = ['id','student','tutor','title','description','subject',
                  'milestones','current_milestone','progress_percent','is_active','created_at']

class KnowledgeBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeBase
        fields = ['id','lesson','title','content_type','content','subject','tags','created_at']
