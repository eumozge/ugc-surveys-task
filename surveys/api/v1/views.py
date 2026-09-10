from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from surveys.api.v1.serializers import SurveyProgressSerializer
from surveys.models import Survey
from surveys.services.survey_progress import get_user_survey_progress


class SurveyViewSet(viewsets.GenericViewSet):
    lookup_field = "public_id"
    permission_classes = [IsAuthenticated]

    def get_published_survey(self):
        return get_object_or_404(Survey.objects.published(), public_id=self.kwargs["public_id"])

    @action(
        detail=True,
        methods=["get"],
        url_path="current-question",
        serializer_class=SurveyProgressSerializer,
    )
    def current_question(self, request, *args, **kwargs):
        survey = self.get_published_survey()
        progress = get_user_survey_progress(survey=survey, respondent=request.user)
        serializer = self.get_serializer(progress)
        return Response(serializer.data)
