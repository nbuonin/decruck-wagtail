from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db.models import (
    CharField, DecimalField, DurationField, FileField, ForeignKey, Model,
    PROTECT, URLField, FloatField, DateField, OneToOneField, CASCADE
)
from django.shortcuts import render
from django.utils.safestring import mark_safe
from edtf import parse_edtf, struct_time_to_date
from edtf.parser.edtf_exceptions import EDTFParseException
from modelcluster.fields import ParentalManyToManyField, ParentalKey
from wagtail.admin.edit_handlers import (
    StreamFieldPanel, FieldPanel, InlinePanel
)
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
    """Home Page"""
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


class CompositionEDTF(Model):
    composition = ParentalKey(
        'CompositionPage',
        on_delete=CASCADE,
        unique=True,
        related_name='date'
    )
    nat_lang_edtf_string = CharField(
        verbose_name='Natural Language Date',
        help_text=('The EDTF date in natural language. This field is help '
                   'users who aren\'t familiar with the EDTF. It does not '
                   'change how the date is represented.'),
        max_length=256)
    edtf_string = CharField(
        verbose_name='EDTF Date',
        help_text=mark_safe(
            'A date in the <a href="https://www.loc.gov/standards/datetime/" '
            'target="_blank"><strong>Extended Date Time Format</strong></a>'),
        max_length=256)
    lower_fuzzy = DateField(editable=False)
    upper_fuzzy = DateField(editable=False)
    lower_strict = DateField(editable=False)
    upper_strict = DateField(editable=False)

    panels = [
        FieldPanel('edtf_string'),
        FieldPanel('nat_lang_edtf_string')
    ]

    def __str__(self):
        return self.edtf_string

    def clean(self):
        try:
            e = parse_edtf(self.edtf_string)
        except EDTFParseException:
            raise ValidationError(
                {'edtf_string': '{} is not a valid EDTF string'.
                                format(self.edtf_string)})

        self.lower_fuzzy = struct_time_to_date(e.lower_fuzzy())
        self.upper_fuzzy = struct_time_to_date(e.upper_fuzzy())
        self.lower_strict = struct_time_to_date(e.lower_strict())
        self.upper_strict = struct_time_to_date(e.upper_strict())

    def save(self, *args, **kwargs):
        try:
            e = parse_edtf(self.edtf_string)
        except EDTFParseException:
            raise ValidationError('{} is not a valid EDTF string'.
                                  format(self.edtf_string))

        self.lower_fuzzy = struct_time_to_date(e.lower_fuzzy())
        self.upper_fuzzy = struct_time_to_date(e.upper_fuzzy())
        self.lower_strict = struct_time_to_date(e.lower_strict())
        self.upper_strict = struct_time_to_date(e.upper_strict())

        super().save(*args, **kwargs)


class CompositionListingPage(Page, MenuPageMixin):
    def serve(self, request):
        # Local import to break circular dependency
        from decruck.main.forms import CompositionListingForm
        if request.method == 'GET':
            if len(request.GET.keys()) > 0:
                form = CompositionListingForm(request.GET)
                compositions = None
                if form.is_valid():
                    # Implement search functionality here and
                    # assign to compositions
                    compositions = []
                return render(request, "main/composition_listing_page.html", {
                    'page': self,
                    'form': form,
                    'compositions': compositions
                })

            # Else return an empty form
            form = CompositionListingForm()
            return render(request, "main/composition_listing_page.html", {
                'page': self,
                'form': form,
                'compositions': CompositionPage.objects.all()  # TODO order by date
            })

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
        InlinePanel(
            'date',
            label='Date',
            help_text='Enter a date in the LOC Extended Date Time Format',
            max_num=1
        ),
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

    def __str__(self):
        return self.instrument


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
