import uuid

from django.conf import settings
from django.db import models

from surveys.querysets import ChoiceQuerySet, QuestionQuerySet, SurveyQuerySet


class Survey(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    is_published = models.BooleanField(default=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="surveys")
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = SurveyQuerySet.as_manager()


class Question(models.Model):
    survey = models.ForeignKey("surveys.Survey", on_delete=models.PROTECT, related_name="questions")
    text = models.TextField(max_length=1000)
    position = models.PositiveSmallIntegerField()

    objects = QuestionQuerySet.as_manager()


class Choice(models.Model):
    question = models.ForeignKey("surveys.Question", on_delete=models.PROTECT, related_name="choices")
    text = models.TextField(max_length=1000)
    position = models.PositiveSmallIntegerField()

    objects = ChoiceQuerySet.as_manager()


class AttemptState(models.IntegerChoices):
    IN_PROGRESS = 1, "in_progress"
    COMPLETED = 2, "completed"


class SurveyAttempt(models.Model):
    survey = models.ForeignKey("surveys.Survey", on_delete=models.PROTECT, related_name="attempts")
    respondent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="survey_attempts")
    state = models.PositiveSmallIntegerField(choices=AttemptState, default=AttemptState.IN_PROGRESS)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["survey", "respondent"], name="survey_respondent_unique"),
            models.CheckConstraint(
                condition=(
                    models.Q(state=AttemptState.IN_PROGRESS, completed_at__isnull=True)
                    | models.Q(state=AttemptState.COMPLETED, completed_at__isnull=False)
                ),
                name="valid_state_date_invariant",
            ),
        ]


class Answer(models.Model):
    attempt = models.ForeignKey("surveys.SurveyAttempt", on_delete=models.PROTECT)
    question = models.ForeignKey("surveys.Question", on_delete=models.PROTECT)
    choice = models.ForeignKey("surveys.Choice", on_delete=models.PROTECT)

    class Meta:
        default_related_name = "answers"
        constraints = [
            models.UniqueConstraint(fields=["attempt", "question"], name="attempt_question_unique"),
        ]
