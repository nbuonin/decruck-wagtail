from django.core.validators import FileExtensionValidator
from django.db.models import (
    CharField, DecimalField, DurationField, FileField, ForeignKey, Model,
    PROTECT, URLField
)
from django.shortcuts import render
from modelcluster.fields import ParentalManyToManyField
from wagtail.admin.edit_handlers import StreamFieldPanel, FieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.core.blocks import RichTextBlock
from wagtail.core.fields import StreamField, RichTextField
from wagtail.core.models import Page
from wagtail.images.blocks import ImageChooserBlock
from wagtailmenus.models import MenuPageMixin
from wagtailmenus.panels import menupage_panel


ARRANGEMENTS = 'ARRANGEMENTS'
CHAMBER = 'CHAMBER'
ETUDES = 'ETUDES'
ORCHESTRAL = 'ORCHESTRAL'
ORGAN = 'ORGAN'
SOLO_PIANO = 'SOLO_PIANO'
ART_SONG = 'ART_SONG'
CHORAL = 'CHORAL'
GENRE = (
    (ARRANGEMENTS, 'Arrangements'),
    (CHAMBER, 'Chamber Music'),
    (ETUDES, 'Etudes'),
    (ORCHESTRAL, 'Orchstral Music'),
    (ORGAN, 'Organ Music'),
    (SOLO_PIANO, 'Solo Piano Music'),
    (ART_SONG, 'Art Song'),
    (CHORAL, 'Choral')
)


class HomePage(Page, MenuPageMixin):
    class Meta:
        verbose_name = "Homepage"

    settings_panels = Page.settings_panels + [
        menupage_panel
    ]

    parent_page_types = ['wagtailcore.Page']


class BiographyPage(Page, MenuPageMixin):
    body = StreamField([
        ('paragraph', RichTextBlock()),
        ('image', ImageChooserBlock())
    ])

    class Meta:
        verbose_name = "Biography Page"

    content_panels = Page.content_panels + [
        StreamFieldPanel('body')
    ]

    settings_panels = Page.settings_panels + [
        menupage_panel
    ]

    parent_page_types = ['HomePage']


class CompositionListingPage(Page, MenuPageMixin):
    class Meta:
        verbose_name = "Composition Listing Page"

    settings_panels = Page.settings_panels + [
        menupage_panel
    ]

    parent_page_types = ['HomePage']


class CompositionPage(Page):
    composition_title = RichTextField(features=['bold', 'italic'])
    description = StreamField([
        ('paragraph', RichTextBlock()),
        ('image', ImageChooserBlock())
    ], blank=True)
    # Date: TODO decide which type of date field to use
    location = RichTextField(
        blank=True,
        features=['bold', 'italic']
    )
    instrumentation = ParentalManyToManyField(
        'Instrument',
        blank=True,
    )
    orchestral_instrumentation = RichTextField(
        blank=True,
        features=['bold', 'italic'],
        help_text=(
            'If the composition is for an ensemble, use this field to enter '
            'the orchestration of the work.')
    )
    duration = DurationField(
        null=True,
        blank=True,
        help_text='Expects data in the format "HH:MM:SS"'
    )
    dedicatee = RichTextField(
        blank=True,
        features=['bold', 'italic']
    )
    genre = CharField(
        choices=GENRE,
        blank=True,
        max_length=256
    )
    text_source = RichTextField(
        blank=True,
        features=['bold', 'italic'],
        help_text='The source of the text used in the compostition.'
    )
    collaborator = RichTextField(
        blank=True,
        features=['bold', 'italic'],
        help_text='Others that Decruck collaborated with.'
    )
    manuscript_status = RichTextField(
        blank=True,
        features=['bold', 'italic'],
        help_text='Notes about the location and condition of the manuscript.'
    )
    published_work_link = URLField(
        blank=True,
        help_text='A URL to the published score.'
    )
    recording_link = CharField(
        blank=True,
        max_length=256,
        help_text='The You Tube id of a recording.'
    )

    class Meta:
        verbose_name = "Composition"

    content_panels = Page.content_panels + [
        FieldPanel('composition_title'),
        StreamFieldPanel('description'),
        FieldPanel('location'),
        FieldPanel('instrumentation'),
        FieldPanel('orchestral_instrumentation'),
        FieldPanel('duration'),
        FieldPanel('dedicatee'),
        FieldPanel('genre'),
        FieldPanel('text_source'),
        FieldPanel('collaborator'),
        FieldPanel('manuscript_status'),
        FieldPanel('published_work_link'),
        FieldPanel('recording_link'),
    ]

    parent_page_types = ['CompositionListingPage']


