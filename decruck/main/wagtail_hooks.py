from io import BytesIO
from decruck.main.models import (
    CompositionPage, ScorePage, PreviewScoreImage,
    PreviewScoreImageProcessingLock
)
from django import db
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.safestring import mark_safe
from pdf2image import convert_from_bytes
from threading import Thread
from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register
)


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


def process_score_preview_images(instance):
    # Delete existing images if they exist
    PreviewScoreImage.objects.filter(score=instance.pk).delete()

    images = convert_from_bytes(instance.preview_score.read())
    for idx, img in enumerate(images):
        file_name = '{}-{:03d}.jpg'.format(
            instance.preview_score.name, idx)

        buffer = BytesIO()
        img.save(buffer, 'JPEG')

        img_file = InMemoryUploadedFile(
            file=buffer,
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

    PreviewScoreImageProcessingLock.objects.get(score=instance).delete()


@receiver(post_save, sender=ScorePage)
def generate_score_preview(sender, instance, created, update_fields, **kwargs):
    if instance.preview_score_updated:
        PreviewScoreImageProcessingLock.objects.create(score=instance)
        # Close all DB threads before forking
        db.connections.close_all()
        thread = Thread(target=process_score_preview_images, args=[instance])
        thread.start()
