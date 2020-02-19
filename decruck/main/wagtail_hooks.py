from decruck.main.models import CompositionPage
from django.utils.safestring import mark_safe
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