class Instrument(Model):
    instrument = CharField(max_length=256)


class ContactFormPage(RoutablePageMixin, Page, MenuPageMixin):
    body = StreamField([
        ('paragraph', RichTextBlock()),
        ('image', ImageChooserBlock())
    ])
    confirmation_page_text = StreamField([
        ('paragraph', RichTextBlock()),
        ('image', ImageChooserBlock())
    ])

    @route(r'thank-you/$')
    def thank_you(self, request):
        context = self.get_context(request)
        return render(request, "main/contact_form_thank_you.html", context)

    @route(r'^$')
    def contact_form(self, request):
        context = self.get_context(request)
        return render(request, "main/contact_form.html", context)

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
        StreamFieldPanel('confirmation_page_text')
    ]

    settings_panels = Page.settings_panels + [
        menupage_panel
    ]


class ScoreListingPage(Page, MenuPageMixin):
    description = StreamField([
        ('paragraph', RichTextBlock()),
        ('image', ImageChooserBlock())
    ])

    class Meta:
        verbose_name = "Score Listing Page"

    content_panels = Page.content_panels + [
        StreamFieldPanel('description')
    ]

    settings_panels = Page.settings_panels + [
        menupage_panel
    ]


class ScorePage(Page):
    cover_image = ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=PROTECT,
        related_name='cover_image'
    )
    description = StreamField([
        ('paragraph', RichTextBlock()),
        ('image', ImageChooserBlock())
    ])
    duration = DurationField(
        null=True,
        blank=True,
        help_text='Expects data in the format "HH:MM:SS"'
    )
    file = FileField(
        upload_to='scores/',
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf'])
        ]
    )
    genre = CharField(
        choices=GENRE,
        blank=True,
        max_length=256
    )
    instrumentation = RichTextField(
        blank=True,
        features=['bold', 'italic'],
        help_text='The instrumentation of the compostition.'
    )
    price = DecimalField(max_digits=6, decimal_places=2)
    materials = RichTextField(
        blank=True,
        features=['bold', 'italic'],
        help_text='The materials sent in the PDF file.'
    )

    class Meta:
        verbose_name = "Score Listing Page"

    content_panels = Page.content_panels + [
        StreamFieldPanel('description')
    ]


class ShoppingCartPage(RoutablePageMixin, Page):
    body = StreamField([
        ('paragraph', RichTextBlock()),
        ('image', ImageChooserBlock())
    ])
    confirmation_page_text = StreamField([
        ('paragraph', RichTextBlock()),
        ('image', ImageChooserBlock())
    ])

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
        StreamFieldPanel('confirmation_page_text')
    ]

    @route(r'thank-you/$')
    def thank_you(self, request):
        context = self.get_context(request)
        return render(request, "main/shopping_cart_thank_you.html", context)

    @route(r'^$')
    def contact_form(self, request):
        context = self.get_context(request)
        return render(request, "main/shopping_cart.html", context)


class BasicPage(Page, MenuPageMixin):
    body = StreamField([
        ('paragraph', RichTextBlock()),
        ('image', ImageChooserBlock())
    ])

    class Meta:
        verbose_name = "Basic Page"

    content_panels = Page.content_panels + [
        StreamFieldPanel('body')
    ]

    settings_panels = Page.settings_panels + [
        menupage_panel
    ]
