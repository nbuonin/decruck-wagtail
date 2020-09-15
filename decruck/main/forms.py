"""Custom Forms for Decruck Wagatail"""
from django.forms import (
    Form, CharField, IntegerField, ChoiceField, MultipleChoiceField,
    ValidationError, RadioSelect, CheckboxSelectMultiple, EmailField,
    Textarea, HiddenInput
)
from django.utils.translation import gettext as _
from decruck.main.models import Genre, Instrument


def genre_choices():
    return tuple((i.pk, i) for i in Genre.objects.all())


def instrument_choices():
    return tuple((i.pk, i) for i in Instrument.objects.all())


class CompositionListingForm(Form):
    """Composition Listing Form"""
    sort_by_choices = (
        ('year', 'Year'),
        ('title', 'Title'),
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
        initial=('ASC', 'Asc'),
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


class OrderRetrievalForm(Form):
    email_address = EmailField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email_address'].widget.attrs['placeholder'] = _(
            'Email Address')


class ContactForm(Form):
    name = CharField(max_length=64)
    email_address = EmailField()
    message = CharField(widget=Textarea)
    # honeypot field
    msg = CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['placeholder'] = _(
            'Name')
        self.fields['email_address'].widget.attrs['placeholder'] = _(
            'Email Address')
        self.fields['message'].widget.attrs['placeholder'] = _(
            'Message')
