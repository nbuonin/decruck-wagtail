from datetime import timedelta
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError, SuspiciousOperation
from django.core.mail import send_mail
from django.core.validators import FileExtensionValidator
from django.db.models import (
    CharField, DecimalField, DurationField, FileField, ForeignKey, Model,
    PROTECT, URLField, DateField, CASCADE, PositiveSmallIntegerField,
    ImageField, DateTimeField, EmailField, UUIDField, GenericIPAddressField,
    TextField, BooleanField, ManyToManyField
)
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import get_template
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from edtf import parse_edtf, struct_time_to_date
from edtf.parser.edtf_exceptions import EDTFParseException
import hashlib
from modelcluster.fields import ParentalManyToManyField, ParentalKey
from paypal.standard.forms import PayPalPaymentsForm
from paypal.standard.ipn.models import PayPalIPN
import requests
import time
import uuid
from wagtail.admin.edit_handlers import (
    StreamFieldPanel, FieldPanel, InlinePanel, MultiFieldPanel
)
from wagtail.search.backends import get_search_backend
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.core.blocks import (
    RichTextBlock, StructBlock, StreamBlock, BlockQuoteBlock, CharBlock,
    EmailBlock, IntegerBlock
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
                    ('image_max_width', IntegerBlock()),
                    ('caption', CharBlock()),
                ], template='main/blocks/bio-caption-image.html', icon='image')),  # noqa E501
            ])),
            ('right_column', StreamBlock([
                ('rich_text', RichTextBlock(
                    features=['bold', 'italic', 'ol', 'ul', 'link', 'embed']
                )),
                ('caption_image', StructBlock([
                    ('image', ImageChooserBlock()),
                    ('image_max_width', IntegerBlock()),
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
                compositions = CompositionPage.objects.live()\
                    .prefetch_related('genre', 'instrumentation')
                if form.is_valid():
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
                    """

                    if form.cleaned_data['keyword']:
                        sb = get_search_backend()
                        kw_results = sb.autocomplete(
                            form.cleaned_data['keyword'],
                            compositions
                        )
                        # Because of a bug in how dates are extracted in
                        # Wagtail's search, we requery the db based on the
                        # pk's found with the initial keyword search
                        compositions = CompositionPage.objects\
                            .prefetch_related('genre', 'instrumentation')\
                            .filter(
                                pk__in=[c.pk for c in kw_results]
                            )

                    if form.cleaned_data['start_year']:
                        compositions = compositions.filter(
                            lower_strict__year__gte=form.cleaned_data['start_year'])  # NOQA: E501

                    if form.cleaned_data['end_year']:
                        compositions = compositions.filter(
                            upper_strict__year__lte=form.cleaned_data['end_year'])  # NOQA: E501

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
                                'lower_strict')
                        else:
                            # Order by end year
                            compositions = compositions.order_by(
                                '-upper_strict')

                request.session['comp_search_index'] = [
                    comp.pk for comp in compositions]
                request.session['comp_search_qs'] = request.GET.urlencode()
                return render(request, "main/composition_listing_page.html", {
                    'self': self,
                    'page': self,
                    'form': form,
                    'compositions': compositions
                })

            # Else return an empty form
            form = CompositionListingForm()
            compositions = CompositionPage.objects.live()\
                .prefetch_related('genre', 'instrumentation')\
                .order_by('lower_strict')
            request.session['comp_search_index'] = [
                comp.pk for comp in compositions]
            return render(request, "main/composition_listing_page.html", {
                'self': self,
                'page': self,
                'form': form,
                'compositions': compositions
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
        features=['bold', 'italic', 'link', 'document-link'],
    )
    genre = ParentalManyToManyField(
        Genre,
        blank=True,
        related_name='compositions'
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
        features=['bold', 'italic', 'link', 'document-link'],
    )
    text_source = RichTextField(
        blank=True,
        features=['bold', 'italic', 'link', 'document-link'],
        help_text='The source of the text used in the compostition.'
    )
    collaborator = RichTextField(
        blank=True,
        features=['bold', 'italic', 'link', 'document-link'],
        help_text='Others that Decruck collaborated with.'
    )
    manuscript_status = RichTextField(
        blank=True,
        features=['bold', 'italic', 'link', 'document-link'],
        help_text='Notes about the location and condition of the manuscript.'
    )
    recording = StreamField([
        ('rich_text', RichTextBlock()),
        ('image', ImageChooserBlock())
    ], blank=True)
    information_up_to_date = BooleanField(default=False)
    scanned = BooleanField(default=False)
    premiere = RichTextField(
        blank=True,
        features=['bold', 'italic', 'link', 'document-link'],
    )

    # For preview score
    preview_score = FileField(
        upload_to='composition_preview_scores/',
        blank=True,
        null=True,
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

    # Extended Date Time Format
    nat_lang_edtf_string = CharField(
        verbose_name='Natural Language Date',
        help_text=('The EDTF date in natural language. This field is help '
                   'users who aren\'t familiar with the EDTF. It does not '
                   'change how the date is represented.'),
        blank=True,
        max_length=256)
    edtf_string = CharField(
        verbose_name='EDTF Date',
        help_text=mark_safe(
            'A date in the <a href="https://www.loc.gov/standards/datetime/" '
            'target="_blank"><strong>Extended Date Time Format</strong></a>'),
        blank=True,
        max_length=256)
    lower_fuzzy = DateField(editable=False, null=True, blank=True)
    upper_fuzzy = DateField(editable=False, null=True, blank=True)
    lower_strict = DateField(editable=False, null=True, blank=True)
    upper_strict = DateField(editable=False, null=True, blank=True)
    nat_lang_year = CharField(editable=False, max_length=9, blank=True)

    def instrumentation_list(self):
        return ', '.join([str(i) for i in self.instrumentation.all()])

    class Meta:
        verbose_name = "Composition"

    def get_context(self, request, *args, **kwargs):
        ctx = super().get_context(request, *args, **kwargs)

        try:
            search_idx = request.session['comp_search_index']
            if search_idx:
                idx = search_idx.index(self.pk)
                prev_url = None
                next_url = None
                if idx > 0:
                    pk = search_idx[idx - 1]
                    prev_url = CompositionPage.objects.get(pk=pk).url

                if idx < len(search_idx) - 1:
                    pk = search_idx[idx + 1]
                    next_url = CompositionPage.objects.get(pk=pk).url

                ctx['prev_url'] = prev_url
                ctx['next_url'] = next_url
                ctx['comp_search_qs'] = request.\
                    session.get('comp_search_qs', '')
        except KeyError:
            pass

        return ctx

    def clean(self):
        super().clean()
        # Per Django docs: validate and modify values in Model.clean()
        # https://docs.djangoproject.com/en/3.1/ref/models/instances/#django.db.models.Model.clean

        # Check that nat_lang_edtf_string and edtf_string are either both set, or both unset
        if (self.nat_lang_edtf_string and not self.edtf_string) or (not self.nat_lang_edtf_string and self.edtf_string):
            raise ValidationError('If setting a date on a composition, an EDTF string and a natural language EDTF string must be provided.')

        # Validate edtf_string
        if self.edtf_string and self.nat_lang_edtf_string:
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
        # If there's no preview score file, then just save the model
        if not self.preview_score:
            return super().save(*args, **kwargs)

        if self.preview_score_checked:
            # This was the cause of a subtle bug. Because this method can be
            # called multiple times during model creation, leaving this flag
            # set would cause the post save hook to fire multiple times.
            self.preview_score_updated = False
            return super().save(*args, **kwargs)

        h = hashlib.md5()
        for chunk in iter(lambda: self.preview_score.read(8192), b''):
            h.update(chunk)

        self.preview_score.seek(0)
        checksum = h.hexdigest()
        if not self.preview_score_checksum == checksum:
            self.preview_score_checksum = checksum
            self.preview_score_updated = True

        self.preview_score_checked = True
        return super().save(*args, **kwargs)

    content_panels = Page.content_panels + [
        FieldPanel('composition_title'),
        StreamFieldPanel('description'),
        MultiFieldPanel(
            [
                FieldPanel('edtf_string'),
                FieldPanel('nat_lang_edtf_string')
            ],
            help_text='Enter a date in the LOC Extended Date Time Format',
            heading='Date'
        ),
        FieldPanel('location'),
        FieldPanel('instrumentation'),
        FieldPanel('orchestration'),
        FieldPanel('duration'),
        FieldPanel('dedicatee'),
        FieldPanel('premiere'),
        FieldPanel('genre'),
        FieldPanel('text_source'),
        FieldPanel('collaborator'),
        FieldPanel('manuscript_status'),
        FieldPanel('information_up_to_date'),
        FieldPanel('scanned'),
        FieldPanel('preview_score'),
        StreamFieldPanel('recording'),
    ]

    search_fields = Page.search_fields + [
        index.SearchField('description', partial_match=True),
        index.SearchField('location', partial_match=True),
        index.SearchField('dedicatee', partial_match=True),
        index.SearchField('premiere', partial_match=True),
        index.SearchField('text_source', partial_match=True),
        index.SearchField('collaborator', partial_match=True),
        index.SearchField('manuscript_status', partial_match=True),
        index.SearchField('recording', partial_match=True),
        index.RelatedFields('genre', [
            index.SearchField('genre_en', partial_match=True),
            index.SearchField('genre_fr', partial_match=True),
        ]),
        index.RelatedFields('instrumentation', [
            index.SearchField('instrument_en', partial_match=True),
            index.SearchField('instrument_fr', partial_match=True),
        ]),
    ]

    parent_page_types = ['CompositionListingPage']


class CompositionPreviewScoreImage(Model):
    score = ForeignKey(
        CompositionPage,
        on_delete=CASCADE,
        related_name='preview_score_images'
    )
    preview_score_image = ImageField(
        upload_to='composition_score_preview_images/',
    )
    page_number = PositiveSmallIntegerField()

    class Meta:
        ordering = ['page_number']
        unique_together = ('score', 'page_number')


class Instrument(Model):
    instrument = CharField(max_length=256)

    def __str__(self):
        return self.instrument


class Message(Model):
    created = DateTimeField(auto_now_add=True)
    modified = DateTimeField(auto_now=True)
    name = CharField(max_length=64)
    email = EmailField()
    message = TextField()
    sender_ip = GenericIPAddressField()


class ContactFormPage(RoutablePageMixin, Page, MenuPageMixin):
    body = StreamField([
        ('rich_text', RichTextBlock()),
        ('image', ImageChooserBlock())
    ])
    message_recipients = StreamField([
        ('email_address', EmailBlock())
    ])

    def serve(self, request, *args, **kwargs):
        from decruck.main.forms import ContactForm
        if request.method == 'POST':
            form = ContactForm(request.POST)
            if form.is_valid():
                # Get time from session and bounce the request
                # if it comes in too fast
                start = request.session.get('contact_form_GET_time', None)
                if not start:
                    raise SuspiciousOperation('Suspicious Operation')

                MIN_SECONDS = 5
                diff = int(time.time()) - start
                if diff < MIN_SECONDS:
                    raise SuspiciousOperation('Suspicious Operation')

                # honeypot field
                if form.cleaned_data.get('msg'):
                    raise SuspiciousOperation('Suspicious Operation')

                # Captcha validation
                if getattr(settings, 'CAPTCHA_SECRET_KEY', None):
                    response = requests.post(
                        'https://www.google.com/recaptcha/api/siteverify',
                        data={
                            'secret': getattr(
                                settings, 'CAPTCHA_SECRET_KEY', None),
                            'response': request.POST.get(
                                'g-recaptcha-response'),
                            'remoteip': request.META.get('REMOTE_ADDR')
                        }
                    )
                    if not response.json().get('success', False):
                        raise SuspiciousOperation()

                recipients = [
                    el['value'] for el in self.message_recipients.stream_data]
                name = form.cleaned_data.get('name')
                email = form.cleaned_data.get('email_address')
                message = form.cleaned_data.get('message')

                Message.objects.create(
                    name=name,
                    email=email,
                    message=message,
                    sender_ip=request.META.get('REMOTE_ADDR', '0.0.0.0')
                )

                plaintext = get_template('main/email/contact_form_message.txt')
                send_mail(
                    'Decruck Message Receieved',
                    plaintext.render({
                        'name': name,
                        'email': email,
                        'message': message
                    }),
                    'admin@' + settings.EN_HOST,
                    recipients
                )

                messages.add_message(
                    request,
                    messages.INFO,
                    _('Thank you for your message.')
                )

                # set current time in session
                request.session['contact_form_GET_time'] = int(time.time())
                ctx = {
                    'self': self,
                    'page': self,
                    'form': ContactForm()
                }
                return render(request, "main/contact_form_page.html", ctx)

            else:
                # set current time in session
                request.session['contact_form_GET_time'] = int(time.time())
                ctx = {
                    'self': self,
                    'page': self,
                    'form': form
                }
                return render(request, "main/contact_form_page.html", ctx)
        else:
            # set current time in session
            request.session['contact_form_GET_time'] = int(time.time())
            ctx = {
                'self': self,
                'page': self,
                'form': ContactForm()
            }
            return render(request, "main/contact_form_page.html", ctx)

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
        StreamFieldPanel('message_recipients'),
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

    def get_context(self, request, *args, **kwargs):
        return {
            'self': self,
            'page': self,
            'scores':
                ScorePage.objects.live().order_by('title'),
            'cart_page': ShoppingCartPage.objects.first()
        }


def score_in_cart(request, pk):
    if 'shopping_cart' in request.session and request.session['shopping_cart']:
        return pk in request.session['shopping_cart']
    return False


def toggle_score_in_cart(request, score_pk):
    """
    Toggles the presence of an item in the shopping cart.
    It returns the current state of the item in the cart.
    """
    if score_in_cart(request, score_pk):
        items = request.session['shopping_cart']
        request.session['shopping_cart'] = [x for x in items if x != score_pk]
        return False
    else:
        if 'shopping_cart' in request.session and request.session['shopping_cart']:
            request.session['shopping_cart'] += [score_pk]
        else:
            request.session['shopping_cart'] = [score_pk]
        return True


class Order(Model):
    INITIATED = 'INITIATED'
    PAYMENT_RECEIVED = 'PAYMENT_RECEIVED'
    FILE_LINKS_SENT = 'FILE_LINKS_SENT'
    STATUS_CHOICES = [
        (INITIATED, 'Initiated'),
        (PAYMENT_RECEIVED, 'Payment Received')
    ]
    created = DateTimeField(auto_now_add=True)
    modified = DateTimeField(auto_now=True)
    uuid = UUIDField(default=uuid.uuid4, unique=True, editable=False)
    status = CharField(
        max_length=24, choices=STATUS_CHOICES, default=INITIATED)
    initiator_ip = GenericIPAddressField()
    paypay_ipn = ForeignKey(
        PayPalIPN,
        on_delete=PROTECT,
        null=True,
        related_name='order'
    )
    first_name = CharField(max_length=256, blank=True)
    last_name = CharField(max_length=256, blank=True)
    email = EmailField(blank=True)
    total = DecimalField(max_digits=5, decimal_places=2)

    @property
    def order_number(self):
        return 1000 + self.pk

    @property
    def full_name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    @property
    def items_ordered(self):
        return ', '.join(str(i) for i in self.items.all())


class OrderItem(Model):
    created = DateTimeField(auto_now_add=True)
    modified = DateTimeField(auto_now=True)
    order = ForeignKey(
        'Order',
        on_delete=CASCADE,
        related_name='items'
    )
    item = ForeignKey(
        'ScorePage',
        on_delete=PROTECT,
        related_name='+'
    )
    price = DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.item.title


def plus_one_day():
    return timezone.now() + timedelta(days=1)


class OrderItemLink(Model):
    created = DateTimeField(auto_now_add=True)
    expires = DateTimeField(default=plus_one_day)
    accessed = DateTimeField(auto_now=True)
    access_ip = GenericIPAddressField(blank=True, null=True)
    slug = UUIDField(default=uuid.uuid4, unique=True, editable=False)
    order_item = ForeignKey(
        'OrderItem',
        on_delete=CASCADE,
        related_name='links'
    )

    @property
    def relative_url(self):
        return self.order_item.item.url + str(self.slug) + '/'

    @property
    def full_url(self):
        return self.order_item.item.full_url + str(self.slug) + '/'

    @property
    def item(self):
        return self.order_item.item

    def is_expired(self):
        return self.expires < timezone.now()


class ScorePage(RoutablePageMixin, Page):
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
    genre = ParentalManyToManyField(
        Genre,
        blank=True,
        related_name='scores'
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
        features=['bold', 'italic', 'link', 'document-link'],
        help_text='The materials sent in the PDF file.'
    )

    def save(self, *args, **kwargs):
        if self.preview_score_checked:
            # This was the cause of a subtle bug. Because this method can be
            # called multiple times during model creation, leaving this flag
            # set would cause the post save hook to fire multiple times.
            self.preview_score_updated = False
            return super().save(*args, **kwargs)

        h = hashlib.md5()
        for chunk in iter(lambda: self.preview_score.read(8192), b''):
            h.update(chunk)

        self.preview_score.seek(0)
        checksum = h.hexdigest()
        if not self.preview_score_checksum == checksum:
            self.preview_score_checksum = checksum
            self.preview_score_updated = True

        self.preview_score_checked = True
        return super().save(*args, **kwargs)

    @route(r'^([\w-]+)/$')
    def get_score_file(self, request, score_link_slug):
        if request.method == 'GET':
            item_link = get_object_or_404(OrderItemLink, slug=score_link_slug)

            if item_link.is_expired():
                raise Http404()

            item_link.access_ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
            item_link.save()

            return render(request, "main/score_page_download.html", {
                'self': self,
                'page': self,
            })
        else:
            raise Http404()

    @route(r'^$')
    def score(self, request):
        cart_page = ShoppingCartPage.objects.first()
        if request.method == 'POST':
            in_cart = toggle_score_in_cart(request, self.pk)
            return render(request, "main/score_page.html", {
                'self': self,
                'page': self,
                'in_cart': in_cart,
                'cart_page': cart_page
            })
        else:
            return render(request, "main/score_page.html", {
                'self': self,
                'page': self,
                'in_cart': score_in_cart(request, self.pk),
                'cart_page': cart_page
            })

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

    @route(r'retrieve-order/$')
    def retreive_order(self, request):
        # Local import to break circular dependency
        from decruck.main.forms import OrderRetrievalForm
        if request.method == 'POST':
            form = OrderRetrievalForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data.get('email_address')
                items = OrderItem.objects.filter(order__email=email)
                if items:
                    # Send email
                    links = []
                    for i in items:
                        link = OrderItemLink.objects.create(order_item=i)
                        links.append(link.full_url)

                    plaintext = get_template('main/email/order_retrieve.txt')
                    send_mail(
                        _('Your ordered items'),
                        plaintext.render({
                            'links': links,
                            'email': email,
                            'retrieval_form_url':
                                self.full_url + self.reverse_subpage('retreive_order')  # NOQA: E501
                        }),
                        settings.ORDER_EMAIL_ADDR,
                        [email],
                    )

                # Set message and render
                messages.add_message(
                    request,
                    messages.INFO,
                    _('If any orders exist for this email address, an email has been sent with links to your purchased scores.')  # NOQA: E501
                )
            ctx = {
                'self': self,
                'page': self,
                'form': form
            }
            return render(
                request, "main/shopping_cart_retrieve.html", ctx)
        else:
            ctx = {
                'self': self,
                'page': self,
                'form': OrderRetrievalForm()
            }
            return render(
                request, "main/shopping_cart_retrieve.html", ctx)

    @route(r'thank-you/$')
    def thank_you(self, request):
        context = self.get_context(request)
        if 'shopping_cart' in request.session and request.session['shopping_cart']:
            del request.session['shopping_cart']

        return render(request, "main/shopping_cart_thank_you.html", context)

    @route(r'remove/(\d+)/$')
    def remove_from_cart(self, request, item_pk):
        pk = int(item_pk)
        if request.method == 'POST' and score_in_cart(request, pk):
            toggle_score_in_cart(request, pk)

        return redirect(self.url)

    @route(r'confirmation/$')
    def order_confirmation(self, request):
        if request.method == 'GET':
            items = None
            total = 0.00
            if 'shopping_cart' in request.session and request.session['shopping_cart']:
                items = ScorePage.objects.filter(pk__in=request.session['shopping_cart'])
                total = sum([i.price for i in items])
            else:
                # If there is nothing in the cart, redirect to the cart page
                return redirect(self.url)

            if not items:
                # If for some reason the items can't be found
                return redirect(self.url)

            order = Order.objects.create(
                status=Order.INITIATED,
                initiator_ip=request.META.get('REMOTE_ADDR', '0.0.0.0'),
                total=total
            )

            for i in items:
                OrderItem.objects.create(order=order, item=i, price=i.price)

            ctx = self.get_context(request)

            form_data = {
                'business': settings.PAYPAL_ACCT_EMAIL,
                'amount': str(total),
                'notify_url': request.build_absolute_uri(
                    reverse('paypal-ipn')),
                'return': request.build_absolute_uri(
                    self.reverse_subpage('thank_you')),
                'cancel_return': request.build_absolute_uri(self.url),
                'item_name': 'Scores by Fernande Breilh Decruck',
                'item_number': order.uuid
            }

            ctx['items'] = items
            ctx['total'] = total
            ctx['checkout_form'] = PayPalPaymentsForm(initial=form_data)
            return render(request, "main/shopping_cart_confirmation.html", ctx)

    @route(r'^$')
    def cart_page(self, request):
        if request.method == 'GET':
            items = None
            total = 0.00
            if 'shopping_cart' in request.session and request.session['shopping_cart']:
                items = ScorePage.objects.filter(
                    pk__in=request.session['shopping_cart'])
                total = sum([i.price for i in items])

            ctx = self.get_context(request)

            ctx['items'] = items
            ctx['total'] = total
            return render(request, "main/shopping_cart.html", ctx)

        if request.method == 'POST':
            return redirect(
                self.url + self.reverse_subpage('order_confirmation'))

        return HttpResponse(status_code='405')


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
