"""Bootstrap the site from a clean database"""
from decruck.main.models import (
    HomePage, CompositionListingPage
)
from django.core.management.base import (
    BaseCommand, CommandError
)
from wagtail.core.models import Page, Site


class Command(BaseCommand):
    """Build out the basic site tree"""
    def handle(self, *args, **options):
        if Page.objects.count() > 2:
            raise CommandError('There already exists content in the database.')
        # Delete the existing 'Welcome to Wagtail' page
        Page.objects.get(id=2).delete()
        Site.objects.all().delete()

        root = Page.objects.get(id=1)
        homepage = HomePage(title='Decruck')
        root.add_child(instance=homepage)
        homepage.save_revision().publish()

        Site.objects.create(
            hostname='localhost',
            root_page_id=homepage.id,
            is_default_site=True
        )

        comp = CompositionListingPage(title='compositions')
        homepage.add_child(instance=comp)
        comp.save_revision().publish()
