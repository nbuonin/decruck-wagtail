"""Custom Forms for Decruck Wagatail"""
from django.forms import (
    Form, CharField, IntegerField, ChoiceField, MultipleChoiceField,
    ValidationError, RadioSelect, CheckboxSelectMultiple
)
from decruck.main.models import Genre, Instrument


def genre_choices():
    return tuple((i.pk, i) for i in Genre.objects.all())


def instrument_choices():
    return tuple((i.pk, i) for i in Instrument.objects.all())


class CompositionListingForm(Form):
    """Composition Listing Form"""
    sort_by_choices = (
        ('genre', 'Genre'),
        ('title', 'Title'),
        ('year', 'Year'),
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
        choices=genre_choices,
        widget=CheckboxSelectMultiple
    )
    sort_by = ChoiceField(
        required=False,
        choices=sort_by_choices,
        initial=sort_by_choices[0],
        widget=RadioSelect
    )
    sort_dir = ChoiceField(
        required=False,
        choices=(('ASC', 'Asc'), ('DESC', 'Desc')),
        initial=('DESC', 'Desc'),
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
