"""Custom Forms for Decruck Wagatail"""
from django.forms import (
    Form, CharField, IntegerField, ChoiceField, MultipleChoiceField,
    ValidationError, RadioSelect
)
from decruck.main.models import Genre, Instrument


def genre_choices():
    return tuple((i.pk, i) for i in Genre.objects.all())


def instrument_choices():
    return tuple((i.pk, i) for i in Instrument.objects.all())


class CompositionListingForm(Form):
    """Composition Listing Form"""
    sort_by_choices = (
        ('TITLE', 'Title'),
        ('START_YEAR', 'Start Year'),
        ('END_YEAR', 'End Year'),
        ('GENRE', 'Genre'),
        ('DURATION', 'Duration')
    )

    keyword = CharField(
        label='Keyword',
        required=False
    )
    start_year = IntegerField(
        required=False,
        min_value=1896,
        max_value=1954
    )
    end_year = IntegerField(
        required=False,
        min_value=1896,
        max_value=1954
    )
    genre = MultipleChoiceField(
        required=False,
        choices=genre_choices
    )
    instrumentation = MultipleChoiceField(
        required=False,
        choices=instrument_choices
    )
    sort_by = ChoiceField(
        required=False,
        choices=sort_by_choices,
        widget=RadioSelect
    )
    sort_dir = ChoiceField(
        required=False,
        choices=(('ASC', 'Asc'), ('DESC', 'Desc')),
        widget=RadioSelect
    )

    def clean(self):
        cleaned_data = super().clean()
        start_year = cleaned_data.get('start_year')
        end_year = cleaned_data.get('end_year')
        if start_year and end_year:
            if start_year > end_year:
                raise ValidationError(
                    'The starting year can not be greater than the end year.')
