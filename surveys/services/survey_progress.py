from dataclasses import dataclass
from enum import StrEnum

from django.contrib.auth.base_user import AbstractBaseUser

from surveys.models import AttemptState, Question, Survey, SurveyAttempt


class SurveyProgressState(StrEnum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

    @property
    def is_completed(self) -> bool:
        return self is SurveyProgressState.COMPLETED

    @classmethod
    def from_survey_attempt(cls, attempt: SurveyAttempt | None) -> "SurveyProgressState":
        """A missing attempt is represented as not_started, because no DB attempt means survey is not started."""
        state_mapping = {
            None: cls.NOT_STARTED,
            AttemptState.IN_PROGRESS: cls.IN_PROGRESS,
            AttemptState.COMPLETED: cls.COMPLETED,
        }
        state = None if attempt is None else attempt.state
        if state in state_mapping:
            return state_mapping[state]
        raise NotImplementedError(attempt, state)


@dataclass(frozen=True, slots=True)
class SurveyProgress:
    progress_state: SurveyProgressState
    current_question: Question | None


def get_user_survey_current_question(survey: Survey, survey_attempt: SurveyAttempt | None) -> Question | None:
    survey_questions = survey.questions.with_ordered_choices().order_by_position()

    if survey_attempt:
        answered_questions_ids = survey_attempt.answers.values_list("question_id", flat=True)
        survey_questions = survey_questions.exclude(id__in=answered_questions_ids)

    return survey_questions.first()


def get_user_survey_progress(survey: Survey, respondent: AbstractBaseUser) -> SurveyProgress:
    survey_attempt = survey.attempts.filter(respondent=respondent).first()
    progress_state = SurveyProgressState.from_survey_attempt(survey_attempt)

    if progress_state.is_completed:
        return SurveyProgress(progress_state, None)

    current_question = get_user_survey_current_question(survey, survey_attempt)
    return SurveyProgress(progress_state, current_question)
