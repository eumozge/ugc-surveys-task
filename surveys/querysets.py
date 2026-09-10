from django.db import models
from django.db.models import Prefetch


class PositionOrderQuerySetMixin:
    def order_by_position(self):
        return self.order_by("position", "pk")


class SurveyQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True)


class QuestionQuerySet(models.QuerySet, PositionOrderQuerySetMixin):
    def with_ordered_choices(self):
        from surveys.models import Choice

        choices = Choice.objects.order_by_position()
        return self.prefetch_related(Prefetch("choices", queryset=choices))


class ChoiceQuerySet(models.QuerySet, PositionOrderQuerySetMixin):
    pass
