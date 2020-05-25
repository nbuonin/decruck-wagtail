from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db.models import (
    CharField, DecimalField, DurationField, FileField, ForeignKey, Model,
    PROTECT, URLField, DateField, CASCADE, PositiveSmallIntegerField,
    ImageField
)
from django.shortcuts import render
from django.utils.safestring import mark_safe
from edtf import parse_edtf, struct_time_to_date
from edtf.parser.edtf_exceptions import EDTFParseException
import hashlib
from modelcluster.fields import ParentalManyToManyField, ParentalKey
from wagtail.admin.edit_handlers import (
    StreamFieldPanel, FieldPanel, InlinePanel
)
from wagtail.search.backends import get_search_backend
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.core.blocks import (
    RichTextBlock, StructBlock, StreamBlock, BlockQuoteBlock, CharBlock
)
from wagtail.core.fields import StreamField, RichTextField
from wagtail.core.models import Page
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
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
    (ORCHESTRAL, 'Orchestral Music'),
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
        ('heading', StructBlock([
            ('left_column', CharBlock()),
            ('right_column', CharBlock())
        ], template='main/blocks/bio-heading.html', icon='bold')),
        ('row', StructBlock([
            ('left_column', StreamBlock([
                ('rich_text', RichTextBlock(
                    features=['bold', 'italic', 'ol', 'ul', 'link', 'embed']
                )),
                ('caption_image', StructBlock([
                    ('image', ImageChooserBlock()),
                    ('caption', CharBlock())
                ], template='main/blocks/bio-caption-image.html', icon='image')),  # noqa E501
            ])),
            ('right_column', StreamBlock([
                ('rich_text', RichTextBlock(
                    features=['bold', 'italic', 'ol', 'ul', 'link', 'embed']
                )),
                ('caption_image', StructBlock([
                    ('image', ImageChooserBlock()),
                    ('caption', CharBlock())
                ], template='main/blocks/bio-caption-image.html', icon='image')),  # noqa E501
            ])),
        ], template='main/blocks/bio-row.html', icon='pilcrow')),
        ('block_quote', StructBlock([
            ('quote', CharBlock()),
            ('caption', RichTextBlock(
                features=['bold', 'italic']
            ))
        ], template='main/blocks/bio-quote.html', icon='openquote')),
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


class Genre(Model):
    genre = CharField(max_length=256)

    def __str__(self):
        return self.genre


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
    nat_lang_year = CharField(editable=False, max_length=9)

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

        if self.lower_strict.year != self.upper_strict.year:
            self.nat_lang_year = '{}-{}'.format(
                self.lower_strict.year,
                self.upper_strict.year
            )
        else:
            self.nat_lang_year = str(self.lower_strict.year)

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

        if self.lower_strict.year != self.upper_strict.year:
            self.nat_lang_year = '{}-{}'.format(
                self.lower_strict.year,
                self.upper_strict.year
            )
        else:
            self.nat_lang_year = str(self.lower_strict.year)

        super().save(*args, **kwargs)


