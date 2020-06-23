"""Custom test runner to initialize test database with Wagtail models"""
from django.core.management import call_command
from django.test.runner import DiscoverRunner


class DecruckTestRunner(DiscoverRunner):
    """Custom test runner
    This runner initializes the test database pages to test against
    """
    def setup_databases(self, **kwargs):
        dbs = super().setup_databases(**kwargs)

        # Run the Wagtail Translation commands to sync the database
        call_command('sync_page_translation_fields')
        call_command('update_translation_fields')
        call_command('bootstrap')

        return dbs
