"""Bootstrap the site from a clean database"""
from decruck.main.models import (
    HomePage, CompositionListingPage, BiographyPage, ScoreListingPage,
    ShoppingCartPage, ContactFormPage
)
from django.core.management import call_command
from django.core.management.base import (
    BaseCommand, CommandError
)
from django.core.serializers.json import DjangoJSONEncoder
import json
from wagtail.core import blocks
from wagtail.core.models import Page, Site
from wagtail.core.rich_text import RichText


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

        # Create Compostion listing page
        comp = CompositionListingPage(title='Compositions')
        homepage.add_child(instance=comp)
        comp.save_revision().publish()

        # Create a Bio page
        bio_page = BiographyPage(
            title='Biography',
            show_in_menus=True,
            body=[
                ('heading', {
                    'left_column': 'Foo',
                    'right_column': 'bar'
                })
            ]
        )
        homepage.add_child(instance=bio_page)
        bio_page.save_revision().publish()

        # Score listing page
        score_listing = ScoreListingPage(
            title='Shop',
            show_in_menus=True,
            description=[('rich_text', RichText('<p>Description text</p>'))],
        )
        homepage.add_child(instance=score_listing)
        score_listing.save_revision().publish()

        # Shopping cart page
        cart = ShoppingCartPage(
            title='Cart',
            show_in_menus=True,
            body=[('rich_text', RichText('<p>Body text</p>'))],
            confirmation_page_text=[
                ('rich_text', RichText('<p>Confirmation text</p>'))]
        )
        score_listing.add_child(instance=cart)
        cart.save_revision().publish()

        # Contact Form Page
        contact = ContactFormPage(
            title='Contact',
            body=[('rich_text', RichText('<p>Body text</p>'))],
            message_recipients=[('email_address', 'admin@fernandedecruck.com')]
        )
        homepage.add_child(instance=contact)
        contact.save_revision().publish()

        # Create the main menu
        call_command('autopopulate_main_menus')
