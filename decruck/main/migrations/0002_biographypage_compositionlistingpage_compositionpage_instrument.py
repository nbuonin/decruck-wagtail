# Generated by Django 2.2.7 on 2019-12-22 17:07

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0041_group_collection_permissions_verbose_name_plural'),
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BiographyPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('body', wagtail.core.fields.StreamField([('paragraph', wagtail.core.blocks.RichTextBlock()), ('image', wagtail.images.blocks.ImageChooserBlock())])),
            ],
            options={
                'verbose_name': 'Biography Page',
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='CompositionListingPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
            ],
            options={
                'verbose_name': 'Composition Listing Page',
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='Instrument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('instrument', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='CompositionPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('composition_title', wagtail.core.fields.RichTextField()),
                ('description', wagtail.core.fields.StreamField([('paragraph', wagtail.core.blocks.RichTextBlock()), ('image', wagtail.images.blocks.ImageChooserBlock())], blank=True)),
                ('location', wagtail.core.fields.RichTextField(blank=True)),
                ('orchestral_instrumentation', wagtail.core.fields.RichTextField(blank=True)),
                ('duration', models.DurationField(blank=True, null=True)),
                ('dedicatee', wagtail.core.fields.RichTextField(blank=True)),
                ('genre', models.CharField(blank=True, choices=[('ARRANGEMENTS', 'Arrangements'), ('CHAMBER', 'Chamber Music'), ('ETUDES', 'Etudes'), ('ORCHESTRAL', 'Orchstral Music'), ('ORGAN', 'Organ Music'), ('SOLO_PIANO', 'Solo Piano Music'), ('ART_SONG', 'Art Song'), ('CHORAL', 'Choral')], max_length=256)),
                ('text_source', wagtail.core.fields.RichTextField(blank=True)),
                ('collaborator', wagtail.core.fields.RichTextField(blank=True)),
                ('manuscript_status', wagtail.core.fields.RichTextField(blank=True)),
                ('published_work_link', models.URLField(blank=True)),
                ('recording_link', models.CharField(blank=True, max_length=256)),
                ('instrumentation', modelcluster.fields.ParentalManyToManyField(blank=True, to='main.Instrument')),
            ],
            options={
                'verbose_name': 'Composition',
            },
            bases=('wagtailcore.page',),
        ),
    ]
