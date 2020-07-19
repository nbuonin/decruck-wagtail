from io import BytesIO
from decimal import Decimal
from decruck.main.models import (
    CompositionPage, ScorePage, PreviewScoreImage, Order, OrderItem,
    OrderItemLink, Message, Instrument, Genre
)
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.images import ImageFile
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import get_template
from django.utils.safestring import mark_safe
import math
from paypal.standard.ipn.signals import valid_ipn_received
from paypal.standard.models import ST_PP_COMPLETED
from pdf2image import convert_from_bytes
import tempfile
from wagtail.contrib.modeladmin.helpers import (
    PermissionHelper, PageButtonHelper
)
from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register
)


class ProtectModelPermissionHelper(PermissionHelper):
    def user_can_create(self, user):
        return False

    def user_can_edit_obj(self, user, obj):
        return False

    def user_can_delete_obj(self, user, obj):
        return False


class CompositionPageAdmin(ModelAdmin):
    model = CompositionPage

    menu_label = 'Compositions'
    menu_icon = 'doc-full-inverse'
    menu_order = 200
    list_display = ('genre', 'title', 'year', 'instrument_list')
    list_filter = ('genre', 'instrumentation')
    search_fields = (
        'composition_title', 'description', 'location', 'dedicatee',
        'text_source', 'collaborator', 'manuscript_status', 'recording'
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by('title')

    def instrument_list(self, obj):
        return ', '.join([i.instrument for i in obj.instrumentation.all()])

    def year(self, obj):
        return obj.date.first().nat_lang_year if obj.date.first() else None


modeladmin_register(CompositionPageAdmin)


class InstrumentAdmin(ModelAdmin):
    model = Instrument

    menu_label = 'Instruments'
    menu_icon = 'doc-full-inverse'
    menu_order = 210
    list_display = ('instrument',)
    search_fields = ('instrument_en', 'instrument_fr')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by('instrument')


modeladmin_register(InstrumentAdmin)


class GenreAdmin(ModelAdmin):
    model = Genre

    menu_label = 'Genres'
    menu_icon = 'doc-full-inverse'
    menu_order = 215
    list_display = ('genre',)
    search_fields = ('genre_en', 'genre_fr')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by('genre')


modeladmin_register(GenreAdmin)


class MessageAdmin(ModelAdmin):
    model = Message
    permission_helper_class = ProtectModelPermissionHelper
    menu_label = 'Contact Form Messages'
    menu_icon = 'form'
    menu_order = 400
    list_display = ('created', 'name', 'email')
    search_fields = (
        'name', 'email', 'message',
    )
    inspect_view_enabled = True


modeladmin_register(MessageAdmin)


@receiver(post_save, sender=ScorePage)
def generate_score_preview(sender, instance, created, update_fields, **kwargs):
    if instance.preview_score_updated:
        PreviewScoreImage.objects.filter(score=instance.pk).delete()

        with tempfile.TemporaryDirectory() as path:
            images = convert_from_bytes(
                instance.preview_score.read(),
                fmt='jpeg',
                output_folder=path,
                paths_only=True,
                size=(555, None)
            )

            for idx, img_path in enumerate(images):
                file_name = '{}-{:03d}.jpg'.format(
                    instance.preview_score.name, idx)

                with open(img_path, mode='rb') as img:
                    # Instantiate an uploaded file object
                    img_file = InMemoryUploadedFile(
                        file=img,
                        field_name=None,
                        name=file_name,
                        size=img.tell,
                        content_type='image/jpeg',
                        charset=None,
                        content_type_extra=None
                    )
                    PreviewScoreImage.objects.create(
                        score=instance,
                        preview_score_image=img_file,
                        page_number=idx
                    )


@receiver(valid_ipn_received)
def process_order(sender, **kwargs):
    ipn_obj = sender
    if ipn_obj.payment_status == ST_PP_COMPLETED:
        # Validate the reciever email
        if ipn_obj.receiver_email != settings.PAYPAL_ACCT_EMAIL:
            return

        # Validate the order exists and the gross amount matches
        try:
            order = Order.objects.get(uuid=ipn_obj.item_number)
        except (Order.DoesNotExist, ValidationError):
            return

        if order.total != Decimal(ipn_obj.mc_gross):
            return

        # Update the order
        order.paypal_ipn = ipn_obj
        order.first_name = ipn_obj.first_name
        order.last_name = ipn_obj.last_name
        order.email = ipn_obj.payer_email
        order.total = ipn_obj.mc_gross
        order.status = Order.PAYMENT_RECEIVED
        order.save()

        links = []
        # Create the order items and links
        for i in order.items.all():
            link = OrderItemLink.objects.create(order_item=i)
            links.append(link.full_url)

        # Send a thank you email
        ctx = {
            'order': order,
            'links': links
        }
        plaintext = get_template('main/email/order_thank_you.txt')
        send_mail(
            'Thank you for your order / Merci pour votre commande',
            plaintext.render(ctx),
            settings.ORDER_EMAIL_ADDR,
            [ipn_obj.payer_email],
        )
