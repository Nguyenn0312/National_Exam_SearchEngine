from rest_framework import serializers
from .models import ExamResult

class ExamResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamResult
        fields = '__all__' 