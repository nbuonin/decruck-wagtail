from io import BytesIO
from decruck.main.models import CompositionPage, ScorePage, PreviewScoreImage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.safestring import mark_safe
from pdf2image import convert_from_bytes
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


@receiver(post_save, sender=ScorePage)
def generate_score_preview(sender, instance, created, update_fields, **kwargs):
    print('post save called')
    if instance.preview_score_updated:
        print('images are being updated')
        if update_fields:
            PreviewScoreImage.objects.filter(score=instance.pk).delete()

        images = convert_from_bytes(instance.preview_score.read())

        for idx, img in enumerate(images):
            file_name = '{}-{:03d}.jpg'.format(
                instance.preview_score.name, idx)

            # Write the extracted image to a buffer
            buffer = BytesIO()
            img.save(buffer, 'JPEG')

            # Instantiate an uploaded file object, and create a new object
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
        return

    return