class CompositionListingPage(Page, MenuPageMixin):
    def serve(self, request):
        # Local import to break circular dependency
        from decruck.main.forms import CompositionListingForm
        if request.method == 'GET':
            if len(request.GET.keys()) > 0:
                form = CompositionListingForm(request.GET)
                compositions = CompositionPage.objects.all()
                if form.is_valid():
                    backend = get_search_backend()
                    # Implement search functionality here and
                    # assign to compositions
                    """
                    (Pdb) pp form.cleaned_data
                    {'end_year': None,
                    'genre': ['11', '13'],
                    'instrumentation': ['47'],
                    'keyword': 'foo',
                    'sort_by': '',
                    'sort_dir': '',
                    'start_year': 1925}
                    (Pdb)
                    """
                    if form.cleaned_data['start_year']:
                        # TODO filtering off of date could be buggy because
                        # it's expecting there to be multiple dates
                        # e.g. 'date__first'...
                        compositions = compositions.filter(
                            date__lower_strict__year__gte=form.cleaned_data['start_year'])

                    if form.cleaned_data['end_year']:
                        compositions = compositions.filter(
                            date__upper_strict__year__lte=form.cleaned_data['end_year'])

                    if form.cleaned_data['genre']:
                        compositions = compositions.filter(
                            genre__in=form.cleaned_data['genre'])

                    # Sort results
                    sort_by = form.cleaned_data['sort_by']
                    sort_dir = form.cleaned_data['sort_dir']
                    if sort_by != 'year':
                        if sort_dir == 'ASC':
                            compositions = compositions.order_by(sort_by)
                        else:
                            compositions = compositions.order_by('-' + sort_by)
                    else:
                        if sort_dir == 'ASC':
                            # Order by start year
                            compositions = compositions.order_by(
                                'date__lower_strict')
                        else:
                            # Order by end year
                            compositions = compositions.order_by(
                                '-date__upper_strict')

                    # Per Wagtail docs, search must come after all filtering
                    if form.cleaned_data['keyword']:
                        compositions = backend.search(
                            form.cleaned_data['keyword'],
                            compositions
                        )

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
        ('rich_text', RichTextBlock()),
        ('image', ImageChooserBlock())
    ], blank=True)
    location = RichTextField(
        blank=True,
        features=['bold', 'italic']
    )
    genre = ForeignKey(
        Genre,
        null=True,
        blank=True,
        on_delete=PROTECT
    )
    instrumentation = ParentalManyToManyField(
        'Instrument',
        blank=True,
    )
    orchestration = RichTextField(
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
        null=True,
        blank=True,
        help_text='A URL to the published score.'
    )
    recording = StreamField([
        ('rich_text', RichTextBlock()),
        ('image', ImageChooserBlock())
    ], blank=True)

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
        FieldPanel('orchestration'),
        FieldPanel('duration'),
        FieldPanel('dedicatee'),
        FieldPanel('genre'),
        FieldPanel('text_source'),
        FieldPanel('collaborator'),
        FieldPanel('manuscript_status'),
        FieldPanel('published_work_link'),
        StreamFieldPanel('recording'),
    ]

    search_fields = Page.search_fields + [
        index.SearchField('description'),
        index.SearchField('location'),
        index.SearchField('dedicatee'),
        index.SearchField('text_source'),
        index.SearchField('collaborator'),
        index.SearchField('manuscript_status'),
        index.SearchField('recording'),
        index.FilterField('genre'),
        index.FilterField('instrument_id')
    ]

    parent_page_types = ['CompositionListingPage']


class Instrument(Model):
    instrument = CharField(max_length=256)

    def __str__(self):
        return self.instrument


class ContactFormPage(RoutablePageMixin, Page, MenuPageMixin):
    body = StreamField([
        ('rich_text', RichTextBlock()),
        ('image', ImageChooserBlock())
    ])
    confirmation_page_text = StreamField([
        ('rich_text', RichTextBlock()),
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
        ('rich_text', RichTextBlock()),
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
        ('rich_text', RichTextBlock()),
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
                allowed_extensions=['pdf', 'zip'])
        ]
    )
    preview_score = FileField(
        upload_to='preview_scores/',
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf'])
        ]
    )
    preview_score_checksum = CharField(
        editable=False,
        max_length=256,
        blank=True
    )
    preview_score_checked = False
    preview_score_updated = False
    genre = ForeignKey(
        Genre,
        null=True,
        blank=True,
        on_delete=PROTECT
    )
    date = CharField(
        max_length=256,
        blank=True
    )
    instrumentation = ParentalManyToManyField(
        'Instrument',
        blank=True,
        help_text='The instrumentation of the compostition.'
    )
    price = DecimalField(max_digits=6, decimal_places=2)
    materials = RichTextField(
        blank=True,
        features=['bold', 'italic'],
        help_text='The materials sent in the PDF file.'
    )

    def clean(self):
        super().clean()
        if self.preview_score_checked:
            return

        h = hashlib.md5()
        for chunk in iter(lambda: self.preview_score.read(8192), b''):
            h.update(chunk)

        self.preview_score.seek(0)
        checksum = h.hexdigest()
        if not self.preview_score_checksum == checksum:
            self.preview_score_checksum = checksum
            self.preview_score_updated = True

        self.preview_score_checked = True

    class Meta:
        verbose_name = "Score Page"

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('duration'),
        FieldPanel('genre'),
        FieldPanel('instrumentation'),
        FieldPanel('price'),
        StreamFieldPanel('description'),
        FieldPanel('materials'),
        FieldPanel('file'),
        FieldPanel('preview_score'),
        ImageChooserPanel('cover_image')
    ]


class PreviewScoreImage(Model):
    score = ForeignKey(
        ScorePage,
        on_delete=CASCADE,
        related_name='preview_score_images'
    )
    preview_score_image = ImageField(
        upload_to='score_preview_images/',
    )
    page_number = PositiveSmallIntegerField()

    class Meta:
        ordering = ['page_number']
        unique_together = ('score', 'page_number')


class ShoppingCartPage(RoutablePageMixin, Page):
    body = StreamField([
        ('rich_text', RichTextBlock()),
        ('image', ImageChooserBlock())
    ])
    confirmation_page_text = StreamField([
        ('rich_text', RichTextBlock()),
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
        ('rich_text', RichTextBlock()),
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
