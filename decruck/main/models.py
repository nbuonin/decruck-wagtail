from wagtail.core.models import Page


class HomePage(Page):
    class Meta:
        verbose_name = "Homepage"

    parent_page_types = ['wagtailcore.Page']
