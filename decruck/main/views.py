from decruck.main.models import CompositionPage, OrderItem
from wagtail.admin.views.reports import PageReportView


class CompositionReportView(PageReportView):
    title = 'Compositions'
    list_export = [
        'genre', 'composition_title', 'description', 'nat_lang_date',
        'location', 'instrumentation_list', 'orchestration', 'duration',
        'manuscript_status', 'collaborator', 'text_source', 'dedicatee',
    ]
    header_icon = 'doc-empty-inverse'

    def get_queryset(self):
        return CompositionPage.objects.all()


class OrderReportView(PageReportView):
    title = 'Orders'
    list_export = [
        'order_number', 'total', 'full_name', 'email', 'created', 'modified',
        'status', 'items_ordered',
    ]
    header_icon = 'doc-empty-inverse'

    def get_queryset(self):
        return OrderItem.objects.all().order_by('created')
