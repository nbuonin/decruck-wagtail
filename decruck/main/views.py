from decruck.main.models import CompositionPage, Order, Message
from wagtail.admin.views.reports import PageReportView, ReportView


class CompositionReportView(PageReportView):
    title = 'Compositions'
    list_export = [
        'information_up_to_date', 'genre', 'composition_title', 'description',
        'nat_lang_date', 'location', 'instrumentation_list', 'orchestration',
        'duration', 'manuscript_status_en', 'manuscript_status_fr',
        'collaborator', 'text_source', 'dedicatee', 'premiere', 'scanned'
    ]
    header_icon = 'doc-empty-inverse'

    def get_queryset(self):
        return CompositionPage.objects.all()


class OrderReportView(ReportView):
    title = 'Orders'
    list_export = [
        'order_number', 'total', 'full_name', 'email', 'created', 'modified',
        'status', 'items_ordered',
    ]
    header_icon = 'doc-empty-inverse'

    def get_queryset(self):
        return Order.objects.all().order_by('created')


class MessageReportView(ReportView):
    title = 'Messages'
    list_export = [
        'name', 'email', 'message'
    ]
    header_icon = 'doc-empty-inverse'

    def get_queryset(self):
        return Message.objects.all().order_by('created')
