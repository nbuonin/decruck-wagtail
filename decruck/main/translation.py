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
    fields = (
        'description',
        'manuscript_status',
    )


@register(ContactFormPage)
class ContactFormPageTR(TranslationOptions):
    fields = (
        'body',
    )


@register(ScoreListingPage)
class ScoreListingPageTR(TranslationOptions):
    fields = (
        'description',
    )


@register(ScorePage)
class ScorePageTR(TranslationOptions):
    fields = (
        'description',
        'materials',
    )


@register(ShoppingCartPage)
class ShoppingCartPageTR(TranslationOptions):
    fields = (
        'body',
        'confirmation_page_text',
    )


@register(BasicPage)
class BasicPageTR(TranslationOptions):
    fields = (
        'body',
    )


@register(Instrument)
class InstrumentTR(TranslationOptions):
    fields = (
        'instrument',
    )


@register(Genre)
class GenreTR(TranslationOptions):
    fields = (
        'genre',
    )
