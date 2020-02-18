import csv
import re
import string
from datetime import timedelta
from decruck.main.models import (
    CompositionPage, CompositionListingPage, Instrument, Genre,
    CompositionEDTF
)
from django.core.management.base import (
    BaseCommand, CommandError
)
from wagtail.core.rich_text import RichText


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('file', nargs=1)

    def handle(self, *args, **options):
        if CompositionPage.objects.all().exists():
            raise CommandError(
                'Compositions already exist in the database. '
                'Delete all compositions before trying to import again.'
            )

        try:
            parent = CompositionListingPage.objects.first()
        except CompositionListingPage.DoesNotExist:
            raise CommandError(
                'A composition listing page does not exist. '
                'A listing page is needed as a parent for composition pages'
            )

        with open(options['file'][0], newline='') as file:
            reader = csv.DictReader(file)
            for line, row in enumerate(reader):
                # Get or create genre
                genre = row.get('Genre', None)
                if genre:
                    genre, _ = Genre.objects.get_or_create(
                        genre=string.capwords(genre.strip()))

                # Assemble description from notes and movements
                description = []
                if row['Notes']:
                    description.append(('rich_text', RichText(row['Notes'])))

                if row['Movements']:
                    description.append(('rich_text', RichText(
                        '<h3>Movements</h3>' + row['Movements']
                    )))

                # Assemble duration
                duration = None
                d = row.get('Estimated Duration', None)
                if re.fullmatch(r'\d{,3}:\d{2}', d):
                    m, s = d.split(':')
                    duration = timedelta(minutes=int(m), seconds=int(s))
                elif d:
                    raise CommandError(
                        'Invalid duration format, row: {} title: {}'.
                        format(line + 2, row['Title'])
                    )

                # Assemble instrumentation
                instruments = []
                ints = row.get('Instrumentation', None)
                ints_list = [
                    string.capwords(i.strip()) for i
                    in ints.split(',') if len(i) > 0]
                for i in ints_list:
                    obj, _ = Instrument.objects.get_or_create(instrument=i)
                    instruments.append(obj)

                # Assemble recordings
                recording = None
                if row['Recording']:
                    recording = [('rich_text', RichText(row['Recording']))]

                comp = CompositionPage(
                    # If there's no Title, let it throw a KeyError
                    title=row['Title'],
                    composition_title=row['Title'],
                    description=description or None,
                    location=row.get('Where'),
                    orchestration=row.get('Orchestration'),
                    duration=duration,
                    dedicatee=row.get('Dedication'),
                    genre=genre,
                    text_source=row.get('Text Source'),
                    collaborator=row.get('Collaborator?'),
                    manuscript_status=row.get('Manuscript Status English'),
                    published_work_link=None,
                    recording=recording
                )
                parent.add_child(instance=comp)
                comp.save_revision().publish()

                # Add instruments
                for i in instruments:
                    comp.instrumentation.add(i)
                comp.save_revision().publish()

                # Add EDTF Date
                nat_lang = row.get('Natural Language Date', None)
                edtf = row.get('EDTF Date', None)
                if edtf:
                    nat_lang = nat_lang.strip()
                    edtf = edtf.strip()
                    edtf_obj = CompositionEDTF(
                        nat_lang_edtf_string=nat_lang,
                        edtf_string=edtf,
                        composition=comp
                    )
                    edtf_obj.save()
