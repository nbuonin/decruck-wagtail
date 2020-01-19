"""Custom Forms for Decruck Wagatail"""
from django.forms import (
    Form, CharField, IntegerField, ChoiceField, MultipleChoiceField,
    ValidationError
)
from decruck.main.models import GENRE, Instrument


class CompositionListingForm(Form):
    """Composition Listing Form"""
    instrument_choices = zip(
        [str(i).replace(' ', '_').upper() for i in Instrument.objects.all()],
        [i for i in Instrument.objects.all()]
    )
    sort_by_choices = (
        ('KEYWORD', 'KEYWORD'),
        ('START_YEAR', 'START_YEAR'),
        ('END_YEAR', 'END_YEAR'),
        ('GENRE', 'GENRE'),
        ('INSTRUMENTATION', 'INSTRUMENTATION')
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
        choices=GENRE
    )
    instrumentation = MultipleChoiceField(
        required=False,
        choices=instrument_choices
    )
    sort_by = ChoiceField(
        required=False,
        choices=sort_by_choices
    )
    sort_dir = ChoiceField(
        required=False,
        choices=(('ASC', 'ASC'), ('DESC', 'DESC'))
    )

    def clean(self):
        cleaned_data = super().clean()
        start_year = cleaned_data.get('start_year')
        end_year = cleaned_data.get('end_year')
        if start_year and end_year:
            if start_year > end_year:
                raise ValidationError(
                    'The starting year can not be greater than the end year.')
