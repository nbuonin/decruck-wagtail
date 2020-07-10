from modeltranslation.translator import TranslationOptions
from modeltranslation.decorators import register
from decruck.main.models import (
    HomePage, BiographyPage, CompositionListingPage, CompositionPage,
    ContactFormPage, ScoreListingPage, ScorePage, ShoppingCartPage,
    BasicPage, Instrument, Genre
)


@register(HomePage)
class HomePageTR(TranslationOptions):
    fields = []


@register(BiographyPage)
class BiographyPageTR(TranslationOptions):
    fields = (
        'body',
    )


@register(CompositionListingPage)
class CompositionListingPageTR(TranslationOptions):
    fields = []


@register(CompositionPage)
class CompositionPageTR(TranslationOptions):
    fields = []


@register(ContactFormPage)
class ContactFormPageTR(TranslationOptions):
    fields = []


@register(ScoreListingPage)
class ScoreListingPageTR(TranslationOptions):
    fields = []


@register(ScorePage)
class ScorePageTR(TranslationOptions):
    fields = []


@register(ShoppingCartPage)
class ShoppingCartPageTR(TranslationOptions):
    fields = []


@register(BasicPage)
class BasicPageTR(TranslationOptions):
    fields = []


@register(Instrument)
class InstrumentTR(TranslationOptions):
    fields = ['instrument']


@register(Genre)
class GenreTR(TranslationOptions):
    fields = ['genre']
