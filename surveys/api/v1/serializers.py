from rest_framework import serializers

from surveys.models import Choice, Question


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ("id", "text")


class SurveyQuestionReadSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ("id", "text", "choices")


class SurveyProgressSerializer(serializers.Serializer):
    state = serializers.CharField(source="progress_state.value")
    question = SurveyQuestionReadSerializer(source="current_question", allow_null=True)
